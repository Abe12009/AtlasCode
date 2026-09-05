"""Apply the authored FR/AR block translations to a freshly seeded database.

Courses 1-5 declare their lesson blocks without translations, so a plain seed
leaves French and Arabic learners reading English lesson bodies. The authored
translations live in the block_translations_* modules and are matched on the
block's English text, not its id, so this stays correct no matter what ids a
fresh seed assigns.
"""

from sqlalchemy import select

from app.models import LessonBlock, LessonBlockTranslation

from .block_translations_cs import CS_FUNDAMENTALS_BLOCKS
from .block_translations_python import PYTHON_FOUNDATIONS_BLOCKS
from .block_translations_web_sql_git import WEB_SQL_GIT_BLOCKS

LANGUAGES = ("en", "fr", "ar")


def _by_english_text() -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {}
    for source in (PYTHON_FOUNDATIONS_BLOCKS, WEB_SQL_GIT_BLOCKS, CS_FUNDAMENTALS_BLOCKS):
        for texts in source.values():
            key = texts["en"].strip()
            # Every authored English text is unique; assert it so a future edit
            # that introduces a collision fails loudly instead of mistranslating.
            assert key not in index, f"duplicate English block text: {key[:60]!r}"
            index[key] = texts
    return index


async def apply_block_translations(db) -> int:
    """Insert en/fr/ar rows for blocks that have none. Returns rows written."""
    index = _by_english_text()

    existing = {
        block_id
        for (block_id,) in (
            await db.execute(select(LessonBlockTranslation.block_id).distinct())
        ).all()
    }

    written = 0
    blocks = (await db.execute(select(LessonBlock))).scalars().all()
    for block in blocks:
        if block.id in existing:
            continue
        texts = index.get((block.content or "").strip())
        if texts is None:
            continue
        for language in LANGUAGES:
            db.add(
                LessonBlockTranslation(
                    block_id=block.id,
                    language=language,
                    content=texts[language],
                    # Code is code: identical in every language.
                    code_example=block.code_example,
                )
            )
            written += 1
    await db.flush()
    return written
