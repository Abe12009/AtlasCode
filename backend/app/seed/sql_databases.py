from .base import (
    get_or_create_course, get_or_create_module, get_or_create_lesson,
    LanguageEnum, DifficultyEnum, ExerciseTypeEnum
)
from .microquest_content import seed_blocks


async def seed_sql_databases(db):
    print("Seeding SQL & Databases...")
    
    course_id = await get_or_create_course(db, "sql-databases", 3, [
        {"language": LanguageEnum.en, "title": "SQL & Databases", "description": "Store, query, and manage data with relational databases", "skills": "SQL, relational databases, queries, joins"},
        {"language": LanguageEnum.fr, "title": "SQL et Bases de Données", "description": "Stockez, interrogez et gérez les données avec les bases relationnelles", "skills": "SQL, bases relationnelles, requêtes, jointures"},
        {"language": LanguageEnum.ar, "title": "SQL وقواعد البيانات", "description": "خزن، استعلم، وأدر البيانات مع قواعد البيانات العلائقية", "skills": "SQL، قواعد علائقية، استعلامات، انضمامات"},
    ])
    
    module_id = await get_or_create_module(db, course_id, "sql-fundamentals", 1, [
        {"language": LanguageEnum.en, "title": "SQL Fundamentals", "description": "Master the language of data"},
        {"language": LanguageEnum.fr, "title": "Fondamentaux SQL", "description": "Maîtrisez le langage des données"},
        {"language": LanguageEnum.ar, "title": "أساسيات SQL", "description": "أتقن لغة البيانات"},
    ])
    
    # Lesson 25: Databases and Tables
    await get_or_create_lesson(db, module_id, "databases-and-tables", 1,
        DifficultyEnum.beginner, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "Databases and Tables", "story": "Understand how data is organized in relational databases", "objective": "Explain tables, rows, columns, primary keys, and relationships", "skills": "Tables, rows, columns, primary keys, foreign keys"},
            {"language": LanguageEnum.fr, "title": "Bases de Données et Tables", "story": "Comprenez comment les données sont organisées dans les bases relationnelles", "objective": "Expliquer tables, lignes, colonnes, clés primaires et relations", "skills": "Tables, lignes, colonnes, clés primaires, clés étrangères"},
            {"language": LanguageEnum.ar, "title": "قواعد البيانات والجداول", "story": "افهم كيف تنظم البيانات في قواعد البيانات العلائقية", "objective": "شرح الجداول، الصفوف، الأعمدة، المفاتيح الأساسية، والعلاقات", "skills": "جداول، صفوف، أعمدة، مفاتيح أساسية، مفاتيح خارجية"},
        ],
        [
            {"type": "text", "order": 1, "content": "A database stores data in tables. Tables have rows (records) and columns (fields). Each table should have a primary key - a unique identifier for each row. Foreign keys link tables together."},
            {"type": "code", "order": 2, "content": "Conceptual table structure:", "code_example": "-- students table\n-- id (PK) | name       | email\n-- 1        | Amine      | amine@email.com\n-- 2        | Fatima     | fatima@email.com\n\n-- courses table\n-- id (PK) | title\n-- 1        | Python\n-- 2        | SQL\n\n-- enrollments table\n-- student_id (FK) | course_id (FK)\n-- 1                | 1\n-- 2                | 1\n-- 2                | 2"},
            {"type": "text", "order": 3, "content": "PK = Primary Key (unique, not null). FK = Foreign Key (references another table's PK). Relationships: one-to-many, many-to-many."},
            # Micro-Quest blocks (hook 0, blueprint 4, exam_tip 5). The blueprint
            # is the match_pairs interaction. Lessons without these render as before.
            *seed_blocks("databases-and-tables"),
        ],
        [
            {
                "type": ExerciseTypeEnum.multiple_choice,
                "order": 1,
                "xp_reward": 10,
                "starter_code": "",
                "solution_code": "",
                "validation_config": "",
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "What is a primary key?", "hint": "Unique identifier for each row", "explanation": "A primary key uniquely identifies each record in a table. It cannot be null and must be unique."},
                    {"language": LanguageEnum.fr, "prompt": "Qu'est-ce qu'une clé primaire ?", "hint": "Identifiant unique pour chaque ligne", "explanation": "Une clé primaire identifie de façon unique chaque enregistrement dans une table. Elle ne peut pas être nulle et doit être unique."},
                    {"language": LanguageEnum.ar, "prompt": "ما هو المفتاح الأساسي؟", "hint": "معرّف فريد لكل صف", "explanation": "المفتاح الأساسي يحدد بشكل فريد كل سجل في الجدول. لا يمكن أن يكون معدوماً ويجب أن يكون فريداً."},
                ],
                "options": [
                    {"order": 1, "is_correct": True, "translations": [{"language": LanguageEnum.en, "text": "A unique identifier for each row"}, {"language": LanguageEnum.fr, "text": "Un identifiant unique pour chaque ligne"}, {"language": LanguageEnum.ar, "text": "معرّف فريد لكل صف"}]},
                    {"order": 2, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "A column that can be empty"}, {"language": LanguageEnum.fr, "text": "Une colonne qui peut être vide"}, {"language": LanguageEnum.ar, "text": "عمود يمكن أن يكون فارغاً"}]},
                    {"order": 3, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "A foreign table reference"}, {"language": LanguageEnum.fr, "text": "Une référence de table étrangère"}, {"language": LanguageEnum.ar, "text": "مرجع جدول خارجي"}]},
                    {"order": 4, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "An index for sorting"}, {"language": LanguageEnum.fr, "text": "Un index pour le tri"}, {"language": LanguageEnum.ar, "text": "فهرس للترتيب"}]},
                ]
            }
        ]
    )
    
    # Lesson 26: SELECT and Filtering
    await get_or_create_lesson(db, module_id, "select-and-filtering", 2,
        DifficultyEnum.beginner, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "SELECT and Filtering", "story": "Retrieve exactly the data you need from tables", "objective": "Write SELECT queries with WHERE, AND, OR, IN, LIKE", "skills": "SELECT, WHERE, filtering, wildcards"},
            {"language": LanguageEnum.fr, "title": "SELECT et Filtrage", "story": "Récupérez exactement les données dont vous avez besoin", "objective": "Écrire des requêtes SELECT avec WHERE, AND, OR, IN, LIKE", "skills": "SELECT, WHERE, filtrage, caractères génériques"},
            {"language": LanguageEnum.ar, "title": "SELECT والتصفية", "story": "استرجع البيانات التي تحتاجها بالضبط من الجداول", "objective": "كتابة استعلامات SELECT مع WHERE، AND، OR، IN، LIKE", "skills": "SELECT، WHERE، تصفية، محارف البدل"},
        ],
        [
            {"type": "text", "order": 1, "content": "SELECT retrieves data. SELECT column FROM table. Use * for all columns. WHERE filters rows. AND/OR combine conditions. IN checks multiple values. LIKE uses % (any chars) and _ (single char) wildcards."},
            {"type": "code", "order": 2, "content": "SELECT examples:", "code_example": "SELECT name, email FROM students;\nSELECT * FROM students WHERE city = 'Casablanca';\nSELECT * FROM students WHERE age >= 20 AND city = 'Rabat';\nSELECT * FROM students WHERE city IN ('Casablanca', 'Rabat');\nSELECT * FROM students WHERE name LIKE 'A%';  -- starts with A"},
            {"type": "text", "order": 3, "content": "String comparisons are case-sensitive in some databases. Use ILIKE for case-insensitive (PostgreSQL). Always quote string values."},
        ],
        [
            {
                "type": ExerciseTypeEnum.code_writing,
                "order": 1,
                "xp_reward": 10,
                "starter_code": "-- Write a query to find all students from Casablanca who are 20 or older\nSELECT ____ FROM students\nWHERE city = '____' AND age ____ 20;",
                "solution_code": "SELECT * FROM students\nWHERE city = 'Casablanca' AND age >= 20;",
                "test_code": "",
                "validation_config": '{"expected_keywords": ["SELECT", "FROM students", "WHERE", "Casablanca", "age >= 20"]}',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Write a query to find students from Casablanca aged 20 or older.", "hint": "Use WHERE with AND, string in quotes, >= for comparison", "explanation": "Combine conditions with AND. String literals in quotes. >= for greater than or equal."},
                    {"language": LanguageEnum.fr, "prompt": "Écrivez une requête pour trouver les étudiants de Casablanca âgés de 20 ans ou plus.", "hint": "Utilisez WHERE avec AND, chaîne entre guillemets, >= pour comparer", "explanation": "Combinez les conditions avec AND. Les littéraux de chaîne entre guillemets. >= pour supérieur ou égal."},
                    {"language": LanguageEnum.ar, "prompt": "اكتب استعلاماً للعثور على الطلاب من الدار البيضاء بعمر 20 أو أكبر.", "hint": "استخدم WHERE مع AND، النص بين علامات التنصيص، >= للمقارنة", "explanation": "اجمع الشروط بـ AND. نصوص بين علامتي تنصيص. >= للأكبر أو يساوي."},
                ]
            }
        ]
    )
    
    # Lesson 27: INSERT, UPDATE and DELETE
    await get_or_create_lesson(db, module_id, "insert-update-delete", 3,
        DifficultyEnum.beginner, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "INSERT, UPDATE and DELETE", "story": "Modify data in your database safely", "objective": "Write INSERT, UPDATE, and DELETE statements", "skills": "INSERT, UPDATE, DELETE, transactions"},
            {"language": LanguageEnum.fr, "title": "INSERT, UPDATE et DELETE", "story": "Modifiez les données dans votre base de données en toute sécurité", "objective": "Écrire les instructions INSERT, UPDATE et DELETE", "skills": "INSERT, UPDATE, DELETE, transactions"},
            {"language": LanguageEnum.ar, "title": "INSERT، UPDATE و DELETE", "story": "عدّل البيانات في قاعدة بياناتك بأمان", "objective": "كتابة عبارات INSERT، UPDATE، و DELETE", "skills": "INSERT، UPDATE، DELETE، المعاملات"},
        ],
        [
            {"type": "text", "order": 1, "content": "INSERT adds rows: INSERT INTO table (col1, col2) VALUES (val1, val2). UPDATE changes existing: UPDATE table SET col = val WHERE condition. DELETE removes: DELETE FROM table WHERE condition. Always use WHERE with UPDATE/DELETE!"},
            {"type": "code", "order": 2, "content": "Data modification:", "code_example": "INSERT INTO students (name, email, city) VALUES ('Omar', 'omar@email.com', 'Marrakech');\n\nUPDATE students SET city = 'Tangier' WHERE id = 1;\n\nDELETE FROM students WHERE id = 2;"},
            {"type": "text", "order": 3, "content": "Without WHERE, UPDATE/DELETE affects ALL rows. Use transactions (BEGIN, COMMIT, ROLLBACK) for multiple related changes."},
        ],
        [
            {
                "type": ExerciseTypeEnum.prediction,
                "order": 1,
                "xp_reward": 10,
                "starter_code": "-- Students table initially:\n-- id | name  | city\n-- 1  | Amine | Casablanca\n-- 2  | Fatima| Rabat\n\nUPDATE students SET city = 'Marrakech' WHERE id = 1;\nDELETE FROM students WHERE id = 2;\n\nSELECT * FROM students;",
                "solution_code": "1 | Amine | Marrakech",
                "validation_config": '{"expected_output": "1 | Amine | Marrakech"}',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "What remains after the UPDATE and DELETE?", "hint": "First row updated, second row deleted", "explanation": "UPDATE changes city for id=1. DELETE removes row with id=2. Only one row remains."},
                    {"language": LanguageEnum.fr, "prompt": "Que reste-t-il après UPDATE et DELETE ?", "hint": "Première ligne modifiée, deuxième supprimée", "explanation": "UPDATE change la ville pour id=1. DELETE supprime la ligne id=2. Une seule ligne reste."},
                    {"language": LanguageEnum.ar, "prompt": "ماذا يبقى بعد UPDATE و DELETE؟", "hint": "الصف الأول معدل، الصف الثاني محذوف", "explanation": "UPDATE يغير المدينة لـ id=1. DELETE يحذف الصف id=2. يبقى صف واحد فقط."},
                ]
            }
        ]
    )
    
    # Lesson 28: Sorting, Grouping and Aggregation
    await get_or_create_lesson(db, module_id, "sorting-grouping-aggregation", 4,
        DifficultyEnum.intermediate, 40, 60,
        [
            {"language": LanguageEnum.en, "title": "Sorting, Grouping and Aggregation", "story": "Summarize and analyze your data", "objective": "Use ORDER BY, GROUP BY, COUNT, SUM, AVG, MIN, MAX", "skills": "ORDER BY, GROUP BY, aggregate functions"},
            {"language": LanguageEnum.fr, "title": "Tri, Groupement et Agrégation", "story": "Résumez et analysez vos données", "objective": "Utiliser ORDER BY, GROUP BY, COUNT, SUM, AVG, MIN, MAX", "skills": "ORDER BY, GROUP BY, fonctions d'agrégation"},
            {"language": LanguageEnum.ar, "title": "الترتيب والتجميع والتجميع", "story": "لخص وحلل بياناتك", "objective": "استخدام ORDER BY، GROUP BY، COUNT، SUM، AVG، MIN، MAX", "skills": "ORDER BY، GROUP BY، دوال التجميع"},
        ],
        [
            {"type": "text", "order": 1, "content": "ORDER BY sorts results: ASC (default) or DESC. GROUP BY aggregates rows with same values. COUNT(), SUM(), AVG(), MIN(), MAX() compute summaries. HAVING filters groups (like WHERE for groups)."},
            {"type": "code", "order": 2, "content": "Aggregation:", "code_example": "SELECT city, COUNT(*) as student_count FROM students GROUP BY city;\nSELECT city, AVG(age) as avg_age FROM students GROUP BY city HAVING COUNT(*) > 1;\nSELECT MAX(score), MIN(score) FROM exams;"},
            {"type": "text", "order": 3, "content": "Columns in SELECT with GROUP BY must be either grouped or aggregated. HAVING runs after GROUP BY, WHERE runs before."},
            # Micro-Quest blocks (hook 0, blueprint 4, exam_tip 5). The blueprint
            # is the spot_the_bug interaction. Lessons without these render as before.
            *seed_blocks("sorting-grouping-aggregation"),
        ],
        [
            {
                "type": ExerciseTypeEnum.code_writing,
                "order": 1,
                "xp_reward": 15,
                "starter_code": "-- Find the average age per city, only for cities with 2+ students\nSELECT city, AVG(age) as avg_age\nFROM students\nGROUP BY ____\nHAVING COUNT(*) ____ 1;",
                "solution_code": "SELECT city, AVG(age) as avg_age\nFROM students\nGROUP BY city\nHAVING COUNT(*) >= 1;",
                "test_code": "",
                "validation_config": '{"expected_keywords": ["GROUP BY city", "HAVING", "COUNT(*)", ">= 1"]}',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Write a query showing average age per city, only for cities with 2+ students.", "hint": "GROUP BY city, HAVING COUNT(*) >= 2", "explanation": "GROUP BY creates groups. HAVING filters groups. COUNT(*) counts rows in each group."},
                    {"language": LanguageEnum.fr, "prompt": "Écrivez une requête montrant l'âge moyen par ville, seulement pour les villes avec 2+ étudiants.", "hint": "GROUP BY city, HAVING COUNT(*) >= 2", "explanation": "GROUP BY crée des groupes. HAVING filtre les groupes. COUNT(*) compte les lignes par groupe."},
                    {"language": LanguageEnum.ar, "prompt": "اكتب استعلاماً يعرض متوسط العمر لكل مدينة، فقط للمدن التي بها طالبان أو أكثر.", "hint": "GROUP BY city، HAVING COUNT(*) >= 2", "explanation": "GROUP BY ينشئ مجموعات. HAVING تصفي المجموعات. COUNT(*) تحسب الصفوف في كل مجموعة."},
                ]
            }
        ]
    )
    
    # Lesson 29: JOINs and Relational Thinking
    await get_or_create_lesson(db, module_id, "joins-relational-thinking", 5,
        DifficultyEnum.intermediate, 45, 60,
        [
            {"language": LanguageEnum.en, "title": "JOINs and Relational Thinking", "story": "Combine data from multiple tables", "objective": "Write INNER, LEFT, RIGHT, FULL JOIN queries", "skills": "INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN, relational thinking"},
            {"language": LanguageEnum.fr, "title": "Jointures et Pensée Relationnelle", "story": "Combinez les données de plusieurs tables", "objective": "Écrire des requêtes INNER, LEFT, RIGHT, FULL JOIN", "skills": "INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL JOIN, pensée relationnelle"},
            {"language": LanguageEnum.ar, "title": "الانضمامات والتفكير العلائقي", "story": "اجمع البيانات من جداول متعددة", "objective": "كتابة استعلامات INNER، LEFT، RIGHT، FULL JOIN", "skills": "INNER JOIN، LEFT JOIN، RIGHT JOIN، FULL JOIN، التفكير العلائقي"},
        ],
        [
            {"type": "text", "order": 1, "content": "JOINs combine rows from two tables based on a related column. INNER JOIN returns matches only. LEFT JOIN returns all from left table, matches from right. RIGHT JOIN opposite. FULL JOIN returns all from both."},
            {"type": "code", "order": 2, "content": "JOIN examples:", "code_example": "-- Students with their enrollments\nSELECT s.name, c.title\nFROM students s\nINNER JOIN enrollments e ON s.id = e.student_id\nINNER JOIN courses c ON e.course_id = c.id;\n\n-- All students, even without enrollments\nSELECT s.name, c.title\nFROM students s\nLEFT JOIN enrollments e ON s.id = e.student_id\nLEFT JOIN courses c ON e.course_id = c.id;"},
            {"type": "text", "order": 3, "content": "Use aliases (s, e, c) for shorter queries. JOIN condition goes in ON clause. Think: what data do I need from both tables?"},
        ],
        [
            {
                "type": ExerciseTypeEnum.multiple_choice,
                "order": 1,
                "xp_reward": 10,
                "starter_code": "",
                "solution_code": "",
                "validation_config": "",
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Which JOIN returns all rows from the left table, even if no match in right?", "hint": "LEFT JOIN keeps all left rows", "explanation": "LEFT JOIN returns all rows from the left table, with NULLs for non-matching right columns."},
                    {"language": LanguageEnum.fr, "prompt": "Quel JOIN retourne toutes les lignes de la table gauche, même sans correspondance à droite ?", "hint": "LEFT JOIN garde toutes les lignes gauches", "explanation": "LEFT JOIN retourne toutes les lignes de la table gauche, avec NULL pour les colonnes droites non correspondantes."},
                    {"language": LanguageEnum.ar, "prompt": "أي JOIN يعيد جميع الصفوف من الجدول الأيسر، حتى لو لم يكن هناك تطابق في الأيمن؟", "hint": "LEFT JOIN يحتفظ بجميع الصفوف اليسرى", "explanation": "LEFT JOIN يعيد جميع الصفوف من الجدول الأيسر، مع قيم NULL للأعمدة اليمنى غير المتطابقة."},
                ],
                "options": [
                    {"order": 1, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "INNER JOIN"}, {"language": LanguageEnum.fr, "text": "INNER JOIN"}, {"language": LanguageEnum.ar, "text": "INNER JOIN"}]},
                    {"order": 2, "is_correct": True, "translations": [{"language": LanguageEnum.en, "text": "LEFT JOIN"}, {"language": LanguageEnum.fr, "text": "LEFT JOIN"}, {"language": LanguageEnum.ar, "text": "LEFT JOIN"}]},
                    {"order": 3, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "RIGHT JOIN"}, {"language": LanguageEnum.fr, "text": "RIGHT JOIN"}, {"language": LanguageEnum.ar, "text": "RIGHT JOIN"}]},
                    {"order": 4, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "CROSS JOIN"}, {"language": LanguageEnum.fr, "text": "CROSS JOIN"}, {"language": LanguageEnum.ar, "text": "CROSS JOIN"}]},
                ]
            }
        ]
    )
    
    print("SQL & Databases seeded successfully!")