"""Stage 2 — Python in Depth.

Picks up where Python Foundations stops. Strings, errors, files, modules,
objects, iterators, generators, decorators, testing and the habits that make
code worth keeping. Every code exercise is graded by the real sandbox.
"""

from app.models import DifficultyEnum as D

from .authoring import (
    CodeWriting,
    Code,
    CourseSpec,
    ExamTip,
    FillBlank,
    Lesson,
    MCQ,
    Module,
    Option,
    Prediction,
    ShortAnswer,
    T,
    Text,
    asserts,
    prints,
    seed_course,
)

PYTHON_IN_DEPTH = CourseSpec(
    slug="python-in-depth",
    stage=2,
    track="programming",
    icon="⚡",
    difficulty=D.intermediate,
    estimated_hours=10,
    prerequisite_slug="python-basics",
    title=T("Python in Depth", "Python en Profondeur", "بايثون بعمق"),
    description=T(
        "Everything after the basics: text handling, exceptions, files, modules, object-oriented design, generators, decorators, testing and clean code.",
        "Tout ce qui vient après les bases : traitement du texte, exceptions, fichiers, modules, conception orientée objet, générateurs, décorateurs, tests et code propre.",
        "كلّ ما بعد الأساسيات: معالجة النصوص، والاستثناءات، والملفّات، والوحدات، والتصميم الكائني، والمولّدات، والمزخرفات، والاختبار، والكود النظيف.",
    ),
    skills=T(
        "Strings, exceptions, files, modules, OOP, iterators, generators, decorators, testing, packaging, clean code",
        "Chaînes, exceptions, fichiers, modules, POO, itérateurs, générateurs, décorateurs, tests, packaging, code propre",
        "السلاسل النصّية، الاستثناءات، الملفّات، الوحدات، البرمجة الكائنية، المُكرِّرات، المولّدات، المزخرفات، الاختبار، التحزيم، الكود النظيف",
    ),
    modules=[
        # ------------------------------------------------------------------
        Module(
            slug="text-and-errors",
            title=T("Text and Errors", "Texte et Erreurs", "النصوص والأخطاء"),
            description=T(
                "Working with strings, and handling the moment things go wrong.",
                "Travailler avec les chaînes, et gérer le moment où ça tourne mal.",
                "التعامل مع السلاسل النصّية، ومعالجة اللحظة التي يسوء فيها كلّ شيء.",
            ),
            lessons=[
                Lesson(
                    slug="strings-in-depth",
                    minutes=35,
                    xp=60,
                    difficulty=D.intermediate,
                    title=T("Strings in Depth", "Les Chaînes en Profondeur", "السلاسل النصّية بعمق"),
                    story=T(
                        "Most real programs spend most of their time moving text around.",
                        "La plupart des programmes réels passent l'essentiel de leur temps à manipuler du texte.",
                        "معظم البرامج الحقيقية تقضي جلّ وقتها في تحريك النصوص.",
                    ),
                    objective=T(
                        "Slice, search, split, join and format strings, and explain why strings are immutable.",
                        "Découper, chercher, séparer, joindre et formater des chaînes, et expliquer pourquoi elles sont immuables.",
                        "تقطيع السلاسل والبحث فيها وتقسيمها ودمجها وتنسيقها، وشرح سبب كونها غير قابلة للتغيير.",
                    ),
                    skills=T(
                        "Slicing, methods, f-strings, immutability, join/split",
                        "Découpage, méthodes, f-strings, immuabilité, join/split",
                        "التقطيع، التوابع، f-strings، عدم القابلية للتغيير، join/split",
                    ),
                    blocks=[
                        Text(
                            T(
                                "A Python string is an **immutable** sequence of characters. Every method that looks like it changes a string actually returns a new one — which is why `text.upper()` on its own does nothing unless you keep the result.",
                                "Une chaîne Python est une séquence de caractères **immuable**. Toute méthode qui semble modifier une chaîne en renvoie en fait une nouvelle — c'est pourquoi `text.upper()` seul ne fait rien si l'on ne conserve pas le résultat.",
                                "السلسلة في بايثون تسلسل محارف **غير قابل للتغيير**. وكلّ تابع يبدو أنّه يغيّر السلسلة يُرجع في الحقيقة سلسلة جديدة — لذلك فإنّ `text.upper()` وحدها لا تفعل شيئًا ما لم تحتفظ بالنتيجة.",
                            )
                        ),
                        Code(
                            T(
                                "Slicing takes [start:stop:step], and stop is never included:",
                                "Le découpage prend [début:fin:pas], et la fin n'est jamais incluse :",
                                "التقطيع يأخذ [البداية:النهاية:الخطوة]، والنهاية لا تُضمَّن أبدًا:",
                            ),
                            "code = 'AC-2026-MAR'\n\n"
                            "print(code[:2])        # 'AC'   - first two\n"
                            "print(code[3:7])       # '2026'\n"
                            "print(code[-3:])       # 'MAR'  - last three\n"
                            "print(code[::-1])      # 'RAM-6202-CA' - reversed\n\n"
                            "parts = code.split('-')\n"
                            "print(parts)           # ['AC', '2026', 'MAR']\n"
                            "print('/'.join(parts)) # 'AC/2026/MAR'",
                        ),
                        Code(
                            T(
                                "f-strings are the readable way to build text, and they can format numbers as they go:",
                                "Les f-strings sont la manière lisible de construire du texte, et elles formatent les nombres au passage :",
                                "تُعدّ f-strings الطريقة المقروءة لبناء النصوص، وتنسّق الأرقام أثناء ذلك:",
                            ),
                            "name = 'Amina'\n"
                            "score = 0.8734\n\n"
                            "print(f'{name} scored {score:.1%}')      # Amina scored 87.3%\n"
                            "print(f'{name:>10}|')                    # right-aligned in 10 columns\n"
                            "print(f'{score = }')                     # debugging form",
                        ),
                        ExamTip(
                            T(
                                "Building a long string by repeated `+=` in a loop copies the whole string each time. Collect the pieces in a list and `''.join(pieces)` once — the same result, far less work.",
                                "Construire une longue chaîne par `+=` répété dans une boucle recopie toute la chaîne à chaque tour. Collectez les morceaux dans une liste puis `''.join(pieces)` une seule fois — même résultat, bien moins de travail.",
                                "بناء سلسلة طويلة بتكرار `+=` داخل حلقة ينسخ السلسلة كاملة في كلّ دورة. اجمع القطع في قائمة ثمّ استخدم `''.join(pieces)` مرّة واحدة — النتيجة نفسها بجهد أقلّ بكثير.",
                            )
                        ),
                    ],
                    exercises=[
                        Prediction(
                            prompt=T("What does this print?", "Qu'affiche ce code ?", "ما الذي يطبعه هذا الكود؟"),
                            hint=T(
                                "upper() returns a new string; it does not change the original.",
                                "upper() renvoie une nouvelle chaîne ; elle ne modifie pas l'originale.",
                                "‏upper() تُرجع سلسلة جديدة ولا تغيّر الأصلية.",
                            ),
                            explanation=T(
                                "Strings are immutable, so the first call is thrown away and `word` is unchanged until it is reassigned.",
                                "Les chaînes sont immuables : le premier appel est perdu et `word` reste inchangé jusqu'à réaffectation.",
                                "السلاسل غير قابلة للتغيير، لذا يُهمَل الاستدعاء الأوّل ويبقى `word` كما هو حتى إعادة الإسناد.",
                            ),
                            code="word = 'atlas'\nword.upper()\nprint(word)\nword = word.upper()\nprint(word)",
                            expected_output="atlas\nATLAS",
                        ),
                        CodeWriting(
                            prompt=T(
                                "Write a function `initials(full_name)` that returns the uppercase initials of each word, separated by dots. `initials('amina ben ali')` must return `'A.B.A'`.",
                                "Écrivez une fonction `initials(full_name)` qui renvoie les initiales majuscules de chaque mot, séparées par des points. `initials('amina ben ali')` doit renvoyer `'A.B.A'`.",
                                "اكتب دالّة `initials(full_name)` تُرجع الأحرف الأولى بحروف كبيرة مفصولة بنقاط. يجب أن تُرجع `initials('amina ben ali')` القيمة `'A.B.A'`.",
                            ),
                            hint=T(
                                "split() the name, take word[0] of each, upper() it, then join with '.'.",
                                "split() le nom, prenez word[0] de chaque, upper(), puis join avec '.'.",
                                "استخدم split() ثمّ خذ word[0] من كلّ كلمة وحوّلها بـ upper() ثمّ ادمجها بـ '.'.",
                            ),
                            explanation=T(
                                "split() breaks the name into words, a comprehension takes and uppercases each first letter, and join puts the dots between them.",
                                "split() découpe le nom en mots, une compréhension prend et met en majuscule chaque première lettre, et join place les points entre elles.",
                                "تقسّم split() الاسم إلى كلمات، ويأخذ الاستيعاب أوّل حرف من كلّ كلمة ويحوّله إلى كبير، ثمّ تضع join النقاط بينها.",
                            ),
                            starter_code="def initials(full_name):\n    # Return 'A.B.A' for 'amina ben ali'\n    pass\n\nprint(initials('amina ben ali'))",
                            solution_code="def initials(full_name):\n    return '.'.join(word[0].upper() for word in full_name.split())\n\nprint(initials('amina ben ali'))",
                            test_code=asserts(
                                "assert initials('amina ben ali') == 'A.B.A', initials('amina ben ali')",
                                "assert initials('youssef alami') == 'Y.A'",
                            ),
                        ),
                    ],
                ),
                Lesson(
                    slug="exceptions",
                    minutes=35,
                    xp=60,
                    difficulty=D.intermediate,
                    title=T("Exceptions and Error Handling", "Exceptions et Gestion des Erreurs", "الاستثناءات ومعالجة الأخطاء"),
                    story=T(
                        "Programs meet bad input, missing files and broken networks. Crashing is a choice, not a fate.",
                        "Les programmes rencontrent de mauvaises entrées, des fichiers absents, des réseaux coupés. Planter est un choix, pas une fatalité.",
                        "تواجه البرامج مدخلات فاسدة وملفّات مفقودة وشبكات معطّلة. والانهيار خيار لا قدر.",
                    ),
                    objective=T(
                        "Catch the exceptions you can handle, raise meaningful ones, and let the rest propagate.",
                        "Attraper les exceptions que vous pouvez traiter, en lever de significatives, et laisser passer le reste.",
                        "التقاط الاستثناءات التي يمكنك معالجتها، وإطلاق استثناءات ذات معنى، وترك الباقي يمرّ.",
                    ),
                    skills=T(
                        "try/except/else/finally, raising, exception types, EAFP",
                        "try/except/else/finally, lever, types d'exceptions, EAFP",
                        "‏try/except/else/finally، الإطلاق، أنواع الاستثناءات، مبدأ EAFP",
                    ),
                    blocks=[
                        Text(
                            T(
                                "An exception is not a bug — it is a message. `try` runs the risky part, `except` handles a specific failure, `else` runs when nothing went wrong, and `finally` always runs, whatever happened.",
                                "Une exception n'est pas un bug — c'est un message. `try` exécute la partie risquée, `except` traite un échec précis, `else` s'exécute si tout s'est bien passé, et `finally` s'exécute toujours, quoi qu'il arrive.",
                                "الاستثناء ليس خطأً برمجيًا بل رسالة. تنفّذ `try` الجزء الخطر، وتعالج `except` فشلًا محدّدًا، وتُنفَّذ `else` عند عدم حدوث خطأ، وتُنفَّذ `finally` دائمًا مهما حدث.",
                            )
                        ),
                        Code(
                            T(
                                "Catch what you can actually handle, and name it:",
                                "Attrapez ce que vous pouvez réellement traiter, et nommez-le :",
                                "التقط ما تستطيع معالجته فعلًا، وسمِّه:",
                            ),
                            "def to_mark(text):\n"
                            "    try:\n"
                            "        value = float(text)\n"
                            "    except ValueError:\n"
                            "        return None                 # 'twelve' is not a number\n"
                            "    else:\n"
                            "        if not 0 <= value <= 20:\n"
                            "            raise ValueError(f'mark out of range: {value}')\n"
                            "        return value\n\n"
                            "print(to_mark('14.5'))\n"
                            "print(to_mark('twelve'))",
                        ),
                        Text(
                            T(
                                "Two rules save most debugging time. **Never write a bare `except:`** — it swallows typos and keyboard interrupts along with the error you meant. And **only catch what you can do something about**; an exception you cannot handle is more useful crashing loudly than being hidden.",
                                "Deux règles font gagner l'essentiel du temps de débogage. **N'écrivez jamais `except:` nu** — il avale les fautes de frappe et les interruptions clavier en même temps que l'erreur visée. Et **n'attrapez que ce que vous pouvez traiter** ; une exception que vous ne savez pas gérer est plus utile en plantant bruyamment qu'en étant masquée.",
                                "قاعدتان توفّران معظم وقت التصحيح. **لا تكتب `except:` عاريًا أبدًا** — فهو يبتلع الأخطاء الإملائية ومقاطعات لوحة المفاتيح مع الخطأ المقصود. و**لا تلتقط إلّا ما تستطيع فعل شيء حياله**؛ فالاستثناء الذي لا تعرف معالجته أنفع وهو ينهار بصوت عالٍ من أن يُخفى.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "Why is a bare `except:` considered bad practice?",
                                "Pourquoi un `except:` nu est-il une mauvaise pratique ?",
                                "لماذا يُعدّ `except:` العاري ممارسة سيّئة؟",
                            ),
                            hint=T("Think about what else it catches.", "Pensez à ce qu'il attrape d'autre.", "فكّر فيما يلتقطه أيضًا."),
                            explanation=T(
                                "It catches every exception, including typos (NameError) and Ctrl-C, hiding real bugs behind silence.",
                                "Il attrape toutes les exceptions, y compris les fautes de frappe (NameError) et Ctrl-C, masquant de vrais bugs dans le silence.",
                                "يلتقط كلّ الاستثناءات بما فيها الأخطاء الإملائية (NameError) وCtrl-C، فيخفي أخطاء حقيقية خلف الصمت.",
                            ),
                            options=[
                                Option(T("It is slower than a specific except", "Il est plus lent qu'un except spécifique", "أبطأ من except محدّد")),
                                Option(
                                    T(
                                        "It hides bugs by catching errors you never meant to handle",
                                        "Il masque des bugs en attrapant des erreurs qu'on ne voulait pas traiter",
                                        "يخفي الأخطاء بالتقاط أخطاء لم تقصد معالجتها",
                                    ),
                                    correct=True,
                                ),
                                Option(T("It cannot be used with finally", "Il ne peut pas être utilisé avec finally", "لا يمكن استخدامه مع finally")),
                                Option(T("It only works inside functions", "Il ne fonctionne que dans les fonctions", "يعمل داخل الدوالّ فقط")),
                            ],
                        ),
                        CodeWriting(
                            prompt=T(
                                "Write `safe_divide(a, b)` that returns a / b, or the string 'undefined' when b is zero.",
                                "Écrivez `safe_divide(a, b)` qui renvoie a / b, ou la chaîne 'undefined' si b vaut zéro.",
                                "اكتب `safe_divide(a, b)` تُرجع a / b، أو السلسلة 'undefined' إذا كانت b تساوي صفرًا.",
                            ),
                            hint=T(
                                "Catch ZeroDivisionError specifically.",
                                "Attrapez spécifiquement ZeroDivisionError.",
                                "التقط ZeroDivisionError تحديدًا.",
                            ),
                            explanation=T(
                                "Handling the one error you expect keeps every other failure visible.",
                                "Traiter la seule erreur attendue laisse toutes les autres défaillances visibles.",
                                "معالجة الخطأ الوحيد المتوقّع تُبقي كلّ فشل آخر ظاهرًا.",
                            ),
                            starter_code="def safe_divide(a, b):\n    pass\n\nprint(safe_divide(10, 2))\nprint(safe_divide(10, 0))",
                            solution_code="def safe_divide(a, b):\n    try:\n        return a / b\n    except ZeroDivisionError:\n        return 'undefined'\n\nprint(safe_divide(10, 2))\nprint(safe_divide(10, 0))",
                            test_code=asserts(
                                "assert safe_divide(10, 2) == 5.0",
                                "assert safe_divide(10, 0) == 'undefined'",
                                "assert safe_divide(-9, 3) == -3.0",
                            ),
                        ),
                    ],
                ),
            ],
        ),
        # ------------------------------------------------------------------
        Module(
            slug="modules-and-files",
            title=T("Modules, Packages and Files", "Modules, Paquets et Fichiers", "الوحدات والحزم والملفّات"),
            description=T(
                "Splitting code across files, and reading and writing data that outlives the program.",
                "Répartir le code entre plusieurs fichiers, et lire/écrire des données qui survivent au programme.",
                "توزيع الكود على ملفّات، وقراءة وكتابة بيانات تبقى بعد انتهاء البرنامج.",
            ),
            lessons=[
                Lesson(
                    slug="modules-and-imports",
                    minutes=30,
                    xp=55,
                    difficulty=D.intermediate,
                    title=T("Modules and Imports", "Modules et Imports", "الوحدات والاستيراد"),
                    story=T(
                        "One file is fine until it is two thousand lines. Then it is not.",
                        "Un seul fichier convient jusqu'à deux mille lignes. Ensuite, non.",
                        "الملفّ الواحد مناسب حتى يبلغ ألفَي سطر. بعدها لا يعود كذلك.",
                    ),
                    objective=T(
                        "Organise code into modules and packages, and import from them without circular dependencies.",
                        "Organiser le code en modules et paquets, et importer sans dépendances circulaires.",
                        "تنظيم الكود في وحدات وحزم، والاستيراد منها دون تبعيّات دائرية.",
                    ),
                    skills=T(
                        "Modules, packages, import forms, __name__, namespaces",
                        "Modules, paquets, formes d'import, __name__, espaces de noms",
                        "الوحدات، الحزم، صيغ الاستيراد، ‎__name__‎، فضاءات الأسماء",
                    ),
                    blocks=[
                        Text(
                            T(
                                "A **module** is one `.py` file. A **package** is a directory of modules. Importing runs the module once and caches it, so the second import of the same module costs nothing.",
                                "Un **module** est un fichier `.py`. Un **paquet** est un répertoire de modules. L'import exécute le module une fois et le met en cache : le second import ne coûte rien.",
                                "**الوحدة** ملفّ `.py` واحد. و**الحزمة** مجلّد من الوحدات. والاستيراد ينفّذ الوحدة مرّة ويخزّنها، فلا يكلّف الاستيراد الثاني شيئًا.",
                            )
                        ),
                        Code(
                            T(
                                "Three import forms, and when each is right:",
                                "Trois formes d'import, et quand chacune convient :",
                                "ثلاث صيغ للاستيراد، ومتى تناسب كلّ منها:",
                            ),
                            "import math                     # keeps the namespace: math.sqrt\n"
                            "from math import sqrt           # one name, used often\n"
                            "from math import sqrt as root   # rename to avoid a clash\n\n"
                            "print(math.sqrt(16), sqrt(16), root(16))\n\n"
                            "# 'from module import *' is avoided: the reader cannot tell\n"
                            "# where a name came from, and it can silently shadow yours.",
                        ),
                        Code(
                            T(
                                "`__name__` lets one file be both a library and a script:",
                                "`__name__` permet à un fichier d'être à la fois bibliothèque et script :",
                                "يتيح `__name__` للملفّ الواحد أن يكون مكتبة وبرنامجًا في آن:",
                            ),
                            "def celsius_to_f(c):\n"
                            "    return c * 9 / 5 + 32\n\n"
                            "if __name__ == '__main__':\n"
                            "    # Runs only when this file is executed directly,\n"
                            "    # never when another module imports it.\n"
                            "    print(celsius_to_f(25))",
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "What does `if __name__ == '__main__':` protect against?",
                                "Contre quoi `if __name__ == '__main__':` protège-t-il ?",
                                "ممّ يحمي `if __name__ == '__main__':`؟",
                            ),
                            hint=T(
                                "Think about what happens when another file imports this one.",
                                "Pensez à ce qui se passe quand un autre fichier importe celui-ci.",
                                "فكّر فيما يحدث عندما يستورد ملفّ آخر هذا الملفّ.",
                            ),
                            explanation=T(
                                "Importing a module executes it top to bottom. The guard keeps the script part from running on import.",
                                "Importer un module l'exécute de haut en bas. Le garde empêche la partie script de s'exécuter à l'import.",
                                "استيراد الوحدة ينفّذها من أوّلها إلى آخرها. والحارس يمنع تنفيذ جزء البرنامج عند الاستيراد.",
                            ),
                            options=[
                                Option(T("Syntax errors in the module", "Les erreurs de syntaxe du module", "أخطاء الصياغة في الوحدة")),
                                Option(
                                    T(
                                        "The script's code running when the module is imported",
                                        "L'exécution du code script lors de l'import du module",
                                        "تنفيذ كود البرنامج عند استيراد الوحدة",
                                    ),
                                    correct=True,
                                ),
                                Option(T("Circular imports", "Les imports circulaires", "الاستيراد الدائري")),
                                Option(T("Name clashes between modules", "Les conflits de noms entre modules", "تعارض الأسماء بين الوحدات")),
                            ],
                        ),
                        FillBlank(
                            prompt=T(
                                "Complete the import that brings in `sqrt` under the name `root`.",
                                "Complétez l'import qui amène `sqrt` sous le nom `root`.",
                                "أكمل الاستيراد الذي يجلب `sqrt` باسم `root`.",
                            ),
                            hint=T("from … import … as …", "from … import … as …", "‏from … import … as …"),
                            explanation=T(
                                "`from math import sqrt as root` imports one name and renames it locally.",
                                "`from math import sqrt as root` importe un seul nom et le renomme localement.",
                                "‏`from math import sqrt as root` تستورد اسمًا واحدًا وتعيد تسميته محليًا.",
                            ),
                            snippet="____ math ____ sqrt ____ root",
                            answers=["from", "import", "as"],
                        ),
                    ],
                ),
                Lesson(
                    slug="working-with-files",
                    minutes=30,
                    xp=55,
                    difficulty=D.intermediate,
                    title=T("Working with Files", "Travailler avec les Fichiers", "التعامل مع الملفّات"),
                    story=T(
                        "Data that disappears when the program ends is not much use to anyone.",
                        "Des données qui disparaissent à la fin du programme ne servent à personne.",
                        "البيانات التي تختفي بانتهاء البرنامج لا تنفع أحدًا.",
                    ),
                    objective=T(
                        "Read and write text files safely with `with`, and choose the right mode and encoding.",
                        "Lire et écrire des fichiers texte en sécurité avec `with`, et choisir le bon mode et le bon encodage.",
                        "قراءة الملفّات النصّية وكتابتها بأمان باستخدام `with`، واختيار الوضع والترميز المناسبين.",
                    ),
                    skills=T(
                        "open modes, context managers, encoding, line iteration",
                        "Modes d'ouverture, gestionnaires de contexte, encodage, itération par ligne",
                        "أوضاع الفتح، مديرو السياق، الترميز، التكرار على الأسطر",
                    ),
                    blocks=[
                        Text(
                            T(
                                "`with open(path, mode, encoding='utf-8') as f:` is the only form worth learning. The `with` block closes the file even if an exception is raised inside it, which a bare `open()` does not.",
                                "`with open(chemin, mode, encoding='utf-8') as f:` est la seule forme à retenir. Le bloc `with` ferme le fichier même si une exception survient à l'intérieur, ce que `open()` seul ne fait pas.",
                                "الصيغة `with open(path, mode, encoding='utf-8') as f:` هي الوحيدة الجديرة بالحفظ. فكتلة `with` تغلق الملفّ حتى لو حدث استثناء داخلها، وهو ما لا تفعله `open()` وحدها.",
                            )
                        ),
                        Code(
                            T(
                                "Modes: 'r' read, 'w' overwrite, 'a' append, 'x' create-only. Always name the encoding.",
                                "Modes : 'r' lecture, 'w' écrasement, 'a' ajout, 'x' création seule. Précisez toujours l'encodage.",
                                "الأوضاع: 'r' للقراءة، 'w' للاستبدال، 'a' للإلحاق، 'x' للإنشاء فقط. وحدّد الترميز دائمًا.",
                            ),
                            "# Writing - 'w' truncates the file first, so it starts empty\n"
                            "with open('marks.txt', 'w', encoding='utf-8') as f:\n"
                            "    f.write('Amina 14\\n')\n"
                            "    f.write('Youssef 11\\n')\n\n"
                            "# Reading line by line - never loads the whole file into memory\n"
                            "with open('marks.txt', encoding='utf-8') as f:\n"
                            "    for line in f:\n"
                            "        name, mark = line.split()\n"
                            "        print(name, float(mark))",
                        ),
                        ExamTip(
                            T(
                                "Opening with 'w' erases the file before you write a single byte. If you meant to add to it, the mode is 'a'. This mistake has destroyed more student data than any bug in the code itself.",
                                "Ouvrir en 'w' efface le fichier avant même d'écrire un octet. Si vous vouliez ajouter, le mode est 'a'. Cette erreur a détruit plus de données d'étudiants que n'importe quel bug.",
                                "الفتح بالوضع 'w' يمسح الملفّ قبل كتابة أيّ بايت. وإن كنت تريد الإضافة فالوضع هو 'a'. هذا الخطأ أتلف من بيانات الطلبة أكثر ممّا أتلفه أيّ خلل برمجي.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "You want to add a line to an existing log file without losing what is in it. Which mode?",
                                "Vous voulez ajouter une ligne à un journal existant sans perdre son contenu. Quel mode ?",
                                "تريد إضافة سطر إلى ملفّ سجلّ موجود دون فقدان محتواه. أيّ وضع؟",
                            ),
                            hint=T("One of the modes empties the file first.", "L'un des modes vide d'abord le fichier.", "أحد الأوضاع يفرّغ الملفّ أوّلًا."),
                            explanation=T(
                                "'a' appends to the end; 'w' would truncate the file to nothing before writing.",
                                "'a' ajoute à la fin ; 'w' viderait le fichier avant d'écrire.",
                                "الوضع 'a' يُلحق في النهاية، أمّا 'w' فيُفرغ الملفّ قبل الكتابة.",
                            ),
                            options=[
                                Option(T("'w'", "'w'", "'w'")),
                                Option(T("'a'", "'a'", "'a'"), correct=True),
                                Option(T("'x'", "'x'", "'x'")),
                                Option(T("'r'", "'r'", "'r'")),
                            ],
                        ),
                        ShortAnswer(
                            prompt=T(
                                "Why should you open files with a `with` block? One sentence.",
                                "Pourquoi ouvrir les fichiers avec un bloc `with` ? Une phrase.",
                                "لماذا تفتح الملفّات بكتلة `with`؟ جملة واحدة.",
                            ),
                            hint=T(
                                "Think about what happens if an exception is raised mid-write.",
                                "Pensez à ce qui se passe si une exception survient en pleine écriture.",
                                "فكّر فيما يحدث إذا وقع استثناء أثناء الكتابة.",
                            ),
                            explanation=T(
                                "`with` closes the file automatically, even when an exception leaves the block early, so no handle is leaked and buffered writes are flushed.",
                                "`with` ferme le fichier automatiquement, même si une exception quitte le bloc, donc aucun descripteur n'est perdu et les écritures tamponnées sont vidées.",
                                "تُغلق `with` الملفّ تلقائيًا حتى عند خروج استثناء من الكتلة، فلا يُهدر مقبض ملفّ وتُفرَّغ الكتابات المؤقّتة.",
                            ),
                            keywords=[["close", "closes", "ferme", "يغلق", "إغلاق"], ["exception", "erreur", "استثناء", "خطأ"]],
                            reference_answer="Because with closes the file automatically even if an exception is raised inside the block, so the file handle is never leaked.",
                        ),
                    ],
                ),
            ],
        ),
        # ------------------------------------------------------------------
        Module(
            slug="object-oriented-python",
            title=T("Object-Oriented Python", "Python Orienté Objet", "بايثون الكائنية"),
            description=T(
                "Classes, objects, inheritance and when not to use them.",
                "Classes, objets, héritage et quand ne pas les utiliser.",
                "الأصناف والكائنات والوراثة، ومتى لا تستخدمها.",
            ),
            lessons=[
                Lesson(
                    slug="classes-and-objects",
                    minutes=40,
                    xp=65,
                    difficulty=D.intermediate,
                    title=T("Classes and Objects", "Classes et Objets", "الأصناف والكائنات"),
                    story=T(
                        "When the same data and the same operations keep travelling together, they want to be a class.",
                        "Quand les mêmes données et les mêmes opérations voyagent toujours ensemble, elles veulent devenir une classe.",
                        "عندما تتنقّل البيانات نفسها والعمليات نفسها معًا دائمًا، فإنّها تريد أن تصير صنفًا.",
                    ),
                    objective=T(
                        "Define a class with state and behaviour, and know when a plain function would be better.",
                        "Définir une classe avec état et comportement, et savoir quand une simple fonction vaudrait mieux.",
                        "تعريف صنف له حالة وسلوك، ومعرفة متى تكون الدالّة البسيطة أفضل.",
                    ),
                    skills=T(
                        "Classes, __init__, instance state, methods, __repr__",
                        "Classes, __init__, état d'instance, méthodes, __repr__",
                        "الأصناف، ‎__init__‎، حالة النسخة، التوابع، ‎__repr__‎",
                    ),
                    blocks=[
                        Text(
                            T(
                                "A class bundles **state** (data) with **behaviour** (functions that act on it). `__init__` sets up a new instance; `self` is that instance. Use a class when several functions would otherwise keep passing the same three variables around.",
                                "Une classe regroupe un **état** (données) et un **comportement** (fonctions qui agissent dessus). `__init__` prépare une nouvelle instance ; `self` est cette instance. Utilisez une classe quand plusieurs fonctions se passeraient sans cesse les trois mêmes variables.",
                                "يجمع الصنف بين **الحالة** (البيانات) و**السلوك** (الدوالّ التي تعمل عليها). تُهيّئ `__init__` نسخة جديدة، و`self` هي تلك النسخة. استخدم الصنف عندما تظلّ عدّة دوالّ تتبادل المتغيّرات الثلاثة نفسها.",
                            )
                        ),
                        Code(
                            T(
                                "A small, complete class:",
                                "Une petite classe complète :",
                                "صنف صغير ومكتمل:",
                            ),
                            "class Student:\n"
                            "    def __init__(self, name):\n"
                            "        self.name = name\n"
                            "        self.marks = []            # state, one list per student\n\n"
                            "    def add_mark(self, mark):\n"
                            "        if not 0 <= mark <= 20:\n"
                            "            raise ValueError('mark out of range')\n"
                            "        self.marks.append(mark)\n\n"
                            "    def average(self):\n"
                            "        return sum(self.marks) / len(self.marks) if self.marks else None\n\n"
                            "    def __repr__(self):            # what you see when debugging\n"
                            "        return f'Student({self.name!r}, {len(self.marks)} marks)'\n\n"
                            "amina = Student('Amina')\n"
                            "amina.add_mark(14)\n"
                            "amina.add_mark(17)\n"
                            "print(amina, amina.average())",
                        ),
                        ExamTip(
                            T(
                                "A class whose methods never touch `self` is a set of functions wearing a costume. Objects earn their place when there is real state to hold.",
                                "Une classe dont les méthodes ne touchent jamais `self` n'est qu'un ensemble de fonctions déguisées. Les objets méritent leur place quand il y a un véritable état à conserver.",
                                "الصنف الذي لا تمسّ توابعه `self` أبدًا ليس إلّا مجموعة دوالّ متنكّرة. والكائنات تستحقّ مكانها عندما توجد حالة حقيقية تُحفَظ.",
                            )
                        ),
                    ],
                    exercises=[
                        CodeWriting(
                            prompt=T(
                                "Write a class `Counter` with a `count` starting at 0, an `increment()` method that adds one, and a `reset()` method that returns it to 0.",
                                "Écrivez une classe `Counter` avec un `count` initialisé à 0, une méthode `increment()` qui ajoute un, et une méthode `reset()` qui le remet à 0.",
                                "اكتب صنفًا `Counter` فيه `count` يبدأ من 0، وتابع `increment()` يزيد واحدًا، وتابع `reset()` يعيده إلى 0.",
                            ),
                            hint=T(
                                "Set self.count = 0 in __init__, then change it inside the methods.",
                                "Mettez self.count = 0 dans __init__, puis modifiez-le dans les méthodes.",
                                "اضبط self.count = 0 داخل ‎__init__‎ ثمّ غيّرها داخل التوابع.",
                            ),
                            explanation=T(
                                "Each instance keeps its own count, because the attribute is set on self rather than on the class.",
                                "Chaque instance conserve son propre compteur, car l'attribut est posé sur self et non sur la classe.",
                                "كلّ نسخة تحتفظ بعدّادها الخاصّ لأنّ السمة تُضبط على self لا على الصنف.",
                            ),
                            starter_code="class Counter:\n    def __init__(self):\n        pass\n\n    def increment(self):\n        pass\n\n    def reset(self):\n        pass\n\nc = Counter()\nc.increment()\nprint(c.count)",
                            solution_code="class Counter:\n    def __init__(self):\n        self.count = 0\n\n    def increment(self):\n        self.count += 1\n\n    def reset(self):\n        self.count = 0\n\nc = Counter()\nc.increment()\nprint(c.count)",
                            test_code=asserts(
                                "c = Counter()",
                                "assert c.count == 0",
                                "c.increment(); c.increment()",
                                "assert c.count == 2, c.count",
                                "c.reset()",
                                "assert c.count == 0",
                                "assert Counter().count == 0, 'each instance needs its own count'",
                            ),
                        ),
                        MCQ(
                            prompt=T(
                                "What is `self` in a method definition?",
                                "Qu'est-ce que `self` dans une définition de méthode ?",
                                "ما هي `self` في تعريف التابع؟",
                            ),
                            hint=T("It is passed automatically when you call the method on an object.", "Il est passé automatiquement quand on appelle la méthode sur un objet.", "تُمرَّر تلقائيًا عند استدعاء التابع على كائن."),
                            explanation=T(
                                "`self` is the instance the method was called on, passed as the first argument automatically.",
                                "`self` est l'instance sur laquelle la méthode a été appelée, passée automatiquement en premier argument.",
                                "‏`self` هي النسخة التي استُدعي عليها التابع، وتُمرَّر تلقائيًا كأوّل وسيط.",
                            ),
                            options=[
                                Option(T("The class itself", "La classe elle-même", "الصنف نفسه")),
                                Option(T("The instance the method was called on", "L'instance sur laquelle la méthode est appelée", "النسخة التي استُدعي عليها التابع"), correct=True),
                                Option(T("A reserved Python keyword", "Un mot-clé réservé de Python", "كلمة محجوزة في بايثون")),
                                Option(T("The module the class lives in", "Le module contenant la classe", "الوحدة التي يوجد فيها الصنف")),
                            ],
                        ),
                    ],
                ),
                Lesson(
                    slug="inheritance-and-composition",
                    minutes=35,
                    xp=65,
                    difficulty=D.intermediate,
                    title=T("Inheritance and Composition", "Héritage et Composition", "الوراثة والتركيب"),
                    story=T(
                        "\"Is a\" or \"has a\"? Getting this wrong is how class hierarchies turn into mazes.",
                        "« Est un » ou « a un » ? Se tromper ici, c'est transformer une hiérarchie de classes en labyrinthe.",
                        "«هو نوع من» أم «يملك»؟ الخطأ هنا هو ما يحوّل تسلسل الأصناف إلى متاهة.",
                    ),
                    objective=T(
                        "Extend a class with inheritance, override a method, and choose composition when it fits better.",
                        "Étendre une classe par héritage, redéfinir une méthode, et choisir la composition quand elle convient mieux.",
                        "توسيع صنف بالوراثة، وإعادة تعريف تابع، واختيار التركيب حين يكون أنسب.",
                    ),
                    skills=T(
                        "Inheritance, super(), overriding, composition, polymorphism",
                        "Héritage, super(), redéfinition, composition, polymorphisme",
                        "الوراثة، ‎super()‎، إعادة التعريف، التركيب، تعدّد الأشكال",
                    ),
                    blocks=[
                        Text(
                            T(
                                "Inheritance says **\"is a\"**: a `Rectangle` is a `Shape`. Composition says **\"has a\"**: a `Course` has a list of `Lesson`s. Most designs that go wrong used inheritance where composition was meant.",
                                "L'héritage dit **« est un »** : un `Rectangle` est une `Shape`. La composition dit **« a un »** : un `Course` a une liste de `Lesson`. La plupart des mauvaises conceptions ont utilisé l'héritage là où il fallait la composition.",
                                "الوراثة تقول **«هو نوع من»**: فـ`Rectangle` هو `Shape`. والتركيب يقول **«يملك»**: فـ`Course` يملك قائمة من `Lesson`. ومعظم التصاميم الفاشلة استخدمت الوراثة حيث كان المقصود التركيب.",
                            )
                        ),
                        Code(
                            T(
                                "Overriding a method, and calling the parent's version with super():",
                                "Redéfinir une méthode et appeler la version du parent avec super() :",
                                "إعادة تعريف تابع واستدعاء نسخة الأب بـ super():",
                            ),
                            "class Shape:\n"
                            "    def __init__(self, name):\n"
                            "        self.name = name\n\n"
                            "    def area(self):\n"
                            "        raise NotImplementedError\n\n"
                            "    def describe(self):\n"
                            "        return f'{self.name} with area {self.area()}'\n\n"
                            "class Rectangle(Shape):\n"
                            "    def __init__(self, width, height):\n"
                            "        super().__init__('rectangle')   # let Shape do its part\n"
                            "        self.width = width\n"
                            "        self.height = height\n\n"
                            "    def area(self):\n"
                            "        return self.width * self.height\n\n"
                            "print(Rectangle(3, 4).describe())",
                        ),
                        Text(
                            T(
                                "Notice that `describe()` was written once, on the parent, and calls `self.area()` — which resolves to whichever subclass is actually there. That is **polymorphism**: the same call, different behaviour, no `if` needed.",
                                "Remarquez que `describe()` n'est écrite qu'une fois, sur le parent, et appelle `self.area()` — qui se résout vers la sous-classe réellement présente. C'est le **polymorphisme** : même appel, comportement différent, sans aucun `if`.",
                                "لاحظ أنّ `describe()` كُتبت مرّة واحدة في الأب وتستدعي `self.area()` — التي تُحلّ إلى الصنف الفرعي الموجود فعلًا. هذا هو **تعدّد الأشكال**: الاستدعاء نفسه بسلوك مختلف دون أيّ `if`.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "A `Playlist` contains many `Song`s. Which relationship is that?",
                                "Une `Playlist` contient plusieurs `Song`. Quelle relation est-ce ?",
                                "قائمة تشغيل `Playlist` تحتوي على عدّة `Song`. ما هذه العلاقة؟",
                            ),
                            hint=T("Try both sentences: \"a playlist is a song\" and \"a playlist has songs\".", "Essayez les deux phrases : « une playlist est une chanson » et « une playlist a des chansons ».", "جرّب الجملتين: «قائمة التشغيل أغنية» و«قائمة التشغيل تملك أغنيات»."),
                            explanation=T(
                                "A playlist has songs, it is not a kind of song — so it holds them as data (composition), not by inheriting from Song.",
                                "Une playlist a des chansons, ce n'est pas une sorte de chanson — elle les détient comme données (composition), sans hériter de Song.",
                                "قائمة التشغيل تملك أغنيات وليست نوعًا من الأغاني — فهي تحتفظ بها كبيانات (تركيب) لا بالوراثة من Song.",
                            ),
                            options=[
                                Option(T("Inheritance: Playlist should extend Song", "Héritage : Playlist devrait étendre Song", "وراثة: يجب أن ترث Playlist من Song")),
                                Option(T("Composition: Playlist holds a list of Songs", "Composition : Playlist détient une liste de Song", "تركيب: تحتفظ Playlist بقائمة من Song"), correct=True),
                                Option(T("Inheritance: Song should extend Playlist", "Héritage : Song devrait étendre Playlist", "وراثة: يجب أن ترث Song من Playlist")),
                                Option(T("Neither — they must be unrelated", "Ni l'un ni l'autre — elles doivent être indépendantes", "لا هذا ولا ذاك — يجب ألّا تربطهما علاقة")),
                            ],
                        ),
                        CodeWriting(
                            prompt=T(
                                "Given the `Shape` class shown, write a `Square(Shape)` subclass whose constructor takes a `side` and whose `area()` returns side squared. It must set the name to 'square'.",
                                "À partir de la classe `Shape` fournie, écrivez une sous-classe `Square(Shape)` dont le constructeur prend un `side` et dont `area()` renvoie le côté au carré. Le nom doit être 'square'.",
                                "انطلاقًا من الصنف `Shape` المعطى، اكتب صنفًا فرعيًا `Square(Shape)` يأخذ بانيه `side` وتُرجع `area()` مربّع الضلع. ويجب أن يكون الاسم 'square'.",
                            ),
                            hint=T(
                                "Call super().__init__('square') first, then store the side.",
                                "Appelez d'abord super().__init__('square'), puis stockez le côté.",
                                "استدعِ ‎super().__init__('square')‎ أوّلًا ثمّ خزّن الضلع.",
                            ),
                            explanation=T(
                                "super() runs the parent's constructor so the inherited describe() has a name to use.",
                                "super() exécute le constructeur du parent, si bien que describe() hérité dispose d'un nom.",
                                "‏super() تنفّذ باني الأب فتجد describe() الموروثة اسمًا تستخدمه.",
                            ),
                            starter_code="class Shape:\n    def __init__(self, name):\n        self.name = name\n\n    def area(self):\n        raise NotImplementedError\n\n    def describe(self):\n        return f'{self.name} with area {self.area()}'\n\n\nclass Square(Shape):\n    pass\n\n\nprint(Square(5).describe())",
                            solution_code="class Shape:\n    def __init__(self, name):\n        self.name = name\n\n    def area(self):\n        raise NotImplementedError\n\n    def describe(self):\n        return f'{self.name} with area {self.area()}'\n\n\nclass Square(Shape):\n    def __init__(self, side):\n        super().__init__('square')\n        self.side = side\n\n    def area(self):\n        return self.side ** 2\n\n\nprint(Square(5).describe())",
                            test_code=asserts(
                                "s = Square(5)",
                                "assert isinstance(s, Shape), 'Square must inherit from Shape'",
                                "assert s.area() == 25, s.area()",
                                "assert s.describe() == 'square with area 25', s.describe()",
                            ),
                        ),
                    ],
                ),
            ],
        ),
        # ------------------------------------------------------------------
        Module(
            slug="iterators-generators-decorators",
            title=T("Iterators, Generators and Decorators", "Itérateurs, Générateurs et Décorateurs", "المُكرِّرات والمولّدات والمزخرفات"),
            description=T(
                "The three ideas that make Python code feel like Python.",
                "Les trois idées qui donnent au code Python son style.",
                "الأفكار الثلاث التي تجعل كود بايثون يبدو بايثونيًا.",
            ),
            lessons=[
                Lesson(
                    slug="iterators-and-generators",
                    minutes=35,
                    xp=65,
                    difficulty=D.intermediate,
                    title=T("Iterators and Generators", "Itérateurs et Générateurs", "المُكرِّرات والمولّدات"),
                    story=T(
                        "How do you loop over ten million records on a laptop with 8 GB of memory?",
                        "Comment parcourir dix millions d'enregistrements sur un portable de 8 Go ?",
                        "كيف تمرّ على عشرة ملايين سجلّ على حاسوب محمول بذاكرة 8 غيغابايت؟",
                    ),
                    objective=T(
                        "Write a generator with `yield` and explain why it uses constant memory.",
                        "Écrire un générateur avec `yield` et expliquer pourquoi il utilise une mémoire constante.",
                        "كتابة مولّد باستخدام `yield` وشرح سبب استهلاكه ذاكرة ثابتة.",
                    ),
                    skills=T(
                        "Iterables, iterators, yield, lazy evaluation, memory",
                        "Itérables, itérateurs, yield, évaluation paresseuse, mémoire",
                        "القابل للتكرار، المُكرِّر، ‎yield‎، التقييم الكسول، الذاكرة",
                    ),
                    blocks=[
                        Text(
                            T(
                                "An **iterable** is anything a `for` loop can walk through. An **iterator** is the thing doing the walking, handing over one item each time `next()` is called. A **generator** is the easiest way to make one: a function that `yield`s instead of `return`ing.",
                                "Un **itérable** est tout ce qu'une boucle `for` peut parcourir. Un **itérateur** est ce qui parcourt, livrant un élément à chaque appel de `next()`. Un **générateur** est la façon la plus simple d'en créer un : une fonction qui `yield` au lieu de `return`.",
                                "**القابل للتكرار** هو كلّ ما تستطيع حلقة `for` المرور عليه. و**المُكرِّر** هو ما يقوم بالمرور، مسلّمًا عنصرًا واحدًا في كلّ استدعاء لـ`next()`. و**المولّد** أسهل طريقة لصنع واحد: دالّة تستخدم `yield` بدل `return`.",
                            )
                        ),
                        Code(
                            T(
                                "The same job, twice: one builds a whole list, one produces values on demand.",
                                "Le même travail, deux fois : l'un construit toute une liste, l'autre produit des valeurs à la demande.",
                                "العمل نفسه مرّتين: أحدهما يبني قائمة كاملة، والآخر ينتج القيم عند الطلب.",
                            ),
                            "def squares_list(n):\n"
                            "    result = []\n"
                            "    for i in range(n):\n"
                            "        result.append(i * i)   # n items held at once\n"
                            "    return result\n\n"
                            "def squares_gen(n):\n"
                            "    for i in range(n):\n"
                            "        yield i * i            # one item at a time, then pauses\n\n"
                            "print(sum(squares_list(5)))\n"
                            "print(sum(squares_gen(5)))     # same answer, constant memory\n"
                            "print(type(squares_gen(5)).__name__)",
                        ),
                        Text(
                            T(
                                "`yield` pauses the function and remembers exactly where it stopped, including every local variable. The next `next()` resumes from that line. This is why a generator over ten million records costs the same memory as one over ten.",
                                "`yield` met la fonction en pause et retient exactement où elle s'est arrêtée, avec toutes ses variables locales. Le `next()` suivant reprend à cette ligne. C'est pourquoi un générateur sur dix millions d'enregistrements coûte autant de mémoire qu'un générateur sur dix.",
                                "تُوقِف `yield` الدالّة مؤقّتًا وتتذكّر بدقّة أين توقّفت بما في ذلك كلّ متغيّراتها المحلّية. ويستأنف `next()` التالي من ذلك السطر. لهذا يكلّف المولّد على عشرة ملايين سجلّ من الذاكرة ما يكلّفه على عشرة.",
                            )
                        ),
                    ],
                    exercises=[
                        Prediction(
                            prompt=T(
                                "What does this print?",
                                "Qu'affiche ce code ?",
                                "ما الذي يطبعه هذا الكود؟",
                            ),
                            hint=T(
                                "Calling a generator function does not run its body yet.",
                                "Appeler une fonction génératrice n'exécute pas encore son corps.",
                                "استدعاء دالّة المولّد لا ينفّذ جسمها بعد.",
                            ),
                            explanation=T(
                                "The call returns a generator object; nothing runs until next() asks for a value, and then it stops again at the yield.",
                                "L'appel renvoie un objet générateur ; rien ne s'exécute avant que next() ne demande une valeur, puis il s'arrête de nouveau au yield.",
                                "يُرجع الاستدعاء كائن مولّد؛ ولا يُنفَّذ شيء حتى يطلب next() قيمة، ثمّ يتوقّف مجدّدًا عند yield.",
                            ),
                            code="def counter():\n    print('start')\n    yield 1\n    print('middle')\n    yield 2\n\ng = counter()\nprint('created')\nprint(next(g))\nprint(next(g))",
                            expected_output="created\nstart\n1\nmiddle\n2",
                        ),
                        CodeWriting(
                            prompt=T(
                                "Write a generator `evens(limit)` that yields every even number from 0 up to but not including `limit`.",
                                "Écrivez un générateur `evens(limit)` qui produit chaque nombre pair de 0 jusqu'à `limit` exclu.",
                                "اكتب مولّدًا `evens(limit)` ينتج كلّ عدد زوجي من 0 حتى `limit` غير مشمولة.",
                            ),
                            hint=T(
                                "Loop with range and use yield, not return.",
                                "Bouclez avec range et utilisez yield, pas return.",
                                "استخدم حلقة مع range واستعمل yield لا return.",
                            ),
                            explanation=T(
                                "Because it yields, the function produces values lazily and works for any limit without building a list.",
                                "Parce qu'elle yield, la fonction produit les valeurs paresseusement et fonctionne pour n'importe quelle limite sans construire de liste.",
                                "لأنّها تستخدم yield، تنتج الدالّة القيم بكسل وتعمل مع أيّ حدّ دون بناء قائمة.",
                            ),
                            starter_code="def evens(limit):\n    pass\n\nprint(list(evens(10)))",
                            solution_code="def evens(limit):\n    for value in range(0, limit, 2):\n        yield value\n\nprint(list(evens(10)))",
                            test_code=asserts(
                                "assert list(evens(10)) == [0, 2, 4, 6, 8], list(evens(10))",
                                "assert list(evens(1)) == [0]",
                                "assert list(evens(0)) == []",
                                "g = evens(6)",
                                "assert hasattr(g, '__next__'), 'evens must be a generator, so use yield'",
                            ),
                        ),
                    ],
                ),
                Lesson(
                    slug="decorators",
                    minutes=35,
                    xp=65,
                    difficulty=D.advanced,
                    title=T("Decorators", "Les Décorateurs", "المزخرفات"),
                    story=T(
                        "Add logging, timing or access checks to a function without editing a single line of it.",
                        "Ajouter journalisation, chronométrage ou contrôle d'accès à une fonction sans en modifier une ligne.",
                        "أضف التسجيل أو التوقيت أو التحقّق من الصلاحية إلى دالّة دون تعديل سطر واحد منها.",
                    ),
                    objective=T(
                        "Read and write a decorator, and explain what `@name` does to the function beneath it.",
                        "Lire et écrire un décorateur, et expliquer ce que `@nom` fait à la fonction en dessous.",
                        "قراءة المزخرف وكتابته، وشرح ما يفعله `@name` بالدالّة التي تحته.",
                    ),
                    skills=T(
                        "First-class functions, closures, decorators, *args/**kwargs",
                        "Fonctions de première classe, fermetures, décorateurs, *args/**kwargs",
                        "الدوالّ كقيم، الإغلاقات، المزخرفات، ‎*args/**kwargs‎",
                    ),
                    blocks=[
                        Text(
                            T(
                                "In Python a function is an ordinary value: you can pass it, return it and store it. A **decorator** takes a function and gives back a new one that wraps it. `@log` above a definition is exactly `greet = log(greet)`.",
                                "En Python, une fonction est une valeur ordinaire : on peut la passer, la renvoyer, la stocker. Un **décorateur** prend une fonction et en renvoie une nouvelle qui l'enveloppe. `@log` au-dessus d'une définition, c'est exactement `greet = log(greet)`.",
                                "في بايثون الدالّة قيمة عادية: يمكنك تمريرها وإرجاعها وتخزينها. و**المزخرف** يأخذ دالّة ويُرجع دالّة جديدة تغلّفها. و`@log` فوق التعريف هي بالضبط `greet = log(greet)`.",
                            )
                        ),
                        Code(
                            T(
                                "A decorator that counts how often a function is called:",
                                "Un décorateur qui compte combien de fois une fonction est appelée :",
                                "مزخرف يعدّ كم مرّة استُدعيت الدالّة:",
                            ),
                            "def counted(func):\n"
                            "    def wrapper(*args, **kwargs):\n"
                            "        wrapper.calls += 1          # the closure remembers\n"
                            "        return func(*args, **kwargs)\n"
                            "    wrapper.calls = 0\n"
                            "    return wrapper\n\n"
                            "@counted\n"
                            "def greet(name):\n"
                            "    return f'Hello, {name}'\n\n"
                            "greet('Amina')\n"
                            "greet('Youssef')\n"
                            "print(greet.calls)",
                        ),
                        Text(
                            T(
                                "`*args, **kwargs` in the wrapper is what lets one decorator work on functions with any signature: it accepts whatever it is given and passes it straight through untouched.",
                                "`*args, **kwargs` dans l'enveloppe est ce qui permet à un décorateur de fonctionner avec n'importe quelle signature : il accepte ce qu'on lui donne et le transmet tel quel.",
                                "‏`*args, **kwargs` في الغلاف هي ما يجعل المزخرف الواحد يعمل مع أيّ توقيع: يقبل ما يُعطى له ويمرّره كما هو.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "What is `@twice` above `def f(): ...` equivalent to?",
                                "À quoi équivaut `@twice` au-dessus de `def f(): ...` ?",
                                "بمَ تكافئ `@twice` فوق `def f(): ...`؟",
                            ),
                            hint=T("The decorator is applied to the function object right after it is defined.", "Le décorateur est appliqué à l'objet fonction juste après sa définition.", "يُطبَّق المزخرف على كائن الدالّة مباشرة بعد تعريفها."),
                            explanation=T(
                                "Decorator syntax is sugar for rebinding the name to the decorator's return value.",
                                "La syntaxe des décorateurs est un sucre pour réaffecter le nom à la valeur renvoyée par le décorateur.",
                                "صياغة المزخرف اختصار لإعادة ربط الاسم بالقيمة التي يُرجعها المزخرف.",
                            ),
                            options=[
                                Option(T("f = twice(f)", "f = twice(f)", "f = twice(f)"), correct=True),
                                Option(T("f = f(twice)", "f = f(twice)", "f = f(twice)")),
                                Option(T("twice = f()", "twice = f()", "twice = f()")),
                                Option(T("f() called two times", "f() appelée deux fois", "استدعاء f() مرّتين")),
                            ],
                        ),
                        CodeWriting(
                            prompt=T(
                                "Write a decorator `double` that makes any function return twice whatever it returned before. `@double` on a function returning 5 must make it return 10.",
                                "Écrivez un décorateur `double` qui fait renvoyer à toute fonction le double de ce qu'elle renvoyait. `@double` sur une fonction renvoyant 5 doit faire renvoyer 10.",
                                "اكتب مزخرفًا `double` يجعل أيّ دالّة تُرجع ضعف ما كانت تُرجعه. فـ`@double` على دالّة تُرجع 5 يجب أن تجعلها تُرجع 10.",
                            ),
                            hint=T(
                                "Define an inner wrapper(*args, **kwargs) that returns func(*args, **kwargs) * 2.",
                                "Définissez un wrapper(*args, **kwargs) interne renvoyant func(*args, **kwargs) * 2.",
                                "عرّف غلافًا داخليًا wrapper(*args, **kwargs) يُرجع func(*args, **kwargs) * 2.",
                            ),
                            explanation=T(
                                "The decorator returns a new function that calls the original and transforms the result before handing it back.",
                                "Le décorateur renvoie une nouvelle fonction qui appelle l'originale et transforme le résultat avant de le rendre.",
                                "يُرجع المزخرف دالّة جديدة تستدعي الأصلية وتحوّل النتيجة قبل إعادتها.",
                            ),
                            starter_code="def double(func):\n    pass\n\n\n@double\ndef five():\n    return 5\n\nprint(five())",
                            solution_code="def double(func):\n    def wrapper(*args, **kwargs):\n        return func(*args, **kwargs) * 2\n    return wrapper\n\n\n@double\ndef five():\n    return 5\n\nprint(five())",
                            test_code=asserts(
                                "assert five() == 10, five()",
                                "@double",
                                "def add(a, b):",
                                "    return a + b",
                                "assert add(3, 4) == 14, 'the decorator must accept any signature'",
                            ),
                        ),
                    ],
                ),
            ],
        ),
        # ------------------------------------------------------------------
        Module(
            slug="testing-and-craft",
            title=T("Testing, Environments and Clean Code", "Tests, Environnements et Code Propre", "الاختبار والبيئات والكود النظيف"),
            description=T(
                "The practices that separate code that works once from code a team can keep.",
                "Les pratiques qui séparent le code qui marche une fois de celui qu'une équipe peut conserver.",
                "الممارسات التي تفصل الكود الذي ينجح مرّة عن الكود الذي يستطيع فريق الحفاظ عليه.",
            ),
            lessons=[
                Lesson(
                    slug="testing-your-code",
                    minutes=35,
                    xp=65,
                    difficulty=D.intermediate,
                    title=T("Testing Your Code", "Tester Votre Code", "اختبار كودك"),
                    story=T(
                        "A test is a sentence about your code that a machine can check every day, for free.",
                        "Un test est une phrase sur votre code qu'une machine peut vérifier chaque jour, gratuitement.",
                        "الاختبار جملة عن كودك يستطيع الجهاز التحقّق منها كلّ يوم مجّانًا.",
                    ),
                    objective=T(
                        "Write focused unit tests, including the edge cases, and know what makes a test valuable.",
                        "Écrire des tests unitaires ciblés, cas limites compris, et savoir ce qui fait la valeur d'un test.",
                        "كتابة اختبارات وحدة مركّزة تشمل الحالات الحدّية، ومعرفة ما يجعل الاختبار ذا قيمة.",
                    ),
                    skills=T(
                        "Unit tests, assertions, edge cases, arrange-act-assert, regression tests",
                        "Tests unitaires, assertions, cas limites, arrange-act-assert, tests de non-régression",
                        "اختبارات الوحدة، التوكيدات، الحالات الحدّية، ترتيب-تنفيذ-توكيد، اختبارات الانحدار",
                    ),
                    blocks=[
                        Text(
                            T(
                                "A unit test has three parts: **arrange** the inputs, **act** by calling the code, **assert** what should be true. One behaviour per test, so a failure names the problem instead of just reporting one.",
                                "Un test unitaire a trois parties : **préparer** les entrées, **agir** en appelant le code, **vérifier** ce qui doit être vrai. Un comportement par test, pour qu'un échec nomme le problème au lieu de le signaler.",
                                "لاختبار الوحدة ثلاثة أجزاء: **تهيئة** المدخلات، ثمّ **التنفيذ** باستدعاء الكود، ثمّ **التوكيد** على ما يجب أن يكون صحيحًا. سلوك واحد لكلّ اختبار، كي يسمّي الفشل المشكلة بدل مجرّد الإبلاغ عنها.",
                            )
                        ),
                        Code(
                            T(
                                "The interesting tests are the ones at the boundaries:",
                                "Les tests intéressants sont ceux des frontières :",
                                "الاختبارات المثيرة للاهتمام هي اختبارات الحدود:",
                            ),
                            "def average(marks):\n"
                            "    if not marks:\n"
                            "        return None\n"
                            "    return sum(marks) / len(marks)\n\n"
                            "# The ordinary case proves it works at all...\n"
                            "assert average([10, 20]) == 15\n"
                            "# ...the edge cases prove it does not fall over.\n"
                            "assert average([]) is None\n"
                            "assert average([7]) == 7\n"
                            "print('all tests passed')",
                        ),
                        Text(
                            T(
                                "When you fix a bug, first write a test that fails because of it. That test then guards the fix forever — it is called a **regression test**, and it is the only reliable way to stop a bug coming back.",
                                "Quand vous corrigez un bug, écrivez d'abord un test qui échoue à cause de lui. Ce test protège ensuite la correction pour toujours — c'est un **test de non-régression**, le seul moyen fiable d'empêcher un bug de revenir.",
                                "عند إصلاح خلل، اكتب أوّلًا اختبارًا يفشل بسببه. عندئذٍ يحرس ذلك الاختبار الإصلاح إلى الأبد — ويُسمّى **اختبار انحدار**، وهو الوسيلة الموثوقة الوحيدة لمنع عودة الخلل.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "You have just fixed a bug. What is the most valuable next step?",
                                "Vous venez de corriger un bug. Quelle est l'étape suivante la plus utile ?",
                                "لقد أصلحت خللًا للتوّ. ما أنفع خطوة تالية؟",
                            ),
                            hint=T("Think about how you would know if the bug returned.", "Comment sauriez-vous que le bug est revenu ?", "كيف ستعرف أنّ الخلل عاد؟"),
                            explanation=T(
                                "A regression test that fails without the fix and passes with it is what keeps the bug from silently returning.",
                                "Un test de non-régression qui échoue sans la correction et passe avec elle est ce qui empêche le retour silencieux du bug.",
                                "اختبار الانحدار الذي يفشل بدون الإصلاح وينجح معه هو ما يمنع عودة الخلل بصمت.",
                            ),
                            options=[
                                Option(T("Delete the old code", "Supprimer l'ancien code", "احذف الكود القديم")),
                                Option(
                                    T(
                                        "Add a test that fails without the fix",
                                        "Ajouter un test qui échoue sans la correction",
                                        "أضف اختبارًا يفشل بدون الإصلاح",
                                    ),
                                    correct=True,
                                ),
                                Option(T("Add a comment describing the bug", "Ajouter un commentaire décrivant le bug", "أضف تعليقًا يصف الخلل")),
                                Option(T("Rename the function", "Renommer la fonction", "غيّر اسم الدالّة")),
                            ],
                        ),
                        CodeWriting(
                            prompt=T(
                                "Write `is_valid_mark(value)` returning True only when value is a number between 0 and 20 inclusive. Both bounds are valid.",
                                "Écrivez `is_valid_mark(value)` renvoyant True uniquement si value est un nombre entre 0 et 20 inclus. Les deux bornes sont valides.",
                                "اكتب `is_valid_mark(value)` تُرجع True فقط إذا كانت القيمة عددًا بين 0 و20 شاملًا الطرفين.",
                            ),
                            hint=T(
                                "Chained comparison: 0 <= value <= 20.",
                                "Comparaison chaînée : 0 <= value <= 20.",
                                "مقارنة متسلسلة: 0 <= value <= 20.",
                            ),
                            explanation=T(
                                "The boundaries 0 and 20 are the cases most implementations get wrong, which is exactly why they are tested.",
                                "Les bornes 0 et 20 sont les cas que la plupart des implémentations ratent, et c'est précisément pourquoi elles sont testées.",
                                "الحدّان 0 و20 هما أكثر ما تخطئ فيه التنفيذات، ولهذا بالذات يُختبَران.",
                            ),
                            starter_code="def is_valid_mark(value):\n    pass\n\nprint(is_valid_mark(20))",
                            solution_code="def is_valid_mark(value):\n    return 0 <= value <= 20\n\nprint(is_valid_mark(20))",
                            test_code=asserts(
                                "assert is_valid_mark(0) is True or is_valid_mark(0) == True",
                                "assert is_valid_mark(20)",
                                "assert not is_valid_mark(21)",
                                "assert not is_valid_mark(-1)",
                                "assert is_valid_mark(13.5)",
                            ),
                        ),
                    ],
                ),
                Lesson(
                    slug="environments-and-clean-code",
                    minutes=30,
                    xp=60,
                    difficulty=D.intermediate,
                    title=T("Virtual Environments and Clean Code", "Environnements Virtuels et Code Propre", "البيئات الافتراضية والكود النظيف"),
                    story=T(
                        "\"It works on my machine\" is a bug report, not a defence.",
                        "« Ça marche sur ma machine » est un rapport de bug, pas une défense.",
                        "«يعمل على جهازي» بلاغ عن خلل، لا دفاع.",
                    ),
                    objective=T(
                        "Isolate project dependencies with a virtual environment and apply the naming and structure rules that keep code readable.",
                        "Isoler les dépendances d'un projet avec un environnement virtuel et appliquer les règles de nommage et de structure qui gardent le code lisible.",
                        "عزل تبعيّات المشروع ببيئة افتراضية، وتطبيق قواعد التسمية والبنية التي تُبقي الكود مقروءًا.",
                    ),
                    skills=T(
                        "venv, pip, requirements, naming, functions, PEP 8",
                        "venv, pip, requirements, nommage, fonctions, PEP 8",
                        "‏venv، pip، ملفّ المتطلّبات، التسمية، الدوالّ، PEP 8",
                    ),
                    blocks=[
                        Text(
                            T(
                                "A **virtual environment** is a private copy of Python's package directory for one project. Without it, two projects that need different versions of the same library cannot coexist on one machine.",
                                "Un **environnement virtuel** est une copie privée du répertoire de paquets de Python pour un projet. Sans lui, deux projets exigeant des versions différentes d'une même bibliothèque ne peuvent coexister sur une machine.",
                                "**البيئة الافتراضية** نسخة خاصّة من مجلّد حزم بايثون لمشروع واحد. وبدونها لا يمكن لمشروعين يحتاجان إصدارين مختلفين من المكتبة نفسها أن يتعايشا على جهاز واحد.",
                            )
                        ),
                        Code(
                            T(
                                "The four commands that begin every Python project:",
                                "Les quatre commandes qui commencent tout projet Python :",
                                "الأوامر الأربعة التي يبدأ بها كلّ مشروع بايثون:",
                            ),
                            "# 1. create an environment inside the project folder\n"
                            "python -m venv .venv\n\n"
                            "# 2. activate it   (Linux/macOS: source .venv/bin/activate)\n"
                            ".venv\\\\Scripts\\\\activate\n\n"
                            "# 3. install what the project needs\n"
                            "pip install requests\n\n"
                            "# 4. record it so anyone can rebuild the same environment\n"
                            "pip freeze > requirements.txt",
                        ),
                        Text(
                            T(
                                "Clean code is mostly three habits. **Name things for what they mean**, not what type they are: `unpaid_invoices`, not `list2`. **Keep a function to one job** — if you need \"and\" to describe it, it is two functions. **Delete dead code** instead of commenting it out; version control already remembers it.",
                                "Le code propre tient surtout en trois habitudes. **Nommer selon le sens**, pas selon le type : `factures_impayees`, pas `liste2`. **Une fonction, une tâche** — s'il faut un « et » pour la décrire, ce sont deux fonctions. **Supprimer le code mort** au lieu de le commenter ; le contrôle de version s'en souvient déjà.",
                                "الكود النظيف ثلاث عادات في الأغلب. **سمِّ الأشياء بمعناها** لا بنوعها: `unpaid_invoices` لا `list2`. و**اجعل للدالّة عملًا واحدًا** — فإن احتجت «و» لوصفها فهي دالّتان. و**احذف الكود الميّت** بدل تعليقه؛ فنظام إدارة الإصدارات يتذكّره أصلًا.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "Why does each project get its own virtual environment?",
                                "Pourquoi chaque projet a-t-il son propre environnement virtuel ?",
                                "لماذا لكلّ مشروع بيئته الافتراضية الخاصّة؟",
                            ),
                            hint=T(
                                "Think about two projects needing different versions of one library.",
                                "Pensez à deux projets exigeant des versions différentes d'une bibliothèque.",
                                "فكّر في مشروعين يحتاجان إصدارين مختلفين من مكتبة واحدة.",
                            ),
                            explanation=T(
                                "Isolation lets each project pin the versions it needs without breaking any other project on the same machine.",
                                "L'isolation permet à chaque projet de fixer les versions dont il a besoin sans casser les autres projets de la machine.",
                                "العزل يتيح لكلّ مشروع تثبيت الإصدارات التي يحتاجها دون كسر أيّ مشروع آخر على الجهاز نفسه.",
                            ),
                            options=[
                                Option(T("It makes Python run faster", "Cela accélère Python", "يجعل بايثون أسرع")),
                                Option(
                                    T(
                                        "So each project can pin its own dependency versions",
                                        "Pour que chaque projet fixe ses propres versions de dépendances",
                                        "كي يثبّت كلّ مشروع إصدارات تبعيّاته الخاصّة",
                                    ),
                                    correct=True,
                                ),
                                Option(T("It encrypts the source code", "Cela chiffre le code source", "يشفّر الكود المصدري")),
                                Option(T("It is required to use functions", "C'est obligatoire pour utiliser des fonctions", "مطلوب لاستخدام الدوالّ")),
                            ],
                        ),
                        MCQ(
                            prompt=T(
                                "Which function name follows clean-code naming best?",
                                "Quel nom de fonction respecte le mieux le nommage propre ?",
                                "أيّ اسم دالّة يلتزم أفضل بقواعد التسمية النظيفة؟",
                            ),
                            hint=T("The name should say what it does, not how it is stored.", "Le nom doit dire ce qu'elle fait, pas comment c'est stocké.", "يجب أن يقول الاسم ما تفعله الدالّة لا كيف تُخزَّن البيانات."),
                            explanation=T(
                                "A verb plus a meaningful noun tells the reader the purpose without opening the body.",
                                "Un verbe et un nom parlant indiquent le but sans ouvrir le corps de la fonction.",
                                "فعل مع اسم ذي معنى يخبر القارئ بالغرض دون فتح جسم الدالّة.",
                            ),
                            options=[
                                Option(T("process_data2()", "process_data2()", "process_data2()")),
                                Option(T("calculate_unpaid_total()", "calculate_unpaid_total()", "calculate_unpaid_total()"), correct=True),
                                Option(T("doIt()", "doIt()", "doIt()")),
                                Option(T("theList()", "theList()", "theList()")),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)


async def seed_python_in_depth(db, order: int) -> int:
    print("Seeding Python in Depth...")
    return await seed_course(db, PYTHON_IN_DEPTH, order)
