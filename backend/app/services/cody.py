"""Cody: the in-app AI companion that answers computer science questions.

Design constraints this module enforces:

- The OpenRouter API key never leaves the backend process (app.core.config,
  read from the server environment only) and is never included in any
  response body or log line.
- Every call is scoped to the *requesting* user's own data. Progression
  context is assembled from ``current_user``'s own StudentProfile/
  CourseProgress rows only -- there is no code path here that can look up
  another user's data, because nothing is ever queried by anything other
  than the authenticated caller's own id.
- The system prompt keeps Cody on-topic (computer science) and instructs it
  to decline unrelated questions politely rather than silently answering
  them, so the feature doesn't quietly turn into a general-purpose chatbot.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from openrouter import OpenRouter

from app.core.config import get_settings
from app.models import CodyMessage, Course, CourseProgress, StudentProfile, User

SYSTEM_PROMPT = """You are Cody, the friendly AI companion built into AtlasCode, \
a computer science learning platform.

Scope: answer questions about computer science -- programming, algorithms, \
data structures, databases, networking, operating systems, software \
engineering, math for CS, cybersecurity, and AtlasCode's own courses. If a \
question is clearly unrelated to computer science or this app (e.g. \
medical, legal, or personal-life advice), politely decline and steer the \
conversation back to what you can help with. Don't lecture the user about \
the boundary at length -- one short sentence, then offer to help with \
something CS-related.

Style: concise, encouraging, and precise. Prefer short explanations with a \
concrete example or snippet over long abstract ones. When the user's own \
progress data is provided below, use it naturally to personalize answers \
(e.g. recommending a sensible next topic) -- never invent progress data \
that wasn't given to you.
"""


@dataclass(frozen=True)
class CodyReply:
    content: str


class CodyNotConfiguredError(RuntimeError):
    """Raised when OPENROUTER_API_KEY is unset -- Cody is disabled."""


async def build_progression_context(db, user: User) -> str:
    """Summarize the *requesting* user's own progress as plain text for the
    system prompt. Every query below is filtered by ``user.id`` -- there is
    no parameter here that could pull another account's data.
    """
    from sqlalchemy import select  # local import keeps this module's top-level surface small

    profile_result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()

    course_progress_result = await db.execute(
        select(CourseProgress, Course.slug)
        .join(Course, Course.id == CourseProgress.course_id)
        .where(CourseProgress.user_id == user.id)
    )
    course_progress = course_progress_result.all()

    if not profile:
        return "This user has no progress yet -- they're brand new to AtlasCode."

    in_progress = [slug for cp, slug in course_progress if 0 < (cp.progress_percent or 0) < 100]
    completed = [slug for cp, slug in course_progress if (cp.progress_percent or 0) >= 100]

    lines = [
        f"XP: {profile.xp}, Level: {profile.level}, current streak: {profile.streak} day(s).",
        f"Lessons completed: {profile.completed_lessons}, projects completed: {profile.completed_projects}.",
    ]
    if in_progress:
        lines.append(f"Course(s) currently in progress: {in_progress}.")
    if completed:
        lines.append(f"Course(s) completed: {completed}.")
    return " ".join(lines)


#: OpenRouter's chat/completions format already uses "user"/"assistant" --
#: the same roles CodyMessage.role.value is stored as (see CodyRoleEnum) --
#: so no per-turn role translation is needed here.
def _to_openrouter_messages(
    system: str, history: Sequence[CodyMessage], new_user_message: str
) -> list[dict]:
    messages = [{"role": "system", "content": system}]
    messages.extend({"role": m.role.value, "content": m.content} for m in history)
    messages.append({"role": "user", "content": new_user_message})
    return messages


async def get_reply(db, user: User, history: Sequence[CodyMessage], user_message: str) -> CodyReply:
    settings = get_settings()
    if not settings.openrouter_api_key:
        raise CodyNotConfiguredError("OPENROUTER_API_KEY is not set")

    progression = await build_progression_context(db, user)
    system = f"{SYSTEM_PROMPT}\n\nThis user's own progress (share only with them, as context, not as raw data dump):\n{progression}"

    async with OpenRouter(api_key=settings.openrouter_api_key) as client:
        response = await client.chat.send_async(
            model=settings.cody_model,
            messages=_to_openrouter_messages(system, history, user_message),
            max_tokens=1024,
        )
    content = response.choices[0].message.content
    if isinstance(content, list):
        content = "".join(part.text for part in content if getattr(part, "type", None) == "text")
    return CodyReply(content=content or "")
