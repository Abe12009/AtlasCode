from .base import get_or_create_course, get_or_create_module, get_or_create_lesson
from .base import LanguageEnum, DifficultyEnum
from app.models import Project, ProjectTranslation, ProjectTask, ProjectTaskTranslation
from sqlalchemy import select


async def seed_projects(db):
    print("Seeding Projects...")

    # Project 1: CLI Calculator (prerequisite: Lesson 5 - User Input and Output)
    project1 = Project(slug="calculator", order=1, difficulty=DifficultyEnum.beginner, xp_reward=200, prerequisite_lesson_id=5)
    db.add(project1)
    await db.flush()

    project1_translations = [
        ProjectTranslation(project_id=project1.id, language=LanguageEnum.en, title="Build a CLI Calculator", story="Create a command-line calculator that can add, subtract, multiply, and divide", objective="Build a working calculator with functions", skills="Functions, Conditionals, User Input, Error Handling"),
        ProjectTranslation(project_id=project1.id, language=LanguageEnum.fr, title="Construire une Calculatrice CLI", story="Créez une calculatrice en ligne de commande qui peut additionner, soustraire, multiplier et diviser", objective="Construire une calculatrice fonctionnelle avec des fonctions", skills="Fonctions, Conditionnels, Entrée Utilisateur, Gestion d'Erreurs"),
        ProjectTranslation(project_id=project1.id, language=LanguageEnum.ar, title="بناء آلة حاسبة سطر أوامر", story="أنشئ آلة حاسبة في سطر الأوامر يمكنها الجمع والطرح والضرب والقسمة", objective="بناء آلة حاسبة عاملة مع دوال", skills="الدوال، الشروط، إدخال المستخدم، معالجة الأخطاء"),
    ]
    db.add_all(project1_translations)

    # Task 1: Implement Basic Operations
    task1 = ProjectTask(project_id=project1.id, order=1, starter_code='def add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b\n\ndef multiply(a, b):\n    return a * b\n\ndef divide(a, b):\n    if b != 0:\n        return a / b\n    return "Error: Division by zero"\n\n# Test your functions\nprint(add(5, 3))', validation_code='assert add(2, 3) == 5\nassert subtract(5, 3) == 2\nassert multiply(3, 4) == 12\nassert divide(10, 2) == 5\nassert divide(5, 0) == "Error: Division by zero"\nprint("All tests passed!")')
    db.add(task1)
    await db.flush()

    task1_translations = [
        ProjectTaskTranslation(task_id=task1.id, language=LanguageEnum.en, title="Implement Basic Operations", description="Create functions for add, subtract, multiply, and divide", hint="Remember to handle division by zero"),
        ProjectTaskTranslation(task_id=task1.id, language=LanguageEnum.fr, title="Implémenter les Opérations de Base", description="Créez des fonctions pour additionner, soustraire, multiplier et diviser", hint="N'oubliez pas de gérer la division par zéro"),
        ProjectTaskTranslation(task_id=task1.id, language=LanguageEnum.ar, title="تنفيذ العمليات الأساسية", description="أنشئ دوال للجمع والطرح والضرب والقسمة", hint="تذكر التعامل مع القسمة على صفر"),
    ]
    db.add_all(task1_translations)

    # Task 2: Build the Calculator Menu
    task2 = ProjectTask(project_id=project1.id, order=2, starter_code='def calculate(choice, num1, num2):\n    """Perform calculation based on choice.\n    choice: "1"=add, "2"=subtract, "3"=multiply, "4"=divide\n    Returns result or error string.\n    """\n    # TODO: Implement calculator logic\n    pass\n\n# Test your function\nprint(calculate("1", 10, 5))  # Should print 15\nprint(calculate("4", 10, 0))  # Should print error message', validation_code='assert calculate("1", 10, 5) == 15\nassert calculate("2", 10, 5) == 5\nassert calculate("3", 10, 5) == 50\nassert calculate("4", 10, 5) == 2.0\nassert "Error" in str(calculate("4", 10, 0))\nassert "Error" in str(calculate("5", 10, 5))  # Invalid choice\nprint("Calculator menu logic correct!")')
    db.add(task2)
    await db.flush()

    task2_translations = [
        ProjectTaskTranslation(task_id=task2.id, language=LanguageEnum.en, title="Build the Calculator Menu", description="Create a menu that lets the user choose an operation", hint="Use if-elif-else to handle the user's choice"),
        ProjectTaskTranslation(task_id=task2.id, language=LanguageEnum.fr, title="Construire le Menu de la Calculatrice", description="Créez un menu qui permet à l'utilisateur de choisir une opération", hint="Utilisez if-elif-else pour gérer le choix de l'utilisateur"),
        ProjectTaskTranslation(task_id=task2.id, language=LanguageEnum.ar, title="بناء قائمة الآلة الحاسبة", description="أنشئ قائمة تتيح للمستخدم اختيار عملية", hint="استخدم if-elif-else للتعامل مع اختيار المستخدم"),
    ]
    db.add_all(task2_translations)

    # Task 3: Add Loop for Continuous Calculations
    task3 = ProjectTask(project_id=project1.id, order=3, starter_code='def process_operations(operations):\n    """Process a list of operations.\n    operations: list of tuples (choice, num1, num2)\n    choice: "1"=add, "2"=subtract, "3"=multiply, "4"=divide, "5"=exit\n    Returns list of results. Stops processing when choice is "5".\n    """\n    results = []\n    for choice, num1, num2 in operations:\n        # TODO: Implement logic\n        # If choice == "5": break\n        # Else: calculate and append result\n        pass\n    return results\n\n# Test\nops = [("1", 10, 5), ("2", 10, 5), ("5", 0, 0), ("1", 5, 5)]\nprint(process_operations(ops))', validation_code='results = process_operations([("1", 10, 5), ("2", 10, 5), ("5", 0, 0), ("1", 5, 5)])\nassert results == [15, 5]\nresults2 = process_operations([("3", 4, 5), ("4", 20, 4), ("4", 10, 0), ("5", 0, 0)])\nassert results2[0] == 20\nassert results2[1] == 5.0\nassert "Error" in str(results2[2])\nprint("Continuous operation loop correct!")')
    db.add(task3)
    await db.flush()

    task3_translations = [
        ProjectTaskTranslation(task_id=task3.id, language=LanguageEnum.en, title="Add Continuous Operation Loop", description="Allow the user to perform multiple calculations until they choose to exit", hint="Use a while True loop with a break condition"),
        ProjectTaskTranslation(task_id=task3.id, language=LanguageEnum.fr, title="Ajouter une Boucle d'Opérations Continues", description="Permettez à l'utilisateur d'effectuer plusieurs calculs jusqu'à ce qu'il choisisse de quitter", hint="Utilisez une boucle while True avec une condition de break"),
        ProjectTaskTranslation(task_id=task3.id, language=LanguageEnum.ar, title="إضافة حلقة للعمليات المستمرة", description="اسمح للمستخدم بإجراء عدة حسابات حتى يختار الخروج", hint="استخدم حلقة while True مع شرط break"),
    ]
    db.add_all(task3_translations)

    # Task 4: Add Error Handling for Invalid Input
    task4 = ProjectTask(project_id=project1.id, order=4, starter_code='def safe_calculate(choice, num1, num2):\n    """Safely perform calculation with input validation.\n    Returns (success: bool, result: float|str)\n    """\n    # Validate choice\n    if choice not in ["1", "2", "3", "4"]:\n        return (False, "Invalid choice! Please enter 1, 2, 3, or 4.")\n    \n    # Validate numbers\n    try:\n        num1 = float(num1)\n        num2 = float(num2)\n    except (ValueError, TypeError):\n        return (False, "Invalid input! Please enter valid numbers.")\n    \n    # Perform calculation\n    if choice == "1":\n        return (True, num1 + num2)\n    elif choice == "2":\n        return (True, num1 - num2)\n    elif choice == "3":\n        return (True, num1 * num2)\n    elif choice == "4":\n        if num2 == 0:\n            return (False, "Error: Division by zero")\n        return (True, num1 / num2)\n\n# Test\nprint(safe_calculate("1", "10", "5"))\nprint(safe_calculate("5", "10", "5"))\nprint(safe_calculate("1", "abc", "5"))\nprint(safe_calculate("4", "10", "0"))', validation_code='assert safe_calculate("1", "10", "5") == (True, 15.0)\nassert safe_calculate("2", "10", "5") == (True, 5.0)\nassert safe_calculate("3", "10", "5") == (True, 50.0)\nassert safe_calculate("4", "10", "5") == (True, 2.0)\nassert safe_calculate("4", "10", "0")[0] is False\nassert "Division by zero" in safe_calculate("4", "10", "0")[1]\nassert safe_calculate("5", "10", "5")[0] is False\nassert "Invalid choice" in safe_calculate("5", "10", "5")[1]\nassert safe_calculate("1", "abc", "5")[0] is False\nassert "Invalid input" in safe_calculate("1", "abc", "5")[1]\nprint("Error handling correct!")')
    db.add(task4)
    await db.flush()

    task4_translations = [
        ProjectTaskTranslation(task_id=task4.id, language=LanguageEnum.en, title="Add Input Validation", description="Handle invalid menu choices and non-numeric input gracefully", hint="Use try-except blocks for ValueError and check if choice is in valid options"),
        ProjectTaskTranslation(task_id=task4.id, language=LanguageEnum.fr, title="Ajouter la Validation des Entrées", description="Gérez les choix de menu invalides et les entrées non numériques avec élégance", hint="Utilisez des blocs try-except pour ValueError et vérifiez si le choix est dans les options valides"),
        ProjectTaskTranslation(task_id=task4.id, language=LanguageEnum.ar, title="إضافة التحقق من المدخلات", description="تعامل مع اختيارات القائمة غير الصالحة والمدخلات غير الرقمية بأسلوب أنيق", hint="استخدم كتل try-except لـ ValueError وتحقق مما إذا كان الاختيار في الخيارات الصالحة"),
    ]
    db.add_all(task4_translations)

    # Project 2: Quiz Game (prerequisite: Lesson 17 - Data Structures Real Problems)
    project2 = Project(slug="quiz-game", order=2, difficulty=DifficultyEnum.beginner, xp_reward=250, prerequisite_lesson_id=17)
    db.add(project2)
    await db.flush()

    project2_translations = [
        ProjectTranslation(project_id=project2.id, language=LanguageEnum.en, title="Build a Quiz Game", story="Create an interactive quiz game with multiple choice questions", objective="Build a quiz game that tracks score", skills="Lists, Loops, Functions, Data Structures"),
        ProjectTranslation(project_id=project2.id, language=LanguageEnum.fr, title="Créer un Jeu de Quiz", story="Créez un jeu de quiz interactif avec des questions à choix multiples", objective="Construire un jeu de quiz qui suit le score", skills="Listes, Boucles, Fonctions, Structures de Données"),
        ProjectTranslation(project_id=project2.id, language=LanguageEnum.ar, title="بناء لعبة اختبار", story="أنشئ لعبة اختبار تفاعلية مع أسئلة متعددة الخيارات", objective="بناء لعبة اختبار تتبع النقاط", skills="قوائم، حلقات، دوال، هياكل البيانات"),
    ]
    db.add_all(project2_translations)

    # Task 1: Create Quiz Data Structure
    task2_1 = ProjectTask(project_id=project2.id, order=1, starter_code='questions = [\n    {\n        "question": "What is the capital of Morocco?",\n        "options": ["Casablanca", "Rabat", "Marrakech", "Fes"],\n        "answer": 1\n    },\n    {\n        "question": "Which language is this course taught in?",\n        "options": ["JavaScript", "Python", "Java", "C++"],\n        "answer": 1\n    },\n]\n\ndef run_quiz(questions):\n    score = 0\n    for q in questions:\n        print(q["question"])\n        for i, opt in enumerate(q["options"]):\n            print(f"{i}: {opt}")\n        # Get user answer\n        # Check if correct\n        # Update score\n    print(f"Final score: {score}/{len(questions)}")\n\nrun_quiz(questions)', validation_code='assert len(questions) == 2\nassert questions[0]["answer"] == 1\nassert questions[1]["answer"] == 1\nprint("Quiz structure valid!")')
    db.add(task2_1)
    await db.flush()

    task2_1_translations = [
        ProjectTaskTranslation(task_id=task2_1.id, language=LanguageEnum.en, title="Create Quiz Data Structure", description="Define questions with options and correct answers", hint="Use a list of dictionaries with question, options, and answer keys"),
        ProjectTaskTranslation(task_id=task2_1.id, language=LanguageEnum.fr, title="Créer la Structure de Données du Quiz", description="Définissez les questions avec options et réponses correctes", hint="Utilisez une liste de dictionnaires avec les clés question, options, et answer"),
        ProjectTaskTranslation(task_id=task2_1.id, language=LanguageEnum.ar, title="إنشاء هيكل بيانات الاختبار", description="حدد الأسئلة مع الخيارات والإجابات الصحيحة", hint="استخدم قائمة من القواميس مع مفاتيح question، options، و answer"),
    ]
    db.add_all(task2_1_translations)

    # Task 2: Implement Quiz Logic
    task2_2 = ProjectTask(project_id=project2.id, order=2, starter_code='def run_quiz(questions, user_answers):\n    """Run quiz with provided answers.\n    questions: list of question dicts\n    user_answers: list of answer indices (int)\n    Returns (score, total) tuple\n    """\n    score = 0\n    for i, q in enumerate(questions):\n        if i < len(user_answers):\n            if user_answers[i] == q["answer"]:\n                score += 1\n    return (score, len(questions))\n\n# Test with sample questions\nquestions = [\n    {"question": "Test?", "options": ["A", "B"], "answer": 0},\n    {"question": "Test2?", "options": ["C", "D"], "answer": 1},\n]\nprint(run_quiz(questions, [0, 1]))  # Both correct\nprint(run_quiz(questions, [1, 0]))  # Both wrong', validation_code='questions = [\n    {"question": "Test?", "options": ["A", "B"], "answer": 0},\n    {"question": "Test2?", "options": ["C", "D"], "answer": 1},\n]\nassert run_quiz(questions, [0, 1]) == (2, 2)\nassert run_quiz(questions, [1, 0]) == (0, 2)\nassert run_quiz(questions, [0]) == (1, 2)  # Only one answer provided\nassert run_quiz([], []) == (0, 0)\nprint("Quiz logic correct!")')
    db.add(task2_2)
    await db.flush()

    task2_2_translations = [
        ProjectTaskTranslation(task_id=task2_2.id, language=LanguageEnum.en, title="Implement Quiz Logic", description="Handle user input, validate answers, and track score", hint="Use input() and int() for user choice, compare with correct answer"),
        ProjectTaskTranslation(task_id=task2_2.id, language=LanguageEnum.fr, title="Implémenter la Logique du Quiz", description="Gérez l'entrée utilisateur, validez les réponses, suivez le score", hint="Utilisez input() et int() pour le choix, comparez avec la bonne réponse"),
        ProjectTaskTranslation(task_id=task2_2.id, language=LanguageEnum.ar, title="تنفيذ منطق الاختبار", description="معالجة إدخال المستخدم، التحقق من الإجابات، تتبع النقاط", hint="استخدم input() و int() لاختيار المستخدم، قارن مع الإجابة الصحيحة"),
    ]
    db.add_all(task2_2_translations)

    # Task 3: Add Multiple Questions and Categories
    task2_3 = ProjectTask(project_id=project2.id, order=3, starter_code='questions = [\n    {"category": "Geography", "question": "What is the capital of Morocco?", "options": ["Casablanca", "Rabat", "Marrakech", "Fes"], "answer": 1},\n    {"category": "Programming", "question": "Which language is this course taught in?", "options": ["JavaScript", "Python", "Java", "C++"], "answer": 1},\n    {"category": "Geography", "question": "What is the largest ocean?", "options": ["Atlantic", "Indian", "Pacific", "Arctic"], "answer": 2},\n    {"category": "Programming", "question": "What does HTML stand for?", "options": ["Hyper Text Markup Language", "High Tech Modern Language", "Hyper Transfer Markup Language", "Home Tool Markup Language"], "answer": 0},\n]\n\ndef run_quiz(questions):\n    score = 0\n    # TODO: Group questions by category, let user choose category\n    # Then run quiz for selected category\n    print(f"Final score: {score}/{len(questions)}")\n\nrun_quiz(questions)', validation_code='assert len(questions) == 4\ncategories = set(q["category"] for q in questions)\nassert "Geography" in categories\nassert "Programming" in categories\nprint("Categories implemented!")')
    db.add(task2_3)
    await db.flush()

    task2_3_translations = [
        ProjectTaskTranslation(task_id=task2_3.id, language=LanguageEnum.en, title="Add Categories and Question Selection", description="Group questions by category and let the user choose which category to play", hint="Use a dictionary to group questions by category, then let user pick one"),
        ProjectTaskTranslation(task_id=task2_3.id, language=LanguageEnum.fr, title="Ajouter des Catégories et Sélection de Questions", description="Regroupez les questions par catégorie et laissez l'utilisateur choisir celle à jouer", hint="Utilisez un dictionnaire pour regrouper les questions par catégorie, puis laissez l'utilisateur choisir"),
        ProjectTaskTranslation(task_id=task2_3.id, language=LanguageEnum.ar, title="إضافة فئات واختيار الأسئلة", description="اجمع الأسئلة حسب الفئة ودع المستخدم يختار الفئة التي يريد لعبها", hint="استخدم قاموساً لتجميع الأسئلة حسب الفئة، ثم دع المستخدم يختار"),
    ]
    db.add_all(task2_3_translations)

    # Task 4: Add Score Persistence and High Scores
    task2_4 = ProjectTask(project_id=project2.id, order=4, starter_code='# High score system using in-memory storage (dict)\nhigh_scores = {}\n\ndef save_score(player_name, score, total):\n    """Save a player score. Returns updated high scores list."""\n    if player_name not in high_scores:\n        high_scores[player_name] = []\n    high_scores[player_name].append({"score": score, "total": total})\n    return get_top_scores()\n\ndef get_top_scores(limit=5):\n    """Get top scores across all players."""\n    all_scores = []\n    for player, scores in high_scores.items():\n        for s in scores:\n            all_scores.append({"player": player, "score": s["score"], "total": s["total"]})\n    all_scores.sort(key=lambda x: x["score"], reverse=True)\n    return all_scores[:limit]\n\n# Test\nsave_score("Alice", 5, 5)\nsave_score("Bob", 3, 5)\nsave_score("Alice", 4, 5)\nprint(get_top_scores())', validation_code='save_score("Alice", 5, 5)\nsave_score("Bob", 3, 5)\nsave_score("Charlie", 4, 5)\nsave_score("Alice", 2, 5)\ntop = get_top_scores(3)\nassert len(top) == 3\nassert top[0]["player"] == "Alice" and top[0]["score"] == 5\nassert top[1]["player"] == "Charlie" and top[1]["score"] == 4\nassert top[2]["player"] == "Bob" and top[2]["score"] == 3\n# Test limit\ntop5 = get_top_scores(2)\nassert len(top5) == 2\nprint("High score system correct!")')
    db.add(task2_4)
    await db.flush()

    task2_4_translations = [
        ProjectTaskTranslation(task_id=task2_4.id, language=LanguageEnum.en, title="Add High Score System", description="Save player scores to a JSON file and display top scores", hint="Use json module to read/write high_scores.json file"),
        ProjectTaskTranslation(task_id=task2_4.id, language=LanguageEnum.fr, title="Ajouter un Système de Meilleurs Scores", description="Sauvegardez les scores des joueurs dans un fichier JSON et affichez les meilleurs scores", hint="Utilisez le module json pour lire/écrire le fichier high_scores.json"),
        ProjectTaskTranslation(task_id=task2_4.id, language=LanguageEnum.ar, title="إضافة نظام أعلى الدرجات", description="احفظ درجات اللاعبين في ملف JSON واعرض أعلى الدرجات", hint="استخدم وحدة json لقراءة/كتابة ملف high_scores.json"),
    ]
    db.add_all(task2_4_translations)

    # Project 3: Personal Portfolio Website (prerequisite: Lesson 25 - Responsive Design)
    project3 = Project(slug="personal-portfolio", order=3, difficulty=DifficultyEnum.intermediate, xp_reward=300, prerequisite_lesson_id=25)
    db.add(project3)
    await db.flush()

    project3_translations = [
        ProjectTranslation(project_id=project3.id, language=LanguageEnum.en, title="Personal Portfolio Website", story="Build your own portfolio website with HTML and CSS", objective="Create a responsive personal website", skills="HTML, CSS, Flexbox, Responsive Design"),
        ProjectTranslation(project_id=project3.id, language=LanguageEnum.fr, title="Site Portfolio Personnel", story="Créez votre propre site portfolio avec HTML et CSS", objective="Créer un site personnel responsive", skills="HTML, CSS, Flexbox, Design Responsive"),
        ProjectTranslation(project_id=project3.id, language=LanguageEnum.ar, title="موقع Portfolio شخصي", story="ابنِ موقع portfolio الخاص بك مع HTML و CSS", objective="إنشاء موقع شخصي متجاوب", skills="HTML، CSS، Flexbox، تصميم متجاوب"),
    ]
    db.add_all(project3_translations)

    # Task 1: Create HTML Structure
    task3_1 = ProjectTask(project_id=project3.id, order=1, starter_code='<!-- Write your HTML here -->\n<!DOCTYPE html>\n<html>\n<head>\n    <title>My Portfolio</title>\n</head>\n<body>\n    <header>\n        <h1>Your Name</h1>\n        <p>Web Developer</p>\n    </header>\n    <main>\n        <section id="about">\n            <h2>About Me</h2>\n            <p>Write about yourself here.</p>\n        </section>\n        <section id="projects">\n            <h2>Projects</h2>\n        </section>\n        <section id="contact">\n            <h2>Contact</h2>\n        </section>\n    </main>\n    <footer>\n        <p>&copy; 2025 Your Name</p>\n    </footer>\n</body>\n</html>', validation_code='code = """<!DOCTYPE html>\n<html>\n<head>\n    <title>My Portfolio</title>\n</head>\n<body>\n    <header>\n        <h1>Your Name</h1>\n        <p>Web Developer</p>\n    </header>\n    <main>\n        <section id="about">\n            <h2>About Me</h2>\n            <p>Write about yourself here.</p>\n        </section>\n        <section id="projects">\n            <h2>Projects</h2>\n        </section>\n        <section id="contact">\n            <h2>Contact</h2>\n        </section>\n    </main>\n    <footer>\n        <p>&copy; 2025 Your Name</p>\n    </footer>\n</body>\n</html>"""\n# Check for required elements\nrequired = ["<!DOCTYPE html>", "<html>", "<head>", "<title>", "</title>", "</head>", "<body>", "<header>", "<h1>", "</h1>", "<main>", "<section id=\"about\">", "<section id=\"projects\">", "<section id=\"contact\">", "<footer>"]\nfor req in required:\n    assert req in code, f"Missing: {req}"\nprint("HTML structure valid!")')
    db.add(task3_1)
    await db.flush()

    task3_1_translations = [
        ProjectTaskTranslation(task_id=task3_1.id, language=LanguageEnum.en, title="Create HTML Structure", description="Build semantic HTML for your portfolio", hint="Use header, main, section, footer"),
        ProjectTaskTranslation(task_id=task3_1.id, language=LanguageEnum.fr, title="Créer la Structure HTML", description="Construisez du HTML sémantique pour votre portfolio", hint="Utilisez header, main, section, footer"),
        ProjectTaskTranslation(task_id=task3_1.id, language=LanguageEnum.ar, title="إنشاء هيكل HTML", description="ابنِ HTML دلالي لـ portfolio الخاص بك", hint="استخدم header، main، section، footer"),
    ]
    db.add_all(task3_1_translations)

    # Task 2: Style with CSS - Basic Layout
    task3_2 = ProjectTask(project_id=project3.id, order=2, starter_code='/* Write your CSS here */\n* {\n    box-sizing: border-box;\n    margin: 0;\n    padding: 0;\n}\n\nbody {\n    font-family: Arial, sans-serif;\n    line-height: 1.6;\n}\n\nheader {\n    background: #2c3e50;\n    color: white;\n    padding: 2rem;\n    text-align: center;\n}\n\nmain {\n    max-width: 800px;\n    margin: 2rem auto;\n    padding: 0 1rem;\n}\n\nsection {\n    margin-bottom: 2rem;\n}\n\nfooter {\n    background: #2c3e50;\n    color: white;\n    text-align: center;\n    padding: 1rem;\n}\n\n@media (max-width: 600px) {\n    header {\n        padding: 1rem;\n    }\n}', validation_code='code = """* {\n    box-sizing: border-box;\n    margin: 0;\n    padding: 0;\n}\n\nbody {\n    font-family: Arial, sans-serif;\n    line-height: 1.6;\n}\n\nheader {\n    background: #2c3e50;\n    color: white;\n    padding: 2rem;\n    text-align: center;\n}\n\nmain {\n    max-width: 800px;\n    margin: 2rem auto;\n    padding: 0 1rem;\n}\n\nsection {\n    margin-bottom: 2rem;\n}\n\nfooter {\n    background: #2c3e50;\n    color: white;\n    text-align: center;\n    padding: 1rem;\n}\n\n@media (max-width: 600px) {\n    header {\n        padding: 1rem;\n    }\n}"""\n# Check for required CSS properties\nrequired = ["box-sizing", "margin: 0", "padding: 0", "font-family", "line-height", "header", "background:", "color: white", "padding:", "text-align: center", "max-width:", "margin:", "auto", "section", "margin-bottom:", "footer", "@media", "max-width: 600px"]\nfor req in required:\n    assert req in code, f"Missing CSS: {req}"\nprint("CSS structure valid!")')
    db.add(task3_2)
    await db.flush()

    task3_2_translations = [
        ProjectTaskTranslation(task_id=task3_2.id, language=LanguageEnum.en, title="Style with CSS - Basic Layout", description="Add basic styling with colors, typography, and layout", hint="Style header, main, sections, and footer. Use a max-width container"),
        ProjectTaskTranslation(task_id=task3_2.id, language=LanguageEnum.fr, title="Styliser avec CSS - Mise en Page de Base", description="Ajoutez un style de base avec couleurs, typographie et mise en page", hint="Stylisez header, main, sections, et footer. Utilisez un conteneur max-width"),
        ProjectTaskTranslation(task_id=task3_2.id, language=LanguageEnum.ar, title="تصميم بـ CSS - تخطيط أساسي", description="أضف تنسيقاً أساسياً مع الألوان والطباعة والتخطيط", hint="صمم header، main، sections، و footer. استخدم حاوية max-width"),
    ]
    db.add_all(task3_2_translations)

    # Task 3: Add Project Cards with Flexbox
    task3_3 = ProjectTask(project_id=project3.id, order=3, starter_code='/* Add to your existing style.css */\n\n.project-grid {\n    display: flex;\n    flex-wrap: wrap;\n    gap: 1.5rem;\n    margin-top: 1rem;\n}\n\n.project-card {\n    flex: 1 1 300px;\n    border: 1px solid #ddd;\n    border-radius: 8px;\n    padding: 1.5rem;\n    background: white;\n    box-shadow: 0 2px 4px rgba(0,0,0,0.1);\n    transition: transform 0.2s;\n}\n\n.project-card:hover {\n    transform: translateY(-4px);\n    box-shadow: 0 4px 12px rgba(0,0,0,0.15);\n}\n\n.project-card h3 {\n    color: #2c3e50;\n    margin-bottom: 0.5rem;\n}\n\n.project-card .tech-stack {\n    font-size: 0.85rem;\n    color: #666;\n    margin-bottom: 1rem;\n}\n\n.project-card a {\n    display: inline-block;\n    padding: 0.5rem 1rem;\n    background: #2c3e50;\n    color: white;\n    text-decoration: none;\n    border-radius: 4px;\n    font-size: 0.9rem;\n}\n\n.project-card a:hover {\n    background: #1a252f;\n}', validation_code='code = """\n.project-grid {\n    display: flex;\n    flex-wrap: wrap;\n    gap: 1.5rem;\n    margin-top: 1rem;\n}\n\n.project-card {\n    flex: 1 1 300px;\n    border: 1px solid #ddd;\n    border-radius: 8px;\n    padding: 1.5rem;\n    background: white;\n    box-shadow: 0 2px 4px rgba(0,0,0,0.1);\n    transition: transform 0.2s;\n}\n\n.project-card:hover {\n    transform: translateY(-4px);\n    box-shadow: 0 4px 12px rgba(0,0,0,0.15);\n}\n\n.project-card h3 {\n    color: #2c3e50;\n    margin-bottom: 0.5rem;\n}\n\n.project-card .tech-stack {\n    font-size: 0.85rem;\n    color: #666;\n    margin-bottom: 1rem;\n}\n\n.project-card a {\n    display: inline-block;\n    padding: 0.5rem 1rem;\n    background: #2c3e50;\n    color: white;\n    text-decoration: none;\n    border-radius: 4px;\n    font-size: 0.9rem;\n}\n\n.project-card a:hover {\n    background: #1a252f;\n}"""\nrequired = ["display: flex", "flex-wrap: wrap", "gap:", "flex: 1 1 300px", "border:", "border-radius:", "padding:", "box-shadow:", "transition:", ":hover", "transform:", ".project-card h3", ".tech-stack", ".project-card a", "text-decoration: none", "border-radius:"]\nfor req in required:\n    assert req in code, f"Missing CSS: {req}"\nprint("Flexbox project cards valid!")')
    db.add(task3_3)
    await db.flush()

    task3_3_translations = [
        ProjectTaskTranslation(task_id=task3_3.id, language=LanguageEnum.en, title="Add Project Cards with Flexbox", description="Create responsive project cards using Flexbox grid", hint="Use flex-wrap and flex-basis for responsive cards. Add hover effects"),
        ProjectTaskTranslation(task_id=task3_3.id, language=LanguageEnum.fr, title="Ajouter des Cartes Projet avec Flexbox", description="Créez des cartes projet responsives avec une grille Flexbox", hint="Utilisez flex-wrap et flex-basis pour des cartes responsives. Ajoutez des effets au survol"),
        ProjectTaskTranslation(task_id=task3_3.id, language=LanguageEnum.ar, title="إضافة بطاقات المشاريع مع Flexbox", description="أنشئ بطاقات مشاريع متجاوبة باستخدام شبكة Flexbox", hint="استخدم flex-wrap و flex-basis لبطاقات متجاوبة. أضف تأثيرات التحويم"),
    ]
    db.add_all(task3_3_translations)

    # Task 4: Add Navigation Bar and Smooth Scrolling
    task3_4 = ProjectTask(project_id=project3.id, order=4, starter_code='/* Add to your existing style.css */\n\nnav {\n    position: fixed;\n    top: 0;\n    width: 100%;\n    background: rgba(44, 62, 80, 0.95);\n    padding: 1rem 2rem;\n    z-index: 1000;\n    display: flex;\n    justify-content: space-between;\n    align-items: center;\n}\n\nnav ul {\n    display: flex;\n    list-style: none;\n    gap: 2rem;\n}\n\nnav a {\n    color: white;\n    text-decoration: none;\n    font-weight: 500;\n    transition: color 0.2s;\n}\n\nnav a:hover {\n    color: #3498db;\n}\n\nbody {\n    padding-top: 60px;\n}\n\nhtml {\n    scroll-behavior: smooth;\n}\n\n@media (max-width: 600px) {\n    nav {\n        padding: 1rem;\n    }\n    nav ul {\n        gap: 1rem;\n    }\n}', validation_code='code = """\nnav {\n    position: fixed;\n    top: 0;\n    width: 100%;\n    background: rgba(44, 62, 80, 0.95);\n    padding: 1rem 2rem;\n    z-index: 1000;\n    display: flex;\n    justify-content: space-between;\n    align-items: center;\n}\n\nnav ul {\n    display: flex;\n    list-style: none;\n    gap: 2rem;\n}\n\nnav a {\n    color: white;\n    text-decoration: none;\n    font-weight: 500;\n    transition: color 0.2s;\n}\n\nnav a:hover {\n    color: #3498db;\n}\n\nbody {\n    padding-top: 60px;\n}\n\nhtml {\n    scroll-behavior: smooth;\n}\n\n@media (max-width: 600px) {\n    nav {\n        padding: 1rem;\n    }\n    nav ul {\n        gap: 1rem;\n    }\n}"""\nrequired = ["position: fixed", "top: 0", "width: 100%", "background:", "z-index:", "display: flex", "justify-content:", "align-items:", "nav ul", "display: flex", "list-style: none", "gap:", "nav a", "color: white", "text-decoration: none", ":hover", "padding-top: 60px", "scroll-behavior: smooth", "@media", "max-width: 600px"]\nfor req in required:\n    assert req in code, f"Missing CSS: {req}"\nprint("Navigation CSS valid!")')
    db.add(task3_4)
    await db.flush()

    task3_4_translations = [
        ProjectTaskTranslation(task_id=task3_4.id, language=LanguageEnum.en, title="Add Navigation Bar and Smooth Scrolling", description="Create a fixed navigation bar with smooth scroll to sections", hint="Use position: fixed for nav, add scroll-behavior: smooth to html"),
        ProjectTaskTranslation(task_id=task3_4.id, language=LanguageEnum.fr, title="Ajouter une Barre de Navigation et Défilement Fluide", description="Créez une barre de navigation fixe avec défilement fluide vers les sections", hint="Utilisez position: fixed pour la nav, ajoutez scroll-behavior: smooth à html"),
        ProjectTaskTranslation(task_id=task3_4.id, language=LanguageEnum.ar, title="إضافة شريط تنقل وتمرير سلس", description="أنشئ شريط تنقل ثابت مع تمرير سلس للأقسام", hint="استخدم position: fixed للشريط، أضف scroll-behavior: smooth لـ html"),
    ]
    db.add_all(task3_4_translations)

    # Task 5: Add Contact Form with Formspree/Backend Integration Prep
    task3_5 = ProjectTask(project_id=project3.id, order=5, starter_code='<!-- Add to your contact section in index.html -->\n<form id="contact-form" action="https://formspree.io/f/your-form-id" method="POST">\n    <div class="form-group">\n        <label for="name">Name</label>\n        <input type="text" id="name" name="name" required>\n    </div>\n    <div class="form-group">\n        <label for="email">Email</label>\n        <input type="email" id="email" name="email" required>\n    </div>\n    <div class="form-group">\n        <label for="message">Message</label>\n        <textarea id="message" name="message" rows="5" required></textarea>\n    </div>\n    <button type="submit">Send Message</button>\n</form>\n\n/* Add to style.css */\n.form-group {\n    margin-bottom: 1rem;\n}\n.form-group label {\n    display: block;\n    margin-bottom: 0.5rem;\n    font-weight: 500;\n}\n.form-group input,\n.form-group textarea {\n    width: 100%;\n    padding: 0.75rem;\n    border: 1px solid #ddd;\n    border-radius: 4px;\n    font-family: inherit;\n}\n.form-group input:focus,\n.form-group textarea:focus {\n    outline: none;\n    border-color: #3498db;\n    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);\n}\nbutton[type="submit"] {\n    background: #2c3e50;\n    color: white;\n    padding: 0.75rem 2rem;\n    border: none;\n    border-radius: 4px;\n    cursor: pointer;\n    font-size: 1rem;\n}\nbutton[type="submit"]:hover {\n    background: #1a252f;\n}', validation_code='code = """<form id=\"contact-form\" action=\"https://formspree.io/f/your-form-id\" method=\"POST\">\n    <div class=\"form-group\">\n        <label for=\"name\">Name</label>\n        <input type=\"text\" id=\"name\" name=\"name\" required>\n    </div>\n    <div class=\"form-group\">\n        <label for=\"email\">Email</label>\n        <input type=\"email\" id=\"email\" name=\"email\" required>\n    </div>\n    <div class=\"form-group\">\n        <label for=\"message\">Message</label>\n        <textarea id=\"message\" name=\"message\" rows=\"5\" required></textarea>\n    </div>\n    <button type=\"submit\">Send Message</button>\n</form>\n\n.form-group {\n    margin-bottom: 1rem;\n}\n.form-group label {\n    display: block;\n    margin-bottom: 0.5rem;\n    font-weight: 500;\n}\n.form-group input,\n.form-group textarea {\n    width: 100%;\n    padding: 0.75rem;\n    border: 1px solid #ddd;\n    border-radius: 4px;\n    font-family: inherit;\n}\n.form-group input:focus,\n.form-group textarea:focus {\n    outline: none;\n    border-color: #3498db;\n    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);\n}\nbutton[type=\"submit\"] {\n    background: #2c3e50;\n    color: white;\n    padding: 0.75rem 2rem;\n    border: none;\n    border-radius: 4px;\n    cursor: pointer;\n    font-size: 1rem;\n}\nbutton[type=\"submit\"]:hover {\n    background: #1a252f;\n}"""\nrequired = ["<form", "id=\"contact-form\"", "method=\"POST\"", "<label for=\"name\">", "id=\"name\"", "name=\"name\"", "required", "<label for=\"email\">", "type=\"email\"", "id=\"email\"", "<label for=\"message\">", "<textarea", "rows=\"5\"", "<button type=\"submit\">", ".form-group", "display: block", "width: 100%", "padding:", "border:", "border-radius:", ":focus", "outline: none", "box-shadow:", "button[type=\\\"submit\\\"]", "background:", "cursor: pointer", ":hover"]\nfor req in required:\n    assert req in code, f"Missing: {req}"\nprint("Contact form valid!")')
    db.add(task3_5)
    await db.flush()

    task3_5_translations = [
        ProjectTaskTranslation(task_id=task3_5.id, language=LanguageEnum.en, title="Add Contact Form", description="Create a functional contact form with validation", hint="Use Formspree or similar service for form handling. Add client-side validation"),
        ProjectTaskTranslation(task_id=task3_5.id, language=LanguageEnum.fr, title="Ajouter un Formulaire de Contact", description="Créez un formulaire de contact fonctionnel avec validation", hint="Utilisez Formspree ou service similaire pour le traitement. Ajoutez validation côté client"),
        ProjectTaskTranslation(task_id=task3_5.id, language=LanguageEnum.ar, title="إضافة نموذج اتصال", description="أنشئ نموذج اتصال وظيفي مع التحقق من الصحة", hint="استخدم Formspree أو خدمة مماثلة للمعالجة. أضف التحقق من جانب العميل"),
    ]
    db.add_all(task3_5_translations)

    # Project 4: Student Database (prerequisite: Lesson 30 - Joins Relational Thinking)
    project4 = Project(slug="student-database", order=4, difficulty=DifficultyEnum.intermediate, xp_reward=300, prerequisite_lesson_id=30)
    db.add(project4)
    await db.flush()

    project4_translations = [
        ProjectTranslation(project_id=project4.id, language=LanguageEnum.en, title="Student Database", story="Build a SQLite database application to manage student records", objective="Create a CRUD application with SQLite", skills="SQL, SQLite, Python, CRUD Operations"),
        ProjectTranslation(project_id=project4.id, language=LanguageEnum.fr, title="Base de Données Étudiants", story="Créez une application SQLite pour gérer les dossiers étudiants", objective="Créer une application CRUD avec SQLite", skills="SQL, SQLite, Python, Opérations CRUD"),
        ProjectTranslation(project_id=project4.id, language=LanguageEnum.ar, title="قاعدة بيانات الطلاب", story="ابنِ تطبيق SQLite لإدارة سجلات الطلاب", objective="إنشاء تطبيق CRUD مع SQLite", skills="SQL، SQLite، Python، عمليات CRUD"),
    ]
    db.add_all(project4_translations)

    # Task 1: Create Database and Table
    task4_1 = ProjectTask(project_id=project4.id, order=1, starter_code='# SQLite table creation SQL\nCREATE_TABLE_SQL = """\n    CREATE TABLE IF NOT EXISTS students (\n        id INTEGER PRIMARY KEY AUTOINCREMENT,\n        name TEXT NOT NULL,\n        email TEXT UNIQUE,\n        age INTEGER,\n        city TEXT\n    )\n"""\n\nprint("Table SQL defined!")', validation_code='assert "CREATE TABLE" in CREATE_TABLE_SQL\nassert "students" in CREATE_TABLE_SQL\nassert "id INTEGER PRIMARY KEY" in CREATE_TABLE_SQL\nassert "name TEXT NOT NULL" in CREATE_TABLE_SQL\nassert "email TEXT UNIQUE" in CREATE_TABLE_SQL\nassert "age INTEGER" in CREATE_TABLE_SQL\nassert "city TEXT" in CREATE_TABLE_SQL\nprint("Table creation SQL valid!")')
    db.add(task4_1)
    await db.flush()

    task4_1_translations = [
        ProjectTaskTranslation(task_id=task4_1.id, language=LanguageEnum.en, title="Create Database and Table", description="Set up SQLite database with students table", hint="Use CREATE TABLE with appropriate columns"),
        ProjectTaskTranslation(task_id=task4_1.id, language=LanguageEnum.fr, title="Créer la Base et la Table", description="Configurez la base SQLite avec table students", hint="Utilisez CREATE TABLE avec colonnes appropriées"),
        ProjectTaskTranslation(task_id=task4_1.id, language=LanguageEnum.ar, title="إنشاء القاعدة والجدول", description="قم بإعداد قاعدة SQLite مع جدول students", hint="استخدم CREATE TABLE بأعمدة مناسبة"),
    ]
    db.add_all(task4_1_translations)

    # Task 2: Implement CRUD Operations
    task4_2 = ProjectTask(project_id=project4.id, order=2, starter_code='# In-memory mock database\nstudents_db = []\nnext_id = 1\n\ndef add_student(name, email, age, city):\n    """Add a student. Returns the new student dict with ID."""\n    global next_id\n    # TODO: Implement\n    pass\n\ndef get_all_students():\n    """Return all students."""\n    # TODO: Implement\n    pass\n\ndef update_student(student_id, **kwargs):\n    """Update a student. Returns updated student or None if not found."""\n    # TODO: Implement\n    pass\n\ndef delete_student(student_id):\n    """Delete a student. Returns True if deleted, False if not found."""\n    # TODO: Implement\n    pass\n\n# Test (will work after implementation)\n# add_student("Amine", "amine@email.com", 20, "Casablanca")\n# print(get_all_students())', validation_code='global students_db, next_id\nstudents_db = []\nnext_id = 1\n\ndef add_student(name, email, age, city):\n    global next_id\n    student = {"id": next_id, "name": name, "email": email, "age": age, "city": city}\n    students_db.append(student)\n    next_id += 1\n    return student\n\ndef get_all_students():\n    return students_db[:]\n\ndef update_student(student_id, **kwargs):\n    for s in students_db:\n        if s["id"] == student_id:\n            s.update(kwargs)\n            return s\n    return None\n\ndef delete_student(student_id):\n    global students_db\n    for i, s in enumerate(students_db):\n        if s["id"] == student_id:\n            students_db.pop(i)\n            return True\n    return False\n\n# Run tests\ns1 = add_student("Amine", "amine@email.com", 20, "Casablanca")\nassert s1["id"] == 1\nassert s1["name"] == "Amine"\ns2 = add_student("Sara", "sara@email.com", 22, "Rabat")\nassert s2["id"] == 2\nassert len(get_all_students()) == 2\nupdated = update_student(1, age=21, city="Marrakech")\nassert updated["age"] == 21\nassert updated["city"] == "Marrakech"\ndeleted = delete_student(2)\nassert deleted is True\nassert len(get_all_students()) == 1\nassert get_all_students()[0]["name"] == "Amine"\nnot_found = delete_student(999)\nassert not_found is False\nprint("CRUD operations correct!")')
    db.add(task4_2)
    await db.flush()

    task4_2_translations = [
        ProjectTaskTranslation(task_id=task4_2.id, language=LanguageEnum.en, title="Implement CRUD Operations", description="Create functions for Create, Read, Update, Delete", hint="Use INSERT, SELECT, UPDATE, DELETE"),
        ProjectTaskTranslation(task_id=task4_2.id, language=LanguageEnum.fr, title="Implémenter les Opérations CRUD", description="Créez des fonctions pour Créer, Lire, Modifier, Supprimer", hint="Utilisez INSERT, SELECT, UPDATE, DELETE"),
        ProjectTaskTranslation(task_id=task4_2.id, language=LanguageEnum.ar, title="تنفيذ عمليات CRUD", description="أنشئ دوال لـ إنشاء، قراءة، تحديث، حذف", hint="استخدم INSERT، SELECT، UPDATE، DELETE"),
    ]
    db.add_all(task4_2_translations)

    # Task 3: Add Search and Filter Functionality
    task4_3 = ProjectTask(project_id=project4.id, order=3, starter_code='# In-memory mock database\nstudents_db = [\n    {"id": 1, "name": "Amine", "email": "amine@email.com", "age": 20, "city": "Casablanca"},\n    {"id": 2, "name": "Sara", "email": "sara@email.com", "age": 22, "city": "Rabat"},\n    {"id": 3, "name": "Omar", "email": "omar@email.com", "age": 19, "city": "Casablanca"},\n    {"id": 4, "name": "Leila", "email": "leila@email.com", "age": 25, "city": "Tangier"},\n]\n\ndef search_students(name=None, city=None, min_age=None, max_age=None):\n    """Search students with optional filters.\n    Returns list of matching students.\n    """\n    # TODO: Implement\n    pass\n\n# Test\nresults = search_students(city="Casablanca")\nfor r in results:\n    print(r)', validation_code='students_db = [\n    {"id": 1, "name": "Amine", "email": "amine@email.com", "age": 20, "city": "Casablanca"},\n    {"id": 2, "name": "Sara", "email": "sara@email.com", "age": 22, "city": "Rabat"},\n    {"id": 3, "name": "Omar", "email": "omar@email.com", "age": 19, "city": "Casablanca"},\n    {"id": 4, "name": "Leila", "email": "leila@email.com", "age": 25, "city": "Tangier"},\n]\n\ndef search_students(name=None, city=None, min_age=None, max_age=None):\n    results = []\n    for s in students_db:\n        if name and name.lower() not in s["name"].lower():\n            continue\n        if city and s["city"] != city:\n            continue\n        if min_age is not None and s["age"] < min_age:\n            continue\n        if max_age is not None and s["age"] > max_age:\n            continue\n        results.append(s)\n    return results\n\n# Test\nresults = search_students(city="Casablanca")\nassert len(results) == 2\nassert all(r["city"] == "Casablanca" for r in results)\nresults = search_students(min_age=21)\nassert len(results) == 2\nassert all(r["age"] >= 21 for r in results)\nresults = search_students(name="am")\nassert len(results) == 1\nassert results[0]["name"] == "Amine"\nresults = search_students(city="Casablanca", max_age=20)\nassert len(results) == 1\nassert results[0]["name"] == "Omar"\nprint("Search and filter correct!")')
    db.add(task4_3)
    await db.flush()

    task4_3_translations = [
        ProjectTaskTranslation(task_id=task4_3.id, language=LanguageEnum.en, title="Add Search and Filter", description="Implement flexible search by name, city, and age range", hint="Build dynamic WHERE clause with parameterized queries"),
        ProjectTaskTranslation(task_id=task4_3.id, language=LanguageEnum.fr, title="Ajouter Recherche et Filtres", description="Implémentez une recherche flexible par nom, ville et tranche d'âge", hint="Construisez une clause WHERE dynamique avec des requêtes paramétrées"),
        ProjectTaskTranslation(task_id=task4_3.id, language=LanguageEnum.ar, title="إضافة البحث والتصفية", description="نفذ بحثاً مرناً بالاسم، المدينة، والنطاق العمري", hint="ابنِ جملة WHERE ديناميكية مع استعلامات ذات معاملات"),
    ]
    db.add_all(task4_3_translations)

    # Task 4: Build Interactive Menu-Driven Application
    task4_4 = ProjectTask(project_id=project4.id, order=4, starter_code='import sqlite3\n\ndef main_menu():\n    while True:\n        print("\\n=== Student Database ===")\n        print("1. Add Student")\n        print("2. View All Students")\n        print("3. Search Students")\n        print("4. Update Student")\n        print("5. Delete Student")\n        print("6. Exit")\n        \n        choice = input("Enter choice (1-6): ")\n        \n        if choice == "1":\n            name = input("Name: ")\n            email = input("Email: ")\n            age = int(input("Age: "))\n            city = input("City: ")\n            add_student(name, email, age, city)\n            print("Student added!")\n        elif choice == "2":\n            for s in get_all_students():\n                print(f"ID: {s[0]}, Name: {s[1]}, Email: {s[2]}, Age: {s[3]}, City: {s[4]}")\n        elif choice == "3":\n            # TODO: Implement search menu\n            pass\n        elif choice == "4":\n            # TODO: Implement update\n            pass\n        elif choice == "5":\n            # TODO: Implement delete\n            pass\n        elif choice == "6":\n            print("Goodbye!")\n            break\n        else:\n            print("Invalid choice!")\n\n# Uncomment to run\n# main_menu()\nprint("Menu structure ready!")', validation_code='print("Menu-driven app structure implemented!")')
    db.add(task4_4)
    await db.flush()

    task4_4_translations = [
        ProjectTaskTranslation(task_id=task4_4.id, language=LanguageEnum.en, title="Build Interactive Menu Application", description="Create a complete menu-driven CLI application", hint="Implement all menu options using your CRUD and search functions"),
        ProjectTaskTranslation(task_id=task4_4.id, language=LanguageEnum.fr, title="Construire une Application Menu Interactive", description="Créez une application CLI complète pilotée par menu", hint="Implémentez toutes les options du menu en utilisant vos fonctions CRUD et recherche"),
        ProjectTaskTranslation(task_id=task4_4.id, language=LanguageEnum.ar, title="بناء تطبيق قائمة تفاعلي", description="أنشئ تطبيق سطر أوامر كامل مدفوع بالقائمة", hint="نفذ جميع خيارات القائمة باستخدام دوال CRUD والبحث خاصتك"),
    ]
    db.add_all(task4_4_translations)

    # Project 5: Algorithm Challenge (prerequisite: Lesson 39 - Sorting Algorithms)
    project5 = Project(slug="algorithm-challenge", order=5, difficulty=DifficultyEnum.advanced, xp_reward=400, prerequisite_lesson_id=39)
    db.add(project5)
    await db.flush()

    project5_translations = [
        ProjectTranslation(project_id=project5.id, language=LanguageEnum.en, title="Algorithm Challenge", story="Implement and analyze classic algorithms", objective="Implement sorting, searching, and graph algorithms", skills="Algorithms, Complexity Analysis, Recursion, Data Structures"),
        ProjectTranslation(project_id=project5.id, language=LanguageEnum.fr, title="Défi Algorithmique", story="Implémentez et analysez des algorithmes classiques", objective="Implémenter tris, recherche, algorithmes de graphes", skills="Algorithmes, Analyse Complexité, Récursivité, Structures de Données"),
        ProjectTranslation(project_id=project5.id, language=LanguageEnum.ar, title="تحدي خوارزمي", story="نفذ وحلل خوارزميات كلاسيكية", objective="تنفيذ ترتيب، بحث، وخوارزميات رسوم بيانية", skills="خوارزميات، تحليل تعقيد، تكرار، هياكل بيانات"),
    ]
    db.add_all(project5_translations)

    # Task 1: Implement Merge Sort
    task5_1 = ProjectTask(project_id=project5.id, order=1, starter_code='# Implement merge sort\ndef merge_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    mid = len(arr) // 2\n    left = merge_sort(arr[:mid])\n    right = merge_sort(arr[mid:])\n    return merge(left, right)\n\ndef merge(left, right):\n    result = []\n    i = j = 0\n    while i < len(left) and j < len(right):\n        if left[i] <= right[j]:\n            result.append(left[i])\n            i += 1\n        else:\n            result.append(right[j])\n            j += 1\n    result.extend(left[i:])\n    result.extend(right[j:])\n    return result\n\n# Test\nimport random\narr = [random.randint(1, 100) for _ in range(20)]\nprint("Original:", arr)\nprint("Sorted:", merge_sort(arr))', validation_code='assert merge_sort([3,1,4,1,5]) == [1,1,3,4,5]\nassert merge_sort([]) == []\nassert merge_sort([1]) == [1]\nprint("Merge sort correct!")')
    db.add(task5_1)
    await db.flush()

    task5_1_translations = [
        ProjectTaskTranslation(task_id=task5_1.id, language=LanguageEnum.en, title="Implement Merge Sort", description="Write a correct merge sort implementation", hint="Divide, conquer, merge"),
        ProjectTaskTranslation(task_id=task5_1.id, language=LanguageEnum.fr, title="Implémenter le Tri Fusion", description="Écrivez une implémentation correcte du tri fusion", hint="Diviser, conquérir, fusionner"),
        ProjectTaskTranslation(task_id=task5_1.id, language=LanguageEnum.ar, title="تنفيذ الترتيب بالدمج", description="اكتب تنفيذاً صحيحاً للترتيب بالدمج", hint="قسّم، غلب، ادمج"),
    ]
    db.add_all(task5_1_translations)

    # Task 2: Implement Binary Search Tree
    task5_2 = ProjectTask(project_id=project5.id, order=2, starter_code='# Implement binary search tree\nclass Node:\n    def __init__(self, value):\n        self.value = value\n        self.left = None\n        self.right = None\n\nclass BST:\n    def __init__(self):\n        self.root = None\n    \n    def insert(self, value):\n        if not self.root:\n            self.root = Node(value)\n        else:\n            self._insert(self.root, value)\n    \n    def _insert(self, node, value):\n        # TODO: Implement\n        pass\n    \n    def search(self, value):\n        # TODO: Implement\n        pass\n    \n    def inorder(self):\n        # TODO: Implement\n        pass\n\n# Test\nbst = BST()\nfor v in [50, 30, 70, 20, 40, 60, 80]:\n    bst.insert(v)\n\nprint("Inorder:", bst.inorder())\nprint("Search 40:", bst.search(40))\nprint("Search 25:", bst.search(25))', validation_code='print("BST structure defined!")')
    db.add(task5_2)
    await db.flush()

    task5_2_translations = [
        ProjectTaskTranslation(task_id=task5_2.id, language=LanguageEnum.en, title="Implement Binary Search Tree", description="Create BST with insert, search, and inorder traversal", hint="Recursive insertion and traversal"),
        ProjectTaskTranslation(task_id=task5_2.id, language=LanguageEnum.fr, title="Implémenter l'Arbre Binaire de Recherche", description="Créez un ABR avec insertion, recherche, parcours inorder", hint="Insertion et parcours récursifs"),
        ProjectTaskTranslation(task_id=task5_2.id, language=LanguageEnum.ar, title="تنفيذ شجرة البحث الثنائية", description="أنشئ ABR مع إدراج، بحث، ومرور inorder", hint="إدراج ومرور تكراريان"),
    ]
    db.add_all(task5_2_translations)

    # Task 3: Implement Quick Sort with Complexity Analysis
    task5_3 = ProjectTask(project_id=project5.id, order=3, starter_code='# Implement Quick Sort\ndef quick_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quick_sort(left) + middle + quick_sort(right)\n\n# Test and compare with merge sort\nimport random\nimport time\n\narr = [random.randint(1, 1000) for _ in range(100)]\n\nstart = time.time()\nmerge_result = merge_sort(arr.copy())\nmerge_time = time.time() - start\n\nstart = time.time()\nquick_result = quick_sort(arr.copy())\nquick_time = time.time() - start\n\nprint(f"Merge Sort: {merge_time:.4f}s")\nprint(f"Quick Sort: {quick_time:.4f}s")\nprint(f"Results match: {merge_result == quick_result}")', validation_code='assert quick_sort([3,1,4,1,5]) == [1,1,3,4,5]\nassert quick_sort([]) == []\nassert quick_sort([1]) == [1]\nprint("Quick sort correct!")')
    db.add(task5_3)
    await db.flush()

    task5_3_translations = [
        ProjectTaskTranslation(task_id=task5_3.id, language=LanguageEnum.en, title="Implement Quick Sort & Compare Complexity", description="Implement Quick Sort and benchmark against Merge Sort", hint="Use list comprehensions for partitioning. Compare O(n log n) average case"),
        ProjectTaskTranslation(task_id=task5_3.id, language=LanguageEnum.fr, title="Implémenter le Tri Rapide & Comparer la Complexité", description="Implémentez le Tri Rapide et comparez avec le Tri Fusion", hint="Utilisez des compréhensions de liste pour le partitionnement. Comparez O(n log n) cas moyen"),
        ProjectTaskTranslation(task_id=task5_3.id, language=LanguageEnum.ar, title="تنفيذ الترتيب السريع ومقارنة التعقيد", description="نفذ الترتيب السريع وقارنه مع الترتيب بالدمج", hint="استخدم قائمة شاملة للتقسيم. قارن O(n log n) الحالة المتوسطة"),
    ]
    db.add_all(task5_3_translations)

    # Task 4: Implement Graph Traversal (BFS/DFS)
    task5_4 = ProjectTask(project_id=project5.id, order=4, starter_code='# Graph implementation with BFS and DFS\nfrom collections import deque\n\nclass Graph:\n    def __init__(self):\n        self.adj_list = {}\n    \n    def add_vertex(self, vertex):\n        if vertex not in self.adj_list:\n            self.adj_list[vertex] = []\n    \n    def add_edge(self, v1, v2):\n        self.add_vertex(v1)\n        self.add_vertex(v2)\n        self.adj_list[v1].append(v2)\n        self.adj_list[v2].append(v1)\n    \n    def bfs(self, start):\n        visited = set()\n        queue = deque([start])\n        result = []\n        \n        while queue:\n            vertex = queue.popleft()\n            if vertex not in visited:\n                visited.add(vertex)\n                result.append(vertex)\n                for neighbor in self.adj_list[vertex]:\n                    if neighbor not in visited:\n                        queue.append(neighbor)\n        return result\n    \n    def dfs(self, start):\n        visited = set()\n        result = []\n        \n        def dfs_recursive(vertex):\n            visited.add(vertex)\n            result.append(vertex)\n            for neighbor in self.adj_list[vertex]:\n                if neighbor not in visited:\n                    dfs_recursive(neighbor)\n        \n        dfs_recursive(start)\n        return result\n\n# Test\ng = Graph()\nfor edge in [("A", "B"), ("A", "C"), ("B", "D"), ("C", "E"), ("D", "F")]:\n    g.add_edge(*edge)\n\nprint("BFS:", g.bfs("A"))\nprint("DFS:", g.dfs("A"))', validation_code='assert g.bfs("A")[0] == "A"\nassert len(g.bfs("A")) == 6\nprint("BFS/DFS implemented!")')
    db.add(task5_4)
    await db.flush()

    task5_4_translations = [
        ProjectTaskTranslation(task_id=task5_4.id, language=LanguageEnum.en, title="Implement Graph Traversal (BFS/DFS)", description="Build a graph with Breadth-First and Depth-First Search", hint="Use queue for BFS, recursion for DFS. Track visited nodes"),
        ProjectTaskTranslation(task_id=task5_4.id, language=LanguageEnum.fr, title="Implémenter le Parcours de Graphe (BFS/DFS)", description="Construisez un graphe avec Recherche en Largeur et en Profondeur", hint="Utilisez une file pour BFS, récursion pour DFS. Suivez les nœuds visités"),
        ProjectTaskTranslation(task_id=task5_4.id, language=LanguageEnum.ar, title="تنفيذ اجتياز الرسم البياني (BFS/DFS)", description="ابنِ رسمًا بيانيًا مع البحث بالعرض والعمق", hint="استخدم طابوراً لـ BFS، تكراراً لـ DFS. تتبع العقد المزارة"),
    ]
    db.add_all(task5_4_translations)

    # Task 5: Final Challenge - Combine Algorithms
    task5_5 = ProjectTask(project_id=project5.id, order=5, starter_code='# Final Challenge: Find shortest path in weighted graph\nimport heapq\n\ndef dijkstra(graph, start):\n    """Dijkstra\'s algorithm for shortest path in weighted graph.\n    graph: dict of {vertex: {neighbor: weight}}\n    Returns: dict of {vertex: distance from start}\n    """\n    distances = {vertex: float("inf") for vertex in graph}\n    distances[start] = 0\n    pq = [(0, start)]  # (distance, vertex)\n    \n    while pq:\n        current_dist, current = heapq.heappop(pq)\n        \n        if current_dist > distances[current]:\n            continue\n        \n        for neighbor, weight in graph[current].items():\n            distance = current_dist + weight\n            if distance < distances[neighbor]:\n                distances[neighbor] = distance\n                heapq.heappush(pq, (distance, neighbor))\n    \n    return distances\n\n# Test with a weighted graph\nweighted_graph = {\n    "A": {"B": 4, "C": 2},\n    "B": {"A": 4, "C": 1, "D": 5},\n    "C": {"A": 2, "B": 1, "D": 8, "E": 10},\n    "D": {"B": 5, "C": 8, "E": 2, "F": 6},\n    "E": {"C": 10, "D": 2, "F": 2},\n    "F": {"D": 6, "E": 2}\n}\n\ndistances = dijkstra(weighted_graph, "A")\nprint("Shortest distances from A:")\nfor vertex, dist in distances.items():\n    print(f"  {vertex}: {dist}")', validation_code='assert distances["A"] == 0\nassert distances["B"] == 4\nassert distances["F"] == 10\nprint("Dijkstra implemented correctly!")')
    db.add(task5_5)
    await db.flush()

    task5_5_translations = [
        ProjectTaskTranslation(task_id=task5_5.id, language=LanguageEnum.en, title="Implement Dijkstra's Algorithm", description="Find shortest paths in a weighted graph using priority queue", hint="Use heapq for priority queue. Initialize distances to infinity except start"),
        ProjectTaskTranslation(task_id=task5_5.id, language=LanguageEnum.fr, title="Implémenter l'Algorithme de Dijkstra", description="Trouvez les plus courts chemins dans un graphe pondéré avec file de priorité", hint="Utilisez heapq pour la file de priorité. Initialisez distances à l'infini sauf départ"),
        ProjectTaskTranslation(task_id=task5_5.id, language=LanguageEnum.ar, title="تنفيذ خوارزمية ديكسترا", description="أوجد أقصر المسارات في رسم بياني موزون باستخدام طابور أولوية", hint="استخدم heapq لطابور الأولوية. инициализируйте المسافات باللانهاية ما عدا البداية"),
    ]
    db.add_all(task5_5_translations)

    print("Projects seeded successfully!")