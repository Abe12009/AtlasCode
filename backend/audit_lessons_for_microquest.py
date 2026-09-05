"""Audit all 127 lessons for Micro-Quest candidacy (Phase 11, Task 1).

Classifies every lesson by course, module, title, exercise type(s), exercise
count, difficulty, and whether it already has Micro-Quest blocks. Suggests a
blueprint type based on simple, transparent heuristics (kept deliberately
dumb — this is a starting point for human selection, not an authority).

Run:  python audit_lessons_for_microquest.py [path/to/atlascode.db]

Writes:
  - microquest_audit.json   (machine-readable, every lesson)
  - microquest_audit.md     (human-readable summary + top candidates)
"""

import json
import sys
import sqlite3

DB = sys.argv[1] if len(sys.argv) > 1 else "atlascode.db"

#: Keyword hints -> suggested blueprint kind. Order matters: first match wins.
BLUEPRINT_HINTS = [
    (("debug", "bug", "fix the", "off-by-one", "broken"), "spot_the_bug"),
    (("order", "sequence", "flow", "steps", "workflow", "execution", "lifecycle", "process"), "order_steps"),
    (("vs.", "vs ", "types", "compare", "difference", "terms", "vocabulary", "definitions",
      "commands", "protocols", "keywords", "concepts"), "match_pairs"),
]


def suggest_blueprint(title: str, exercise_type: str) -> str:
    text = title.lower()
    if exercise_type == "debugging":
        return "spot_the_bug"
    for keywords, kind in BLUEPRINT_HINTS:
        if any(k in text for k in keywords):
            return kind
    # Default: most concepts in this curriculum are "term <-> meaning" pairs.
    return "match_pairs"


def main() -> int:
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row

    lessons = list(conn.execute(
        """
        select l.id, l.slug, l.`order`, l.difficulty, l.estimated_minutes, l.xp_reward,
               lt.title as title_en,
               m.id as module_id, mt.title as module_title,
               c.id as course_id, ct.title as course_title
        from lessons l
        join lesson_translations lt on lt.lesson_id = l.id and lt.language = 'en'
        join modules m on m.id = l.module_id
        join module_translations mt on mt.module_id = m.id and mt.language = 'en'
        join courses c on c.id = m.course_id
        join course_translations ct on ct.course_id = c.id and ct.language = 'en'
        order by l.id
        """
    ))

    existing_mq_lessons = {
        r["lesson_id"]
        for r in conn.execute(
            "select distinct lesson_id from lesson_blocks where block_type = 'hook'"
        )
    }

    records = []
    for lesson in lessons:
        exercises = list(conn.execute(
            "select id, exercise_type, xp_reward, test_code, validation_config "
            "from exercises where lesson_id = ? order by `order`, id",
            (lesson["id"],),
        ))
        exercise_types = sorted({e["exercise_type"] for e in exercises})
        n_blocks = conn.execute(
            "select count(*) from lesson_blocks where lesson_id = ?", (lesson["id"],)
        ).fetchone()[0]

        record = {
            "lesson_id": lesson["id"],
            "slug": lesson["slug"],
            "order": lesson["order"],
            "title_en": lesson["title_en"],
            "module_id": lesson["module_id"],
            "module_title": lesson["module_title"],
            "course_id": lesson["course_id"],
            "course_title": lesson["course_title"],
            "difficulty": lesson["difficulty"],
            "estimated_minutes": lesson["estimated_minutes"],
            "n_exercises": len(exercises),
            "exercise_types": exercise_types,
            "exercise_ids": [e["id"] for e in exercises],
            "n_reading_blocks": n_blocks,
            "already_microquest": lesson["id"] in existing_mq_lessons,
            "single_exercise": len(exercises) == 1,
            "suggested_blueprint": (
                suggest_blueprint(lesson["title_en"], exercise_types[0])
                if len(exercise_types) == 1
                else None
            ),
        }
        records.append(record)

    with open("microquest_audit.json", "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    candidates = [
        r for r in records
        if r["single_exercise"] and not r["already_microquest"]
    ]

    with open("microquest_audit.md", "w", encoding="utf-8") as f:
        f.write(f"# Micro-Quest candidacy audit\n\n")
        f.write(f"Total lessons: {len(records)}\n\n")
        f.write(f"Already Micro-Quest: {len(existing_mq_lessons)} -> {sorted(existing_mq_lessons)}\n\n")
        f.write(f"Single-exercise, not yet Micro-Quest (candidates): {len(candidates)}\n\n")

        f.write("## Candidates by course\n\n")
        by_course: dict[str, list] = {}
        for r in candidates:
            by_course.setdefault(r["course_title"], []).append(r)
        for course_title in sorted(by_course):
            group = by_course[course_title]
            f.write(f"### {course_title} ({len(group)} candidates)\n\n")
            f.write("| lesson | title | exercise type | difficulty | suggested blueprint |\n")
            f.write("|---|---|---|---|---|\n")
            for r in sorted(group, key=lambda x: x["lesson_id"]):
                f.write(
                    f"| {r['lesson_id']} | {r['title_en']} | {r['exercise_types'][0]} | "
                    f"{r['difficulty']} | {r['suggested_blueprint']} |\n"
                )
            f.write("\n")

        f.write("## All lessons NOT eligible (multi-exercise or already Micro-Quest)\n\n")
        ineligible = [r for r in records if not r["single_exercise"] or r["already_microquest"]]
        f.write(f"Count: {len(ineligible)}\n\n")
        f.write("| lesson | title | n_exercises | already_mq |\n|---|---|---|---|\n")
        for r in sorted(ineligible, key=lambda x: x["lesson_id"]):
            f.write(f"| {r['lesson_id']} | {r['title_en']} | {r['n_exercises']} | {r['already_microquest']} |\n")

    print(f"Total lessons: {len(records)}")
    print(f"Already Micro-Quest: {sorted(existing_mq_lessons)}")
    print(f"Eligible candidates (single exercise, not yet Micro-Quest): {len(candidates)}")
    print("\nCandidates by course:")
    for course_title in sorted(by_course):
        types = sorted({r["exercise_types"][0] for r in by_course[course_title]})
        print(f"  {course_title}: {len(by_course[course_title])} candidates, exercise types present: {types}")
    print("\nWrote microquest_audit.json and microquest_audit.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
