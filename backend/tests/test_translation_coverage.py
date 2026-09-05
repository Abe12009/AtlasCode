"""Every translatable curriculum entity must exist in en, fr and ar.

Courses 1-5 shipped their lesson blocks with English bodies only, so French and
Arabic learners read English lesson content in the five original courses. These
tests keep that from coming back, and are the automated check that the seeded
database really carries all three languages.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select

from app.models import (
    Course,
    Exercise,
    ExerciseOption,
    ExerciseOptionTranslation,
    ExerciseTranslation,
    Lesson,
    LessonBlock,
    LessonBlockTranslation,
    LessonTranslation,
    Module,
    ModuleTranslation,
)

LANGUAGES = {"en", "fr", "ar"}


async def missing_languages(db_session, parent_model, child_model, fk_attr):
    """Ids of parent rows that lack at least one of en/fr/ar."""
    parents = (await db_session.execute(select(parent_model.id))).scalars().all()
    rows = (
        await db_session.execute(
            select(getattr(child_model, fk_attr), child_model.language)
        )
    ).all()

    seen: dict[int, set[str]] = {}
    for parent_id, language in rows:
        seen.setdefault(parent_id, set()).add(
            language.value if hasattr(language, "value") else language
        )

    return [pid for pid in parents if not LANGUAGES.issubset(seen.get(pid, set()))]


class TestCurriculumTranslationCoverage:
    async def test_every_lesson_block_has_all_three_languages(self, db_session):
        incomplete = await missing_languages(
            db_session, LessonBlock, LessonBlockTranslation, "block_id"
        )
        assert incomplete == [], f"lesson blocks missing en/fr/ar: {incomplete}"

    async def test_every_lesson_has_all_three_languages(self, db_session):
        incomplete = await missing_languages(
            db_session, Lesson, LessonTranslation, "lesson_id"
        )
        assert incomplete == [], f"lessons missing en/fr/ar: {incomplete}"

    async def test_every_module_has_all_three_languages(self, db_session):
        incomplete = await missing_languages(
            db_session, Module, ModuleTranslation, "module_id"
        )
        assert incomplete == [], f"modules missing en/fr/ar: {incomplete}"

    async def test_every_exercise_has_all_three_languages(self, db_session):
        incomplete = await missing_languages(
            db_session, Exercise, ExerciseTranslation, "exercise_id"
        )
        assert incomplete == [], f"exercises missing en/fr/ar: {incomplete}"

    async def test_every_exercise_option_has_all_three_languages(self, db_session):
        incomplete = await missing_languages(
            db_session, ExerciseOption, ExerciseOptionTranslation, "option_id"
        )
        assert incomplete == [], f"exercise options missing en/fr/ar: {incomplete}"

    async def test_no_translation_row_is_blank(self, db_session):
        blank = (
            await db_session.execute(
                select(func.count())
                .select_from(LessonBlockTranslation)
                .where(
                    (LessonBlockTranslation.content.is_(None))
                    | (func.trim(LessonBlockTranslation.content) == "")
                )
            )
        ).scalar()
        assert blank == 0, "a blank translation renders as an empty lesson"

    async def test_code_examples_are_identical_in_every_language(self, db_session):
        """Code is code: translating identifiers would break the lesson."""
        rows = (
            await db_session.execute(
                select(LessonBlockTranslation.block_id, LessonBlockTranslation.code_example,
                       LessonBlock.code_example)
                .join(LessonBlock, LessonBlock.id == LessonBlockTranslation.block_id)
            )
        ).all()
        drifted = [
            block_id
            for block_id, translated, base in rows
            if (translated or "") != (base or "")
        ]
        assert drifted == [], f"blocks whose translated code differs from the source: {drifted}"


class TestTranslatedContentIsActuallyDifferent:
    """Coverage alone is not quality: prose must genuinely change per language."""

    async def test_original_course_blocks_are_not_english_in_french(self, db_session):
        """Course 1's block bodies used to be English in every language."""
        rows = (
            await db_session.execute(
                select(LessonBlockTranslation.block_id, LessonBlockTranslation.language,
                       LessonBlockTranslation.content)
                .join(LessonBlock, LessonBlock.id == LessonBlockTranslation.block_id)
                .join(Lesson, Lesson.id == LessonBlock.lesson_id)
                .join(Module, Module.id == Lesson.module_id)
                .where(Module.course_id == 1, LessonBlock.block_type == "text")
            )
        ).all()
        assert rows, "expected translated text blocks in course 1"

        by_block: dict[int, dict[str, str]] = {}
        for block_id, language, content in rows:
            key = language.value if hasattr(language, "value") else language
            by_block.setdefault(block_id, {})[key] = content

        identical = [
            block_id
            for block_id, texts in by_block.items()
            if len(LANGUAGES.intersection(texts)) == 3
            and (texts["fr"] == texts["en"] or texts["ar"] == texts["en"])
        ]
        assert identical == [], f"blocks whose fr/ar body is still the English text: {identical}"

    async def test_arabic_block_bodies_contain_arabic_script(self, db_session):
        rows = (
            await db_session.execute(
                select(LessonBlockTranslation.block_id, LessonBlockTranslation.content)
                .join(LessonBlock, LessonBlock.id == LessonBlockTranslation.block_id)
                .join(Lesson, Lesson.id == LessonBlock.lesson_id)
                .join(Module, Module.id == Lesson.module_id)
                .where(
                    LessonBlockTranslation.language == "ar",
                    Module.course_id <= 5,
                    LessonBlock.block_type == "text",
                )
            )
        ).all()
        assert rows, "expected Arabic text blocks in the original courses"

        def has_arabic(text: str) -> bool:
            return any("؀" <= ch <= "ۿ" for ch in (text or ""))

        without = [block_id for block_id, content in rows if not has_arabic(content)]
        assert without == [], f"Arabic blocks with no Arabic script: {without}"


class TestApiServesTranslatedBlocks:
    async def test_lesson_endpoint_returns_the_requested_language(
        self, client: AsyncClient, test_user
    ):
        """Lesson 1 is in course 1, the worst-affected course."""
        seen = {}
        for language in ("en", "fr", "ar"):
            lesson = (
                await client.get(
                    f"/lessons/1?language={language}", headers=test_user["headers"]
                )
            ).json()
            text_blocks = [b for b in lesson["blocks"] if b["block_type"] == "text"]
            assert text_blocks, "expected text blocks on lesson 1"
            block = text_blocks[0]
            assert block["translations"], f"no {language} translation served for block {block['id']}"
            assert block["translations"][0]["language"] == language
            seen[language] = block["translations"][0]["content"]

        assert seen["en"] != seen["fr"], seen
        assert seen["en"] != seen["ar"], seen
        assert any("؀" <= ch <= "ۿ" for ch in seen["ar"]), seen["ar"]
