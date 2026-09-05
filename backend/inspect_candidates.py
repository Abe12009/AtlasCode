import sqlite3, sys, json

conn = sqlite3.connect('file:atlascode.db?mode=ro', uri=True)
conn.row_factory = sqlite3.Row

IDS = [int(x) for x in sys.argv[1:]]

for lid in IDS:
    print('=' * 90)
    for r in conn.execute('select id,`order`,difficulty,xp_reward,estimated_minutes,slug from lessons where id=?', (lid,)):
        print(dict(r))
    for r in conn.execute("select title from lesson_translations where lesson_id=? and language='en'", (lid,)):
        print('TITLE:', r['title'])
    print('-- blocks --')
    for b in conn.execute('select id,block_type,`order`,content,code_example from lesson_blocks where lesson_id=? order by `order`', (lid,)):
        d = dict(b)
        print({k: (v[:400] if isinstance(v, str) else v) for k, v in d.items()})
    print('-- exercises --')
    for e in conn.execute('select id,exercise_type,`order`,xp_reward,starter_code,solution_code,test_code,validation_config from exercises where lesson_id=? order by `order`', (lid,)):
        d = dict(e)
        print({k: (v[:400] if isinstance(v, str) else v) for k, v in d.items()})
    print('-- ex translations (en) --')
    for e in conn.execute("select et.exercise_id,et.prompt,et.hint,et.explanation from exercise_translations et join exercises e on e.id=et.exercise_id where e.lesson_id=? and et.language='en'", (lid,)):
        print(dict(e))
    print('-- options (en) --')
    for o in conn.execute("select o.id,o.exercise_id,o.`order`,o.is_correct,ot.text from exercise_options o join exercise_option_translations ot on ot.option_id=o.id and ot.language='en' join exercises e on e.id=o.exercise_id where e.lesson_id=? order by o.exercise_id,o.`order`", (lid,)):
        print(dict(o))
