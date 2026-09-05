from .base import (
    get_or_create_course, get_or_create_module, get_or_create_lesson,
    LanguageEnum, DifficultyEnum, ExerciseTypeEnum
)
from .microquest_content import seed_blocks


async def seed_python_foundations(db):
    print("Seeding Python Foundations...")
    
    course_id = await get_or_create_course(db, "python-basics", 1, [
        {"language": LanguageEnum.en, "title": "Python Foundations", "description": "Master the fundamentals of Python programming from variables to data structures", "skills": "Variables, Control Flow, Functions, Data Structures"},
        {"language": LanguageEnum.fr, "title": "Fondamentaux de Python", "description": "Maîtrisez les fondamentaux de la programmation Python des variables aux structures de données", "skills": "Variables, Contrôle de flux, Fonctions, Structures de données"},
        {"language": LanguageEnum.ar, "title": "أساسيات بايثون", "description": "أتقن أساسيات برمجة بايثون من المتغيرات إلى هياكل البيانات", "skills": "المتغيرات، التحكم في التدفق، الدوال، هياكل البيانات"},
    ])
    
    # Module 1: Getting Started
    module1_id = await get_or_create_module(db, course_id, "getting-started", 1, [
        {"language": LanguageEnum.en, "title": "Getting Started", "description": "Set up your environment and write your first Python programs"},
        {"language": LanguageEnum.fr, "title": "Démarrage", "description": "Configurez votre environnement et écrivez vos premiers programmes Python"},
        {"language": LanguageEnum.ar, "title": "البداية", "description": "قم بإعداد بيئتك واكتب أول برامج بايثون"},
    ])
    
    # Lesson 1: What Is Programming?
    await get_or_create_lesson(db, module1_id, "what-is-programming", 1,
        DifficultyEnum.beginner, 30, 50,
        [
            {"language": LanguageEnum.en, "title": "What Is Programming?", "story": "Discover what programming really is and why Python is a great first language", "objective": "Understand what programming means and write your first program", "skills": "Programming concepts, Python, print()"},
            {"language": LanguageEnum.fr, "title": "Qu'est-ce que la Programmation ?", "story": "Découvrez ce qu'est vraiment la programmation et pourquoi Python est un excellent premier langage", "objective": "Comprendre ce que signifie programmer et écrire votre premier programme", "skills": "Concepts de programmation, Python, print()"},
            {"language": LanguageEnum.ar, "title": "ما هي البرمجة؟", "story": "اكتشف ما هي البرمجة حقاً ولماذا بايثون لغة أولى رائعة", "objective": "فهم معنى البرمجة وكتابة أول برنامج", "skills": "مفاهيم البرمجة، بايثون، print()"},
        ],
        [
            {"type": "text", "order": 1, "content": "Programming is giving instructions to a computer to perform tasks. Python is a popular programming language because it reads like English."},
            {"type": "code", "order": 2, "content": "Your first Python program:", "code_example": 'print("Hello, World!")\nprint("Welcome to MoroccoCode!")'},
            {"type": "text", "order": 3, "content": "The print() function displays text on the screen. Each print() starts on a new line."},
        ],
        [
            {
                "type": ExerciseTypeEnum.code_writing,
                "order": 1,
                "xp_reward": 10,
                "starter_code": 'print("Hello, World!")',
                "solution_code": 'print("Hello, World!")',
                "test_code": 'import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "Hello, World!" in output',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": 'Write a program that prints "Hello, World!" to the console.', "hint": "Use the print() function", "explanation": "The print() function outputs text to the console."},
                    {"language": LanguageEnum.fr, "prompt": 'Écrivez un programme qui affiche "Bonjour le monde !" dans la console.', "hint": "Utilisez la fonction print()", "explanation": "La fonction print() affiche du texte dans la console."},
                    {"language": LanguageEnum.ar, "prompt": 'اكتب برنامجاً يطبع "مرحباً بالعالم!" في وحدة التحكم.', "hint": "استخدم دالة print()", "explanation": "دالة print() تطبع النص في وحدة التحكم."},
                ]
            },
            {
                "type": ExerciseTypeEnum.code_writing,
                "order": 2,
                "xp_reward": 10,
                "starter_code": '# Write a program that prints two lines\nprint("Hello, World!")\n# Add another print statement below',
                "solution_code": 'print("Hello, World!")\nprint("Welcome to MoroccoCode!")',
                "test_code": 'import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "Hello, World!" in output and "Welcome to MoroccoCode!" in output',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": 'Write a program that prints "Hello, World!" on the first line and "Welcome to MoroccoCode!" on the second line.', "hint": "Use two print() statements", "explanation": "Each print() outputs text followed by a newline."},
                    {"language": LanguageEnum.fr, "prompt": 'Écrivez un programme qui affiche "Bonjour le monde !" sur la première ligne et "Bienvenue sur MoroccoCode !" sur la deuxième.', "hint": "Utilisez deux instructions print()", "explanation": "Chaque print() affiche du texte suivi d'un saut de ligne."},
                    {"language": LanguageEnum.ar, "prompt": 'اكتب برنامجاً يطبع "مرحباً بالعالم!" في السطر الأول و "مرحباً بكم في MoroccoCode!" في السطر الثاني.', "hint": "استخدم جملتي print()", "explanation": "كل print() تطبع النص متبوعاً بسطر جديد."},
                ]
            },
            {
                "type": ExerciseTypeEnum.prediction,
                "order": 3,
                "xp_reward": 10,
                "starter_code": 'print("Line 1")\nprint("Line 2")\nprint("Line 3")',
                "solution_code": "Line 1\nLine 2\nLine 3",
                "validation_config": '{"expected_output": "Line 1\\nLine 2\\nLine 3"}',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "What will this code print?", "hint": "Each print() creates a new line", "explanation": "Each print() statement outputs its argument on a separate line."},
                    {"language": LanguageEnum.fr, "prompt": "Qu'affichera ce code ?", "hint": "Chaque print() crée une nouvelle ligne", "explanation": "Chaque instruction print() affiche son argument sur une ligne séparée."},
                    {"language": LanguageEnum.ar, "prompt": "ماذا سيطبع هذا الكود؟", "hint": "كل print() ينشئ سطراً جديداً", "explanation": "كل جملة print() تطبع معاملها في سطر منفصل."},
                ]
            }
        ]
    )
    
    # Lesson 2: Variables and Values
    await get_or_create_lesson(db, module1_id, "variables-and-values", 2,
        DifficultyEnum.beginner, 30, 50,
        [
            {"language": LanguageEnum.en, "title": "Variables and Values", "story": "Learn how to store and reuse data using variables", "objective": "Create variables and understand assignment", "skills": "Variables, assignment, data types"},
            {"language": LanguageEnum.fr, "title": "Variables et Valeurs", "story": "Apprenez à stocker et réutiliser des données avec des variables", "objective": "Créer des variables et comprendre l'affectation", "skills": "Variables, affectation, types de données"},
            {"language": LanguageEnum.ar, "title": "المتغيرات والقيم", "story": "تعلم كيف تخزن وتعيد استخدام البيانات باستخدام المتغيرات", "objective": "إنشاء المتغيرات وفهم التعيين", "skills": "المتغيرات، التعيين، أنواع البيانات"},
        ],
        [
            {"type": "text", "order": 1, "content": "Variables are named containers that store values. Think of them like labeled boxes where you can put data."},
            {"type": "code", "order": 2, "content": "Creating variables in Python:", "code_example": 'student_name = "Youssef"\nage = 20\nheight = 1.75\nis_student = True'},
            {"type": "text", "order": 3, "content": "Variable names can contain letters, numbers, and underscores, but cannot start with a number."},
        ],
        [
            {
                "type": ExerciseTypeEnum.code_writing,
                "order": 1,
                "xp_reward": 10,
                "starter_code": '# Create variables for a student\nname = \nage = \ncity = \nprint(name, age, city)',
                "solution_code": 'name = "Fatima"\nage = 22\ncity = "Casablanca"\nprint(name, age, city)',
                "test_code": 'import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "Fatima" in output and "22" in output and "Casablanca" in output',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Create variables for a student's name, age, and city, then print them.", "hint": "Strings need quotes, numbers don't", "explanation": "Variables store values that can be used later in your program."},
                    {"language": LanguageEnum.fr, "prompt": "Créez des variables pour le nom, l'âge et la ville d'un étudiant, puis affichez-les.", "hint": "Les chaînes nécessitent des guillemets, les nombres non", "explanation": "Les variables stockent des valeurs qui peuvent être utilisées plus tard."},
                    {"language": LanguageEnum.ar, "prompt": "أنشئ متغيرات لاسم الطالب وعمره ومدينته، ثم اطبعها.", "hint": "النصوص تحتاج لعلامات تنصيص، الأرقام لا تحتاج", "explanation": "المتغيرات تخزن القيم التي يمكن استخدامها لاحقاً في برنامجك."},
                ]
            },
            {
                "type": ExerciseTypeEnum.fill_blank,
                "order": 2,
                "xp_reward": 10,
                "starter_code": 'student_name = "____"\nstudent_age = ____\nprint(student_name, student_age)',
                "solution_code": 'student_name = "Amine"\nstudent_age = 19\nprint(student_name, student_age)',
                "validation_config": '{"blanks": [{"answer": "\\"Amine\\""}, {"answer": "19"}]}',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Fill in the blanks to create a student named Amine, age 19.", "hint": "Text goes in quotes, numbers don't", "explanation": "String values must be wrapped in quotes. Numbers are written directly."},
                    {"language": LanguageEnum.fr, "prompt": "Remplissez les blancs pour créer un étudiant nommé Amine, âgé de 19 ans.", "hint": "Le texte va entre guillemets, les nombres non", "explanation": "Les valeurs texte doivent être entre guillemets. Les nombres s'écrivent directement."},
                    {"language": LanguageEnum.ar, "prompt": "املأ الفراغات لإنشاء طالب اسمه أمين، عمره 19 سنة.", "hint": "النص بين علامات التنصيص، الأرقام مباشرة", "explanation": "يجب وضع القيم النصية بين علامتي تنصيص. الأرقام تكتب مباشرة."},
                ]
            }
        ]
    )
    
    # Lesson 3: Data Types
    await get_or_create_lesson(db, module1_id, "data-types", 3,
        DifficultyEnum.beginner, 30, 50,
        [
            {"language": LanguageEnum.en, "title": "Data Types", "story": "Discover the different types of data Python can handle", "objective": "Identify and use int, float, str, and bool types", "skills": "int, float, str, bool, type()"},
            {"language": LanguageEnum.fr, "title": "Types de Données", "story": "Découvrez les différents types de données que Python peut gérer", "objective": "Identifier et utiliser les types int, float, str et bool", "skills": "int, float, str, bool, type()"},
            {"language": LanguageEnum.ar, "title": "أنواع البيانات", "story": "اكتشف أنواع البيانات المختلفة التي يمكن لبايثون التعامل معها", "objective": "تحديد واستخدام أنواع int، float، str، و bool", "skills": "int، float، str، bool، type()"},
        ],
        [
            {"type": "text", "order": 1, "content": "Every value in Python has a type. The main types are: int (whole numbers), float (decimals), str (text), and bool (True/False)."},
            {"type": "code", "order": 2, "content": "Checking types:", "code_example": 'age = 25\nprice = 19.99\nname = "Omar"\nis_active = True\nprint(type(age))\nprint(type(price))\nprint(type(name))\nprint(type(is_active))'},
            {"type": "text", "order": 3, "content": "Use type() to check what type a value is. Python automatically chooses the type based on the value."},
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
                    {"language": LanguageEnum.en, "prompt": "What is the type of the value 3.14?", "hint": "It has a decimal point", "explanation": "3.14 is a float because it contains a decimal point."},
                    {"language": LanguageEnum.fr, "prompt": "Quel est le type de la valeur 3.14 ?", "hint": "Elle a un point décimal", "explanation": "3.14 est un float car elle contient un point décimal."},
                    {"language": LanguageEnum.ar, "prompt": "ما هو نوع القيمة 3.14؟", "hint": "لها نقطة عشرية", "explanation": "3.14 هو float لأنه يحتوي على نقطة عشرية."},
                ],
                "options": [
                    {"order": 1, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "int"}, {"language": LanguageEnum.fr, "text": "int"}, {"language": LanguageEnum.ar, "text": "int"}]},
                    {"order": 2, "is_correct": True, "translations": [{"language": LanguageEnum.en, "text": "float"}, {"language": LanguageEnum.fr, "text": "float"}, {"language": LanguageEnum.ar, "text": "float"}]},
                    {"order": 3, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "str"}, {"language": LanguageEnum.fr, "text": "str"}, {"language": LanguageEnum.ar, "text": "str"}]},
                    {"order": 4, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "bool"}, {"language": LanguageEnum.fr, "text": "bool"}, {"language": LanguageEnum.ar, "text": "bool"}]},
                ]
            },
            {
                "type": ExerciseTypeEnum.prediction,
                "order": 2,
                "xp_reward": 10,
                "starter_code": 'x = 42\ny = 3.14\nz = "Hello"\nprint(type(x))\nprint(type(y))\nprint(type(z))',
                "solution_code": "<class 'int'>\n<class 'float'>\n<class 'str'>",
                "validation_config": '{"expected_output": "<class \'int\'>\\n<class \'float\'>\\n<class \'str\'>"}',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "What will this code print?", "hint": "type() shows the type name", "explanation": "type() returns the type of the value: int, float, or str."},
                    {"language": LanguageEnum.fr, "prompt": "Qu'affichera ce code ?", "hint": "type() montre le nom du type", "explanation": "type() retourne le type de la valeur : int, float ou str."},
                    {"language": LanguageEnum.ar, "prompt": "ماذا سيطبع هذا الكود؟", "hint": "type() يظهر اسم النوع", "explanation": "type() ترجع نوع القيمة: int أو float أو str."},
                ]
            }
        ]
    )
    
    # Lesson 4: Operators and Expressions
    await get_or_create_lesson(db, module1_id, "operators-and-expressions", 4,
        DifficultyEnum.beginner, 30, 50,
        [
            {"language": LanguageEnum.en, "title": "Operators and Expressions", "story": "Learn how to perform calculations and comparisons in Python", "objective": "Use arithmetic, comparison, and logical operators", "skills": "Arithmetic, comparison, logical operators, precedence"},
            {"language": LanguageEnum.fr, "title": "Opérateurs et Expressions", "story": "Apprenez à effectuer des calculs et des comparaisons en Python", "objective": "Utiliser les opérateurs arithmétiques, de comparaison et logiques", "skills": "Opérateurs arithmétiques, comparaison, logiques, priorité"},
            {"language": LanguageEnum.ar, "title": "العوامل والتعبيرات", "story": "تعلم كيف تجري الحسابات والمقارنات في بايثون", "objective": "استخدام العوامل الحسابية والمقارنة والمنطقية", "skills": "عوامل حسابية، مقارنة، منطقية، أولوية"},
        ],
        [
            {"type": "text", "order": 1, "content": "Python supports arithmetic operators (+, -, *, /, //, %, **), comparison operators (==, !=, <, >, <=, >=), and logical operators (and, or, not)."},
            {"type": "code", "order": 2, "content": "Arithmetic operations:", "code_example": 'a = 10\nb = 3\nprint(a + b)  # 13\nprint(a - b)  # 7\nprint(a * b)  # 30\nprint(a / b)  # 3.333...\nprint(a // b) # 3 (floor division)\nprint(a % b)  # 1 (remainder)\nprint(a ** b) # 1000 (power)'},
            {"type": "text", "order": 3, "content": "Operator precedence: ** first, then *, /, //, %, then +, -. Use parentheses to control order."},
        ],
        [
            {
                "type": ExerciseTypeEnum.code_writing,
                "order": 1,
                "xp_reward": 10,
                "starter_code": '# Calculate the area of a rectangle\nwidth = 5\nheight = 8\narea = \nperimeter = \nprint("Area:", area)\nprint("Perimeter:", perimeter)',
                "solution_code": 'width = 5\nheight = 8\narea = width * height\nperimeter = 2 * (width + height)\nprint("Area:", area)\nprint("Perimeter:", perimeter)',
                "test_code": 'import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "Area: 40" in output and "Perimeter: 26" in output',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Calculate the area and perimeter of a rectangle with width 5 and height 8.", "hint": "Area = width * height, Perimeter = 2 * (width + height)", "explanation": "Use * for multiplication and + for addition. Parentheses control order of operations."},
                    {"language": LanguageEnum.fr, "prompt": "Calculez l'aire et le périmètre d'un rectangle de largeur 5 et hauteur 8.", "hint": "Aire = largeur * hauteur, Périmètre = 2 * (largeur + hauteur)", "explanation": "Utilisez * pour la multiplication et + pour l'addition. Les parenthèses contrôlent l'ordre."},
                    {"language": LanguageEnum.ar, "prompt": "احسب مساحة ومحيط مستطيل عرضه 5 وارتفاعه 8.", "hint": "المساحة = العرض * الارتفاع، المحيط = 2 * (العرض + الارتفاع)", "explanation": "استخدم * للضرب و + للجمع. الأقواس تتحكم في ترتيب العمليات."},
                ]
            },
            {
                "type": ExerciseTypeEnum.multiple_choice,
                "order": 2,
                "xp_reward": 10,
                "starter_code": "",
                "solution_code": "",
                "validation_config": "",
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "What is the result of 10 // 3?", "hint": "Floor division rounds down", "explanation": "// is floor division, which rounds down to the nearest integer. 10 // 3 = 3."},
                    {"language": LanguageEnum.fr, "prompt": "Quel est le résultat de 10 // 3 ?", "hint": "La division entière arrondit vers le bas", "explanation": "// est la division entière, qui arrondit vers le bas. 10 // 3 = 3."},
                    {"language": LanguageEnum.ar, "prompt": "ما هي نتيجة 10 // 3؟", "hint": "القسمة الصحيحة تقرب للأسفل", "explanation": "// هي قسمة صحيحة تقرب للأسفل. 10 // 3 = 3."},
                ],
                "options": [
                    {"order": 1, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "3.33"}, {"language": LanguageEnum.fr, "text": "3.33"}, {"language": LanguageEnum.ar, "text": "3.33"}]},
                    {"order": 2, "is_correct": True, "translations": [{"language": LanguageEnum.en, "text": "3"}, {"language": LanguageEnum.fr, "text": "3"}, {"language": LanguageEnum.ar, "text": "3"}]},
                    {"order": 3, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "4"}, {"language": LanguageEnum.fr, "text": "4"}, {"language": LanguageEnum.ar, "text": "4"}]},
                    {"order": 4, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "1"}, {"language": LanguageEnum.fr, "text": "1"}, {"language": LanguageEnum.ar, "text": "1"}]},
                ]
            }
        ]
    )
    
    # Lesson 5: User Input and Output
    await get_or_create_lesson(db, module1_id, "user-input-output", 5,
        DifficultyEnum.beginner, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "User Input and Output", "story": "Learn how to interact with users through input and output", "objective": "Use input() and print() to create interactive programs", "skills": "input(), print(), type conversion, f-strings"},
            {"language": LanguageEnum.fr, "title": "Entrée et Sortie Utilisateur", "story": "Apprenez à interagir avec les utilisateurs via l'entrée et la sortie", "objective": "Utiliser input() et print() pour créer des programmes interactifs", "skills": "input(), print(), conversion de type, f-strings"},
            {"language": LanguageEnum.ar, "title": "إدخال وإخراج المستخدم", "story": "تعلم كيف تتفاعل مع المستخدمين عبر الإدخال والإخراج", "objective": "استخدام input() و print() لإنشاء برامج تفاعلية", "skills": "input()، print()، تحويل النوع، f-strings"},
        ],
        [
            {"type": "text", "order": 1, "content": "Programs often need to get information from users. Use input() to ask for information and print() to show results. input() always returns a string, so you may need to convert it."},
            {"type": "code", "order": 2, "content": "Getting user input:", "code_example": 'name = input("What is your name? ")\nage = input("How old are you? ")\nprint(f"Hello {name}, you are {age} years old!")'},
            {"type": "text", "order": 3, "content": "input() always returns a string. Use int() to convert to integer, float() for decimals. f-strings let you embed variables in strings with {variable}."},
        ],
        [
            {
                "type": ExerciseTypeEnum.code_writing,
                "order": 1,
                "xp_reward": 10,
                "starter_code": '# Ask for user\'s name and age\nname = input("What is your name? ")\nage = input("How old are you? ")\n# Convert age to integer and calculate birth year\nbirth_year = 2025 - int(age)\nprint(f"Hello {name}, you were born in {birth_year}!")',
                "solution_code": 'name = input("What is your name? ")\nage = input("How old are you? ")\nbirth_year = 2025 - int(age)\nprint(f"Hello {name}, you were born in {birth_year}!")',
                # Graded by keywords, not the Python sandbox: this answer is not Python.
                "validation_config": '{"expected_keywords": ["input(", ["int(", "float("], "print(", ["2025", "2024"]]}',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Ask for the user's name and age, then calculate and print their birth year (assume current year is 2025).", "hint": "Use int() to convert age to integer", "explanation": "input() returns a string. Use int() to convert to integer for math operations."},
                    {"language": LanguageEnum.fr, "prompt": "Demandez le nom et l'âge de l'utilisateur, puis calculez et affichez son année de naissance (année actuelle = 2025).", "hint": "Utilisez int() pour convertir l'âge en entier", "explanation": "input() retourne une chaîne. Utilisez int() pour la convertir en entier pour les calculs."},
                    {"language": LanguageEnum.ar, "prompt": "اطلب اسم وعمر المستخدم، ثم احسب واطبع سنة ميلاده (السنة الحالية = 2025).", "hint": "استخدم int() لتحويل العمر إلى عدد صحيح", "explanation": "input() ترجع نصاً. استخدم int() لتحويله إلى عدد صحيح للعمليات الحسابية."},
                ]
            },
            {
                "type": ExerciseTypeEnum.multiple_choice,
                "order": 2,
                "xp_reward": 10,
                "starter_code": "",
                "solution_code": "",
                "validation_config": "",
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "What does input() always return?", "hint": "It's always text", "explanation": "input() always returns a string, even if the user types numbers."},
                    {"language": LanguageEnum.fr, "prompt": "Que retourne toujours input() ?", "hint": "C'est toujours du texte", "explanation": "input() retourne toujours une chaîne de caractères, même si l'utilisateur tape des chiffres."},
                    {"language": LanguageEnum.ar, "prompt": "ماذا ترجع input() دائماً؟", "hint": "هي دائماً نص", "explanation": "input() ترجع دائماً سلسلة نصية، حتى لو أدخل المستخدم أرقاماً."},
                ],
                "options": [
                    {"order": 1, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "int"}, {"language": LanguageEnum.fr, "text": "int"}, {"language": LanguageEnum.ar, "text": "int"}]},
                    {"order": 2, "is_correct": True, "translations": [{"language": LanguageEnum.en, "text": "str"}, {"language": LanguageEnum.fr, "text": "str"}, {"language": LanguageEnum.ar, "text": "str"}]},
                    {"order": 3, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "int or float"}, {"language": LanguageEnum.fr, "text": "int ou float"}, {"language": LanguageEnum.ar, "text": "int أو float"}]},
                    {"order": 4, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "bool"}, {"language": LanguageEnum.fr, "text": "bool"}, {"language": LanguageEnum.ar, "text": "bool"}]},
                ]
            }
        ]
    )
    
    # Module 2: Control Flow
    module2_id = await get_or_create_module(db, course_id, "control-flow", 2, [
        {"language": LanguageEnum.en, "title": "Control Flow", "description": "Make decisions and repeat code with conditions and loops"},
        {"language": LanguageEnum.fr, "title": "Contrôle de Flux", "description": "Prenez des décisions et répétez du code avec des conditions et des boucles"},
        {"language": LanguageEnum.ar, "title": "التحكم في التدفق", "description": "اتخذ القرارات وكرر الكود بالشروط والحلقات"},
    ])
    
    # Lesson 5: Conditions
    await get_or_create_lesson(db, module2_id, "conditions", 1,
        DifficultyEnum.beginner, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "Conditions", "story": "Teach your programs to make decisions based on different situations", "objective": "Write if, elif, and else statements", "skills": "if, elif, else, boolean logic"},
            {"language": LanguageEnum.fr, "title": "Conditions", "story": "Apprenez à vos programmes à prendre des décisions selon les situations", "objective": "Écrire des instructions if, elif et else", "skills": "if, elif, else, logique booléenne"},
            {"language": LanguageEnum.ar, "title": "الشروط", "story": "علم برامجك اتخاذ القرارات بناءً على حالات مختلفة", "objective": "كتابة جمل if، elif، و else", "skills": "if، elif، else، المنطق البولياني"},
        ],
        [
            {"type": "text", "order": 1, "content": "Conditions let your program choose different paths. Use if for a condition, elif for additional conditions, and else for everything else."},
            {"type": "code", "order": 2, "content": "Basic if-elif-else:", "code_example": 'score = 85\nif score >= 90:\n    grade = "A"\nelif score >= 80:\n    grade = "B"\nelif score >= 70:\n    grade = "C"\nelse:\n    grade = "F"\nprint("Grade:", grade)'},
            {"type": "text", "order": 3, "content": "Only one branch executes. Conditions are checked in order from top to bottom."},
        ],
        [
            {
                "type": ExerciseTypeEnum.code_writing,
                "order": 1,
                "xp_reward": 10,
                "starter_code": 'temperature = 25\n# Write if-elif-else to check temperature\n# If >= 30: print("Hot")\n# Elif >= 20: print("Warm")\n# Else: print("Cool")',
                "solution_code": 'temperature = 25\nif temperature >= 30:\n    print("Hot")\nelif temperature >= 20:\n    print("Warm")\nelse:\n    print("Cool")',
                "test_code": 'import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "Warm" in output',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Write a program that prints \"Hot\" if temperature >= 30, \"Warm\" if >= 20, otherwise \"Cool\".", "hint": "Use if, elif, else in order", "explanation": "Conditions are checked top to bottom. Only the first matching branch runs."},
                    {"language": LanguageEnum.fr, "prompt": "Écrivez un programme qui affiche \"Chaud\" si température >= 30, \"Tiède\" si >= 20, sinon \"Frais\".", "hint": "Utilisez if, elif, else dans l'ordre", "explanation": "Les conditions sont vérifiées de haut en bas. Seule la première branche correspondante s'exécute."},
                    {"language": LanguageEnum.ar, "prompt": "اكتب برنامجاً يطبع \"حار\" إذا كانت الحرارة >= 30، \"دافئ\" إذا كانت >= 20، وإلا \"بارد\".", "hint": "استخدم if، elif، else بالترتيب", "explanation": "يتم التحقق من الشروط من الأعلى إلى الأسفل. يتم تنفيذ الفرع الأول المطابق فقط."},
                ]
            },
            {
                "type": ExerciseTypeEnum.debugging,
                "order": 2,
                "xp_reward": 15,
                "starter_code": 'age = 17\nif age >= 18:\n    print("Adult")\nelse:\n    print("Minor")\n# The code above works, but what if we want to check for teenager (13-17)?',
                "solution_code": 'age = 17\nif age >= 18:\n    print("Adult")\nelif age >= 13:\n    print("Teenager")\nelse:\n    print("Child")',
                "test_code": 'import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "Teenager" in output',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "The code only checks for adult/minor. Add an elif branch to print \"Teenager\" for ages 13-17.", "hint": "Add elif age >= 13 before the else", "explanation": "elif allows you to check multiple conditions in sequence."},
                    {"language": LanguageEnum.fr, "prompt": "Le code ne vérifie que adulte/mineur. Ajoutez une branche elif pour afficher \"Adolescent\" pour les 13-17 ans.", "hint": "Ajoutez elif age >= 13 avant le else", "explanation": "elif permet de vérifier plusieurs conditions en séquence."},
                    {"language": LanguageEnum.ar, "prompt": "الكود يتحقق فقط من بالغ/قاصر. أضف فرع elif لطباعة \"مراهق\" للأعمار 13-17.", "hint": "أضف elif age >= 13 قبل else", "explanation": "elif يسمح لك بالتحقق من عدة شروط بالتسلسل."},
                ]
            }
        ]
    )
    
    # Lesson 6: Loops
    await get_or_create_lesson(db, module2_id, "loops", 2,
        DifficultyEnum.beginner, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "Loops", "story": "Automate repetitive tasks with for and while loops", "objective": "Write for loops with range and while loops", "skills": "for loops, range(), while loops"},
            {"language": LanguageEnum.fr, "title": "Boucles", "story": "Automatisez les tâches répétitives avec les boucles for et while", "objective": "Écrire des boucles for avec range et des boucles while", "skills": "boucles for, range(), boucles while"},
            {"language": LanguageEnum.ar, "title": "الحلقات", "story": "أتمتة المهام المتكررة بحلقات for و while", "objective": "كتابة حلقات for مع range وحلقات while", "skills": "حلقات for، range()، حلقات while"},
        ],
        [
            {"type": "text", "order": 1, "content": "Loops repeat code multiple times. for loops iterate over a sequence, while loops repeat while a condition is true."},
            {"type": "code", "order": 2, "content": "For loop with range:", "code_example": 'for i in range(5):\n    print(i)\n\nprint("---")\n\ncount = 0\nwhile count < 3:\n    print(count)\n    count += 1'},
            {"type": "text", "order": 3, "content": "range(n) creates numbers 0 to n-1. range(start, stop) creates numbers from start to stop-1. Always update your counter in while loops!"},
        ],
        [
            {
                "type": ExerciseTypeEnum.code_writing,
                "order": 1,
                "xp_reward": 10,
                "starter_code": '# Write a for loop that prints numbers 1 to 10\nfor i in range(1, 11):\n    print(i)',
                "solution_code": 'for i in range(1, 11):\n    print(i)',
                "test_code": 'import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "1" in output and "10" in output',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Write a for loop that prints numbers 1 through 10.", "hint": "range(1, 11) gives 1 to 10", "explanation": "range(start, stop) includes start but excludes stop."},
                    {"language": LanguageEnum.fr, "prompt": "Écrivez une boucle for qui affiche les nombres de 1 à 10.", "hint": "range(1, 11) donne 1 à 10", "explanation": "range(start, stop) inclut start mais exclut stop."},
                    {"language": LanguageEnum.ar, "prompt": "اكتب حلقة for تطبع الأرقام من 1 إلى 10.", "hint": "range(1, 11) يعطي 1 إلى 10", "explanation": "range(start, stop) تتضمن start ولكن تستثني stop."},
                ]
            },
            {
                "type": ExerciseTypeEnum.visual_programming,
                "order": 2,
                "xp_reward": 15,
                "starter_code": '{"nodes": [{"id": "1", "type": "start", "config": {}}, {"id": "2", "type": "loop", "config": {"var": "i", "times": "5"}}, {"id": "3", "type": "output", "config": {"value": "i"}}, {"id": "4", "type": "end", "config": {}}], "edges": [{"source": "1", "target": "2"}, {"source": "2", "target": "3"}, {"source": "3", "target": "4"}]}',
                "solution_code": 'for i in range(5):\n    print(i)',
                "test_code": 'import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "0" in output and "4" in output',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Build a visual program that loops 5 times and prints the counter.", "hint": "Connect start → loop → output → end", "explanation": "The loop node creates a for loop. Connect it to an output node to print each iteration."},
                    {"language": LanguageEnum.fr, "prompt": "Construisez un programme visuel qui boucle 5 fois et affiche le compteur.", "hint": "Connectez start → boucle → sortie → end", "explanation": "Le nœud boucle crée une boucle for. Connectez-le à un nœud sortie pour afficher chaque itération."},
                    {"language": LanguageEnum.ar, "prompt": "ابنِ برنامجاً مرئياً يكرر 5 مرات ويطبع العداد.", "hint": "اربط start → loop → output → end", "explanation": "عقدة الحلقة تنشئ حلقة for. قم بتوصيلها بعقدة إخراج لطباعة كل تكرار."},
                ]
            }
        ]
    )
    
    # Lesson 7: Loop Control
    await get_or_create_lesson(db, module2_id, "loop-control", 3,
        DifficultyEnum.beginner, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "Loop Control", "story": "Fine-tune your loops with break, continue, and nested loops", "objective": "Use break, continue, and create nested loops", "skills": "break, continue, nested loops"},
            {"language": LanguageEnum.fr, "title": "Contrôle de Boucle", "story": "Affinez vos boucles avec break, continue et les boucles imbriquées", "objective": "Utiliser break, continue et créer des boucles imbriquées", "skills": "break, continue, boucles imbriquées"},
            {"language": LanguageEnum.ar, "title": "التحكم في الحلقات", "story": "ضبط حلقاتك بدقة مع break، continue، والحلقات المتداخلة", "objective": "استخدام break، continue، وإنشاء حلقات متداخلة", "skills": "break، continue، حلقات متداخلة"},
        ],
        [
            {"type": "text", "order": 1, "content": "break exits a loop immediately. continue skips to the next iteration. Nested loops are loops inside other loops."},
            {"type": "code", "order": 2, "content": "Loop control examples:", "code_example": '# break example\nfor i in range(10):\n    if i == 5:\n        break\n    print(i)  # prints 0,1,2,3,4\n\n# continue example\nfor i in range(5):\n    if i == 2:\n        continue\n    print(i)  # prints 0,1,3,4\n\n# nested loops\nfor i in range(3):\n    for j in range(2):\n        print(f"i={i}, j={j}")'},
            {"type": "text", "order": 3, "content": "Use break to exit early when you find what you're looking for. Use continue to skip unwanted iterations."},
        ],
        [
            {
                "type": ExerciseTypeEnum.code_writing,
                "order": 1,
                "xp_reward": 10,
                "starter_code": '# Print numbers 1 to 10, but stop when you reach 7\nfor i in range(1, 11):\n    if i == 7:\n        \n    print(i)',
                "solution_code": 'for i in range(1, 11):\n    if i == 7:\n        break\n    print(i)',
                "test_code": 'import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "1" in output and "6" in output and "7" not in output',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Print numbers 1 to 10, but stop (break) when you reach 7.", "hint": "Use break when i == 7", "explanation": "break immediately exits the loop, so 7 and above won't be printed."},
                    {"language": LanguageEnum.fr, "prompt": "Affichez les nombres 1 à 10, mais arrêtez-vous (break) quand vous atteignez 7.", "hint": "Utilisez break quand i == 7", "explanation": "break quitte immédiatement la boucle, donc 7 et plus ne seront pas affichés."},
                    {"language": LanguageEnum.ar, "prompt": "اطبع الأرقام من 1 إلى 10، لكن توقف (break) عند الوصول لـ 7.", "hint": "استخدم break عندما i == 7", "explanation": "break تخرج من الحلقة فوراً، لذا 7 وما فوق لن تطبع."},
                ]
            },
            {
                "type": ExerciseTypeEnum.ordering,
                "order": 2,
                "xp_reward": 10,
                "starter_code": "",
                "solution_code": "",
                "validation_config": "",
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Put these lines in order to create a loop that prints only odd numbers 1-5.", "hint": "continue skips even numbers", "explanation": "continue jumps to the next iteration, skipping the print for even numbers."},
                    {"language": LanguageEnum.fr, "prompt": "Mettez ces lignes dans l'ordre pour créer une boucle qui n'affiche que les nombres impairs 1-5.", "hint": "continue saute les nombres pairs", "explanation": "continue passe à l'itération suivante, sautant l'affichage pour les nombres pairs."},
                    {"language": LanguageEnum.ar, "prompt": "ضع هذه الأسطر بالترتيب لإنشاء حلقة تطبع فقط الأرقام الفردية 1-5.", "hint": "continue تتخطى الأرقام الزوجية", "explanation": "continue تنتقل للتكرار التالي، متخطية الطباعة للأرقام الزوجية."},
                ],
                "options": [
                    {"order": 1, "is_correct": True, "translations": [{"language": LanguageEnum.en, "text": "for i in range(1, 6):"}, {"language": LanguageEnum.fr, "text": "for i in range(1, 6):"}, {"language": LanguageEnum.ar, "text": "for i in range(1, 6):"}]},
                    {"order": 2, "is_correct": True, "translations": [{"language": LanguageEnum.en, "text": "    if i % 2 == 0:"}, {"language": LanguageEnum.fr, "text": "    if i % 2 == 0:"}, {"language": LanguageEnum.ar, "text": "    if i % 2 == 0:"}]},
                    {"order": 3, "is_correct": True, "translations": [{"language": LanguageEnum.en, "text": "        continue"}, {"language": LanguageEnum.fr, "text": "        continue"}, {"language": LanguageEnum.ar, "text": "        continue"}]},
                    {"order": 4, "is_correct": True, "translations": [{"language": LanguageEnum.en, "text": "    print(i)"}, {"language": LanguageEnum.fr, "text": "    print(i)"}, {"language": LanguageEnum.ar, "text": "    print(i)"}]},
                ]
            }
        ]
    )
    
    # Lesson 8: Problem Solving with Control Flow
    await get_or_create_lesson(db, module2_id, "problem-solving-control-flow", 4,
        DifficultyEnum.intermediate, 40, 60,
        [
            {"language": LanguageEnum.en, "title": "Problem Solving with Control Flow", "story": "Combine conditions and loops to solve real programming problems", "objective": "Solve problems by combining if/else with loops", "skills": "Algorithmic thinking, combining control structures"},
            {"language": LanguageEnum.fr, "title": "Résolution de Problèmes avec le Contrôle de Flux", "story": "Combinez conditions et boucles pour résoudre de vrais problèmes de programmation", "objective": "Résoudre des problèmes en combinant if/else avec des boucles", "skills": "Pensée algorithmique, combinaison de structures de contrôle"},
            {"language": LanguageEnum.ar, "title": "حل المشكلات مع التحكم في التدفق", "story": "اجمع الشروط والحلقات لحل مشاكل برمجية حقيقية", "objective": "حل المشكلات بجمع if/else مع الحلقات", "skills": "التفكير الخوارزمي، جمع هياكل التحكم"},
        ],
        [
            {"type": "text", "order": 1, "content": "Real programming problems often need both decisions and repetition. Break the problem into steps, then code each step."},
            {"type": "code", "order": 2, "content": "Finding the largest number:", "code_example": 'numbers = [15, 42, 8, 23, 91, 7]\nlargest = numbers[0]\nfor n in numbers:\n    if n > largest:\n        largest = n\nprint("Largest:", largest)'},
            # Micro-Quest blocks. Other lessons have none and render as before.
            {"type": 'hook', "order": 0, "content": 'A school needs the total of every even-numbered locker in a corridor. Counting them one by one works, but it is slow and easy to get wrong.', "config": '{"kind": "hook", "challenge": {"en": "How can a program look at every number, keep only the ones it wants, and add them up on its own?", "fr": "Comment un programme peut-il parcourir chaque nombre, ne garder que ceux qui l\'intéressent et les additionner tout seul ?", "ar": "كيف يمكن لبرنامج أن يمرّ على كل عدد، ويحتفظ بما يهمّه منها فقط، ثم يجمعها من تلقاء نفسه؟"}, "learn": {"en": "You will combine a loop with a condition to build a running total — the pattern behind counting, summing and finding a maximum.", "fr": "Vous allez combiner une boucle et une condition pour construire un total cumulé — le schéma qui sert à compter, additionner et trouver un maximum.", "ar": "ستجمع بين حلقة وشرط لبناء مجموع تراكمي، وهو النمط نفسه المستخدم في العدّ والجمع وإيجاد القيمة العظمى."}}', "translations": [{"language": LanguageEnum.en, "content": 'A school needs the total of every even-numbered locker in a corridor. Counting them one by one works, but it is slow and easy to get wrong.'}, {"language": LanguageEnum.fr, "content": "Une école a besoin du total de tous les casiers portant un numéro pair dans un couloir. Les compter un par un fonctionne, mais c'est lent et on se trompe facilement."}, {"language": LanguageEnum.ar, "content": 'تحتاج مدرسة إلى مجموع أرقام كل الخزانات ذات الأرقام الزوجية في ممرّ واحد. عدّها واحدة تلو الأخرى ممكن، لكنه بطيء ويسهل الوقوع فيه في الخطأ.'}]},
            {"type": "text", "order": 3, "content": "This pattern (initialize, loop, compare, update) works for finding max, min, sum, average, and more."},
            {"type": 'blueprint', "order": 4, "content": 'Before writing any code, put the four steps of the pattern in the order a program would run them.', "config": '{"kind": "order_steps", "steps": [{"id": "init", "label": {"en": "Start a total at zero", "fr": "Démarrer un total à zéro", "ar": "ابدأ بمجموع قيمته صفر"}}, {"id": "visit", "label": {"en": "Look at the next number in the range", "fr": "Passer au nombre suivant de l\'intervalle", "ar": "انتقل إلى العدد التالي في المجال"}}, {"id": "decide", "label": {"en": "Ask: is this number even?", "fr": "Se demander : ce nombre est-il pair ?", "ar": "اسأل: هل هذا العدد زوجي؟"}}, {"id": "update", "label": {"en": "If it is, add it to the total", "fr": "Si oui, l\'ajouter au total", "ar": "إذا كان كذلك، أضفه إلى المجموع"}}], "correct_order": ["init", "visit", "decide", "update"], "success": {"en": "That is the pattern: initialise, visit, decide, update. Now write it in Python.", "fr": "Voilà le schéma : initialiser, parcourir, décider, mettre à jour. À vous de l\'écrire en Python.", "ar": "هذا هو النمط: التهيئة، ثم المرور، ثم القرار، ثم التحديث. والآن اكتبه بلغة Python."}, "hint": {"en": "The total has to exist before the loop can add anything to it.", "fr": "Le total doit exister avant que la boucle puisse y ajouter quoi que ce soit.", "ar": "يجب أن يوجد المجموع قبل أن تتمكّن الحلقة من إضافة أي شيء إليه."}}', "translations": [{"language": LanguageEnum.en, "content": 'Before writing any code, put the four steps of the pattern in the order a program would run them.'}, {"language": LanguageEnum.fr, "content": "Avant d'écrire la moindre ligne de code, remettez les quatre étapes du schéma dans l'ordre où un programme les exécuterait."}, {"language": LanguageEnum.ar, "content": 'قبل كتابة أي شيفرة، رتّب خطوات النمط الأربع بالترتيب الذي ينفّذها به البرنامج.'}]},
            {"type": 'exam_tip', "order": 5, "content": 'Everything indented under a for or if line belongs to it. Put the line that adds to your total one level too far left and it runs after the loop instead of inside it — the total will be wrong, with no error message.', "config": '{"kind": "exam_tip"}', "translations": [{"language": LanguageEnum.en, "content": 'Everything indented under a for or if line belongs to it. Put the line that adds to your total one level too far left and it runs after the loop instead of inside it — the total will be wrong, with no error message.'}, {"language": LanguageEnum.fr, "content": "Tout ce qui est indenté sous une ligne for ou if lui appartient. Placez la ligne qui ajoute au total un niveau trop à gauche et elle s'exécutera après la boucle au lieu d'être dedans : le total sera faux, sans aucun message d'erreur."}, {"language": LanguageEnum.ar, "content": 'كل ما يُزاح إلى الداخل تحت سطر for أو if ينتمي إليه. وإذا وضعت السطر الذي يضيف إلى المجموع مستوى واحدًا أبعد إلى اليسار، فسيُنفَّذ بعد الحلقة بدل أن يكون داخلها، فيخرج المجموع خاطئًا دون أي رسالة خطأ.'}]},
        ],
        [
            {
                "type": ExerciseTypeEnum.code_writing,
                "order": 1,
                "xp_reward": 15,
                "starter_code": '# Find the sum of all even numbers from 1 to 20\ntotal = 0\nfor i in range(1, 21):\n    if i % 2 == 0:\n        total += i\nprint("Sum of evens:", total)',
                "solution_code": 'total = 0\nfor i in range(1, 21):\n    if i % 2 == 0:\n        total += i\nprint("Sum of evens:", total)',
                "test_code": 'import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "110" in output',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Find the sum of all even numbers from 1 to 20.", "hint": "Use % 2 == 0 to check if even, then add to total", "explanation": "Loop through 1-20, check if each number is even, and add it to a running total."},
                    {"language": LanguageEnum.fr, "prompt": "Trouvez la somme de tous les nombres pairs de 1 à 20.", "hint": "Utilisez % 2 == 0 pour vérifier si pair, puis ajoutez au total", "explanation": "Parcourez 1-20, vérifiez si chaque nombre est pair, et ajoutez-le à un total cumulatif."},
                    {"language": LanguageEnum.ar, "prompt": "أوجد مجموع جميع الأرقام الزوجية من 1 إلى 20.", "hint": "استخدم % 2 == 0 للتحقق من الزوجية، ثم أضف للمجموع", "explanation": "مرّ من 1 إلى 20، تحقق مما إذا كان كل رقم زوجياً، وأضفه لمجموع متزايد."},
                ]
            }
        ]
    )
    
    # Module 3: Functions
    module3_id = await get_or_create_module(db, course_id, "functions", 3, [
        {"language": LanguageEnum.en, "title": "Functions", "description": "Create reusable code blocks with functions"},
        {"language": LanguageEnum.fr, "title": "Fonctions", "description": "Créez des blocs de code réutilisables avec des fonctions"},
        {"language": LanguageEnum.ar, "title": "الدوال", "description": "أنشئ كتل كود قابلة لإعادة الاستخدام بالدوال"},
    ])
    
    # Lesson 9: Functions
    await get_or_create_lesson(db, module3_id, "functions", 1,
        DifficultyEnum.beginner, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "Functions", "story": "Organize your code into reusable pieces with functions", "objective": "Define and call functions with parameters and return values", "skills": "def, parameters, return, function calls"},
            {"language": LanguageEnum.fr, "title": "Fonctions", "story": "Organisez votre code en morceaux réutilisables avec des fonctions", "objective": "Définir et appeler des fonctions avec paramètres et valeurs de retour", "skills": "def, paramètres, return, appels de fonction"},
            {"language": LanguageEnum.ar, "title": "الدوال", "story": "نظم كودك في قطع قابلة لإعادة الاستخدام بالدوال", "objective": "تعريف واستدعاء الدوال بالمعاملات وقيم الإرجاع", "skills": "def، المعاملات، return، استدعاء الدوال"},
        ],
        [
            {"type": "text", "order": 1, "content": "Functions let you group code that does one thing, give it a name, and reuse it. They can take inputs (parameters) and give back outputs (return values)."},
            {"type": "code", "order": 2, "content": "Defining and calling functions:", "code_example": 'def greet(name):\n    return "Hello, " + name + "!"\n\ngreeting = greet("Youssef")\nprint(greeting)\nprint(greet("Fatima"))'},
            {"type": "text", "order": 3, "content": "def defines a function. The code inside only runs when you call the function. return sends a value back to the caller."},
        ],
        [
            {
                "type": ExerciseTypeEnum.code_writing,
                "order": 1,
                "xp_reward": 10,
                "starter_code": '# Define a function that adds two numbers\ndef add(a, b):\n    \n# Call it and print the result\nresult = add(5, 3)\nprint(result)',
                "solution_code": 'def add(a, b):\n    return a + b\n\nresult = add(5, 3)\nprint(result)',
                "test_code": 'import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "8" in output',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Write a function called add that takes two numbers and returns their sum. Then call it with 5 and 3.", "hint": "Use return a + b", "explanation": "Functions use parameters as placeholders. return sends the result back."},
                    {"language": LanguageEnum.fr, "prompt": "Écrivez une fonction add qui prend deux nombres et retourne leur somme. Appelez-la avec 5 et 3.", "hint": "Utilisez return a + b", "explanation": "Les fonctions utilisent des paramètres comme emplacements. return renvoie le résultat."},
                    {"language": LanguageEnum.ar, "prompt": "اكتب دالة تسمى add تأخذ رقمين وتعيد مجموعهما. ثم استدعيها بـ 5 و 3.", "hint": "استخدم return a + b", "explanation": "الدوال تستخدم المعاملات كعناصر نائبة. return ترجع النتيجة."},
                ]
            },
            {
                "type": ExerciseTypeEnum.visual_programming,
                "order": 2,
                "xp_reward": 15,
                "starter_code": '{"nodes": [{"id": "1", "type": "start", "config": {}}, {"id": "2", "type": "function", "config": {"name": "double", "params": "x"}}, {"id": "3", "type": "return", "config": {"value": "x * 2"}}, {"id": "4", "type": "output", "config": {"value": "double(5)"}}, {"id": "5", "type": "end", "config": {}}], "edges": [{"source": "1", "target": "2"}, {"source": "2", "target": "3"}, {"source": "2", "target": "4"}, {"source": "4", "target": "5"}]}',
                "solution_code": 'def double(x):\n    return x * 2\n\nprint(double(5))',
                "test_code": 'import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "10" in output',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Build a visual function that doubles a number and test it with 5.", "hint": "Function node with parameter x, return x * 2, then output the function call", "explanation": "The function node defines a function. Connect return and output to use it."},
                    {"language": LanguageEnum.fr, "prompt": "Construisez une fonction visuelle qui double un nombre et testez-la avec 5.", "hint": "Nœud fonction avec paramètre x, retour x * 2, puis sortie de l'appel", "explanation": "Le nœud fonction définit une fonction. Connectez retour et sortie pour l'utiliser."},
                    {"language": LanguageEnum.ar, "prompt": "ابنِ دالة مرئية تضاعف رقمًا واختبرها بـ 5.", "hint": "عقدة دالة بمعامل x، إرجاع x * 2، ثم إخراج استدعاء الدالة", "explanation": "عقدة الدالة تعرف دالة. قم بتوصيل الإرجاع والإخراج لاستخدامها."},
                ]
            }
        ]
    )
    
    # Lesson 10: Function Parameters
    await get_or_create_lesson(db, module3_id, "function-parameters", 2,
        DifficultyEnum.beginner, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "Function Parameters", "story": "Make your functions more flexible with multiple parameters and default values", "objective": "Use multiple parameters, default values, and keyword arguments", "skills": "Multiple parameters, default values, keyword arguments"},
            {"language": LanguageEnum.fr, "title": "Paramètres de Fonction", "story": "Rendez vos fonctions plus flexibles avec plusieurs paramètres et valeurs par défaut", "objective": "Utiliser plusieurs paramètres, valeurs par défaut et arguments nommés", "skills": "Paramètres multiples, valeurs par défaut, arguments nommés"},
            {"language": LanguageEnum.ar, "title": "معاملات الدوال", "story": "اجعل دوالك أكثر مرونة بمعاملات متعددة وقيم افتراضية", "objective": "استخدام معاملات متعددة، قيم افتراضية، وسيطة مسماة", "skills": "معاملات متعددة، قيم افتراضية، وسيطة مسماة"},
        ],
        [
            {"type": "text", "order": 1, "content": "Functions can take multiple parameters. You can also give parameters default values so they're optional when calling."},
            {"type": "code", "order": 2, "content": "Multiple parameters and defaults:", "code_example": 'def greet(name, greeting="Hello"):\n    return greeting + ", " + name + "!"\n\nprint(greet("Omar"))        # uses default\nprint(greet("Omar", "Hi"))  # overrides default\nprint(greet(name="Ali", greeting="Welcome"))  # keyword arguments'},
            {"type": "text", "order": 3, "content": "Default parameters must come after required parameters. Keyword arguments let you specify parameters by name in any order."},
        ],
        [
            {
                "type": ExerciseTypeEnum.code_writing,
                "order": 1,
                "xp_reward": 10,
                "starter_code": '# Create a function that calculates price with tax\ndef calculate_total(price, tax_rate=0.2):\n    \nprint(calculate_total(100))       # 120.0\nprint(calculate_total(100, 0.1))    # 110.0',
                "solution_code": 'def calculate_total(price, tax_rate=0.2):\n    return price * (1 + tax_rate)\n\nprint(calculate_total(100))\nprint(calculate_total(100, 0.1))',
                "test_code": 'import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "120.0" in output and "110.0" in output',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Write a function calculate_total(price, tax_rate=0.2) that returns price with tax. Default tax is 20%.", "hint": "Return price * (1 + tax_rate)", "explanation": "Default parameters make arguments optional. The caller can override them."},
                    {"language": LanguageEnum.fr, "prompt": "Écrivez une fonction calculate_total(price, tax_rate=0.2) qui retourne le prix avec taxe. Taxe par défaut 20%.", "hint": "Retournez price * (1 + tax_rate)", "explanation": "Les paramètres par défaut rendent les arguments optionnels. L'appelant peut les remplacer."},
                    {"language": LanguageEnum.ar, "prompt": "اكتب دالة calculate_total(price, tax_rate=0.2) ترجع السعر مع الضريبة. الضريبة الافتراضية 20%.", "hint": "أرجع price * (1 + tax_rate)", "explanation": "المعاملات الافتراضية تجعل الوسيطات اختيارية. يمكن للمستدعي تجاوزها."},
                ]
            }
        ]
    )
    
    # Lesson 11: Scope and Function Design
    await get_or_create_lesson(db, module3_id, "scope-and-function-design", 3,
        DifficultyEnum.intermediate, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "Scope and Function Design", "story": "Understand where variables live and how to write clean functions", "objective": "Understand local vs global scope, write single-purpose functions", "skills": "Local scope, global scope, clean function design"},
            {"language": LanguageEnum.fr, "title": "Portée et Conception de Fonctions", "story": "Comprenez où vivent les variables et comment écrire des fonctions propres", "objective": "Comprendre portée locale vs globale, écrire des fonctions à usage unique", "skills": "Portée locale, portée globale, conception de fonctions propres"},
            {"language": LanguageEnum.ar, "title": "النطاق وتصميم الدوال", "story": "افهم أين تعيش المتغيرات وكيف تكتب دوال نظيفة", "objective": "فهم النطاق المحلي مقابل العام، كتابة دوال ذات غرض واحد", "skills": "نطاق محلي، نطاق عام، تصميم دوال نظيفة"},
        ],
        [
            {"type": "text", "order": 1, "content": "Variables created inside a function are local - they only exist inside that function. Variables outside are global. Prefer local variables and pass data through parameters."},
            {"type": "code", "order": 2, "content": "Scope example:", "code_example": 'message = "global"\n\ndef my_function():\n    message = "local"  # creates new local variable\n    print("Inside:", message)\n\nmy_function()\nprint("Outside:", message)'},
            {"type": "text", "order": 3, "content": "Good functions do one thing well, have clear names, and don't rely on global variables. This makes them easier to test and reuse."},
            # Micro-Quest blocks (hook 0, blueprint 4, exam_tip 5). The blueprint
            # is the match_pairs interaction. Lessons without these render as before.
            *seed_blocks("scope-and-function-design"),
        ],
        [
            {
                "type": ExerciseTypeEnum.prediction,
                "order": 1,
                "xp_reward": 10,
                "starter_code": 'x = 10\n\ndef modify():\n    x = 20\n    print("Inside:", x)\n\nmodify()\nprint("Outside:", x)',
                "solution_code": "Inside: 20\nOutside: 10",
                "validation_config": '{"expected_output": "Inside: 20\\nOutside: 10"}',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "What will this print? The function creates its own local x.", "hint": "Local x doesn't affect global x", "explanation": "Assigning to x inside the function creates a new local variable. The global x is unchanged."},
                    {"language": LanguageEnum.fr, "prompt": "Qu'affichera ceci ? La fonction crée sa propre variable locale x.", "hint": "Le x local n'affecte pas le x global", "explanation": "Affecter x dans la fonction crée une nouvelle variable locale. Le x global est inchangé."},
                    {"language": LanguageEnum.ar, "prompt": "ماذا سيطبع هذا؟ الدالة تنشئ متغير x محلي خاص بها.", "hint": "المتغير x المحلي لا يؤثر على x العام", "explanation": "تعيين x داخل الدالة ينشئ متغير محلي جديد. المتغير x العام يبقى دون تغيير."},
                ]
            }
        ]
    )
    
    # Lesson 12: Decomposition and Problem Solving
    await get_or_create_lesson(db, module3_id, "decomposition-problem-solving", 4,
        DifficultyEnum.intermediate, 40, 60,
        [
            {"language": LanguageEnum.en, "title": "Decomposition and Problem Solving", "story": "Break big problems into small, manageable functions", "objective": "Decompose problems into multiple functions", "skills": "Problem decomposition, modular design"},
            {"language": LanguageEnum.fr, "title": "Décomposition et Résolution de Problèmes", "story": "Divisez les gros problèmes en petites fonctions gérables", "objective": "Décomposer les problèmes en plusieurs fonctions", "skills": "Décomposition de problèmes, conception modulaire"},
            {"language": LanguageEnum.ar, "title": "التقسيم وحل المشكلات", "story": "اقسم المشاكل الكبيرة إلى دوال صغيرة قابلة للإدارة", "objective": "تحليل المشاكل إلى دوال متعددة", "skills": "تحليل المشكلات، التصميم المعياري"},
        ],
        [
            {"type": "text", "order": 1, "content": "Complex problems become manageable when broken into smaller functions. Each function should do one thing well."},
            {"type": "code", "order": 2, "content": "Decomposing a grade calculator:", "code_example": 'def get_letter_grade(score):\n    if score >= 90: return "A"\n    elif score >= 80: return "B"\n    elif score >= 70: return "C"\n    else: return "F"\n\ndef calculate_average(scores):\n    return sum(scores) / len(scores)\n\ndef main():\n    scores = [85, 92, 78, 90, 88]\n    avg = calculate_average(scores)\n    grade = get_letter_grade(avg)\n    print(f"Average: {avg}, Grade: {grade}")\n\nmain()'},
            {"type": "text", "order": 3, "content": "Each function has a single responsibility. This makes code easier to read, test, and modify."},
            # Micro-Quest blocks (hook 0, blueprint 4, exam_tip 5). The blueprint
            # is the order_steps interaction. Lessons without these render as before.
            *seed_blocks("decomposition-problem-solving"),
        ],
        [
            {
                "type": ExerciseTypeEnum.code_writing,
                "order": 1,
                "xp_reward": 15,
                "starter_code": '# Decompose this problem into functions:\n# 1. is_even(n) - returns True if n is even\n# 2. count_evens(numbers) - returns count of even numbers in list\n# 3. Use them to count evens in [1,2,3,4,5,6,7,8,9,10]\n\ndef is_even(n):\n    \n\ndef count_evens(numbers):\n    \n\nprint(count_evens([1,2,3,4,5,6,7,8,9,10]))',
                "solution_code": 'def is_even(n):\n    return n % 2 == 0\n\ndef count_evens(numbers):\n    count = 0\n    for n in numbers:\n        if is_even(n):\n            count += 1\n    return count\n\nprint(count_evens([1,2,3,4,5,6,7,8,9,10]))',
                "test_code": 'import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "5" in output',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Write two functions: is_even(n) returns True if n is even, count_evens(numbers) counts evens in a list. Use them to count evens in [1,2,3,4,5,6,7,8,9,10].", "hint": "is_even uses n % 2 == 0. count_evens loops and calls is_even.", "explanation": "Breaking a problem into small functions makes each part simple and reusable."},
                    {"language": LanguageEnum.fr, "prompt": "Écrivez deux fonctions : is_even(n) retourne True si n est pair, count_evens(numbers) compte les pairs dans une liste. Utilisez-les pour compter les pairs dans [1,2,3,4,5,6,7,8,9,10].", "hint": "is_even utilise n % 2 == 0. count_evens boucle et appelle is_even.", "explanation": "Diviser un problème en petites fonctions rend chaque partie simple et réutilisable."},
                    {"language": LanguageEnum.ar, "prompt": "اكتب دالتين: is_even(n) ترجع True إذا كان n زوجياً، count_evens(numbers) تحسب الزوجيات في قائمة. استخدمهما لحساب الزوجيات في [1,2,3,4,5,6,7,8,9,10].", "hint": "is_even تستخدم n % 2 == 0. count_evens تدور وتستدعي is_even.", "explanation": "تقسيم المشكلة إلى دوال صغيرة يجعل كل جزء بسيطاً وقابلاً لإعادة الاستخدام."},
                ]
            }
        ]
    )
    
    # Module 4: Data Structures
    module4_id = await get_or_create_module(db, course_id, "data-structures", 4, [
        {"language": LanguageEnum.en, "title": "Data Structures", "description": "Organize collections of data with lists, tuples, sets, and dictionaries"},
        {"language": LanguageEnum.fr, "title": "Structures de Données", "description": "Organisez des collections de données avec listes, tuples, ensembles et dictionnaires"},
        {"language": LanguageEnum.ar, "title": "هياكل البيانات", "description": "نظم مجموعات البيانات بقوائم، توابل، مجموعات، وقواميس"},
    ])
    
    # Lesson 13: Lists
    await get_or_create_lesson(db, module4_id, "lists", 1,
        DifficultyEnum.beginner, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "Lists", "story": "Store ordered collections of items that can be changed", "objective": "Create, access, modify, and iterate over lists", "skills": "Lists, indexing, slicing, append, iteration"},
            {"language": LanguageEnum.fr, "title": "Listes", "story": "Stockez des collections ordonnées d'éléments qui peuvent être modifiés", "objective": "Créer, accéder, modifier et itérer sur des listes", "skills": "Listes, indexation, tranchage, append, itération"},
            {"language": LanguageEnum.ar, "title": "القوائم", "story": "خزن مجموعات مرتبة من العناصر يمكن تغييرها", "objective": "إنشاء، الوصول، تعديل، والتكرار على القوائم", "skills": "قوائم، الفهرسة، الشرائح، append، التكرار"},
        ],
        [
            {"type": "text", "order": 1, "content": "Lists are ordered collections that can hold any type of data. They're created with square brackets and can be modified after creation."},
            {"type": "code", "order": 2, "content": "List operations:", "code_example": 'fruits = ["apple", "banana", "cherry"]\nprint(fruits[0])      # first item\nprint(fruits[-1])     # last item\nfruits.append("date")\nfor fruit in fruits:\n    print(fruit)'},
            {"type": "text", "order": 3, "content": "Index 0 is the first item. Negative indices count from the end. append() adds to the end. for loops iterate over each item."},
        ],
        [
            {
                "type": ExerciseTypeEnum.code_writing,
                "order": 1,
                "xp_reward": 10,
                "starter_code": '# Create a list of Moroccan cities\ncities = ["Casablanca", "Rabat", "Marrakech"]\n# Add "Fes" to the list\n# Print the first and last city\n# Loop through all cities and print each',
                "solution_code": 'cities = ["Casablanca", "Rabat", "Marrakech"]\ncities.append("Fes")\nprint(cities[0])\nprint(cities[-1])\nfor city in cities:\n    print(city)',
                "test_code": 'import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "Casablanca" in output and "Fes" in output',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Create a list of cities, add Fes, print first and last, then loop through all.", "hint": "append() adds to end, [0] is first, [-1] is last", "explanation": "Lists are mutable - you can add, remove, and modify elements after creation."},
                    {"language": LanguageEnum.fr, "prompt": "Créez une liste de villes, ajoutez Fès, affichez la première et la dernière, puis parcourez toutes.", "hint": "append() ajoute à la fin, [0] est premier, [-1] est dernier", "explanation": "Les listes sont mutables - vous pouvez ajouter, supprimer et modifier les éléments."},
                    {"language": LanguageEnum.ar, "prompt": "أنشئ قائمة مدن، أضف فاس، اطبع الأولى والأخيرة، ثم مرر على الكل.", "hint": "append() تضيف للنهاية، [0] أول، [-1] آخر", "explanation": "القوائم قابلة للتعديل - يمكنك إضافة وحذف وتعديل العناصر بعد الإنشاء."},
                ]
            },
            {
                "type": ExerciseTypeEnum.multiple_choice,
                "order": 2,
                "xp_reward": 10,
                "starter_code": "",
                "solution_code": "",
                "validation_config": "",
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "What does fruits[-1] return for fruits = ['apple', 'banana', 'cherry']?", "hint": "Negative index counts from end", "explanation": "-1 is the last element, -2 is second to last, etc."},
                    {"language": LanguageEnum.fr, "prompt": "Que retourne fruits[-1] pour fruits = ['apple', 'banana', 'cherry'] ?", "hint": "L'index négatif compte depuis la fin", "explanation": "-1 est le dernier élément, -2 l'avant-dernier, etc."},
                    {"language": LanguageEnum.ar, "prompt": "ماذا ترجع fruits[-1] لـ fruits = ['apple', 'banana', 'cherry']؟", "hint": "الفهرس السلبي يحسب من النهاية", "explanation": "-1 هو العنصر الأخير، -2 هو ما قبل الأخير، وهكذا."},
                ],
                "options": [
                    {"order": 1, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "apple"}, {"language": LanguageEnum.fr, "text": "apple"}, {"language": LanguageEnum.ar, "text": "apple"}]},
                    {"order": 2, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "banana"}, {"language": LanguageEnum.fr, "text": "banana"}, {"language": LanguageEnum.ar, "text": "banana"}]},
                    {"order": 3, "is_correct": True, "translations": [{"language": LanguageEnum.en, "text": "cherry"}, {"language": LanguageEnum.fr, "text": "cherry"}, {"language": LanguageEnum.ar, "text": "cherry"}]},
                    {"order": 4, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "Error"}, {"language": LanguageEnum.fr, "text": "Erreur"}, {"language": LanguageEnum.ar, "text": "خطأ"}]},
                ]
            }
        ]
    )
    
    # Lesson 14: Tuples and Sets
    await get_or_create_lesson(db, module4_id, "tuples-and-sets", 2,
        DifficultyEnum.beginner, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "Tuples and Sets", "story": "Discover immutable sequences and unique collections", "objective": "Use tuples for fixed data and sets for uniqueness", "skills": "Tuples, immutability, sets, uniqueness"},
            {"language": LanguageEnum.fr, "title": "Tuples et Ensembles", "story": "Découvrez les séquences immuables et les collections uniques", "objective": "Utiliser les tuples pour des données fixes et les ensembles pour l'unicité", "skills": "Tuples, immuabilité, ensembles, unicité"},
            {"language": LanguageEnum.ar, "title": "التوابل والمجموعات", "story": "اكتشف التسلسلات غير القابلة للتغيير والمجموعات الفريدة", "objective": "استخدام التوابل للبيانات الثابتة والمجموعات للتفرد", "skills": "التوابل، عدم التغيير، المجموعات، التفرد"},
        ],
        [
            {"type": "text", "order": 1, "content": "Tuples are like lists but immutable (cannot be changed). Sets are unordered collections with no duplicates. Use tuples for fixed data, sets when you need uniqueness."},
            {"type": "code", "order": 2, "content": "Tuples and sets:", "code_example": 'coordinates = (33.5, -7.6)  # tuple - immutable\nprint(coordinates[0])\n\nunique_numbers = {1, 2, 2, 3, 3, 3}  # set - removes duplicates\nprint(unique_numbers)  # {1, 2, 3}\n\nunique_numbers.add(4)\nprint(4 in unique_numbers)  # True'},
            {"type": "text", "order": 3, "content": "Tuples use parentheses, sets use curly braces. Sets automatically remove duplicates. The in operator checks membership efficiently."},
            # Micro-Quest blocks (hook 0, blueprint 4, exam_tip 5). The blueprint
            # is the spot_the_bug interaction. Lessons without these render as before.
            *seed_blocks("tuples-and-sets"),
        ],
        [
            {
                "type": ExerciseTypeEnum.fill_blank,
                "order": 1,
                "xp_reward": 10,
                "starter_code": '# Tuple - fixed data\npoint = (____, ____)\n\n# Set - unique values\ncolors = {____, "red", "green", "red"}\nprint(colors)  # Should show {"red", "green", "blue"}',
                "solution_code": 'point = (10, 20)\n\ncolors = {"blue", "red", "green", "red"}\nprint(colors)',
                "validation_config": '{"blanks": [{"answer": "10"}, {"answer": "20"}, {"answer": "\\"blue\\""}]}',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Fill in the tuple coordinates (10, 20) and add \"blue\" to the set so it contains red, green, blue.", "hint": "Tuples use parentheses, sets use curly braces", "explanation": "Tuples are immutable ordered pairs. Sets automatically remove duplicates."},
                    {"language": LanguageEnum.fr, "prompt": "Remplissez les coordonnées du tuple (10, 20) et ajoutez \"blue\" à l'ensemble pour qu'il contienne red, green, blue.", "hint": "Les tuples utilisent des parenthèses, les ensembles des accolades", "explanation": "Les tuples sont des paires ordonnées immuables. Les ensembles suppriment automatiquement les doublons."},
                    {"language": LanguageEnum.ar, "prompt": "املأ إحداثيات التوابل (10, 20) وأضف \"blue\" للمجموعة لتحتوي على red، green، blue.", "hint": "التوابل تستخدم أقواساً، المجموعات تستخدم أقواساً معقوفة", "explanation": "التوابل أزواج مرتبة غير قابلة للتغيير. المجموعات تزيل التكرارات تلقائياً."},
                ]
            }
        ]
    )
    
    # Lesson 15: Dictionaries
    await get_or_create_lesson(db, module4_id, "dictionaries", 3,
        DifficultyEnum.beginner, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "Dictionaries", "story": "Store key-value pairs for fast lookups", "objective": "Create, access, update, and iterate dictionaries", "skills": "Dictionaries, key-value pairs, get(), iteration"},
            {"language": LanguageEnum.fr, "title": "Dictionnaires", "story": "Stockez des paires clé-valeur pour des recherches rapides", "objective": "Créer, accéder, mettre à jour et itérer des dictionnaires", "skills": "Dictionnaires, paires clé-valeur, get(), itération"},
            {"language": LanguageEnum.ar, "title": "القواميس", "story": "خزن أزواج مفتاح-قيمة للبحث السريع", "objective": "إنشاء، الوصول، تحديث، والتكرار على القواميس", "skills": "قواميس، أزواج مفتاح-قيمة، get()، التكرار"},
        ],
        [
            {"type": "text", "order": 1, "content": "Dictionaries map keys to values. Keys must be unique and immutable. Use square brackets or get() to access values. get() returns None if key missing instead of error."},
            {"type": "code", "order": 2, "content": "Dictionary operations:", "code_example": 'student = {"name": "Youssef", "age": 20, "city": "Casablanca"}\nprint(student["name"])\nprint(student.get("grade", "Not set"))\nstudent["age"] = 21\nstudent["grade"] = "A"\nfor key, value in student.items():\n    print(key, ":", value)'},
            {"type": "text", "order": 3, "content": "Use items() to iterate over key-value pairs. Dictionaries are perfect for lookup tables, configurations, and structured data."},
            # Micro-Quest blocks (hook 0, blueprint 4, exam_tip 5). The blueprint
            # is the match_pairs interaction. Lessons without these render as before.
            *seed_blocks("dictionaries"),
        ],
        [
            {
                "type": ExerciseTypeEnum.code_writing,
                "order": 1,
                "xp_reward": 10,
                "starter_code": '# Create a dictionary for a product\nproduct = {\n    "name": "____",\n    "price": ____,\n    "in_stock": ____\n}\n# Update price\nproduct["price"] = ____\nprint(product)',
                "solution_code": 'product = {\n    "name": "Tagine",\n    "price": 150,\n    "in_stock": True\n}\nproduct["price"] = 180\nprint(product)',
                "test_code": 'import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "Tagine" in output and "180" in output',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Create a product dictionary with name, price, in_stock. Update the price and print.", "hint": "Use string for name, number for price, boolean for in_stock", "explanation": "Dictionaries store structured data with named fields. Update values by key."},
                    {"language": LanguageEnum.fr, "prompt": "Créez un dictionnaire produit avec nom, prix, en_stock. Mettez à jour le prix et affichez.", "hint": "Chaîne pour nom, nombre pour prix, booléen pour en_stock", "explanation": "Les dictionnaires stockent des données structurées avec des champs nommés. Mettez à jour par clé."},
                    {"language": LanguageEnum.ar, "prompt": "أنشئ قاموس منتج مع الاسم، السعر، in_stock. حدث السعر واطبع.", "hint": "نص للاسم، رقم للسعر، منطقي لـ in_stock", "explanation": "القواميس تخزن بيانات منظمة مع حقول مسماة. حدث القيم بالمفتاح."},
                ]
            }
        ]
    )
    
    # Lesson 16: Data Structures in Real Problems
    await get_or_create_lesson(db, module4_id, "data-structures-real-problems", 4,
        DifficultyEnum.intermediate, 40, 60,
        [
            {"language": LanguageEnum.en, "title": "Data Structures in Real Problems", "story": "Combine lists, dictionaries, and sets to solve practical problems", "objective": "Choose the right data structure for each task", "skills": "Choosing data structures, combining structures, practical problems"},
            {"language": LanguageEnum.fr, "title": "Structures de Données dans les Problèmes Réels", "story": "Combinez listes, dictionnaires et ensembles pour résoudre des problèmes pratiques", "objective": "Choisir la bonne structure de données pour chaque tâche", "skills": "Choix de structures, combinaison, problèmes pratiques"},
            {"language": LanguageEnum.ar, "title": "هياكل البيانات في المشاكل الواقعية", "story": "اجمع القوائم، القواميس، والمجموعات لحل مشاكل عملية", "objective": "اختيار هيكل البيانات المناسب لكل مهمة", "skills": "اختيار الهياكل، الجمع، مشاكل عملية"},
        ],
        [
            {"type": "text", "order": 1, "content": "Lists for ordered sequences, dictionaries for key-value lookups, sets for uniqueness. Real problems often need a combination."},
            {"type": "code", "order": 2, "content": "Student grade tracker:", "code_example": 'students = [\n    {"name": "Amine", "grades": [85, 90, 78]},\n    {"name": "Fatima", "grades": [92, 88, 95]}\n]\n\nfor student in students:\n    avg = sum(student["grades"]) / len(student["grades"])\n    print(f"{student[\"name\"]}: {avg:.1f}")'},
            {"type": "text", "order": 3, "content": "Lists hold multiple students (order matters). Each student is a dictionary (named fields). Grades are a list (multiple values)."},
        ],
        [
            {
                "type": ExerciseTypeEnum.code_writing,
                "order": 1,
                "xp_reward": 15,
                "starter_code": '# Count how many students got each grade\n# A: 90+, B: 80-89, C: 70-79, F: <70\nstudents = [\n    {"name": "Amine", "score": 92},\n    {"name": "Fatima", "score": 85},\n    {"name": "Omar", "score": 76},\n    {"name": "Aicha", "score": 65}\n]\n\ngrade_counts = {"A": 0, "B": 0, "C": 0, "F": 0}\n\nfor student in students:\n    score = student["score"]\n    if score >= 90:\n        grade_counts["A"] += 1\n    elif score >= 80:\n        grade_counts["B"] += 1\n    elif score >= 70:\n        grade_counts["C"] += 1\n    else:\n        grade_counts["F"] += 1\n\nprint(grade_counts)',
                "solution_code": 'students = [\n    {"name": "Amine", "score": 92},\n    {"name": "Fatima", "score": 85},\n    {"name": "Omar", "score": 76},\n    {"name": "Aicha", "score": 65}\n]\n\ngrade_counts = {"A": 0, "B": 0, "C": 0, "F": 0}\n\nfor student in students:\n    score = student["score"]\n    if score >= 90:\n        grade_counts["A"] += 1\n    elif score >= 80:\n        grade_counts["B"] += 1\n    elif score >= 70:\n        grade_counts["C"] += 1\n    else:\n        grade_counts["F"] += 1\n\nprint(grade_counts)',
                "test_code": 'import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "A" in output and "1" in output',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Complete the program to count how many students got each letter grade.", "hint": "Use if/elif/else to categorize, increment the dictionary counter", "explanation": "Dictionaries are perfect for counting categories. Loop through students, determine grade, increment counter."},
                    {"language": LanguageEnum.fr, "prompt": "Complétez le programme pour compter combien d'étudiants ont obtenu chaque note.", "hint": "Utilisez if/elif/else pour catégoriser, incrémentez le compteur du dictionnaire", "explanation": "Les dictionnaires sont parfaits pour compter les catégories. Parcourez les étudiants, déterminez la note, incrémentez."},
                    {"language": LanguageEnum.ar, "prompt": "أكمل البرنامج لحساب عدد الطلاب الذين حصلوا على كل تقدير.", "hint": "استخدم if/elif/else للتصنيف، زد عداد القاموس", "explanation": "القواميس مثالية لحساب الفئات. مرر على الطلاب، حدد التقدير، زد العداد."},
                ]
            }
        ]
    )
    
    print("Python Foundations seeded successfully!")