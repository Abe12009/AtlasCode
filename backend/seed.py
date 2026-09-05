import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from app.db.session import init_db, Base
from app.models import (
    User, StudentProfile, Course, CourseTranslation, Module, ModuleTranslation,
    Lesson, LessonTranslation, LessonBlock, LessonBlockTranslation,
    Exercise, ExerciseTranslation, ExerciseOption, ExerciseOptionTranslation,
    Project, ProjectTranslation, ProjectTask, ProjectTaskTranslation,
    Achievement, AchievementTranslation,
    LanguageEnum, DifficultyEnum, ExerciseTypeEnum, MissionStatusEnum
)
from app.core.security import get_password_hash


def get_test_session_maker():
    test_engine = create_async_engine("sqlite+aiosqlite:///./test_atlascode.db", echo=False)
    return async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def seed_data(session_maker=None):
    if session_maker is None:
        session_maker = get_test_session_maker()
    
    async with session_maker() as db:
        # Check if data already exists
        result = await db.execute(select(Course))
        if result.scalars().first():
            print("Data already exists, skipping seed")
            return

        print("Seeding database...")

        # Create Course 1: Python Basics
        course1 = Course(slug="python-basics", order=1)
        db.add(course1)
        await db.flush()

        course1_translations = [
            CourseTranslation(course_id=course1.id, language=LanguageEnum.en, title="Python Basics", description="Learn the fundamentals of Python programming", skills="Variables, Control Flow, Functions, Data Structures"),
            CourseTranslation(course_id=course1.id, language=LanguageEnum.fr, title="Les Bases de Python", description="Apprenez les fondamentaux de la programmation Python", skills="Variables, Contrôle de flux, Fonctions, Structures de données"),
            CourseTranslation(course_id=course1.id, language=LanguageEnum.ar, title="أساسيات بايثون", description="تعلم أساسيات برمجة بايثون", skills="المتغيرات، التحكم في التدفق، الدوال، هياكل البيانات"),
        ]
        db.add_all(course1_translations)

        # Module 1: Getting Started
        module1 = Module(course_id=course1.id, slug="getting-started", order=1)
        db.add(module1)
        await db.flush()

        module1_translations = [
            ModuleTranslation(module_id=module1.id, language=LanguageEnum.en, title="Getting Started", description="Set up your environment and write your first program"),
            ModuleTranslation(module_id=module1.id, language=LanguageEnum.fr, title="Démarrage", description="Configurez votre environnement et écrivez votre premier programme"),
            ModuleTranslation(module_id=module1.id, language=LanguageEnum.ar, title="البداية", description="قم بإعداد بيئتك واكتب أول برنامج"),
        ]
        db.add_all(module1_translations)

        # Lesson 1: Hello World
        lesson1 = Lesson(module_id=module1.id, slug="hello-world", order=1, difficulty=DifficultyEnum.beginner, estimated_minutes=30, xp_reward=50)
        db.add(lesson1)
        await db.flush()

        lesson1_translations = [
            LessonTranslation(lesson_id=lesson1.id, language=LanguageEnum.en, title="Hello, World!", story="Your first step into programming", objective="Learn to print output to the console", skills="print() function"),
            LessonTranslation(lesson_id=lesson1.id, language=LanguageEnum.fr, title="Bonjour le monde !", story="Votre premier pas dans la programmation", objective="Apprendre à afficher du texte dans la console", skills="fonction print()"),
            LessonTranslation(lesson_id=lesson1.id, language=LanguageEnum.ar, title="مرحباً بالعالم!", story="خطوتك الأولى في البرمجة", objective="تعلم كيفية طباعة المخرجات في وحدة التحكم", skills="دالة print()"),
        ]
        db.add_all(lesson1_translations)

        # Lesson blocks
        blocks1 = [
            LessonBlock(lesson_id=lesson1.id, block_type="text", order=1, content="Welcome to Python! Let's write your first program."),
            LessonBlock(lesson_id=lesson1.id, block_type="code", order=2, content="The print() function outputs text to the console:", code_example='print("Hello, World!")'),
            LessonBlock(lesson_id=lesson1.id, block_type="text", order=3, content="Try changing the text inside the quotes to say something different!"),
        ]
        db.add_all(blocks1)
        await db.flush()

        for block in blocks1:
            block_translations = [
                LessonBlockTranslation(block_id=block.id, language=LanguageEnum.en, content=block.content, code_example=block.code_example),
                LessonBlockTranslation(block_id=block.id, language=LanguageEnum.fr, content=block.content.replace("Welcome", "Bienvenue").replace("Let's write", "Écrivons").replace("The print() function", "La fonction print()").replace("Try changing", "Essayez de changer"), code_example=block.code_example),
                LessonBlockTranslation(block_id=block.id, language=LanguageEnum.ar, content=block.content.replace("Welcome", "مرحباً").replace("Let's write", "لنكتب").replace("The print() function", "دالة print()").replace("Try changing", "حاول تغيير"), code_example=block.code_example),
            ]
            db.add_all(block_translations)

        # Exercise 1a: code_writing - Hello World
        ex1a = Exercise(lesson_id=lesson1.id, exercise_type=ExerciseTypeEnum.code_writing, order=1, xp_reward=10, starter_code='print("Hello, World!")', solution_code='print("Hello, World!")', test_code='import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "Hello, World!" in output')
        db.add(ex1a)
        await db.flush()

        ex1a_translations = [
            ExerciseTranslation(exercise_id=ex1a.id, language=LanguageEnum.en, prompt='Write a program that prints "Hello, World!" to the console.', hint='Use the print() function', explanation='The print() function outputs text to the console.'),
            ExerciseTranslation(exercise_id=ex1a.id, language=LanguageEnum.fr, prompt='Écrivez un programme qui affiche "Bonjour le monde !" dans la console.', hint='Utilisez la fonction print()', explanation='La fonction print() affiche du texte dans la console.'),
            ExerciseTranslation(exercise_id=ex1a.id, language=LanguageEnum.ar, prompt='اكتب برنامجاً يطبع "مرحباً بالعالم!" في وحدة التحكم.', hint='استخدم دالة print()', explanation='دالة print() تطبع النص في وحدة التحكم.'),
        ]
        db.add_all(ex1a_translations)

        # Exercise 1b: prediction - What does this print?
        ex1b = Exercise(lesson_id=lesson1.id, exercise_type=ExerciseTypeEnum.prediction, order=2, xp_reward=10, starter_code='print("Hello")\nprint("World")', solution_code='Hello\nWorld', test_code='', validation_config='{"expected_output": "Hello\\nWorld"}')
        db.add(ex1b)
        await db.flush()

        ex1b_translations = [
            ExerciseTranslation(exercise_id=ex1b.id, language=LanguageEnum.en, prompt='What will this code print?', hint='Each print() call outputs on a new line', explanation='Each print() statement outputs its argument followed by a newline.'),
            ExerciseTranslation(exercise_id=ex1b.id, language=LanguageEnum.fr, prompt='Qu\'affichera ce code ?', hint='Chaque appel print() affiche sur une nouvelle ligne', explanation='Chaque instruction print() affiche son argument suivi d\'un saut de ligne.'),
            ExerciseTranslation(exercise_id=ex1b.id, language=LanguageEnum.ar, prompt='ماذا سيطبع هذا الكود؟', hint='كل استدعاء print() يطبع في سطر جديد', explanation='كل جملة print() تطبع المعامل الخاص بها متبوعاً بسطر جديد.'),
        ]
        db.add_all(ex1b_translations)

        # Lesson 2: Variables
        lesson2 = Lesson(module_id=module1.id, slug="variables", order=2, difficulty=DifficultyEnum.beginner, estimated_minutes=30, xp_reward=50)
        db.add(lesson2)
        await db.flush()

        lesson2_translations = [
            LessonTranslation(lesson_id=lesson2.id, language=LanguageEnum.en, title="Variables", story="Store and manipulate data", objective="Learn to create and use variables", skills="Variables, Data Types, Assignment"),
            LessonTranslation(lesson_id=lesson2.id, language=LanguageEnum.fr, title="Variables", story="Stockez et manipulez des données", objective="Apprenez à créer et utiliser des variables", skills="Variables, Types de données, Affectation"),
            LessonTranslation(lesson_id=lesson2.id, language=LanguageEnum.ar, title="المتغيرات", story="خزن البيانات وتعامل معها", objective="تعلم إنشاء واستخدام المتغيرات", skills="المتغيرات، أنواع البيانات، التعيين"),
        ]
        db.add_all(lesson2_translations)

        blocks2 = [
            LessonBlock(lesson_id=lesson2.id, block_type="text", order=1, content="Variables are containers for storing data values."),
            LessonBlock(lesson_id=lesson2.id, block_type="code", order=2, content="Creating variables in Python:", code_example='name = "Alice"\nage = 25\nheight = 5.5\nis_student = True'),
            LessonBlock(lesson_id=lesson2.id, block_type="text", order=3, content="Python automatically determines the data type based on the value assigned."),
        ]
        db.add_all(blocks2)
        await db.flush()

        for block in blocks2:
            block_translations = [
                LessonBlockTranslation(block_id=block.id, language=LanguageEnum.en, content=block.content, code_example=block.code_example),
                LessonBlockTranslation(block_id=block.id, language=LanguageEnum.fr, content=block.content.replace("Variables are", "Les variables sont").replace("Creating variables", "Création de variables").replace("Python automatically", "Python détermine automatiquement"), code_example=block.code_example),
                LessonBlockTranslation(block_id=block.id, language=LanguageEnum.ar, content=block.content.replace("Variables are", "المتغيرات هي").replace("Creating variables", "إنشاء المتغيرات").replace("Python automatically", "بايثون تحدد تلقائياً"), code_example=block.code_example),
            ]
            db.add_all(block_translations)

        # Exercise 2a: code_writing - Variables
        ex2a = Exercise(lesson_id=lesson2.id, exercise_type=ExerciseTypeEnum.code_writing, order=1, xp_reward=10, starter_code='# Create a variable called name with your name\n# Create a variable called age with your age\nprint(name, age)', solution_code='name = "Alice"\nage = 25\nprint(name, age)', test_code='import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "Alice" in output and "25" in output')
        db.add(ex2a)
        await db.flush()

        ex2a_translations = [
            ExerciseTranslation(exercise_id=ex2a.id, language=LanguageEnum.en, prompt='Create a variable called name with your name and a variable called age with your age. Then print both.', hint='Use the assignment operator (=)', explanation='Variables store values that can be used later in your program.'),
            ExerciseTranslation(exercise_id=ex2a.id, language=LanguageEnum.fr, prompt='Créez une variable name avec votre nom et une variable age avec votre âge. Affichez les deux.', hint='Utilisez l\'opérateur d\'affectation (=)', explanation='Les variables stockent des valeurs qui peuvent être utilisées plus tard.'),
            ExerciseTranslation(exercise_id=ex2a.id, language=LanguageEnum.ar, prompt='أنشئ متغيراً يسمى name باسمك ومتغيراً يسمى age بعمرك. ثم اطبع كلاهما.', hint='استخدم عامل التعيين (=)', explanation='المتغيرات تخزن القيم التي يمكن استخدامها لاحقاً في برنامجك.'),
        ]
        db.add_all(ex2a_translations)

        # Exercise 2b: fill_blank - Complete the variable assignment
        ex2b = Exercise(lesson_id=lesson2.id, exercise_type=ExerciseTypeEnum.fill_blank, order=2, xp_reward=10, starter_code='name = "____"\nage = ____\nprint(name, age)', solution_code='name = "Bob"\nage = 30\nprint(name, age)', test_code='', validation_config='{"blanks": [{"answer": "\"Bob\""}, {"answer": "30"}]}')
        db.add(ex2b)
        await db.flush()

        ex2b_translations = [
            ExerciseTranslation(exercise_id=ex2b.id, language=LanguageEnum.en, prompt='Fill in the blanks to create a variable name with value "Bob" and age with value 30.', hint='String values need quotes, numbers do not', explanation='Strings must be wrapped in quotes. Numbers are written directly.'),
            ExerciseTranslation(exercise_id=ex2b.id, language=LanguageEnum.fr, prompt='Remplissez les blancs pour créer une variable name avec la valeur "Bob" et age avec la valeur 30.', hint='Les chaînes de caractères nécessitent des guillemets, les nombres non', explanation='Les chaînes doivent être entre guillemets. Les nombres s\'écrivent directement.'),
            ExerciseTranslation(exercise_id=ex2b.id, language=LanguageEnum.ar, prompt='املأ الفراغات لإنشاء متغير name بقيمة "Bob" ومتغير age بقيمة 30.', hint='القيم النصية تحتاج لعلامات تنصيص، الأرقام لا تحتاج', explanation='يجب وضع النصوص بين علامتي تنصيص. الأرقام تكتب مباشرة.'),
        ]
        db.add_all(ex2b_translations)

        # Module 2: Control Flow
        module2 = Module(course_id=course1.id, slug="control-flow", order=2)
        db.add(module2)
        await db.flush()

        module2_translations = [
            ModuleTranslation(module_id=module2.id, language=LanguageEnum.en, title="Control Flow", description="Make decisions and repeat code"),
            ModuleTranslation(module_id=module2.id, language=LanguageEnum.fr, title="Contrôle de Flux", description="Prenez des décisions et répétez du code"),
            ModuleTranslation(module_id=module2.id, language=LanguageEnum.ar, title="التحكم في التدفق", description="اتخذ القرارات وكرر الكود"),
        ]
        db.add_all(module2_translations)

        # Lesson 3: If Statements
        lesson3 = Lesson(module_id=module2.id, slug="if-statements", order=1, difficulty=DifficultyEnum.beginner, estimated_minutes=30, xp_reward=50)
        db.add(lesson3)
        await db.flush()

        lesson3_translations = [
            LessonTranslation(lesson_id=lesson3.id, language=LanguageEnum.en, title="If Statements", story="Make decisions in your code", objective="Learn to use if, elif, and else statements", skills="Conditional Logic, Comparison Operators"),
            LessonTranslation(lesson_id=lesson3.id, language=LanguageEnum.fr, title="Instructions If", story="Prenez des décisions dans votre code", objective="Apprenez à utiliser les instructions if, elif et else", skills="Logique conditionnelle, Opérateurs de comparaison"),
            LessonTranslation(lesson_id=lesson3.id, language=LanguageEnum.ar, title="جمل If", story="اتخذ القرارات في الكود الخاص بك", objective="تعلم استخدام جمل if و elif و else", skills="المنطق الشرطي، عوامل المقارنة"),
        ]
        db.add_all(lesson3_translations)

        blocks3 = [
            LessonBlock(lesson_id=lesson3.id, block_type="text", order=1, content="If statements let your program make decisions based on conditions."),
            LessonBlock(lesson_id=lesson3.id, block_type="code", order=2, content="Basic if statement:", code_example='age = 18\nif age >= 18:\n    print("You are an adult")'),
            LessonBlock(lesson_id=lesson3.id, block_type="code", order=3, content="If-elif-else:", code_example='score = 85\nif score >= 90:\n    print("A")\nelif score >= 80:\n    print("B")\nelse:\n    print("C")'),
        ]
        db.add_all(blocks3)
        await db.flush()

        for block in blocks3:
            block_translations = [
                LessonBlockTranslation(block_id=block.id, language=LanguageEnum.en, content=block.content, code_example=block.code_example),
                LessonBlockTranslation(block_id=block.id, language=LanguageEnum.fr, content=block.content.replace("If statements let", "Les instructions if permettent").replace("Basic if statement", "Instruction if de base").replace("If-elif-else", "If-elif-else"), code_example=block.code_example),
                LessonBlockTranslation(block_id=block.id, language=LanguageEnum.ar, content=block.content.replace("If statements let", "جمل If تسمح").replace("Basic if statement", "جملة If أساسية").replace("If-elif-else", "If-elif-else"), code_example=block.code_example),
            ]
            db.add_all(block_translations)

        # Exercise 3a: code_writing - If statements
        ex3a = Exercise(lesson_id=lesson3.id, exercise_type=ExerciseTypeEnum.code_writing, order=1, xp_reward=10, starter_code='age = 20\n# Write an if statement to check if age >= 18\n# Print "Adult" if true, "Minor" if false', solution_code='age = 20\nif age >= 18:\n    print("Adult")\nelse:\n    print("Minor")', test_code='import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "Adult" in output')
        db.add(ex3a)
        await db.flush()

        ex3a_translations = [
            ExerciseTranslation(exercise_id=ex3a.id, language=LanguageEnum.en, prompt='Write an if-else statement that prints "Adult" if age is 18 or older, otherwise prints "Minor".', hint='Use >= for comparison', explanation='If-else statements allow you to run different code based on a condition.'),
            ExerciseTranslation(exercise_id=ex3a.id, language=LanguageEnum.fr, prompt='Écrivez une instruction if-else qui affiche "Adulte" si l\'âge est >= 18, sinon "Mineur".', hint='Utilisez >= pour la comparaison', explanation='Les instructions if-else permettent d\'exécuter du code différent selon une condition.'),
            ExerciseTranslation(exercise_id=ex3a.id, language=LanguageEnum.ar, prompt='اكتب جملة if-else تطبع "بالغ" إذا كان العمر 18 أو أكبر، وإلا تطبع "قاصر".', hint='استخدم >= للمقارنة', explanation='جمل if-else تسمح لك بتشغيل كود مختلف بناءً على شرط.'),
        ]
        db.add_all(ex3a_translations)

        # Exercise 3b: multiple_choice - Which condition is true?
        ex3b = Exercise(lesson_id=lesson3.id, exercise_type=ExerciseTypeEnum.multiple_choice, order=2, xp_reward=10, starter_code='', solution_code='', test_code='', validation_config='')
        db.add(ex3b)
        await db.flush()

        ex3b_translations = [
            ExerciseTranslation(exercise_id=ex3b.id, language=LanguageEnum.en, prompt='If x = 10, which condition is True?', hint='Compare x with 10', explanation='10 == 10 is True, 10 > 10 is False, 10 < 10 is False.'),
            ExerciseTranslation(exercise_id=ex3b.id, language=LanguageEnum.fr, prompt='Si x = 10, quelle condition est Vraie ?', hint='Comparez x avec 10', explanation='10 == 10 est Vrai, 10 > 10 est Faux, 10 < 10 est Faux.'),
            ExerciseTranslation(exercise_id=ex3b.id, language=LanguageEnum.ar, prompt='إذا كانت x = 10، أي شرط صحيح؟', hint='قارن x مع 10', explanation='10 == 10 صحيح، 10 > 10 خطأ، 10 < 10 خطأ.'),
        ]
        db.add_all(ex3b_translations)

        # Options for multiple choice
        opt3b_1 = ExerciseOption(exercise_id=ex3b.id, order=1, is_correct=True)
        opt3b_2 = ExerciseOption(exercise_id=ex3b.id, order=2, is_correct=False)
        opt3b_3 = ExerciseOption(exercise_id=ex3b.id, order=3, is_correct=False)
        db.add_all([opt3b_1, opt3b_2, opt3b_3])
        await db.flush()

        opt3b_translations = [
            ExerciseOptionTranslation(option_id=opt3b_1.id, language=LanguageEnum.en, text='x == 10'),
            ExerciseOptionTranslation(option_id=opt3b_2.id, language=LanguageEnum.en, text='x > 10'),
            ExerciseOptionTranslation(option_id=opt3b_3.id, language=LanguageEnum.en, text='x < 10'),
            ExerciseOptionTranslation(option_id=opt3b_1.id, language=LanguageEnum.fr, text='x == 10'),
            ExerciseOptionTranslation(option_id=opt3b_2.id, language=LanguageEnum.fr, text='x > 10'),
            ExerciseOptionTranslation(option_id=opt3b_3.id, language=LanguageEnum.fr, text='x < 10'),
            ExerciseOptionTranslation(option_id=opt3b_1.id, language=LanguageEnum.ar, text='x == 10'),
            ExerciseOptionTranslation(option_id=opt3b_2.id, language=LanguageEnum.ar, text='x > 10'),
            ExerciseOptionTranslation(option_id=opt3b_3.id, language=LanguageEnum.ar, text='x < 10'),
        ]
        db.add_all(opt3b_translations)

        # Lesson 4: Loops
        lesson4 = Lesson(module_id=module2.id, slug="loops", order=2, difficulty=DifficultyEnum.beginner, estimated_minutes=30, xp_reward=50)
        db.add(lesson4)
        await db.flush()

        lesson4_translations = [
            LessonTranslation(lesson_id=lesson4.id, language=LanguageEnum.en, title="Loops", story="Repeat code efficiently", objective="Learn to use for and while loops", skills="For Loops, While Loops, Range"),
            LessonTranslation(lesson_id=lesson4.id, language=LanguageEnum.fr, title="Boucles", story="Répétez du code efficacement", objective="Apprenez à utiliser les boucles for et while", skills="Boucles For, Boucles While, Range"),
            LessonTranslation(lesson_id=lesson4.id, language=LanguageEnum.ar, title="الحلقات", story="كرر الكود بكفاءة", objective="تعلم استخدام حلقات for و while", skills="حلقات For، حلقات While، Range"),
        ]
        db.add_all(lesson4_translations)

        blocks4 = [
            LessonBlock(lesson_id=lesson4.id, block_type="text", order=1, content="Loops allow you to repeat code multiple times without writing it over and over."),
            LessonBlock(lesson_id=lesson4.id, block_type="code", order=2, content="For loop with range:", code_example='for i in range(5):\n    print(i)'),
            LessonBlock(lesson_id=lesson4.id, block_type="code", order=3, content="For loop over a list:", code_example='fruits = ["apple", "banana", "cherry"]\nfor fruit in fruits:\n    print(fruit)'),
            LessonBlock(lesson_id=lesson4.id, block_type="code", order=4, content="While loop:", code_example='count = 0\nwhile count < 3:\n    print(count)\n    count += 1'),
        ]
        db.add_all(blocks4)
        await db.flush()

        for block in blocks4:
            block_translations = [
                LessonBlockTranslation(block_id=block.id, language=LanguageEnum.en, content=block.content, code_example=block.code_example),
                LessonBlockTranslation(block_id=block.id, language=LanguageEnum.fr, content=block.content.replace("Loops allow", "Les boucles permettent").replace("For loop with", "Boucle for avec").replace("For loop over", "Boucle for sur").replace("While loop", "Boucle while"), code_example=block.code_example),
                LessonBlockTranslation(block_id=block.id, language=LanguageEnum.ar, content=block.content.replace("Loops allow", "الحلقات تسمح").replace("For loop with", "حلقة for مع").replace("For loop over", "حلقة for على").replace("While loop", "حلقة while"), code_example=block.code_example),
            ]
            db.add_all(block_translations)

        # Exercise 4a: code_writing - For loop
        ex4a = Exercise(lesson_id=lesson4.id, exercise_type=ExerciseTypeEnum.code_writing, order=1, xp_reward=10, starter_code='# Write a for loop that prints numbers 1 to 5\nfor i in range(1, 6):\n    print(i)', solution_code='for i in range(1, 6):\n    print(i)', test_code='import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "1" in output and "5" in output')
        db.add(ex4a)
        await db.flush()

        ex4a_translations = [
            ExerciseTranslation(exercise_id=ex4a.id, language=LanguageEnum.en, prompt='Write a for loop that prints numbers 1 through 5.', hint='Use range(1, 6)', explanation='range(1, 6) generates numbers from 1 to 5.'),
            ExerciseTranslation(exercise_id=ex4a.id, language=LanguageEnum.fr, prompt='Écrivez une boucle for qui affiche les nombres de 1 à 5.', hint='Utilisez range(1, 6)', explanation='range(1, 6) génère les nombres de 1 à 5.'),
            ExerciseTranslation(exercise_id=ex4a.id, language=LanguageEnum.ar, prompt='اكتب حلقة for تطبع الأرقام من 1 إلى 5.', hint='استخدم range(1, 6)', explanation='range(1, 6) تولد الأرقام من 1 إلى 5.'),
        ]
        db.add_all(ex4a_translations)

        # Exercise 4b: debugging - Fix the infinite loop
        ex4b = Exercise(lesson_id=lesson4.id, exercise_type=ExerciseTypeEnum.debugging, order=2, xp_reward=15, starter_code='count = 0\nwhile count < 5:\n    print(count)\n    # Missing: count += 1', solution_code='count = 0\nwhile count < 5:\n    print(count)\n    count += 1', test_code='import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "0" in output and "4" in output and output.count("\\n") >= 5')
        db.add(ex4b)
        await db.flush()

        ex4b_translations = [
            ExerciseTranslation(exercise_id=ex4b.id, language=LanguageEnum.en, prompt='This loop runs forever! Fix it so it prints 0, 1, 2, 3, 4 and stops.', hint='You need to increment the counter inside the loop', explanation='The variable count must be increased inside the loop, otherwise the condition count < 5 is always true.'),
            ExerciseTranslation(exercise_id=ex4b.id, language=LanguageEnum.fr, prompt='Cette boucle tourne à l\'infini ! Corrigez-la pour qu\'elle affiche 0, 1, 2, 3, 4 et s\'arrête.', hint='Vous devez incrémenter le compteur à l\'intérieur de la boucle', explanation='La variable count doit être augmentée dans la boucle, sinon la condition count < 5 est toujours vraie.'),
            ExerciseTranslation(exercise_id=ex4b.id, language=LanguageEnum.ar, prompt='هذه الحلقة تعمل للأبد! أصلحها لتطبع 0، 1، 2، 3، 4 ثم تتوقف.', hint='يجب زيادة العداد داخل الحلقة', explanation='يجب زيادة المتغير count داخل الحلقة، وإلا ستبقى الشرط count < 5 صحيحاً دائماً.'),
        ]
        db.add_all(ex4b_translations)

        # Exercise 4c: ordering - Put loop parts in order
        ex4c = Exercise(lesson_id=lesson4.id, exercise_type=ExerciseTypeEnum.ordering, order=3, xp_reward=10, starter_code='', solution_code='', test_code='', validation_config='')
        db.add(ex4c)
        await db.flush()

        ex4c_translations = [
            ExerciseTranslation(exercise_id=ex4c.id, language=LanguageEnum.en, prompt='Put these lines in the correct order to create a working for loop.', hint='Think about the structure of a for loop', explanation='A for loop starts with the for statement, then the indented body.'),
            ExerciseTranslation(exercise_id=ex4c.id, language=LanguageEnum.fr, prompt='Mettez ces lignes dans l\'ordre correct pour créer une boucle for qui fonctionne.', hint='Pensez à la structure d\'une boucle for', explanation='Une boucle for commence par l\'instruction for, puis le corps indenté.'),
            ExerciseTranslation(exercise_id=ex4c.id, language=LanguageEnum.ar, prompt='ضع هذه الأسطر بالترتيب الصحيح لإنشاء حلقة for تعمل.', hint='فكر في هيكل حلقة for', explanation='تبدأ حلقة for بعبارة for، ثم الجسم المسطر.'),
        ]
        db.add_all(ex4c_translations)

        opt4c_1 = ExerciseOption(exercise_id=ex4c.id, order=1, is_correct=True)
        opt4c_2 = ExerciseOption(exercise_id=ex4c.id, order=2, is_correct=True)
        opt4c_3 = ExerciseOption(exercise_id=ex4c.id, order=3, is_correct=True)
        db.add_all([opt4c_1, opt4c_2, opt4c_3])
        await db.flush()

        opt4c_translations = [
            ExerciseOptionTranslation(option_id=opt4c_1.id, language=LanguageEnum.en, text='for i in range(3):'),
            ExerciseOptionTranslation(option_id=opt4c_2.id, language=LanguageEnum.en, text='    print(i)'),
            ExerciseOptionTranslation(option_id=opt4c_3.id, language=LanguageEnum.en, text='print("Done")'),
            ExerciseOptionTranslation(option_id=opt4c_1.id, language=LanguageEnum.fr, text='for i in range(3):'),
            ExerciseOptionTranslation(option_id=opt4c_2.id, language=LanguageEnum.fr, text='    print(i)'),
            ExerciseOptionTranslation(option_id=opt4c_3.id, language=LanguageEnum.fr, text='print("Terminé")'),
            ExerciseOptionTranslation(option_id=opt4c_1.id, language=LanguageEnum.ar, text='for i in range(3):'),
            ExerciseOptionTranslation(option_id=opt4c_2.id, language=LanguageEnum.ar, text='    print(i)'),
            ExerciseOptionTranslation(option_id=opt4c_3.id, language=LanguageEnum.ar, text='print("انتهى")'),
        ]
        db.add_all(opt4c_translations)

        # Exercise 4d: visual_programming - Simple loop
        visual_starter_4d = '{"nodes": [{"id": "1", "type": "start", "config": {}}, {"id": "2", "type": "loop", "config": {"var": "i", "times": "3"}}, {"id": "3", "type": "output", "config": {"value": "i"}}, {"id": "4", "type": "end", "config": {}}], "edges": [{"source": "1", "target": "2"}, {"source": "2", "target": "3"}, {"source": "3", "target": "4"}]}'
        ex4d = Exercise(lesson_id=lesson4.id, exercise_type=ExerciseTypeEnum.visual_programming, order=4, xp_reward=15, starter_code=visual_starter_4d, solution_code='for i in range(3):\n    print(i)', test_code='import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "0" in output and "1" in output and "2" in output')
        db.add(ex4d)
        await db.flush()

        ex4d_translations = [
            ExerciseTranslation(exercise_id=ex4d.id, language=LanguageEnum.en, prompt='Build a visual program that loops 3 times and prints the counter.', hint='Use a loop node connected to an output node', explanation='The loop node creates a for loop. Connect it to an output node to print each iteration.'),
            ExerciseTranslation(exercise_id=ex4d.id, language=LanguageEnum.fr, prompt='Construisez un programme visuel qui boucle 3 fois et affiche le compteur.', hint='Utilisez un nœud boucle connecté à un nœud sortie', explanation='Le nœud boucle crée une boucle for. Connectez-le à un nœud sortie pour afficher chaque itération.'),
            ExerciseTranslation(exercise_id=ex4d.id, language=LanguageEnum.ar, prompt='ابنِ برنامجاً مرئياً يكرر 3 مرات ويطبع العداد.', hint='استخدم عقدة حلقة متصلة بعقدة إخراج', explanation='عقدة الحلقة تنشئ حلقة for. قم بتوصيلها بعقدة إخراج لطباعة كل تكرار.'),
        ]
        db.add_all(ex4d_translations)

        # Course 2: Web Development Basics
        course2 = Course(slug="web-basics", order=2)
        db.add(course2)
        await db.flush()

        course2_translations = [
            CourseTranslation(course_id=course2.id, language=LanguageEnum.en, title="Web Development Basics", description="Build your first website with HTML and CSS", skills="HTML, CSS, Responsive Design"),
            CourseTranslation(course_id=course2.id, language=LanguageEnum.fr, title="Bases du Développement Web", description="Créez votre premier site web avec HTML et CSS", skills="HTML, CSS, Design Responsive"),
            CourseTranslation(course_id=course2.id, language=LanguageEnum.ar, title="أساسيات تطوير الويب", description="ابنِ أول موقع ويب مع HTML و CSS", skills="HTML، CSS، التصميم المتجاوب"),
        ]
        db.add_all(course2_translations)

        # Module 3: HTML Basics
        module3 = Module(course_id=course2.id, slug="html-basics", order=1)
        db.add(module3)
        await db.flush()

        module3_translations = [
            ModuleTranslation(module_id=module3.id, language=LanguageEnum.en, title="HTML Basics", description="Learn the structure of web pages"),
            ModuleTranslation(module_id=module3.id, language=LanguageEnum.fr, title="Bases HTML", description="Apprenez la structure des pages web"),
            ModuleTranslation(module_id=module3.id, language=LanguageEnum.ar, title="أساسيات HTML", description="تعلم هيكل صفحات الويب"),
        ]
        db.add_all(module3_translations)

        # Lesson 5: HTML Structure
        lesson5 = Lesson(module_id=module3.id, slug="html-structure", order=1, difficulty=DifficultyEnum.beginner, estimated_minutes=30, xp_reward=50)
        db.add(lesson5)
        await db.flush()

        lesson5_translations = [
            LessonTranslation(lesson_id=lesson5.id, language=LanguageEnum.en, title="HTML Structure", story="Build the skeleton of a web page", objective="Learn HTML tags and document structure", skills="HTML Tags, Document Structure, Elements"),
            LessonTranslation(lesson_id=lesson5.id, language=LanguageEnum.fr, title="Structure HTML", story="Construisez le squelette d'une page web", objective="Apprenez les balises HTML et la structure du document", skills="Balises HTML, Structure du document, Éléments"),
            LessonTranslation(lesson_id=lesson5.id, language=LanguageEnum.ar, title="هيكل HTML", story="ابنِ هيكل صفحة ويب", objective="تعلم علامات HTML وهيكل المستند", skills="علامات HTML، هيكل المستند، العناصر"),
        ]
        db.add_all(lesson5_translations)

        blocks5 = [
            LessonBlock(lesson_id=lesson5.id, block_type="text", order=1, content="HTML (HyperText Markup Language) is the standard language for creating web pages."),
            LessonBlock(lesson_id=lesson5.id, block_type="code", order=2, content="Basic HTML structure:", code_example='<!DOCTYPE html>\n<html>\n<head>\n    <title>My Page</title>\n</head>\n<body>\n    <h1>Hello, World!</h1>\n    <p>This is a paragraph.</p>\n</body>\n</html>'),
        ]
        db.add_all(blocks5)
        await db.flush()

        for block in blocks5:
            block_translations = [
                LessonBlockTranslation(block_id=block.id, language=LanguageEnum.en, content=block.content, code_example=block.code_example),
                LessonBlockTranslation(block_id=block.id, language=LanguageEnum.fr, content=block.content.replace("HTML (HyperText Markup Language)", "HTML (HyperText Markup Language)").replace("is the standard", "est le langage standard").replace("Basic HTML structure", "Structure HTML de base"), code_example=block.code_example),
                LessonBlockTranslation(block_id=block.id, language=LanguageEnum.ar, content=block.content.replace("HTML (HyperText Markup Language)", "HTML (لغة ترميز النص التشعبي)").replace("is the standard", "هو اللغة القياسية").replace("Basic HTML structure", "هيكل HTML أساسي"), code_example=block.code_example),
            ]
            db.add_all(block_translations)

        # Exercise 5a: code_writing - HTML
        ex5a = Exercise(lesson_id=lesson5.id, exercise_type=ExerciseTypeEnum.code_writing, order=1, xp_reward=10, starter_code='<!DOCTYPE html>\n<html>\n<head>\n    <title>My Page</title>\n</head>\n<body>\n    <!-- Add an h1 and a p tag here -->\n</body>\n</html>', solution_code='<!DOCTYPE html>\n<html>\n<head>\n    <title>My Page</title>\n</head>\n<body>\n    <h1>Hello, World!</h1>\n    <p>This is a paragraph.</p>\n</body>\n</html>', test_code='import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "<h1>" in output and "<p>" in output')
        db.add(ex5a)
        await db.flush()

        ex5a_translations = [
            ExerciseTranslation(exercise_id=ex5a.id, language=LanguageEnum.en, prompt='Add an h1 heading and a p paragraph to the body of the HTML document.', hint='Use <h1> for heading and <p> for paragraph', explanation='HTML uses tags like <h1> for headings and <p> for paragraphs.'),
            ExerciseTranslation(exercise_id=ex5a.id, language=LanguageEnum.fr, prompt='Ajoutez un titre h1 et un paragraphe p au body du document HTML.', hint='Utilisez <h1> pour le titre et <p> pour le paragraphe', explanation='HTML utilise des balises comme <h1> pour les titres et <p> pour les paragraphes.'),
            ExerciseTranslation(exercise_id=ex5a.id, language=LanguageEnum.ar, prompt='أضف عنوان h1 وفقرة p إلى body مستند HTML.', hint='استخدم <h1> للعنوان و <p> للفقرة', explanation='يستخدم HTML علامات مثل <h1> للعناوين و <p> لل الفقرات.'),
        ]
        db.add_all(ex5a_translations)

        # Exercise 5b: fill_blank - HTML tags
        ex5b = Exercise(lesson_id=lesson5.id, exercise_type=ExerciseTypeEnum.fill_blank, order=2, xp_reward=10, starter_code='<____>Heading</____>\n<____>Paragraph</____>', solution_code='<h1>Heading</h1>\n<p>Paragraph</p>', test_code='', validation_config='{"blanks": [{"answer": "h1"}, {"answer": "h1"}, {"answer": "p"}, {"answer": "p"}]}')
        db.add(ex5b)
        await db.flush()

        ex5b_translations = [
            ExerciseTranslation(exercise_id=ex5b.id, language=LanguageEnum.en, prompt='Fill in the HTML tags to create a heading and a paragraph.', hint='Heading uses h1, paragraph uses p', explanation='<h1> creates a top-level heading. <p> creates a paragraph.'),
            ExerciseTranslation(exercise_id=ex5b.id, language=LanguageEnum.fr, prompt='Remplissez les balises HTML pour créer un titre et un paragraphe.', hint='Le titre utilise h1, le paragraphe utilise p', explanation='<h1> crée un titre de premier niveau. <p> crée un paragraphe.'),
            ExerciseTranslation(exercise_id=ex5b.id, language=LanguageEnum.ar, prompt='املأ علامات HTML لإنشاء عنوان وفقرة.', hint='العنوان يستخدم h1، الفقرة تستخدم p', explanation='<h1> تنشئ عنواناً من المستوى الأول. <p> تنشئ فقرة.'),
        ]
        db.add_all(ex5b_translations)

        # Projects - Remove prerequisite so tests can access it
        project1 = Project(slug="calculator", order=1, difficulty=DifficultyEnum.beginner, xp_reward=200, prerequisite_lesson_id=None)
        db.add(project1)
        await db.flush()

        project1_translations = [
            ProjectTranslation(project_id=project1.id, language=LanguageEnum.en, title="Build a Calculator", story="Create a simple calculator that can add, subtract, multiply, and divide", objective="Build a command-line calculator", skills="Functions, Conditionals, User Input"),
            ProjectTranslation(project_id=project1.id, language=LanguageEnum.fr, title="Construire une Calculatrice", story="Créez une calculatrice simple qui peut additionner, soustraire, multiplier et diviser", objective="Construisez une calculatrice en ligne de commande", skills="Fonctions, Conditionnels, Entrée utilisateur"),
            ProjectTranslation(project_id=project1.id, language=LanguageEnum.ar, title="بناء آلة حاسبة", story="أنشئ آلة حاسبة بسيطة يمكنها الجمع والطرح والضرب والقسمة", objective="ابنِ آلة حاسبة في سطر الأوامر", skills="الدوال، الشروط، إدخال المستخدم"),
        ]
        db.add_all(project1_translations)

        task1 = ProjectTask(project_id=project1.id, order=1, starter_code='def add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b\n\ndef multiply(a, b):\n    return a * b\n\ndef divide(a, b):\n    if b != 0:\n        return a / b\n    return "Error: Division by zero"\n\n# Test your functions\nprint(add(5, 3))', validation_code='assert add(2, 3) == 5\nassert subtract(5, 3) == 2\nassert multiply(3, 4) == 12\nassert divide(10, 2) == 5\nassert divide(5, 0) == "Error: Division by zero"\nprint("All tests passed!")')
        db.add(task1)
        await db.flush()

        task1_translations = [
            ProjectTaskTranslation(task_id=task1.id, language=LanguageEnum.en, title="Implement Basic Operations", description="Create functions for add, subtract, multiply, and divide", hint="Remember to handle division by zero"),
            ProjectTaskTranslation(task_id=task1.id, language=LanguageEnum.fr, title="Implémenter les Opérations de Base", description="Créez des fonctions pour additionner, soustraire, multiplier et diviser", hint="N'oubliez pas de gérer la division par zéro"),
            ProjectTaskTranslation(task_id=task1.id, language=LanguageEnum.ar, title="تنفيذ العمليات الأساسية", description="أنشئ دوال للجمع والطرح والضرب والقسمة", hint="تذكر التعامل مع القسمة على صفر"),
        ]
        db.add_all(task1_translations)

        task2 = ProjectTask(project_id=project1.id, order=2, starter_code='def calculator():\n    print("Simple Calculator")\n    print("1. Add")\n    print("2. Subtract")\n    print("3. Multiply")\n    print("4. Divide")\n    \n    choice = input("Enter choice (1/2/3/4): ")\n    \n    num1 = float(input("Enter first number: "))\n    num2 = float(input("Enter second number: "))\n    \n    # Complete the calculator logic here\n    \ncalculator()', validation_code='print("Calculator structure looks good!")')
        db.add(task2)
        await db.flush()

        task2_translations = [
            ProjectTaskTranslation(task_id=task2.id, language=LanguageEnum.en, title="Build the Calculator Menu", description="Create a menu that lets the user choose an operation", hint="Use if-elif-else to handle the user's choice"),
            ProjectTaskTranslation(task_id=task2.id, language=LanguageEnum.fr, title="Construire le Menu de la Calculatrice", description="Créez un menu qui permet à l'utilisateur de choisir une opération", hint="Utilisez if-elif-else pour gérer le choix de l'utilisateur"),
            ProjectTaskTranslation(task_id=task2.id, language=LanguageEnum.ar, title="بناء قائمة الآلة الحاسبة", description="أنشئ قائمة تتيح للمستخدم اختيار عملية", hint="استخدم if-elif-else للتعامل مع اختيار المستخدم"),
        ]
        db.add_all(task2_translations)

        # Achievements
        achievements = [
            Achievement(slug="first-lesson", icon="🎓", xp_reward=50, condition_type="lessons_completed", condition_value=1),
            Achievement(slug="first-course", icon="🏆", xp_reward=200, condition_type="courses_completed", condition_value=1),
            Achievement(slug="streak-7", icon="🔥", xp_reward=100, condition_type="streak", condition_value=7),
            Achievement(slug="level-5", icon="⭐", xp_reward=300, condition_type="level", condition_value=5),
            Achievement(slug="first-project", icon="🚀", xp_reward=200, condition_type="projects_completed", condition_value=1),
        ]
        db.add_all(achievements)
        await db.flush()

        for ach in achievements:
            ach_translations = [
                AchievementTranslation(achievement_id=ach.id, language=LanguageEnum.en, title=ach.slug.replace("-", " ").title(), description=f"Earned for {ach.condition_type.replace('_', ' ')}"),
                AchievementTranslation(achievement_id=ach.id, language=LanguageEnum.fr, title=ach.slug.replace("-", " ").title(), description=f"Gagné pour {ach.condition_type.replace('_', ' ')}"),
                AchievementTranslation(achievement_id=ach.id, language=LanguageEnum.ar, title=ach.slug.replace("-", " ").title(), description=f"تم الحصول عليه لـ {ach.condition_type.replace('_', ' ')}"),
            ]
            db.add_all(ach_translations)

        await db.commit()
        print("Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
    asyncio.run(seed_data())