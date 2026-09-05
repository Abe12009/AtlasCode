"""Authoring-time sanity checks for Micro-Quest content.

These run against the raw Python data in microquest_content.py, before it
ever reaches a database — the same content check_microquests.py audits again,
authoritatively, once it has actually been seeded. Catching a mistake here is
strictly earlier and strictly cheaper than catching it there.
"""

import pytest

from app.seed.microquest_authoring import (
    exam_tip_block,
    hook_block,
    match_pairs_blueprint,
    order_steps_blueprint,
    spot_the_bug_blueprint,
    validate_blocks,
)
from app.seed.microquest_content import MICROQUEST_BY_SLUG


class TestEveryAuthoredMicroQuestPassesTheAuthoringValidator:
    @pytest.mark.parametrize("slug", sorted(MICROQUEST_BY_SLUG))
    def test_no_problems(self, slug):
        assert validate_blocks(MICROQUEST_BY_SLUG[slug]) == []


class TestBuilders:
    def test_hook_block_derives_content_from_the_english_prose(self):
        block = hook_block(
            order=0,
            prose={"en": "Scenario.", "fr": "Scénario.", "ar": "سيناريو."},
            challenge={"en": "Q?", "fr": "Q ?", "ar": "س؟"},
            learn={"en": "L.", "fr": "L.", "ar": "ل."},
        )
        assert block["content"] == "Scenario."
        assert block["translations"] == {"en": "Scenario.", "fr": "Scénario.", "ar": "سيناريو."}
        assert block["config"] == {
            "kind": "hook",
            "challenge": {"en": "Q?", "fr": "Q ?", "ar": "س؟"},
            "learn": {"en": "L.", "fr": "L.", "ar": "ل."},
        }
        assert block["block_type"] == "hook"
        assert block["order"] == 0

    def test_hook_block_requires_english(self):
        with pytest.raises(ValueError):
            hook_block(order=0, prose={"fr": "Scénario."}, challenge={}, learn={})

    def test_exam_tip_block(self):
        block = exam_tip_block(order=5, prose={"en": "Tip.", "fr": "Astuce.", "ar": "نصيحة."})
        assert block["block_type"] == "exam_tip"
        assert block["content"] == "Tip."
        assert block["config"] == {"kind": "exam_tip"}

    def test_order_steps_blueprint_builds_steps_and_correct_order(self):
        block = order_steps_blueprint(
            order=4,
            prose={"en": "Order these.", "fr": "Ordonnez.", "ar": "رتّب."},
            steps=[("a", {"en": "First"}), ("b", {"en": "Second"})],
            correct_order=["a", "b"],
            hint={"en": "hint", "fr": "indice", "ar": "تلميح"},
        )
        assert block["config"]["kind"] == "order_steps"
        assert block["config"]["steps"] == [
            {"id": "a", "label": {"en": "First"}},
            {"id": "b", "label": {"en": "Second"}},
        ]
        assert block["config"]["correct_order"] == ["a", "b"]
        assert block["config"]["hint"] == {"en": "hint", "fr": "indice", "ar": "تلميح"}
        assert "success" not in block["config"]

    def test_match_pairs_blueprint_builds_pairs(self):
        block = match_pairs_blueprint(
            order=4,
            prose={"en": "Connect these.", "fr": "Reliez.", "ar": "صِل."},
            pairs=[("x", {"en": "Left"}, {"en": "Right"})],
        )
        assert block["config"]["kind"] == "match_pairs"
        assert block["config"]["pairs"] == [{"id": "x", "left": {"en": "Left"}, "right": {"en": "Right"}}]

    def test_spot_the_bug_blueprint_builds_statements(self):
        block = spot_the_bug_blueprint(
            order=4,
            prose={"en": "Spot it.", "fr": "Trouvez.", "ar": "اكتشف."},
            statements=[
                ("a", {"en": "True claim"}),
                ("b", {"en": "False claim"}),
                ("c", {"en": "Another true claim"}),
            ],
            buggy_id="b",
            snippet="x = 1",
        )
        assert block["config"]["kind"] == "spot_the_bug"
        assert block["config"]["buggy_id"] == "b"
        assert block["config"]["snippet"] == "x = 1"
        assert len(block["config"]["statements"]) == 3

    def test_spot_the_bug_blueprint_rejects_a_buggy_id_that_names_no_statement(self):
        with pytest.raises(ValueError):
            spot_the_bug_blueprint(
                order=4,
                prose={"en": "Spot it."},
                statements=[("a", {"en": "A"}), ("b", {"en": "B"}), ("c", {"en": "C"})],
                buggy_id="nope",
            )


class TestValidateBlocksCatchesRealMistakes:
    """The exact class of mistake the authoring module exists to prevent:
    content drifting out of sync with the English translation, a missing
    language, an unsupported blueprint kind, or a lesson shaped wrong."""

    def _good_blocks(self):
        return [
            hook_block(
                order=0,
                prose={"en": "Scenario.", "fr": "Scénario.", "ar": "سيناريو."},
                challenge={"en": "Q?"},
                learn={"en": "L."},
            ),
            spot_the_bug_blueprint(
                order=4,
                prose={"en": "Spot it.", "fr": "Trouvez.", "ar": "اكتشف."},
                statements=[("a", {"en": "A"}), ("b", {"en": "B"}), ("c", {"en": "C"})],
                buggy_id="b",
            ),
            exam_tip_block(order=5, prose={"en": "Tip.", "fr": "Astuce.", "ar": "نصيحة."}),
        ]

    def test_the_reference_shape_passes(self):
        assert validate_blocks(self._good_blocks()) == []

    def test_catches_content_drifted_from_the_english_translation(self):
        blocks = self._good_blocks()
        blocks[0]["content"] = "Something the author edited without updating translations['en']."
        problems = validate_blocks(blocks)
        assert any("does not match translations" in p for p in problems)

    def test_catches_a_missing_language(self):
        blocks = self._good_blocks()
        del blocks[0]["translations"]["ar"]
        problems = validate_blocks(blocks)
        assert any("missing or blank ar" in p for p in problems)

    def test_catches_a_blank_translation(self):
        blocks = self._good_blocks()
        blocks[0]["translations"]["fr"] = "   "
        problems = validate_blocks(blocks)
        assert any("missing or blank fr" in p for p in problems)

    def test_catches_an_unsupported_blueprint_kind(self):
        blocks = self._good_blocks()
        blocks[1]["config"] = {"kind": "draw_flowchart"}
        problems = validate_blocks(blocks)
        assert any("unsupported blueprint kind" in p for p in problems)

    def test_catches_a_missing_block_type(self):
        blocks = self._good_blocks()[:2]  # drop the exam_tip
        problems = validate_blocks(blocks)
        assert any("exactly 1 'exam_tip'" in p for p in problems)

    def test_catches_a_duplicate_block_type(self):
        blocks = self._good_blocks()
        blocks.append(self._good_blocks()[0])  # a second hook
        problems = validate_blocks(blocks)
        assert any("exactly 1 'hook'" in p for p in problems)
