# -*- coding: utf-8 -*-
"""Builders for authoring a Micro-Quest lesson's three special blocks.

``microquest_content.py`` originally wrote each block as a raw dict, which
meant typing the English prose twice — once as the top-level ``content`` (what
the pre-Micro-Quest schema always stored) and again as
``translations["en"]`` — with nothing to catch the two drifting apart. These
builders take the English text exactly once, as part of a normal
``{"en": ..., "fr": ..., "ar": ...}`` localized dict, and derive ``content``
from it.

Adding a Micro-Quest lesson with this module is:

    from app.seed.microquest_authoring import hook_block, spot_the_bug_blueprint, exam_tip_block

    MY_LESSON_BLOCKS = [
        hook_block(order=0, prose={...}, challenge={...}, learn={...}),
        spot_the_bug_blueprint(order=4, prose={...}, statements=[...], buggy_id="..."),
        exam_tip_block(order=5, prose={...}),
    ]

— a content operation. No frontend change is needed: the blueprint kind
dispatches through the existing ``Blueprint.tsx``, and a kind it does not
recognise falls back safely (see ``Blueprint.tsx``'s ``UnsupportedBlueprint``)
rather than crashing the lesson.

Every builder returns a block in the shape ``seed_blocks()`` (this package)
and the ``add_microquest_lessons_*`` migrations already expect:
``{"block_type", "order", "content", "translations", "config"}``, with
``translations`` a language -> text dict and ``config`` a plain (not yet
JSON-encoded) dict. Nothing downstream needs to change to support a new
builder's output.
"""

from typing import Optional

#: A piece of prose or a label, written once in every language it must ship
#: in. Every builder requires at least "en"; check_microquests.py is the
#: authority on which languages a shipped lesson must actually carry.
Localized = dict[str, str]


def _text_block(block_type: str, order: int, prose: Localized, config: dict) -> dict:
    if "en" not in prose:
        raise ValueError(f"{block_type} at order {order}: prose has no 'en' entry")
    return {
        "block_type": block_type,
        "order": order,
        "content": prose["en"],
        "translations": dict(prose),
        "config": config,
    }


def hook_block(*, order: int, prose: Localized, challenge: Localized, learn: Localized) -> dict:
    """The Local Hook: a short real-world scenario (``prose``), the question it
    raises (``challenge``), and what the student is about to learn (``learn``)."""
    return _text_block(
        "hook", order, prose, {"kind": "hook", "challenge": challenge, "learn": learn}
    )


def exam_tip_block(*, order: int, prose: Localized) -> dict:
    """One short callout about a mechanic the student can verify in this
    lesson. Never a claim about an official exam paper — see
    ``microquest_content.py``'s module docstring for why."""
    return _text_block("exam_tip", order, prose, {"kind": "exam_tip"})


def order_steps_blueprint(
    *,
    order: int,
    prose: Localized,
    steps: list[tuple[str, Localized]],
    correct_order: list[str],
    success: Optional[Localized] = None,
    hint: Optional[Localized] = None,
) -> dict:
    """"Put these plain-language steps in the order a program runs them."
    ``steps`` is a list of ``(id, label)`` pairs; ``correct_order`` lists those
    same ids in the order they belong."""
    config: dict = {
        "kind": "order_steps",
        "steps": [{"id": step_id, "label": label} for step_id, label in steps],
        "correct_order": correct_order,
    }
    if success is not None:
        config["success"] = success
    if hint is not None:
        config["hint"] = hint
    return _text_block("blueprint", order, prose, config)


def match_pairs_blueprint(
    *,
    order: int,
    prose: Localized,
    pairs: list[tuple[str, Localized, Localized]],
    success: Optional[Localized] = None,
    hint: Optional[Localized] = None,
) -> dict:
    """"Connect each concept to what it actually does." ``pairs`` is a list of
    ``(id, left, right)`` triples; left and right of the same id belong
    together."""
    config: dict = {
        "kind": "match_pairs",
        "pairs": [{"id": pid, "left": left, "right": right} for pid, left, right in pairs],
    }
    if success is not None:
        config["success"] = success
    if hint is not None:
        config["hint"] = hint
    return _text_block("blueprint", order, prose, config)


def spot_the_bug_blueprint(
    *,
    order: int,
    prose: Localized,
    statements: list[tuple[str, Localized]],
    buggy_id: str,
    snippet: Optional[str] = None,
    success: Optional[Localized] = None,
    hint: Optional[Localized] = None,
) -> dict:
    """"Exactly one of these claims is wrong — which one?" ``statements`` is a
    list of ``(id, text)`` pairs; ``buggy_id`` names the one that is false.
    ``snippet``, if given, is plain (not localized) source code shown above the
    statements for context — code is never translated."""
    if buggy_id not in {sid for sid, _ in statements}:
        raise ValueError(f"buggy_id {buggy_id!r} is not one of the statement ids")
    config: dict = {
        "kind": "spot_the_bug",
        "statements": [{"id": sid, "text": text} for sid, text in statements],
        "buggy_id": buggy_id,
    }
    if snippet is not None:
        config["snippet"] = snippet
    if success is not None:
        config["success"] = success
    if hint is not None:
        config["hint"] = hint
    return _text_block("blueprint", order, prose, config)


#: Every block_type a Micro-Quest is expected to carry, and how many.
_REQUIRED_BLOCK_COUNTS = {"hook": 1, "blueprint": 1, "exam_tip": 1}

#: Blueprint kinds this authoring module (and the frontend's Blueprint.tsx)
#: knows how to build/render. Keep in sync with Blueprint.tsx's dispatch.
_SUPPORTED_BLUEPRINT_KINDS = {"order_steps", "match_pairs", "spot_the_bug"}


def validate_blocks(blocks: list[dict]) -> list[str]:
    """Cheap, immediate sanity checks an author can run before ever seeding a
    lesson — a typo caught here is a typo that never reaches the database.

    This is deliberately not a replacement for ``check_microquests.py``, which
    is the authoritative audit and runs against the real, seeded database (it
    also catches things no amount of authoring-time checking can, like a
    second lesson accidentally claiming the same block order). This exists so
    a mistake is visible immediately, in the same file the content was typed
    in, rather than several steps later.
    """
    problems: list[str] = []
    counts: dict[str, int] = {}

    for block in blocks:
        block_type = block.get("block_type")
        counts[block_type] = counts.get(block_type, 0) + 1
        label = f"{block_type} (order {block.get('order')})"

        translations = block.get("translations") or {}
        if block.get("content") != translations.get("en"):
            problems.append(f"{label}: content does not match translations['en']")
        for language in ("en", "fr", "ar"):
            if not (translations.get(language) or "").strip():
                problems.append(f"{label}: missing or blank {language} translation")

        config = block.get("config")
        if not isinstance(config, dict):
            problems.append(f"{label}: config is missing or not a dict")
            continue
        kind = config.get("kind")
        if block_type in ("hook", "exam_tip") and kind != block_type:
            problems.append(f"{label}: config.kind is {kind!r}, expected {block_type!r}")
        if block_type == "blueprint" and kind not in _SUPPORTED_BLUEPRINT_KINDS:
            problems.append(f"{label}: unsupported blueprint kind {kind!r}")

    for block_type, wanted in _REQUIRED_BLOCK_COUNTS.items():
        found = counts.get(block_type, 0)
        if found != wanted:
            problems.append(f"expected exactly {wanted} '{block_type}' block, found {found}")

    return problems
