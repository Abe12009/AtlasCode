"""Micro-Quest block metadata: storage, API compatibility, no grading impact.

The Micro-Quest adds three new lesson_blocks.block_type values ('hook',
'blueprint', 'exam_tip') and one new nullable column (config) on top of the
existing lesson/block architecture. These tests establish: the column round
trips through the API, existing lessons that carry none of this are completely
unaffected, and exercise grading was not touched to support any of it.
"""

import json

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models import Exercise, LessonBlock, LessonBlockTranslation

REFERENCE_LESSON_ID = 9
REFERENCE_EXERCISE_ID = 18


class TestMicroQuestBlocksExistOnTheReferenceLesson:
    async def test_lesson_9_has_hook_blueprint_and_exam_tip_blocks(self, db_session):
        result = await db_session.execute(
            select(LessonBlock).where(LessonBlock.lesson_id == REFERENCE_LESSON_ID)
        )
        blocks = result.scalars().all()
        types = {b.block_type for b in blocks}
        assert {"hook", "blueprint", "exam_tip"}.issubset(types)

    async def test_hook_and_blueprint_blocks_carry_valid_json_config(self, db_session):
        result = await db_session.execute(
            select(LessonBlock).where(
                LessonBlock.lesson_id == REFERENCE_LESSON_ID,
                LessonBlock.block_type.in_(["hook", "blueprint"]),
            )
        )
        blocks = result.scalars().all()
        assert len(blocks) == 2
        for block in blocks:
            assert block.config, f"{block.block_type} block has no config"
            parsed = json.loads(block.config)
            assert isinstance(parsed, dict)
            assert parsed.get("kind")

    async def test_blueprint_config_has_a_well_formed_step_order(self, db_session):
        result = await db_session.execute(
            select(LessonBlock).where(
                LessonBlock.lesson_id == REFERENCE_LESSON_ID,
                LessonBlock.block_type == "blueprint",
            )
        )
        block = result.scalar_one()
        config = json.loads(block.config)
        step_ids = {step["id"] for step in config["steps"]}
        assert set(config["correct_order"]) == step_ids
        assert len(config["correct_order"]) == len(config["steps"]) >= 2

    async def test_microquest_blocks_have_en_fr_ar_translations(self, db_session):
        result = await db_session.execute(
            select(LessonBlock).where(
                LessonBlock.lesson_id == REFERENCE_LESSON_ID,
                LessonBlock.block_type.in_(["hook", "blueprint", "exam_tip"]),
            )
        )
        blocks = result.scalars().all()
        assert len(blocks) == 3
        for block in blocks:
            langs = {
                t.language.value if hasattr(t.language, "value") else t.language
                for t in (
                    await db_session.execute(
                        select(LessonBlockTranslation).where(
                            LessonBlockTranslation.block_id == block.id
                        )
                    )
                ).scalars()
            }
            assert langs == {"en", "fr", "ar"}, f"{block.block_type} missing languages: {langs}"

    async def test_reference_lesson_still_has_exactly_one_exercise(self, db_session):
        """Quest Clear depends on this: the exercise's own success == lesson completion."""
        exercises = (
            await db_session.execute(
                select(Exercise).where(Exercise.lesson_id == REFERENCE_LESSON_ID)
            )
        ).scalars().all()
        assert len(exercises) == 1
        assert exercises[0].id == REFERENCE_EXERCISE_ID


class TestLessonApiServesMicroQuestBlocks:
    async def test_lesson_endpoint_returns_the_new_block_types_in_order(
        self, client: AsyncClient, test_user
    ):
        response = await client.get(
            f"/lessons/{REFERENCE_LESSON_ID}", headers=test_user["headers"]
        )
        assert response.status_code == 200
        lesson = response.json()

        types = [b["block_type"] for b in lesson["blocks"]]
        assert types[0] == "hook", types
        assert "blueprint" in types
        assert "exam_tip" in types

    async def test_hook_block_config_is_valid_json_over_the_wire(
        self, client: AsyncClient, test_user
    ):
        lesson = (
            await client.get(
                f"/lessons/{REFERENCE_LESSON_ID}", headers=test_user["headers"]
            )
        ).json()
        hook = next(b for b in lesson["blocks"] if b["block_type"] == "hook")
        assert hook["config"] is not None
        parsed = json.loads(hook["config"])
        assert parsed["kind"] == "hook"
        assert "en" in parsed["challenge"]
        assert "fr" in parsed["challenge"]
        assert "ar" in parsed["challenge"]

    async def test_block_translation_matches_requested_language(
        self, client: AsyncClient, test_user
    ):
        for language in ("en", "fr", "ar"):
            lesson = (
                await client.get(
                    f"/lessons/{REFERENCE_LESSON_ID}?language={language}",
                    headers=test_user["headers"],
                )
            ).json()
            hook = next(b for b in lesson["blocks"] if b["block_type"] == "hook")
            assert hook["translations"], f"no {language} translation for the hook block"
            assert hook["translations"][0]["language"] == language

    async def test_arabic_hook_content_contains_arabic_script(
        self, client: AsyncClient, test_user
    ):
        lesson = (
            await client.get(
                f"/lessons/{REFERENCE_LESSON_ID}?language=ar", headers=test_user["headers"]
            )
        ).json()
        hook = next(b for b in lesson["blocks"] if b["block_type"] == "hook")
        content = hook["translations"][0]["content"]
        assert any("؀" <= ch <= "ۿ" for ch in content)


class TestExistingLessonsAreUnaffected:
    """A lesson with no Micro-Quest metadata must render exactly as before."""

    @pytest.mark.parametrize("lesson_id", [1, 5, 10, 20, 50, 100, 127])
    async def test_ordinary_lessons_have_no_microquest_block_types(
        self, client: AsyncClient, test_user, lesson_id
    ):
        response = await client.get(f"/lessons/{lesson_id}", headers=test_user["headers"])
        if response.status_code == 404:
            pytest.skip(f"lesson {lesson_id} does not exist")
        lesson = response.json()
        types = {b["block_type"] for b in lesson["blocks"]}
        assert not types & {"hook", "blueprint", "exam_tip"}
        for block in lesson["blocks"]:
            assert block["config"] is None

    async def test_lesson_1_response_shape_is_unchanged_apart_from_the_new_field(
        self, client: AsyncClient, test_user
    ):
        lesson = (
            await client.get("/lessons/1", headers=test_user["headers"])
        ).json()
        assert lesson["id"] == 1
        assert len(lesson["blocks"]) > 0
        assert len(lesson["exercises"]) > 0
        for block in lesson["blocks"]:
            assert block["block_type"] in ("text", "code")
            assert "config" in block  # present, and null for ordinary blocks
            assert block["config"] is None


class TestExerciseGradingIsUnchangedByMicroQuest:
    """Task 5's promise: the Micro-Quest layer must not touch grading."""

    async def test_reference_exercise_grades_exactly_like_any_code_exercise(
        self, client: AsyncClient, test_user
    ):
        await client.post(f"/lessons/{REFERENCE_LESSON_ID}/start", headers=test_user["headers"])

        wrong = await client.post(
            f"/exercises/{REFERENCE_EXERCISE_ID}/submit",
            headers=test_user["headers"],
            json={"exercise_id": REFERENCE_EXERCISE_ID, "code": "print('nope')"},
        )
        assert wrong.status_code == 200
        assert wrong.json()["is_correct"] is False
        assert wrong.json()["xp_earned"] == 0

        correct = await client.post(
            f"/exercises/{REFERENCE_EXERCISE_ID}/submit",
            headers=test_user["headers"],
            json={
                "exercise_id": REFERENCE_EXERCISE_ID,
                "code": (
                    "total = 0\n"
                    "for i in range(1, 21):\n"
                    "    if i % 2 == 0:\n"
                    "        total += i\n"
                    'print("Sum of evens:", total)'
                ),
            },
        )
        assert correct.status_code == 200
        body = correct.json()
        assert body["is_correct"] is True
        assert body["xp_earned"] == 15  # the exercise's own configured xp_reward, untouched
        assert body["is_completed"] is True
        assert body["lesson_completed"] is True  # the lesson's only exercise

        progress = (
            await client.get(
                f"/lessons/{REFERENCE_LESSON_ID}/progress", headers=test_user["headers"]
            )
        ).json()
        assert progress["status"] == "completed"

    async def test_resubmitting_the_reference_exercise_awards_no_extra_xp(
        self, client: AsyncClient, test_user
    ):
        payload = {
            "exercise_id": REFERENCE_EXERCISE_ID,
            "code": (
                "total = 0\n"
                "for i in range(1, 21):\n"
                "    if i % 2 == 0:\n"
                "        total += i\n"
                'print("Sum of evens:", total)'
            ),
        }
        first = (
            await client.post(
                f"/exercises/{REFERENCE_EXERCISE_ID}/submit",
                headers=test_user["headers"],
                json=payload,
            )
        ).json()
        second = (
            await client.post(
                f"/exercises/{REFERENCE_EXERCISE_ID}/submit",
                headers=test_user["headers"],
                json=payload,
            )
        ).json()
        assert first["xp_earned"] == 15
        assert second["xp_earned"] == 0
        assert second["is_correct"] is True


# --------------------------------------------------------------------------
# Phase 9: the same architecture over more than one exercise type and more
# than one blueprint type.
# --------------------------------------------------------------------------

#: lesson id -> (blueprint kind, exercise id, exercise type, xp reward)
REFERENCE_QUESTS = {
    9: ("order_steps", 18, "code_writing", 15),
    12: ("match_pairs", 22, "prediction", 10),
    36: ("order_steps", 47, "multiple_choice", 10),
    38: ("spot_the_bug", 49, "debugging", 15),
    # Phase 11's ten additional lessons.
    16: ("match_pairs", 27, "code_writing", 10),
    13: ("order_steps", 23, "code_writing", 15),
    15: ("spot_the_bug", 26, "fill_blank", 10),
    18: ("order_steps", 29, "multiple_choice", 10),
    23: ("match_pairs", 34, "multiple_choice", 10),
    26: ("match_pairs", 37, "multiple_choice", 10),
    29: ("spot_the_bug", 40, "code_writing", 15),
    45: ("order_steps", 56, "multiple_choice", 10),
    47: ("spot_the_bug", 58, "multiple_choice", 10),
    32: ("match_pairs", 43, "ordering", 10),
}

#: The answer that solves a reference quest, in the shape its type submits.
#: Exercise 47 is multiple choice, whose option ids are only known at runtime.
CORRECT_ANSWERS = {
    18: {
        "code": (
            "total = 0\n"
            "for i in range(1, 21):\n"
            "    if i % 2 == 0:\n"
            "        total += i\n"
            'print("Sum of evens:", total)'
        )
    },
    22: {"answer": "Inside: 20\nOutside: 10"},
    49: {
        "code": (
            "def binary_search(arr, target):\n"
            "    left, right = 0, len(arr) - 1\n"
            "    while left <= right:\n"
            "        mid = (left + right) // 2\n"
            "        if arr[mid] == target:\n"
            "            return mid\n"
            "        elif arr[mid] < target:\n"
            "            left = mid + 1\n"
            "        else:\n"
            "            right = mid - 1\n"
            "    return -1"
        )
    },
    # Phase 11's ten additional lessons.
    27: {
        "code": (
            'product = {\n    "name": "Tagine",\n    "price": 150,\n    "in_stock": True\n}\n'
            'product["price"] = 180\nprint(product)'
        )
    },
    23: {
        "code": (
            "def is_even(n):\n    return n % 2 == 0\n\n"
            "def count_evens(numbers):\n    count = 0\n    for n in numbers:\n"
            "        if is_even(n):\n            count += 1\n    return count\n\n"
            "print(count_evens([1,2,3,4,5,6,7,8,9,10]))"
        )
    },
    26: {"blanks": ["10", "20", "blue"]},
    40: {
        "code": (
            "SELECT city, AVG(age) as avg_age\nFROM students\nGROUP BY city\nHAVING COUNT(*) >= 1;"
        )
    },
}

ARABIC_RANGE = ("؀", "ۿ")


def _has_arabic(text: str) -> bool:
    return any(ARABIC_RANGE[0] <= ch <= ARABIC_RANGE[1] for ch in text)


async def _blueprint_config(db_session, lesson_id: int) -> dict:
    block = (
        await db_session.execute(
            select(LessonBlock).where(
                LessonBlock.lesson_id == lesson_id,
                LessonBlock.block_type == "blueprint",
            )
        )
    ).scalar_one()
    return json.loads(block.config)


class TestEveryReferenceMicroQuestIsWellFormed:
    @pytest.mark.parametrize("lesson_id", sorted(REFERENCE_QUESTS))
    async def test_lesson_has_exactly_one_hook_blueprint_and_exam_tip(self, db_session, lesson_id):
        blocks = (
            await db_session.execute(
                select(LessonBlock).where(
                    LessonBlock.lesson_id == lesson_id,
                    LessonBlock.block_type.in_(["hook", "blueprint", "exam_tip"]),
                )
            )
        ).scalars().all()
        counts = {
            block_type: sum(1 for b in blocks if b.block_type == block_type)
            for block_type in ("hook", "blueprint", "exam_tip")
        }
        assert counts == {"hook": 1, "blueprint": 1, "exam_tip": 1}

    @pytest.mark.parametrize("lesson_id", sorted(REFERENCE_QUESTS))
    async def test_micro_quest_blocks_have_en_fr_ar_translations(self, db_session, lesson_id):
        blocks = (
            await db_session.execute(
                select(LessonBlock).where(
                    LessonBlock.lesson_id == lesson_id,
                    LessonBlock.block_type.in_(["hook", "blueprint", "exam_tip"]),
                )
            )
        ).scalars().all()
        for block in blocks:
            langs = {
                t.language.value if hasattr(t.language, "value") else t.language
                for t in (
                    await db_session.execute(
                        select(LessonBlockTranslation).where(
                            LessonBlockTranslation.block_id == block.id
                        )
                    )
                ).scalars()
            }
            assert langs == {"en", "fr", "ar"}, f"lesson {lesson_id} {block.block_type}: {langs}"

    @pytest.mark.parametrize(
        "lesson_id,expected_kind", [(k, v[0]) for k, v in REFERENCE_QUESTS.items()]
    )
    async def test_blueprint_declares_the_expected_kind(self, db_session, lesson_id, expected_kind):
        assert (await _blueprint_config(db_session, lesson_id))["kind"] == expected_kind

    async def test_match_pairs_config_is_structurally_sound(self, db_session):
        """Both sides of every pair, in every language, and unique ids — the
        frontend refuses to render a match_pairs blueprint without them."""
        config = await _blueprint_config(db_session, 12)
        pairs = config["pairs"]
        assert len(pairs) >= 2
        assert len({pair["id"] for pair in pairs}) == len(pairs)
        for pair in pairs:
            for side in ("left", "right"):
                assert set(pair[side]) >= {"en", "fr", "ar"}, f"{pair['id']}.{side}"
                assert all(pair[side][lang].strip() for lang in ("en", "fr", "ar"))

    async def test_order_steps_config_on_the_new_lesson_is_a_real_permutation(self, db_session):
        config = await _blueprint_config(db_session, 36)
        step_ids = [step["id"] for step in config["steps"]]
        assert len(step_ids) >= 2
        assert len(set(step_ids)) == len(step_ids)
        assert sorted(config["correct_order"]) == sorted(step_ids)
        for step in config["steps"]:
            assert set(step["label"]) >= {"en", "fr", "ar"}

    async def test_spot_the_bug_config_names_exactly_one_real_statement_as_the_bug(self, db_session):
        """Structurally the same guarantee order_steps and match_pairs get:
        the frontend refuses to render a spot_the_bug blueprint without it."""
        config = await _blueprint_config(db_session, 38)
        statements = config["statements"]
        assert len(statements) >= 3
        ids = [s["id"] for s in statements]
        assert len(set(ids)) == len(ids)
        assert config["buggy_id"] in ids
        for statement in statements:
            assert set(statement["text"]) >= {"en", "fr", "ar"}, statement["id"]
            assert all(statement["text"][lang].strip() for lang in ("en", "fr", "ar"))

    async def test_spot_the_bug_blueprint_never_states_the_exercise_49_solution(self, db_session):
        """The blueprint teaches the general shape of the bug (an off-by-one
        search boundary); it must not spell out the exercise's actual fix for
        left/right's update rules, or the sandbox exercise stops being real
        work."""
        config = await _blueprint_config(db_session, 38)
        text = json.dumps(config, ensure_ascii=False)
        for leaked in ("mid + 1", "mid - 1", "mid+1", "mid-1"):
            assert leaked not in text, f"blueprint leaks the exercise's update rule: {leaked!r}"

    @pytest.mark.parametrize(
        "lesson_id,exercise_id,exercise_type",
        [(k, v[1], v[2]) for k, v in REFERENCE_QUESTS.items()],
    )
    async def test_each_quest_ends_in_exactly_one_real_exercise(
        self, db_session, lesson_id, exercise_id, exercise_type
    ):
        """Quest Clear depends on this: the exercise's own success is the
        lesson's completion, so the XP shown is the XP actually awarded."""
        exercises = (
            await db_session.execute(select(Exercise).where(Exercise.lesson_id == lesson_id))
        ).scalars().all()
        assert len(exercises) == 1
        assert exercises[0].id == exercise_id
        assert exercises[0].exercise_type.value == exercise_type


class TestEveryBlueprintIsStructurallyValidRegardlessOfLesson:
    """The kind-specific checks above (test_match_pairs_config_is_..., etc.)
    hand-pick one reference lesson each. This runs the matching structural
    check against *every* lesson in REFERENCE_QUESTS -- including Phase 11's
    ten -- so a new lesson's config is held to the same bar without needing
    its own bespoke test."""

    @pytest.mark.parametrize(
        "lesson_id",
        sorted(lid for lid, (kind, *_ ) in REFERENCE_QUESTS.items() if kind == "order_steps"),
    )
    async def test_order_steps_lessons_have_a_real_permutation(self, db_session, lesson_id):
        config = await _blueprint_config(db_session, lesson_id)
        step_ids = [step["id"] for step in config["steps"]]
        assert len(step_ids) >= 2
        assert len(set(step_ids)) == len(step_ids)
        assert sorted(config["correct_order"]) == sorted(step_ids)
        for step in config["steps"]:
            assert set(step["label"]) >= {"en", "fr", "ar"}
            assert all(step["label"][lang].strip() for lang in ("en", "fr", "ar"))

    @pytest.mark.parametrize(
        "lesson_id",
        sorted(lid for lid, (kind, *_ ) in REFERENCE_QUESTS.items() if kind == "match_pairs"),
    )
    async def test_match_pairs_lessons_have_unique_fully_localized_pairs(self, db_session, lesson_id):
        config = await _blueprint_config(db_session, lesson_id)
        pairs = config["pairs"]
        assert len(pairs) >= 2
        assert len({pair["id"] for pair in pairs}) == len(pairs)
        for pair in pairs:
            for side in ("left", "right"):
                assert set(pair[side]) >= {"en", "fr", "ar"}, f"lesson {lesson_id} {pair['id']}.{side}"
                assert all(pair[side][lang].strip() for lang in ("en", "fr", "ar"))

    @pytest.mark.parametrize(
        "lesson_id",
        sorted(lid for lid, (kind, *_ ) in REFERENCE_QUESTS.items() if kind == "spot_the_bug"),
    )
    async def test_spot_the_bug_lessons_name_exactly_one_real_statement_as_the_bug(
        self, db_session, lesson_id
    ):
        config = await _blueprint_config(db_session, lesson_id)
        statements = config["statements"]
        assert len(statements) >= 3
        ids = [s["id"] for s in statements]
        assert len(set(ids)) == len(ids)
        assert config["buggy_id"] in ids
        for statement in statements:
            assert set(statement["text"]) >= {"en", "fr", "ar"}, f"lesson {lesson_id} {statement['id']}"
            assert all(statement["text"][lang].strip() for lang in ("en", "fr", "ar"))

    @pytest.mark.parametrize("lesson_id", sorted(REFERENCE_QUESTS))
    async def test_no_blueprint_config_carries_its_own_exercise_secrets(self, db_session, lesson_id):
        """Generic version of the lesson-38-specific leak test above: no
        blueprint's config may contain its own exercise's stored solution,
        test code or validation config, whatever blueprint kind it uses."""
        config = await _blueprint_config(db_session, lesson_id)
        text = json.dumps(config, ensure_ascii=False)
        _, exercise_id, _, _ = REFERENCE_QUESTS[lesson_id]
        exercise = (
            await db_session.execute(select(Exercise).where(Exercise.id == exercise_id))
        ).scalar_one()
        for secret in (exercise.solution_code, exercise.test_code, exercise.validation_config):
            if secret and secret.strip():
                assert secret not in text, f"lesson {lesson_id} blueprint leaks: {secret[:60]!r}"


class TestMicroQuestApiOverEveryExerciseType:
    @pytest.mark.parametrize("lesson_id", sorted(REFERENCE_QUESTS))
    async def test_lesson_endpoint_puts_the_hook_first(
        self, client: AsyncClient, test_user, lesson_id
    ):
        lesson = (await client.get(f"/lessons/{lesson_id}", headers=test_user["headers"])).json()
        types = [b["block_type"] for b in lesson["blocks"]]
        assert types[0] == "hook", types
        assert "blueprint" in types
        assert "exam_tip" in types

    @pytest.mark.parametrize("lesson_id", sorted(REFERENCE_QUESTS))
    @pytest.mark.parametrize("language", ["en", "fr", "ar"])
    async def test_every_micro_quest_block_is_served_in_every_language(
        self, client: AsyncClient, test_user, lesson_id, language
    ):
        lesson = (
            await client.get(
                f"/lessons/{lesson_id}?language={language}", headers=test_user["headers"]
            )
        ).json()
        for block_type in ("hook", "blueprint", "exam_tip"):
            block = next(b for b in lesson["blocks"] if b["block_type"] == block_type)
            assert block["translations"], f"{block_type} has no {language} translation"
            assert block["translations"][0]["language"] == language
            assert block["translations"][0]["content"].strip()

    async def test_arabic_blueprint_pairs_are_actually_arabic(self, client: AsyncClient, test_user):
        """Config carries its own per-language values, so an Arabic reader must
        get Arabic pair text rather than the English fallback."""
        lesson = (await client.get("/lessons/12?language=ar", headers=test_user["headers"])).json()
        blueprint = next(b for b in lesson["blocks"] if b["block_type"] == "blueprint")
        config = json.loads(blueprint["config"])
        for pair in config["pairs"]:
            for side in ("left", "right"):
                assert _has_arabic(pair[side]["ar"]), f"{pair['id']}.{side}"

    async def test_arabic_blueprint_steps_are_actually_arabic(self, client: AsyncClient, test_user):
        lesson = (await client.get("/lessons/36?language=ar", headers=test_user["headers"])).json()
        blueprint = next(b for b in lesson["blocks"] if b["block_type"] == "blueprint")
        config = json.loads(blueprint["config"])
        for step in config["steps"]:
            assert _has_arabic(step["label"]["ar"]), step["id"]

    async def test_arabic_spot_the_bug_statements_are_actually_arabic(
        self, client: AsyncClient, test_user
    ):
        lesson = (await client.get("/lessons/38?language=ar", headers=test_user["headers"])).json()
        blueprint = next(b for b in lesson["blocks"] if b["block_type"] == "blueprint")
        config = json.loads(blueprint["config"])
        for statement in config["statements"]:
            assert _has_arabic(statement["text"]["ar"]), statement["id"]
        # The snippet is code, never translated — it must stay the same string
        # regardless of the requested language.
        assert "left, right" in config["snippet"]


class TestMicroQuestGradingUsesTheExistingGrader:
    """Each new quest is completed exactly the way its exercise type always
    was. Nothing about grading, XP or completion is special-cased."""

    async def test_multiple_choice_quest_awards_real_xp_once(self, client: AsyncClient, test_user):
        # Exactly what a browser does on entering a lesson, and what
        # lesson_completed depends on: see the progress-row test below.
        await client.post("/lessons/36/start", headers=test_user["headers"])
        lesson = (await client.get("/lessons/36", headers=test_user["headers"])).json()
        options = sorted(lesson["exercises"][0]["options"], key=lambda o: o["order"])
        correct_option = next(
            o for o in options if o["translations"][0]["text"] == "Runs forever"
        )
        wrong_option = next(o for o in options if o["id"] != correct_option["id"])

        wrong = (
            await client.post(
                "/exercises/47/submit",
                headers=test_user["headers"],
                json={"exercise_id": 47, "selected_option_id": wrong_option["id"]},
            )
        ).json()
        assert wrong["is_correct"] is False
        assert wrong["xp_earned"] == 0

        correct = (
            await client.post(
                "/exercises/47/submit",
                headers=test_user["headers"],
                json={"exercise_id": 47, "selected_option_id": correct_option["id"]},
            )
        ).json()
        assert correct["is_correct"] is True
        assert correct["xp_earned"] == 10
        assert correct["lesson_completed"] is True

        again = (
            await client.post(
                "/exercises/47/submit",
                headers=test_user["headers"],
                json={"exercise_id": 47, "selected_option_id": correct_option["id"]},
            )
        ).json()
        assert again["is_correct"] is True
        assert again["xp_earned"] == 0, "a solved quest must never pay out twice"

        progress = (await client.get("/lessons/36/progress", headers=test_user["headers"])).json()
        assert progress["status"] == "completed"
        assert progress["xp_earned"] == 10

    async def test_prediction_quest_awards_real_xp_once(self, client: AsyncClient, test_user):
        await client.post("/lessons/12/start", headers=test_user["headers"])
        wrong = (
            await client.post(
                "/exercises/22/submit",
                headers=test_user["headers"],
                json={"exercise_id": 22, "answer": "Inside: 10\nOutside: 20"},
            )
        ).json()
        assert wrong["is_correct"] is False
        assert wrong["xp_earned"] == 0

        correct = (
            await client.post(
                "/exercises/22/submit",
                headers=test_user["headers"],
                json={"exercise_id": 22, **CORRECT_ANSWERS[22]},
            )
        ).json()
        assert correct["is_correct"] is True
        assert correct["xp_earned"] == 10
        assert correct["lesson_completed"] is True

        again = (
            await client.post(
                "/exercises/22/submit",
                headers=test_user["headers"],
                json={"exercise_id": 22, **CORRECT_ANSWERS[22]},
            )
        ).json()
        assert again["xp_earned"] == 0

        progress = (await client.get("/lessons/12/progress", headers=test_user["headers"])).json()
        assert progress["status"] == "completed"
        assert progress["xp_earned"] == 10

    async def test_debugging_quest_awards_real_xp_once(self, client: AsyncClient, test_user):
        """Lesson 38's exercise is graded by the real sandbox, exactly like any
        other debugging exercise — nothing about it being reached through a
        Micro-Quest changes what runs or how it is scored."""
        await client.post("/lessons/38/start", headers=test_user["headers"])

        # The exercise's own starter code is the bug: submitting it unmodified
        # must fail the real assertions in the sandbox, not merely "run".
        lesson = (await client.get("/lessons/38", headers=test_user["headers"])).json()
        exercise = lesson["exercises"][0]
        assert exercise["id"] == 49

        wrong = (
            await client.post(
                "/exercises/49/submit",
                headers=test_user["headers"],
                json={"exercise_id": 49, "code": exercise["starter_code"]},
            )
        ).json()
        assert wrong["is_correct"] is False
        assert wrong["xp_earned"] == 0

        correct = (
            await client.post(
                "/exercises/49/submit",
                headers=test_user["headers"],
                json={"exercise_id": 49, **CORRECT_ANSWERS[49]},
            )
        ).json()
        assert correct["is_correct"] is True
        assert correct["xp_earned"] == 15
        assert correct["lesson_completed"] is True

        again = (
            await client.post(
                "/exercises/49/submit",
                headers=test_user["headers"],
                json={"exercise_id": 49, **CORRECT_ANSWERS[49]},
            )
        ).json()
        assert again["is_correct"] is True
        assert again["xp_earned"] == 0, "a solved quest must never pay out twice"

        progress = (await client.get("/lessons/38/progress", headers=test_user["headers"])).json()
        assert progress["status"] == "completed"
        assert progress["xp_earned"] == 15

    # ---- Phase 11's ten additional lessons -----------------------------

    async def _assert_code_quest_awards_xp_once(
        self, client: AsyncClient, headers: dict, lesson_id: int, exercise_id: int, xp: int, wrong_code: str
    ):
        await client.post(f"/lessons/{lesson_id}/start", headers=headers)
        wrong = (
            await client.post(
                f"/exercises/{exercise_id}/submit",
                headers=headers,
                json={"exercise_id": exercise_id, "code": wrong_code},
            )
        ).json()
        assert wrong["is_correct"] is False
        assert wrong["xp_earned"] == 0

        correct = (
            await client.post(
                f"/exercises/{exercise_id}/submit",
                headers=headers,
                json={"exercise_id": exercise_id, **CORRECT_ANSWERS[exercise_id]},
            )
        ).json()
        assert correct["is_correct"] is True, correct
        assert correct["xp_earned"] == xp
        assert correct["lesson_completed"] is True

        again = (
            await client.post(
                f"/exercises/{exercise_id}/submit",
                headers=headers,
                json={"exercise_id": exercise_id, **CORRECT_ANSWERS[exercise_id]},
            )
        ).json()
        assert again["xp_earned"] == 0, "a solved quest must never pay out twice"

        progress = (
            await client.get(f"/lessons/{lesson_id}/progress", headers=headers)
        ).json()
        assert progress["status"] == "completed"
        assert progress["xp_earned"] == xp

    async def test_dictionaries_quest_awards_real_xp_once(self, client: AsyncClient, test_user):
        await self._assert_code_quest_awards_xp_once(
            client, test_user["headers"], 16, 27, 10, wrong_code="print('nope')"
        )

    async def test_decomposition_quest_awards_real_xp_once(self, client: AsyncClient, test_user):
        await self._assert_code_quest_awards_xp_once(
            client, test_user["headers"], 13, 23, 15, wrong_code="print('nope')"
        )

    async def test_sorting_grouping_quest_awards_real_xp_once(self, client: AsyncClient, test_user):
        await self._assert_code_quest_awards_xp_once(
            client, test_user["headers"], 29, 40, 15, wrong_code="SELECT * FROM nowhere;"
        )

    async def test_tuples_sets_quest_awards_real_xp_once(self, client: AsyncClient, test_user):
        """fill_blank, graded by the blanks strategy -- the first Micro-Quest
        reference lesson to use this exercise type."""
        await client.post("/lessons/15/start", headers=test_user["headers"])

        wrong = (
            await client.post(
                "/exercises/26/submit",
                headers=test_user["headers"],
                json={"exercise_id": 26, "blanks": ["1", "2", "green"]},
            )
        ).json()
        assert wrong["is_correct"] is False
        assert wrong["xp_earned"] == 0

        correct = (
            await client.post(
                "/exercises/26/submit",
                headers=test_user["headers"],
                json={"exercise_id": 26, **CORRECT_ANSWERS[26]},
            )
        ).json()
        assert correct["is_correct"] is True, correct
        assert correct["xp_earned"] == 10
        assert correct["lesson_completed"] is True

        again = (
            await client.post(
                "/exercises/26/submit",
                headers=test_user["headers"],
                json={"exercise_id": 26, **CORRECT_ANSWERS[26]},
            )
        ).json()
        assert again["xp_earned"] == 0

        progress = (await client.get("/lessons/15/progress", headers=test_user["headers"])).json()
        assert progress["status"] == "completed"
        assert progress["xp_earned"] == 10

    async def _assert_mcq_quest_awards_xp_once(
        self, client, test_user, lesson_id: int, exercise_id: int, xp: int, correct_text: str
    ):
        # lesson_completed only fires once a lesson_progress row already
        # exists -- see test_multiple_choice_quest_awards_real_xp_once above.
        await client.post(f"/lessons/{lesson_id}/start", headers=test_user["headers"])
        lesson = (
            await client.get(f"/lessons/{lesson_id}", headers=test_user["headers"])
        ).json()
        options = sorted(lesson["exercises"][0]["options"], key=lambda o: o["order"])
        correct_option = next(o for o in options if o["translations"][0]["text"] == correct_text)
        wrong_option = next(o for o in options if o["id"] != correct_option["id"])

        wrong = (
            await client.post(
                f"/exercises/{exercise_id}/submit",
                headers=test_user["headers"],
                json={"exercise_id": exercise_id, "selected_option_id": wrong_option["id"]},
            )
        ).json()
        assert wrong["is_correct"] is False
        assert wrong["xp_earned"] == 0

        correct = (
            await client.post(
                f"/exercises/{exercise_id}/submit",
                headers=test_user["headers"],
                json={"exercise_id": exercise_id, "selected_option_id": correct_option["id"]},
            )
        ).json()
        assert correct["is_correct"] is True
        assert correct["xp_earned"] == xp
        assert correct["lesson_completed"] is True

        again = (
            await client.post(
                f"/exercises/{exercise_id}/submit",
                headers=test_user["headers"],
                json={"exercise_id": exercise_id, "selected_option_id": correct_option["id"]},
            )
        ).json()
        assert again["is_correct"] is True
        assert again["xp_earned"] == 0, "a solved quest must never pay out twice"

        progress = (
            await client.get(f"/lessons/{lesson_id}/progress", headers=test_user["headers"])
        ).json()
        assert progress["status"] == "completed"
        assert progress["xp_earned"] == xp

    async def test_how_web_works_quest_awards_real_xp_once(self, client: AsyncClient, test_user):
        await self._assert_mcq_quest_awards_xp_once(
            client, test_user, 18, 29, 10, "Requests and displays web pages"
        )

    async def test_selectors_quest_awards_real_xp_once(self, client: AsyncClient, test_user):
        await self._assert_mcq_quest_awards_xp_once(client, test_user, 23, 34, 10, "nav a")

    async def test_databases_tables_quest_awards_real_xp_once(self, client: AsyncClient, test_user):
        await self._assert_mcq_quest_awards_xp_once(
            client, test_user, 26, 37, 10, "A unique identifier for each row"
        )

    async def test_memory_storage_quest_awards_real_xp_once(self, client: AsyncClient, test_user):
        await self._assert_mcq_quest_awards_xp_once(client, test_user, 45, 56, 10, "RAM")

    async def test_networks_quest_awards_real_xp_once(self, client: AsyncClient, test_user):
        await self._assert_mcq_quest_awards_xp_once(client, test_user, 47, 58, 10, "TCP")

    async def test_commits_history_quest_awards_real_xp_once(self, client: AsyncClient, test_user):
        """The ordering strategy: correctness depends only on the options'
        stored `order` column, not on `is_correct` (every option on this
        exercise is marked correct -- ordering exercises use position, not a
        correctness flag)."""
        lesson = (await client.get("/lessons/32", headers=test_user["headers"])).json()
        options = sorted(lesson["exercises"][0]["options"], key=lambda o: o["order"])
        expected_ids = [o["id"] for o in options]

        await client.post("/lessons/32/start", headers=test_user["headers"])

        wrong = (
            await client.post(
                "/exercises/43/submit",
                headers=test_user["headers"],
                json={"exercise_id": 43, "ordered_option_ids": list(reversed(expected_ids))},
            )
        ).json()
        assert wrong["is_correct"] is False
        assert wrong["xp_earned"] == 0

        correct = (
            await client.post(
                "/exercises/43/submit",
                headers=test_user["headers"],
                json={"exercise_id": 43, "ordered_option_ids": expected_ids},
            )
        ).json()
        assert correct["is_correct"] is True
        assert correct["xp_earned"] == 10
        assert correct["lesson_completed"] is True

        again = (
            await client.post(
                "/exercises/43/submit",
                headers=test_user["headers"],
                json={"exercise_id": 43, "ordered_option_ids": expected_ids},
            )
        ).json()
        assert again["xp_earned"] == 0

        progress = (await client.get("/lessons/32/progress", headers=test_user["headers"])).json()
        assert progress["status"] == "completed"
        assert progress["xp_earned"] == 10

    async def test_lesson_progress_is_the_reload_source_of_truth(
        self, client: AsyncClient, test_user
    ):
        """After a reload the browser has no submission response left, so the
        Micro-Quest reads completion and XP from this endpoint instead."""
        # GET /progress is itself what creates the row for a student who has
        # not started the lesson yet, which is why the Micro-Quest issues it on
        # mount: submit_exercise only marks a lesson complete when the row is
        # already there.
        before = (await client.get("/lessons/12/progress", headers=test_user["headers"])).json()
        assert before["status"] != "completed"
        assert before["xp_earned"] == 0

        await client.post(
            "/exercises/22/submit",
            headers=test_user["headers"],
            json={"exercise_id": 22, **CORRECT_ANSWERS[22]},
        )

        after = (await client.get("/lessons/12/progress", headers=test_user["headers"])).json()
        assert after["status"] == "completed"
        assert after["xp_earned"] == 10
        assert after["id"] == before["id"], "a second progress row was created"

    async def test_one_students_completion_does_not_complete_it_for_another(
        self, client: AsyncClient, test_user, second_user
    ):
        """The per-user isolation the frontend's storage key mirrors, proven on
        the side that actually matters."""
        await client.post(
            "/exercises/22/submit",
            headers=test_user["headers"],
            json={"exercise_id": 22, **CORRECT_ANSWERS[22]},
        )
        other = (await client.get("/lessons/12/progress", headers=second_user["headers"])).json()
        assert other["status"] != "completed"
        assert other["xp_earned"] == 0


class TestMicroQuestLeaksNothing:
    """A Micro-Quest lesson goes through the same serializers as any other, so
    it must give the client no more than any other lesson does."""

    @pytest.mark.parametrize("lesson_id", sorted(REFERENCE_QUESTS))
    async def test_lesson_response_hides_answers_and_grading_configuration(
        self, client: AsyncClient, test_user, lesson_id
    ):
        payload = (await client.get(f"/lessons/{lesson_id}", headers=test_user["headers"])).json()
        for exercise in payload["exercises"]:
            assert "solution_code" not in exercise
            assert "test_code" not in exercise
            assert "validation_config" not in exercise
            for option in exercise["options"]:
                assert "is_correct" not in option

    @pytest.mark.parametrize(
        "exercise_id", [18, 22, 47, 49, 27, 23, 26, 29, 34, 37, 40, 56, 58, 43]
    )
    async def test_exercise_endpoint_hides_the_same_fields(
        self, client: AsyncClient, test_user, exercise_id
    ):
        payload = (
            await client.get(f"/exercises/{exercise_id}", headers=test_user["headers"])
        ).json()
        assert "solution_code" not in payload
        assert "test_code" not in payload
        assert "validation_config" not in payload
        for option in payload["options"]:
            assert "is_correct" not in option

    async def test_blueprint_config_never_carries_the_graded_answer(self, db_session):
        """A blueprint's own answer is in its config by design — it is a
        teaching device that awards nothing. What must never leak through it is
        the *exercise's* answer, which is what XP actually depends on."""
        for lesson_id, (_, exercise_id, _, _) in REFERENCE_QUESTS.items():
            config = json.dumps(await _blueprint_config(db_session, lesson_id), ensure_ascii=False)
            exercise = (
                await db_session.execute(select(Exercise).where(Exercise.id == exercise_id))
            ).scalar_one()
            for secret in (exercise.solution_code, exercise.test_code, exercise.validation_config):
                if secret and secret.strip():
                    assert secret not in config, f"lesson {lesson_id} blueprint leaks the answer"
