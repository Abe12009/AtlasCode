"""Audit en/fr/ar coverage across every translatable curriculum table.

Run:  python check_translations.py [path/to/atlascode.db]

Exits non-zero if anything is missing, so it can gate a release.
"""

import sqlite3
import sys

DB = sys.argv[1] if len(sys.argv) > 1 else "atlascode.db"
LANGUAGES = ("en", "fr", "ar")

#: (label, parent table, translation table, foreign key column)
TABLES = [
    ("courses", "courses", "course_translations", "course_id"),
    ("modules", "modules", "module_translations", "module_id"),
    ("lessons", "lessons", "lesson_translations", "lesson_id"),
    ("lesson blocks", "lesson_blocks", "lesson_block_translations", "block_id"),
    ("exercises", "exercises", "exercise_translations", "exercise_id"),
    ("exercise options", "exercise_options", "exercise_option_translations", "option_id"),
    ("projects", "projects", "project_translations", "project_id"),
    ("project tasks", "project_tasks", "project_task_translations", "task_id"),
    ("achievements", "achievements", "achievement_translations", "achievement_id"),
]


def main() -> int:
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row

    print(f"Database: {DB}")
    print(f"Required languages: {', '.join(LANGUAGES)}\n")
    print(f"{'entity':18} {'rows':>6} {'complete':>9} {'missing':>8}")
    print("-" * 45)

    problems = 0
    details = []
    for label, parent, child, fk in TABLES:
        total = conn.execute(f"select count(*) from {parent}").fetchone()[0]
        complete = conn.execute(
            f"""select count(*) from {parent} p
                where (select count(distinct language) from {child} t
                       where t.{fk} = p.id and t.language in ({','.join('?' * len(LANGUAGES))})) >= ?""",
            (*LANGUAGES, len(LANGUAGES)),
        ).fetchone()[0]
        missing = total - complete
        problems += missing
        print(f"{label:18} {total:6} {complete:9} {missing:8}")

        if missing:
            rows = conn.execute(
                f"""select p.id, (select group_concat(distinct t.language) from {child} t
                                  where t.{fk} = p.id) langs
                    from {parent} p
                    where (select count(distinct language) from {child} t
                           where t.{fk} = p.id and t.language in ({','.join('?' * len(LANGUAGES))})) < ?
                    limit 15""",
                (*LANGUAGES, len(LANGUAGES)),
            ).fetchall()
            for row in rows:
                details.append(f"    {label} id={row['id']} has: {row['langs'] or '(none)'}")

    # Blank translations count as missing: a row that exists but says nothing
    # would silently render as an empty lesson.
    blank = conn.execute(
        "select count(*) from lesson_block_translations "
        "where content is null or trim(content) = ''"
    ).fetchone()[0]
    print(f"\nblank lesson-block translation rows: {blank}")
    problems += blank

    # Code must be identical in every language: it is code, not prose.
    code_drift = conn.execute(
        """select count(*) from lesson_block_translations t
           join lesson_blocks b on b.id = t.block_id
           where coalesce(t.code_example, '') <> coalesce(b.code_example, '')"""
    ).fetchone()[0]
    print(f"translation rows whose code differs from the base block: {code_drift}")
    problems += code_drift

    if details:
        print("\nIncomplete entities:")
        for line in details:
            print(line)

    print(f"\n{'ALL TRANSLATIONS COMPLETE' if problems == 0 else f'PROBLEMS FOUND: {problems}'}")
    return 0 if problems == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
