"""Audit every Micro-Quest lesson in the database.

Run:  python check_microquests.py [path/to/atlascode.db]

A Micro-Quest is any lesson carrying a 'hook' block. Everything downstream --
the frontend's MicroQuestLesson, its blueprint renderer, the Quest Clear
screen -- assumes a set of invariants that ordinary lessons do not have to
satisfy, and this checks every one of them against the real database:

  * exactly one hook, one blueprint and one exam_tip per Micro-Quest lesson
  * no duplicate blueprint (or hook, or exam tip) rows
  * every hook/blueprint/exam_tip config is valid JSON with a 'kind'
  * every blueprint kind is one the frontend can actually render
  * order_steps configs: >= 2 uniquely-identified steps, and a correct_order
    that is a permutation of exactly those step ids
  * match_pairs configs: >= 2 uniquely-identified pairs, each with both sides
    written in every required language
  * spot_the_bug configs: >= 3 uniquely-identified statements, each localized,
    and a buggy_id that names exactly one of them
  * every Micro-Quest block has en/fr/ar translations, none of them blank
  * every per-language config value (challenge, learn, labels, pair sides,
    hint, success) covers en/fr/ar
  * the lesson has at least one exercise, every exercise row really exists,
    and each resolves to a real grading strategy in the existing grader

Exits non-zero if any invariant fails, so it can gate a release.
"""

import json
import sqlite3
import sys
from collections import defaultdict

sys.path.insert(0, ".")

from app.models import ExerciseTypeEnum
from app.services.exercise_grading import UNGRADABLE, resolve_strategy

DB = sys.argv[1] if len(sys.argv) > 1 else "atlascode.db"

LANGUAGES = ("en", "fr", "ar")

#: Block types that make up a Micro-Quest, and how many of each a lesson needs.
REQUIRED_BLOCKS = {"hook": 1, "blueprint": 1, "exam_tip": 1}

#: Blueprint interactions the frontend can render. Adding one here without
#: adding it to Blueprint.tsx would let a lesson ship a puzzle nobody can play.
SUPPORTED_BLUEPRINT_KINDS = {"order_steps", "match_pairs", "spot_the_bug"}


class Row:
    """Duck-types the bits of the Exercise/Option models the grader reads."""

    def __init__(self, **kw):
        self.__dict__.update(kw)


def localized_problems(where: str, value, *, required=True) -> list[str]:
    """A per-language config value must be an object covering en/fr/ar."""
    if value is None:
        return [] if not required else [f"{where}: missing"]
    if not isinstance(value, dict):
        return [f"{where}: expected an object of language -> text, got {type(value).__name__}"]
    problems = []
    for language in LANGUAGES:
        text = value.get(language)
        if not isinstance(text, str) or not text.strip():
            problems.append(f"{where}: no usable {language} text")
    return problems


def check_order_steps(config: dict) -> list[str]:
    problems = []
    steps = config.get("steps")
    order = config.get("correct_order")

    if not isinstance(steps, list) or len(steps) < 2:
        return ["steps: need a list of at least 2 steps"]

    ids = []
    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            problems.append(f"steps[{index}]: not an object")
            continue
        step_id = step.get("id")
        if not isinstance(step_id, str) or not step_id:
            problems.append(f"steps[{index}]: missing a string id")
        else:
            ids.append(step_id)
        problems += localized_problems(f"steps[{index}].label", step.get("label"))

    if len(set(ids)) != len(ids):
        problems.append("steps: duplicate step ids")

    if not isinstance(order, list) or not all(isinstance(i, str) for i in order):
        problems.append("correct_order: expected a list of step ids")
    elif sorted(order) != sorted(ids):
        problems.append(
            f"correct_order {order} is not a permutation of the step ids {sorted(ids)}"
        )

    problems += localized_problems("hint", config.get("hint"), required=False)
    problems += localized_problems("success", config.get("success"), required=False)
    return problems


def check_match_pairs(config: dict) -> list[str]:
    problems = []
    pairs = config.get("pairs")

    if not isinstance(pairs, list) or len(pairs) < 2:
        return ["pairs: need a list of at least 2 pairs"]

    ids = []
    for index, pair in enumerate(pairs):
        if not isinstance(pair, dict):
            problems.append(f"pairs[{index}]: not an object")
            continue
        pair_id = pair.get("id")
        if not isinstance(pair_id, str) or not pair_id:
            problems.append(f"pairs[{index}]: missing a string id")
        else:
            ids.append(pair_id)
        problems += localized_problems(f"pairs[{index}].left", pair.get("left"))
        problems += localized_problems(f"pairs[{index}].right", pair.get("right"))

    if len(set(ids)) != len(ids):
        problems.append("pairs: duplicate pair ids")

    problems += localized_problems("hint", config.get("hint"), required=False)
    problems += localized_problems("success", config.get("success"), required=False)
    return problems


def check_spot_the_bug(config: dict) -> list[str]:
    problems = []
    statements = config.get("statements")
    buggy_id = config.get("buggy_id")
    snippet = config.get("snippet")

    if snippet is not None and not isinstance(snippet, str):
        problems.append("snippet: must be a string when present")

    if not isinstance(statements, list) or len(statements) < 3:
        return problems + ["statements: need a list of at least 3 statements"]

    ids = []
    for index, statement in enumerate(statements):
        if not isinstance(statement, dict):
            problems.append(f"statements[{index}]: not an object")
            continue
        statement_id = statement.get("id")
        if not isinstance(statement_id, str) or not statement_id:
            problems.append(f"statements[{index}]: missing a string id")
        else:
            ids.append(statement_id)
        problems += localized_problems(f"statements[{index}].text", statement.get("text"))

    if len(set(ids)) != len(ids):
        problems.append("statements: duplicate statement ids")

    if not isinstance(buggy_id, str) or not buggy_id:
        problems.append("buggy_id: missing a string id")
    elif buggy_id not in ids:
        problems.append(f"buggy_id {buggy_id!r} does not name any statement")

    problems += localized_problems("hint", config.get("hint"), required=False)
    problems += localized_problems("success", config.get("success"), required=False)
    return problems


BLUEPRINT_CHECKS = {
    "order_steps": check_order_steps,
    "match_pairs": check_match_pairs,
    "spot_the_bug": check_spot_the_bug,
}


def main() -> int:
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row

    print(f"Database: {DB}")
    print(f"Required languages: {', '.join(LANGUAGES)}")
    print(f"Supported blueprint kinds: {', '.join(sorted(SUPPORTED_BLUEPRINT_KINDS))}\n")

    quest_lessons = [
        r["lesson_id"]
        for r in conn.execute(
            "select distinct lesson_id from lesson_blocks where block_type = 'hook' "
            "order by lesson_id"
        )
    ]
    if not quest_lessons:
        print("No Micro-Quest lessons found. Nothing to audit, and nothing is broken.")
        return 0

    translations = defaultdict(dict)
    for row in conn.execute(
        "select block_id, language, content from lesson_block_translations"
    ):
        translations[row["block_id"]][row["language"]] = row["content"]

    options_by_exercise = defaultdict(list)
    for o in conn.execute("select id, exercise_id, `order`, is_correct from exercise_options"):
        options_by_exercise[o["exercise_id"]].append(
            Row(id=o["id"], order=o["order"], is_correct=bool(o["is_correct"]))
        )

    problems: list[str] = []
    kinds_seen = defaultdict(int)

    for lesson_id in quest_lessons:
        title_row = conn.execute(
            "select title from lesson_translations where lesson_id = ? and language = 'en'",
            (lesson_id,),
        ).fetchone()
        title = title_row["title"] if title_row else "(no English title)"

        blocks = list(
            conn.execute(
                "select id, block_type, `order`, content, config from lesson_blocks "
                "where lesson_id = ? and block_type in ('hook', 'blueprint', 'exam_tip') "
                "order by `order`, id",
                (lesson_id,),
            )
        )
        counts = defaultdict(int)
        for block in blocks:
            counts[block["block_type"]] += 1

        print(f"lesson {lesson_id}: {title}")

        def fail(message: str) -> None:
            problems.append(f"lesson {lesson_id}: {message}")
            print(f"    FAIL {message}")

        for block_type, wanted in REQUIRED_BLOCKS.items():
            found = counts[block_type]
            if found != wanted:
                fail(f"expected exactly {wanted} '{block_type}' block, found {found}")

        for block in blocks:
            label = f"{block['block_type']} block {block['id']}"

            have = translations.get(block["id"], {})
            missing = [lang for lang in LANGUAGES if not (have.get(lang) or "").strip()]
            if missing:
                fail(f"{label} has no usable {'/'.join(missing)} translation")

            raw = block["config"]
            if not raw or not raw.strip():
                fail(f"{label} has no config")
                continue
            try:
                config = json.loads(raw)
            except ValueError as exc:
                fail(f"{label} config is not valid JSON: {exc}")
                continue
            if not isinstance(config, dict):
                fail(f"{label} config is not a JSON object")
                continue

            kind = config.get("kind")
            if not isinstance(kind, str) or not kind:
                fail(f"{label} config has no 'kind'")
                continue

            if block["block_type"] == "hook":
                if kind != "hook":
                    fail(f"{label} config kind is {kind!r}, expected 'hook'")
                for field in ("challenge", "learn"):
                    for detail in localized_problems(f"{label} config.{field}", config.get(field)):
                        fail(detail)

            elif block["block_type"] == "exam_tip":
                if kind != "exam_tip":
                    fail(f"{label} config kind is {kind!r}, expected 'exam_tip'")

            elif block["block_type"] == "blueprint":
                kinds_seen[kind] += 1
                if kind not in SUPPORTED_BLUEPRINT_KINDS:
                    fail(f"{label} uses unsupported blueprint kind {kind!r}")
                    continue
                print(f"    blueprint kind: {kind}")
                for detail in BLUEPRINT_CHECKS[kind](config):
                    fail(f"{label} ({kind}) {detail}")

        exercises = list(
            conn.execute(
                "select id, exercise_type, xp_reward, test_code, validation_config "
                "from exercises where lesson_id = ? order by `order`, id",
                (lesson_id,),
            )
        )
        if not exercises:
            fail("has no exercise, so the quest can never be completed")
        for exercise in exercises:
            try:
                etype = ExerciseTypeEnum(exercise["exercise_type"])
            except ValueError:
                fail(f"exercise {exercise['id']} has unknown type {exercise['exercise_type']!r}")
                continue
            strategy = resolve_strategy(
                Row(
                    id=exercise["id"],
                    exercise_type=etype,
                    test_code=exercise["test_code"],
                    validation_config=exercise["validation_config"],
                ),
                options_by_exercise.get(exercise["id"], []),
            )
            print(
                f"    exercise {exercise['id']}: {exercise['exercise_type']} "
                f"({exercise['xp_reward']} XP) -> {strategy}"
            )
            if strategy == UNGRADABLE:
                fail(f"exercise {exercise['id']} has no valid grading strategy")
        print()

    # A blueprint row whose lesson has no hook would never be rendered by the
    # Micro-Quest and would silently disappear, so it counts as a defect too.
    orphans = list(
        conn.execute(
            "select id, lesson_id, block_type from lesson_blocks "
            "where block_type in ('blueprint', 'exam_tip') and lesson_id not in "
            "(select lesson_id from lesson_blocks where block_type = 'hook')"
        )
    )
    for row in orphans:
        problems.append(
            f"lesson {row['lesson_id']}: {row['block_type']} block {row['id']} has no hook, "
            "so it is never rendered"
        )
        print(f"FAIL lesson {row['lesson_id']}: orphan {row['block_type']} block {row['id']}")

    print(f"Micro-Quest lessons: {len(quest_lessons)} {quest_lessons}")
    print(
        "Blueprint kinds in use: "
        + (", ".join(f"{k}={n}" for k, n in sorted(kinds_seen.items())) or "(none)")
    )
    print(f"\n{'ALL MICRO-QUESTS OK' if not problems else f'PROBLEMS FOUND: {len(problems)}'}")
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
