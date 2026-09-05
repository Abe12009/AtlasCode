"""Audit every exercise in the database for a valid grading strategy.

Run:  python check_exercises.py [path/to/atlascode.db]

Reports totals by type, which grading strategy each exercise resolves to, and
every structural defect that would make an exercise ungradable or unanswerable.
Exits non-zero if anything is broken, so it can gate a release.
"""

import json
import sys
from collections import Counter, defaultdict

sys.path.insert(0, ".")

from app.models import ExerciseTypeEnum
from app.services.exercise_grading import UNGRADABLE, resolve_strategy

DB = sys.argv[1] if len(sys.argv) > 1 else "atlascode.db"
LANGUAGES = {"en", "fr", "ar"}


class Row:
    """Duck-types the bits of the Exercise/Option models the grader reads."""

    def __init__(self, **kw):
        self.__dict__.update(kw)


def main():
    import sqlite3

    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row

    options_by_exercise = defaultdict(list)
    for o in conn.execute("select id, exercise_id, `order`, is_correct from exercise_options"):
        options_by_exercise[o["exercise_id"]].append(
            Row(id=o["id"], order=o["order"], is_correct=bool(o["is_correct"]))
        )

    option_langs = defaultdict(set)
    for r in conn.execute("select option_id, language from exercise_option_translations"):
        option_langs[r["option_id"]].add(r["language"])

    exercise_langs = defaultdict(set)
    for r in conn.execute("select exercise_id, language from exercise_translations"):
        exercise_langs[r["exercise_id"]].add(r["language"])

    exercises = list(conn.execute("select * from exercises order by id"))

    by_type = Counter()
    by_strategy = Counter()
    strategy_by_type = defaultdict(Counter)
    with_test = with_config = 0
    bad_json = []
    ungradable = []
    mcq_no_options = []
    mcq_bad_correct = []
    mcq_too_few = []
    missing_ex_translations = []
    missing_opt_translations = []

    for e in exercises:
        etype = ExerciseTypeEnum(e["exercise_type"])
        by_type[e["exercise_type"]] += 1
        opts = options_by_exercise.get(e["id"], [])

        if (e["test_code"] or "").strip():
            with_test += 1
        raw_cfg = (e["validation_config"] or "").strip()
        if raw_cfg:
            with_config += 1
            try:
                json.loads(raw_cfg)
            except ValueError as exc:
                bad_json.append((e["id"], e["exercise_type"], str(exc)))

        ex = Row(
            id=e["id"],
            exercise_type=etype,
            test_code=e["test_code"],
            validation_config=e["validation_config"],
        )
        strategy = resolve_strategy(ex, opts)
        by_strategy[strategy] += 1
        strategy_by_type[e["exercise_type"]][strategy] += 1
        if strategy == UNGRADABLE:
            ungradable.append((e["id"], e["exercise_type"]))

        if etype == ExerciseTypeEnum.multiple_choice:
            if not opts:
                mcq_no_options.append(e["id"])
            else:
                if len(opts) < 2:
                    mcq_too_few.append((e["id"], len(opts)))
                n_correct = sum(1 for o in opts if o.is_correct)
                if n_correct != 1:
                    mcq_bad_correct.append((e["id"], n_correct))

        if not LANGUAGES.issubset(exercise_langs.get(e["id"], set())):
            missing_ex_translations.append(
                (e["id"], sorted(LANGUAGES - exercise_langs.get(e["id"], set())))
            )
        for o in opts:
            if not LANGUAGES.issubset(option_langs.get(o.id, set())):
                missing_opt_translations.append(
                    (o.id, sorted(LANGUAGES - option_langs.get(o.id, set())))
                )

    total = len(exercises)
    mcq_total = by_type.get("multiple_choice", 0)
    mcq_with_options = sum(
        1 for e in exercises
        if e["exercise_type"] == "multiple_choice" and options_by_exercise.get(e["id"])
    )

    print(f"Database: {DB}")
    print(f"\nTotal exercises: {total}")

    print("\nExercises by type:")
    for t, n in by_type.most_common():
        print(f"  {t:20} {n:4}")

    print(f"\nExercises with test_code:         {with_test}")
    print(f"Exercises with validation_config: {with_config}")
    print(f"Malformed validation_config JSON: {len(bad_json)}")
    for row in bad_json:
        print(f"    exercise {row[0]} ({row[1]}): {row[2]}")

    print(f"\nMultiple-choice exercises:            {mcq_total}")
    print(f"  ...with options:                    {mcq_with_options}")
    print(f"  ...with NO options:                 {len(mcq_no_options)} {mcq_no_options}")
    print(f"  ...with fewer than 2 options:       {len(mcq_too_few)} {mcq_too_few}")
    print(f"  ...without exactly one correct:     {len(mcq_bad_correct)} {mcq_bad_correct}")

    print(f"\nExercises missing an en/fr/ar translation: {len(missing_ex_translations)}")
    for row in missing_ex_translations[:20]:
        print(f"    exercise {row[0]} missing {row[1]}")
    print(f"Options missing an en/fr/ar translation:   {len(missing_opt_translations)}")
    for row in missing_opt_translations[:20]:
        print(f"    option {row[0]} missing {row[1]}")

    print("\nGrading strategy resolved per exercise:")
    for s, n in by_strategy.most_common():
        print(f"  {s:20} {n:4}")

    print("\nStrategy by type:")
    for t in sorted(strategy_by_type):
        parts = ", ".join(f"{s}={n}" for s, n in strategy_by_type[t].most_common())
        print(f"  {t:20} {parts}")

    print(f"\nExercises that CANNOT be graded: {len(ungradable)}")
    for row in ungradable:
        print(f"    exercise {row[0]} ({row[1]})")

    problems = (
        len(bad_json) + len(ungradable) + len(mcq_no_options) + len(mcq_bad_correct)
        + len(mcq_too_few) + len(missing_ex_translations) + len(missing_opt_translations)
    )
    print(f"\n{'ALL EXERCISES OK' if problems == 0 else f'PROBLEMS FOUND: {problems}'}")
    return 0 if problems == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
