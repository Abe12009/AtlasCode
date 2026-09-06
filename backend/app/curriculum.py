"""The AtlasCode curriculum roadmap.

This is the single source of truth for *where each course sits in the degree*:
its stage, its position, the course a student should finish first, and the
metadata the UI groups by. Content lives in ``app.seed.*``; ordering lives
here, so the roadmap can be reasoned about — and reordered — without touching a
single lesson.

The progression is deliberately conventional: a student meets binary before
Big-O, Big-O before cryptography, and programming before software engineering.
Prerequisites are advisory. They order the roadmap and are surfaced in the UI,
but nothing is hard-locked: a student arriving with prior knowledge is not made
to re-take material they already know.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

#: Stage keys are stable; titles are translated in the frontend locale files
#: under `curriculum.stages.*`, because they are user-facing UI text.
STAGES: tuple[tuple[int, str], ...] = (
    (1, "foundations"),
    (2, "programming"),
    (3, "theory"),
    (4, "systems"),
    (5, "engineering"),
    (6, "security"),
    (7, "ai"),
    (8, "advanced"),
)

STAGE_KEYS: dict[int, str] = dict(STAGES)


@dataclass(frozen=True)
class RoadmapEntry:
    """Where one course sits in the roadmap."""

    slug: str
    stage: int
    track: str
    icon: str
    difficulty: str
    estimated_hours: int
    prerequisite_slug: Optional[str] = None


#: Declaration order *is* `Course.order`, so inserting a course here moves
#: everything after it — which is exactly what reordering a syllabus means.
ROADMAP: tuple[RoadmapEntry, ...] = (
    # --- Stage 1 · Computer Science Foundations ----------------------------
    RoadmapEntry("cs-foundations", 1, "foundations", "🧭", "beginner", 6),
    RoadmapEntry("computational-thinking", 1, "foundations", "🧩", "beginner", 6, "cs-foundations"),
    # --- Stage 2 · Programming --------------------------------------------
    RoadmapEntry("python-basics", 2, "programming", "🐍", "beginner", 12, "computational-thinking"),
    RoadmapEntry("python-in-depth", 2, "programming", "⚡", "intermediate", 10, "python-basics"),
    RoadmapEntry("git-github", 2, "programming", "🌿", "beginner", 5, "python-basics"),
    # --- Stage 3 · Core Computer Science ----------------------------------
    RoadmapEntry("discrete-mathematics", 3, "theory", "∑", "intermediate", 10, "computational-thinking"),
    RoadmapEntry("math-for-cs", 3, "theory", "📐", "intermediate", 8, "discrete-mathematics"),
    RoadmapEntry("data-structures-algorithms", 3, "theory", "🌳", "intermediate", 14, "python-in-depth"),
    RoadmapEntry("algorithms-complexity", 3, "theory", "⏱️", "intermediate", 12, "data-structures-algorithms"),
    RoadmapEntry("cs-fundamentals", 3, "theory", "🎓", "intermediate", 8, "python-basics"),
    # --- Stage 4 · Data, Systems and Networks ------------------------------
    RoadmapEntry("sql-databases", 4, "systems", "🗄️", "beginner", 6, "python-basics"),
    RoadmapEntry("database-design", 4, "systems", "🏛️", "beginner", 8, "sql-databases"),
    RoadmapEntry("networking", 4, "systems", "🌐", "intermediate", 10, "cs-foundations"),
    RoadmapEntry("computer-systems", 4, "systems", "🖥️", "intermediate", 10, "cs-foundations"),
    RoadmapEntry("c-programming", 4, "systems", "🔧", "intermediate", 12, "python-basics"),
    RoadmapEntry("cpp-programming", 4, "systems", "🧱", "advanced", 12, "c-programming"),
    # --- Stage 5 · Software and Web Engineering ----------------------------
    RoadmapEntry("web-basics", 5, "engineering", "📄", "beginner", 6, "python-basics"),
    RoadmapEntry("javascript", 5, "engineering", "🟨", "beginner", 10, "web-basics"),
    RoadmapEntry("frontend-development", 5, "engineering", "🎨", "intermediate", 10, "javascript"),
    RoadmapEntry("backend-development", 5, "engineering", "🔌", "intermediate", 12, "python-in-depth"),
    RoadmapEntry("fullstack-development", 5, "engineering", "🧬", "advanced", 12, "backend-development"),
    RoadmapEntry("software-engineering", 5, "engineering", "🏗️", "intermediate", 12, "git-github"),
    # --- Stage 6 · Cybersecurity -------------------------------------------
    RoadmapEntry("cybersecurity-foundations", 6, "security", "🛡️", "intermediate", 10, "networking"),
    RoadmapEntry("network-security-fundamentals", 6, "security", "🔐", "intermediate", 10, "cybersecurity-foundations"),
    RoadmapEntry("secure-software-development", 6, "security", "🧰", "advanced", 10, "cybersecurity-foundations"),
    # --- Stage 7 · Artificial Intelligence ---------------------------------
    RoadmapEntry("ai-foundations", 7, "ai", "🤖", "intermediate", 8, "math-for-cs"),
    RoadmapEntry("machine-learning-fundamentals", 7, "ai", "📊", "advanced", 12, "ai-foundations"),
    RoadmapEntry("ai-literacy", 7, "ai", "🧠", "beginner", 6, "ai-foundations"),
    # --- Stage 8 · Advanced Computer Science -------------------------------
    RoadmapEntry("operating-systems", 8, "advanced", "⚙️", "advanced", 12, "computer-systems"),
    RoadmapEntry("computer-architecture", 8, "advanced", "🔬", "advanced", 12, "computer-systems"),
    RoadmapEntry("advanced-computing", 8, "advanced", "🚀", "advanced", 14, "algorithms-complexity"),
)

ROADMAP_BY_SLUG: dict[str, RoadmapEntry] = {entry.slug: entry for entry in ROADMAP}

#: `Course.order` for each slug: 1-based position in ROADMAP.
ORDER_BY_SLUG: dict[str, int] = {entry.slug: i for i, entry in enumerate(ROADMAP, start=1)}

#: Courses that existed before the roadmap was introduced. They keep their
#: content and their rows; only their placement metadata is refreshed.
LEGACY_SLUGS: frozenset[str] = frozenset(
    {
        "python-basics",
        "web-basics",
        "sql-databases",
        "git-github",
        "cs-fundamentals",
        "javascript",
        "frontend-development",
        "backend-development",
        "fullstack-development",
        "c-programming",
        "cpp-programming",
        "data-structures-algorithms",
        "computer-systems",
        "networking",
    }
)
