"""Stage 1 — Computer Science Foundations.

Where a complete beginner starts: what the field actually is, what a computer
does when it runs a program, how everything ends up as numbers, and how to
reason logically. No prior programming is assumed, and nothing here depends on
a particular language.
"""

from app.models import DifficultyEnum as D

from .authoring import (
    AR,
    EN,
    FR,
    Code,
    CourseSpec,
    ExamTip,
    FillBlank,
    Hook,
    Lesson,
    MCQ,
    Module,
    Option,
    Ordering,
    Prediction,
    ShortAnswer,
    T,
    Text,
    seed_course,
)

CS_FOUNDATIONS = CourseSpec(
    slug="cs-foundations",
    stage=1,
    track="foundations",
    icon="🧭",
    difficulty=D.beginner,
    estimated_hours=6,
    title=T(
        "Computer Science Foundations",
        "Fondations de l'Informatique",
        "أسس علوم الحاسوب",
    ),
    description=T(
        "Start here. What computer science really is, what happens inside a machine when it runs your code, how everything becomes numbers, and how to reason with logic.",
        "Commencez ici. Ce qu'est vraiment l'informatique, ce qui se passe dans une machine quand elle exécute votre code, comment tout devient des nombres, et comment raisonner avec la logique.",
        "ابدأ من هنا. ما هي علوم الحاسوب حقًا، وما الذي يحدث داخل الجهاز عند تنفيذ الكود، وكيف يتحول كل شيء إلى أرقام، وكيف تفكر منطقيًا.",
    ),
    skills=T(
        "Computational problems, hardware basics, binary, data representation, boolean logic",
        "Problèmes calculatoires, bases du matériel, binaire, représentation des données, logique booléenne",
        "المسائل الحاسوبية، أساسيات العتاد، النظام الثنائي، تمثيل البيانات، المنطق البولياني",
    ),
    modules=[
        # ------------------------------------------------------------------
        Module(
            slug="what-is-cs",
            title=T("What Is Computer Science?", "Qu'est-ce que l'Informatique ?", "ما هي علوم الحاسوب؟"),
            description=T(
                "The field, its questions, and what makes a problem computational.",
                "Le domaine, ses questions, et ce qui rend un problème calculatoire.",
                "المجال وأسئلته، وما الذي يجعل المسألة قابلة للحوسبة.",
            ),
            lessons=[
                Lesson(
                    slug="what-is-computer-science",
                    minutes=25,
                    xp=50,
                    difficulty=D.beginner,
                    title=T("What Is Computer Science?", "Qu'est-ce que l'Informatique ?", "ما هي علوم الحاسوب؟"),
                    story=T(
                        "Computer science is not the study of computers, any more than astronomy is the study of telescopes.",
                        "L'informatique n'est pas l'étude des ordinateurs, pas plus que l'astronomie n'est l'étude des télescopes.",
                        "علوم الحاسوب ليست دراسة الحواسيب، تمامًا كما أنّ علم الفلك ليس دراسة التلسكوبات.",
                    ),
                    objective=T(
                        "Explain what computer science studies and tell a computational problem from one that is not.",
                        "Expliquer ce qu'étudie l'informatique et distinguer un problème calculatoire d'un problème qui ne l'est pas.",
                        "شرح ما تدرسه علوم الحاسوب والتمييز بين المسألة الحاسوبية وغيرها.",
                    ),
                    skills=T(
                        "Definition of CS, computational problems, algorithms vs programs",
                        "Définition de l'informatique, problèmes calculatoires, algorithmes vs programmes",
                        "تعريف علوم الحاسوب، المسائل الحاسوبية، الخوارزميات مقابل البرامج",
                    ),
                    blocks=[
                        Hook(
                            T(
                                "Your school needs to split 340 students into project groups of four, making sure no group repeats last year's line-up. A teacher could spend a weekend on it. What would you need to know to have a computer do it in a second?",
                                "Votre école doit répartir 340 élèves en groupes de projet de quatre, sans reproduire les équipes de l'an dernier. Un enseignant y passerait un week-end. Que faudrait-il savoir pour qu'un ordinateur le fasse en une seconde ?",
                                "تحتاج مدرستك إلى تقسيم 340 طالبًا إلى مجموعات من أربعة، دون تكرار مجموعات العام الماضي. قد يستغرق ذلك من المعلّم عطلة كاملة. ما الذي تحتاج معرفته ليقوم الحاسوب بذلك في ثانية؟",
                            ),
                            T(
                                "Describe the task precisely enough that a machine could follow it.",
                                "Décrire la tâche assez précisément pour qu'une machine puisse la suivre.",
                                "صف المهمة بدقة كافية ليتمكن الجهاز من تنفيذها.",
                            ),
                        ),
                        Text(
                            T(
                                "Computer science is the study of **problems, and of the procedures that solve them**. The computer is the instrument, not the subject. A computer scientist asks: can this problem be solved at all? If so, by what procedure? How fast, and using how much memory? And is there a better procedure than the obvious one?",
                                "L'informatique est l'étude des **problèmes et des procédures qui les résolvent**. L'ordinateur est l'instrument, pas le sujet. L'informaticien se demande : ce problème peut-il être résolu ? Si oui, par quelle procédure ? À quelle vitesse et avec combien de mémoire ? Et existe-t-il une meilleure procédure que la plus évidente ?",
                                "علوم الحاسوب هي دراسة **المسائل والإجراءات التي تحلّها**. الحاسوب هو الأداة وليس الموضوع. يسأل عالم الحاسوب: هل يمكن حلّ هذه المسألة أصلًا؟ وإذا كان كذلك، بأيّ إجراء؟ وبأيّ سرعة وبكم من الذاكرة؟ وهل هناك إجراء أفضل من الواضح؟",
                            )
                        ),
                        Text(
                            T(
                                "A problem is **computational** when its input and its correct output can both be described exactly. \"Sort these names alphabetically\" is computational: given any list, there is one right answer. \"Write a beautiful poem\" is not, because there is no test that decides whether the output is correct.",
                                "Un problème est **calculatoire** lorsque son entrée et sa sortie correcte peuvent être décrites exactement. « Trier ces noms par ordre alphabétique » est calculatoire : pour toute liste, il existe une seule bonne réponse. « Écrire un beau poème » ne l'est pas, car aucun test ne décide si la sortie est correcte.",
                                "تكون المسألة **حاسوبية** عندما يمكن وصف مدخلاتها ومخرجاتها الصحيحة وصفًا دقيقًا. «رتّب هذه الأسماء أبجديًا» مسألة حاسوبية: لأي قائمة توجد إجابة صحيحة واحدة. أما «اكتب قصيدة جميلة» فليست كذلك، لأنه لا يوجد اختبار يقرّر صحة المخرجات.",
                            )
                        ),
                        Code(
                            T(
                                "An algorithm is the idea; a program is that idea written in a language a machine can run. The same algorithm, two programs:",
                                "L'algorithme est l'idée ; le programme est cette idée écrite dans un langage exécutable. Le même algorithme, deux programmes :",
                                "الخوارزمية هي الفكرة؛ والبرنامج هو تلك الفكرة مكتوبة بلغة ينفّذها الجهاز. الخوارزمية نفسها في برنامجين:",
                            ),
                            "# Algorithm: look at every number, remember the largest one seen.\n\n"
                            "# Program 1 - Python\n"
                            "def largest(numbers):\n"
                            "    biggest = numbers[0]\n"
                            "    for value in numbers:\n"
                            "        if value > biggest:\n"
                            "            biggest = value\n"
                            "    return biggest\n\n"
                            "# Program 2 - the same algorithm in JavaScript\n"
                            "# function largest(numbers) {\n"
                            "#   let biggest = numbers[0];\n"
                            "#   for (const value of numbers) {\n"
                            "#     if (value > biggest) biggest = value;\n"
                            "#   }\n"
                            "#   return biggest;\n"
                            "# }\n\n"
                            "print(largest([3, 17, 8, 42, 5]))",
                        ),
                        ExamTip(
                            T(
                                "If you are asked to define computer science, do not say \"the study of computers\". Say: the study of computational problems and the algorithms that solve them, including what can be computed and at what cost.",
                                "Si l'on vous demande de définir l'informatique, ne dites pas « l'étude des ordinateurs ». Dites : l'étude des problèmes calculatoires et des algorithmes qui les résolvent, y compris ce qui est calculable et à quel coût.",
                                "إذا طُلب منك تعريف علوم الحاسوب، لا تقل «دراسة الحواسيب». قل: دراسة المسائل الحاسوبية والخوارزميات التي تحلّها، بما في ذلك ما يمكن حسابه وبأيّ كلفة.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "Which of these is a computational problem?",
                                "Lequel de ces énoncés est un problème calculatoire ?",
                                "أيّ ممّا يلي يُعدّ مسألة حاسوبية؟",
                            ),
                            hint=T(
                                "Ask whether there is a test that decides if an answer is right.",
                                "Demandez-vous s'il existe un test qui décide si une réponse est correcte.",
                                "اسأل نفسك: هل يوجد اختبار يقرّر صحة الإجابة؟",
                            ),
                            explanation=T(
                                "Finding the shortest route has a precisely defined input (a map, two points) and a checkable correct output. Beauty and enjoyment have no such test.",
                                "Trouver l'itinéraire le plus court a une entrée définie précisément (une carte, deux points) et une sortie correcte vérifiable. La beauté et le plaisir n'ont pas ce test.",
                                "إيجاد أقصر مسار له مدخلات محدّدة بدقّة (خريطة ونقطتان) ومخرجات صحيحة قابلة للتحقّق. أما الجمال والمتعة فلا يوجد لهما اختبار كهذا.",
                            ),
                            options=[
                                Option(T("Deciding which song is the most beautiful", "Décider quelle chanson est la plus belle", "تحديد أجمل أغنية")),
                                Option(
                                    T(
                                        "Finding the shortest route between two bus stops",
                                        "Trouver l'itinéraire le plus court entre deux arrêts de bus",
                                        "إيجاد أقصر مسار بين محطتي حافلات",
                                    ),
                                    correct=True,
                                ),
                                Option(T("Choosing a career you will enjoy", "Choisir une carrière qui vous plaira", "اختيار مهنة تستمتع بها")),
                                Option(T("Deciding whether a film deserves an award", "Décider si un film mérite un prix", "تحديد ما إذا كان الفيلم يستحق جائزة")),
                            ],
                        ),
                        ShortAnswer(
                            prompt=T(
                                "In one or two sentences, explain the difference between an algorithm and a program.",
                                "En une ou deux phrases, expliquez la différence entre un algorithme et un programme.",
                                "في جملة أو جملتين، اشرح الفرق بين الخوارزمية والبرنامج.",
                            ),
                            hint=T(
                                "One is an idea; the other is that idea written in a particular language.",
                                "L'un est une idée ; l'autre est cette idée écrite dans un langage particulier.",
                                "إحداهما فكرة، والأخرى هي تلك الفكرة مكتوبة بلغة معيّنة.",
                            ),
                            explanation=T(
                                "An algorithm is a language-independent procedure. A program is one concrete implementation of it, written in a specific programming language so a machine can run it.",
                                "Un algorithme est une procédure indépendante du langage. Un programme en est une implémentation concrète, écrite dans un langage précis pour être exécutée par une machine.",
                                "الخوارزمية إجراء مستقل عن اللغة. أما البرنامج فهو تنفيذ ملموس لها بلغة برمجة محدّدة كي ينفّذها الجهاز.",
                            ),
                            keywords=[["algorithm", "algorithme", "خوارزمية"], ["program", "programme", "برنامج"], ["language", "langage", "لغة"]],
                            reference_answer="An algorithm is a language-independent procedure for solving a problem; a program is that algorithm written in a particular programming language so a computer can run it.",
                        ),
                    ],
                ),
                Lesson(
                    slug="problems-inputs-outputs",
                    minutes=25,
                    xp=50,
                    difficulty=D.beginner,
                    title=T("Problems, Inputs and Outputs", "Problèmes, Entrées et Sorties", "المسائل والمدخلات والمخرجات"),
                    story=T(
                        "Before you can solve anything, you have to say exactly what you were asked.",
                        "Avant de pouvoir résoudre quoi que ce soit, il faut énoncer exactement ce qui est demandé.",
                        "قبل أن تحلّ أيّ شيء، عليك أن تحدّد بدقّة ما طُلب منك.",
                    ),
                    objective=T(
                        "Write a precise problem specification: inputs, outputs, constraints and edge cases.",
                        "Rédiger une spécification précise : entrées, sorties, contraintes et cas limites.",
                        "كتابة مواصفة دقيقة للمسألة: المدخلات والمخرجات والقيود والحالات الحدّية.",
                    ),
                    skills=T(
                        "Specifications, input/output, constraints, edge cases",
                        "Spécifications, entrée/sortie, contraintes, cas limites",
                        "المواصفات، المدخلات/المخرجات، القيود، الحالات الحدّية",
                    ),
                    blocks=[
                        Text(
                            T(
                                "Every computational problem has three parts. **Input**: what you are given. **Output**: what must come back. **Constraints**: the rules the answer has to respect. Vagueness in any of the three is where most bugs are born.",
                                "Tout problème calculatoire a trois parties. **Entrée** : ce qui est donné. **Sortie** : ce qui doit être renvoyé. **Contraintes** : les règles que la réponse doit respecter. Le flou dans l'une des trois est l'origine de la plupart des bugs.",
                                "لكلّ مسألة حاسوبية ثلاثة أجزاء. **المدخلات**: ما يُعطى لك. **المخرجات**: ما يجب إرجاعه. **القيود**: القواعد التي يجب أن تحترمها الإجابة. والغموض في أيّ منها هو منشأ معظم الأخطاء البرمجية.",
                            )
                        ),
                        Code(
                            T(
                                "\"Find the average mark\" looks obvious until you write the specification:",
                                "« Trouver la moyenne des notes » paraît évident jusqu'à ce qu'on écrive la spécification :",
                                "«احسب معدّل الدرجات» يبدو واضحًا حتى تكتب المواصفة:",
                            ),
                            "# Input:       a list of marks, each between 0 and 20\n"
                            "# Output:      their arithmetic mean, as a number\n"
                            "# Constraints: an empty list has no mean -> return None\n"
                            "#              marks outside 0..20 are invalid input\n\n"
                            "def average(marks):\n"
                            "    if not marks:            # the edge case, decided up front\n"
                            "        return None\n"
                            "    return sum(marks) / len(marks)\n\n"
                            "print(average([12, 15, 18]))\n"
                            "print(average([]))",
                        ),
                        Text(
                            T(
                                "An **edge case** is a legal input that sits at the boundary of the rules: the empty list, the single item, the largest allowed value, the duplicate. Deciding what these should do is part of stating the problem, not part of debugging it later.",
                                "Un **cas limite** est une entrée valide située à la frontière des règles : la liste vide, l'élément unique, la valeur maximale autorisée, le doublon. Décider de leur comportement fait partie de l'énoncé du problème, pas du débogage ultérieur.",
                                "**الحالة الحدّية** هي مدخل صحيح يقع على حدود القواعد: القائمة الفارغة، العنصر الوحيد، أكبر قيمة مسموحة، التكرار. وتحديد سلوكها جزء من صياغة المسألة، لا من تصحيح الأخطاء لاحقًا.",
                            )
                        ),
                    ],
                    exercises=[
                        Prediction(
                            prompt=T(
                                "What does this program print?",
                                "Qu'affiche ce programme ?",
                                "ما الذي يطبعه هذا البرنامج؟",
                            ),
                            hint=T(
                                "Follow the empty-list case first.",
                                "Suivez d'abord le cas de la liste vide.",
                                "تتبّع حالة القائمة الفارغة أوّلًا.",
                            ),
                            explanation=T(
                                "The empty list is handled before any division, so it returns None; the second call averages 12, 15 and 18 to 15.0.",
                                "La liste vide est traitée avant toute division, donc None est renvoyé ; le second appel donne la moyenne de 12, 15 et 18, soit 15.0.",
                                "تُعالَج القائمة الفارغة قبل أيّ قسمة فتُرجع None؛ والاستدعاء الثاني يعطي معدّل 12 و15 و18 وهو 15.0.",
                            ),
                            code="def average(marks):\n    if not marks:\n        return None\n    return sum(marks) / len(marks)\n\nprint(average([]))\nprint(average([12, 15, 18]))",
                            expected_output="None\n15.0",
                        ),
                        MCQ(
                            prompt=T(
                                "Which of these is an edge case for \"find the largest number in a list\"?",
                                "Lequel est un cas limite pour « trouver le plus grand nombre d'une liste » ?",
                                "أيّ ممّا يلي حالة حدّية لمسألة «أوجد أكبر عدد في القائمة»؟",
                            ),
                            hint=T(
                                "Think about the smallest legal input you could be handed.",
                                "Pensez à la plus petite entrée valide qu'on puisse vous donner.",
                                "فكّر في أصغر مدخل صحيح يمكن أن يُعطى لك.",
                            ),
                            explanation=T(
                                "A list with no elements has no largest value, so the specification must say what happens. A list of ten ordinary numbers is just a normal case.",
                                "Une liste sans élément n'a pas de plus grande valeur : la spécification doit dire ce qui se passe. Une liste de dix nombres ordinaires est un cas normal.",
                                "القائمة الخالية لا تحتوي على أكبر قيمة، لذا يجب أن تحدّد المواصفة ما يحدث. أما قائمة من عشرة أعداد عادية فهي حالة اعتيادية.",
                            ),
                            options=[
                                Option(T("A list of ten different numbers", "Une liste de dix nombres différents", "قائمة من عشرة أعداد مختلفة")),
                                Option(T("An empty list", "Une liste vide", "قائمة فارغة"), correct=True),
                                Option(T("A list sorted in ascending order", "Une liste triée par ordre croissant", "قائمة مرتّبة تصاعديًا")),
                                Option(T("A list of positive numbers", "Une liste de nombres positifs", "قائمة من الأعداد الموجبة")),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        # ------------------------------------------------------------------
        Module(
            slug="how-computers-work",
            title=T("How Computers Work", "Comment Fonctionnent les Ordinateurs", "كيف تعمل الحواسيب"),
            description=T(
                "The parts of a machine and what actually happens when your code runs.",
                "Les composants d'une machine et ce qui se passe réellement à l'exécution de votre code.",
                "مكوّنات الجهاز وما يحدث فعليًا عند تنفيذ الكود.",
            ),
            lessons=[
                Lesson(
                    slug="inside-a-computer",
                    minutes=30,
                    xp=50,
                    difficulty=D.beginner,
                    title=T("Inside a Computer", "À l'Intérieur d'un Ordinateur", "داخل الحاسوب"),
                    story=T(
                        "Four parts, one loop, endlessly repeated a few billion times a second.",
                        "Quatre composants, une boucle, répétée quelques milliards de fois par seconde.",
                        "أربعة مكوّنات وحلقة واحدة تتكرّر بلايين المرّات في الثانية.",
                    ),
                    objective=T(
                        "Name the CPU, RAM, storage and I/O, and say what each one is responsible for.",
                        "Nommer le processeur, la RAM, le stockage et les E/S, et dire de quoi chacun est responsable.",
                        "تسمية المعالج والذاكرة والتخزين والمدخلات/المخرجات وتحديد مسؤولية كلّ منها.",
                    ),
                    skills=T(
                        "CPU, RAM, storage, I/O, fetch-decode-execute",
                        "CPU, RAM, stockage, E/S, chercher-décoder-exécuter",
                        "المعالج، الذاكرة، التخزين، المدخلات/المخرجات، الجلب والفكّ والتنفيذ",
                    ),
                    blocks=[
                        Text(
                            T(
                                "**CPU** — carries out instructions, one at a time, extremely fast. **RAM** — fast working memory that holds what is being used right now, and forgets everything when the power goes. **Storage** (SSD/disk) — slower, but keeps its contents. **I/O** — keyboard, screen, network: how the machine meets the world.",
                                "**Processeur (CPU)** — exécute les instructions une par une, très vite. **RAM** — mémoire de travail rapide qui contient ce qui sert maintenant et oublie tout à l'extinction. **Stockage** (SSD/disque) — plus lent, mais conserve son contenu. **E/S** — clavier, écran, réseau : la rencontre de la machine et du monde.",
                                "**المعالج (CPU)** — ينفّذ التعليمات واحدة تلو الأخرى وبسرعة هائلة. **الذاكرة (RAM)** — ذاكرة عمل سريعة تحمل ما يُستخدم الآن وتنسى كلّ شيء عند انقطاع الطاقة. **التخزين** (SSD/قرص) — أبطأ لكنّه يحتفظ بمحتواه. **المدخلات/المخرجات** — لوحة المفاتيح والشاشة والشبكة: لقاء الجهاز بالعالم.",
                            )
                        ),
                        Text(
                            T(
                                "The CPU repeats one loop forever: **fetch** the next instruction from memory, **decode** what it means, **execute** it, then move on. Everything a computer has ever done is that loop, run often enough.",
                                "Le processeur répète une boucle sans fin : **chercher** l'instruction suivante en mémoire, **décoder** son sens, l'**exécuter**, puis passer à la suivante. Tout ce qu'un ordinateur a jamais fait, c'est cette boucle, répétée assez souvent.",
                                "يكرّر المعالج حلقة واحدة إلى ما لا نهاية: **جلب** التعليمة التالية من الذاكرة، ثمّ **فكّ** معناها، ثمّ **تنفيذها**، ثمّ الانتقال. كلّ ما فعله الحاسوب يومًا هو هذه الحلقة مكرّرة بما يكفي.",
                            )
                        ),
                        Code(
                            T(
                                "Why RAM matters: this loop touches memory 3 million times, and the difference between RAM and disk is roughly the difference between a second and a day.",
                                "Pourquoi la RAM compte : cette boucle accède à la mémoire 3 millions de fois, et l'écart entre RAM et disque équivaut à peu près à celui entre une seconde et une journée.",
                                "لماذا تهمّ الذاكرة: هذه الحلقة تصل إلى الذاكرة 3 ملايين مرّة، والفرق بين الذاكرة والقرص يشبه تقريبًا الفرق بين ثانية ويوم كامل.",
                            ),
                            "total = 0\n"
                            "for i in range(3_000_000):   # fetch, decode, execute - 3 million times\n"
                            "    total += i\n"
                            "print(total)",
                        ),
                        ExamTip(
                            T(
                                "RAM is volatile (lost on power-off) and fast; storage is persistent and slow. Saying \"memory\" when you mean storage is the single most common mix-up in exam answers.",
                                "La RAM est volatile (perdue à l'extinction) et rapide ; le stockage est persistant et lent. Dire « mémoire » pour désigner le stockage est la confusion la plus fréquente aux examens.",
                                "الذاكرة RAM متطايرة (تُفقد عند انقطاع الطاقة) وسريعة، والتخزين دائم وبطيء. وقول «ذاكرة» بمعنى «تخزين» هو أكثر الأخطاء شيوعًا في الامتحانات.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "You close a document without saving and the text is gone. Which component was holding it?",
                                "Vous fermez un document sans l'enregistrer et le texte disparaît. Quel composant le contenait ?",
                                "أغلقت مستندًا دون حفظه فاختفى النصّ. أيّ مكوّن كان يحتفظ به؟",
                            ),
                            hint=T(
                                "Which one forgets everything when it stops being powered?",
                                "Lequel oublie tout lorsqu'il n'est plus alimenté ?",
                                "أيّها ينسى كلّ شيء عند انقطاع الطاقة عنه؟",
                            ),
                            explanation=T(
                                "Unsaved work lives only in RAM, which is volatile. Saving copies it to storage, which survives.",
                                "Le travail non enregistré ne vit que dans la RAM, qui est volatile. Enregistrer le copie vers le stockage, qui persiste.",
                                "العمل غير المحفوظ يوجد في الذاكرة RAM فقط، وهي متطايرة. أما الحفظ فينسخه إلى التخزين الذي يبقى.",
                            ),
                            options=[
                                Option(T("RAM", "La RAM", "الذاكرة RAM"), correct=True),
                                Option(T("The SSD", "Le SSD", "قرص SSD")),
                                Option(T("The network card", "La carte réseau", "بطاقة الشبكة")),
                                Option(T("The screen", "L'écran", "الشاشة")),
                            ],
                        ),
                        Ordering(
                            prompt=T(
                                "Put the CPU's instruction cycle in order.",
                                "Remettez le cycle d'instruction du processeur dans l'ordre.",
                                "رتّب دورة التعليمة في المعالج.",
                            ),
                            hint=T(
                                "You cannot decode something you have not collected yet.",
                                "On ne peut pas décoder ce qu'on n'a pas encore récupéré.",
                                "لا يمكن فكّ ما لم تجلبه بعد.",
                            ),
                            explanation=T(
                                "Fetch, decode, execute, then advance to the next instruction — repeated billions of times per second.",
                                "Chercher, décoder, exécuter, puis passer à l'instruction suivante — répété des milliards de fois par seconde.",
                                "الجلب ثمّ الفكّ ثمّ التنفيذ ثمّ الانتقال إلى التعليمة التالية — وتتكرّر بلايين المرّات في الثانية.",
                            ),
                            steps=[
                                T("Fetch the instruction from memory", "Chercher l'instruction en mémoire", "جلب التعليمة من الذاكرة"),
                                T("Decode what the instruction means", "Décoder le sens de l'instruction", "فكّ معنى التعليمة"),
                                T("Execute the operation", "Exécuter l'opération", "تنفيذ العملية"),
                                T("Move to the next instruction", "Passer à l'instruction suivante", "الانتقال إلى التعليمة التالية"),
                            ],
                        ),
                    ],
                ),
                Lesson(
                    slug="how-a-program-runs",
                    minutes=30,
                    xp=50,
                    difficulty=D.beginner,
                    title=T("How a Program Runs", "Comment s'Exécute un Programme", "كيف يُنفَّذ البرنامج"),
                    story=T(
                        "From the text you typed to something a processor can obey.",
                        "Du texte que vous avez tapé à quelque chose qu'un processeur peut obéir.",
                        "من النصّ الذي كتبته إلى شيء يستطيع المعالج تنفيذه.",
                    ),
                    objective=T(
                        "Describe how source code becomes machine instructions, and the difference between compiling and interpreting.",
                        "Décrire comment le code source devient des instructions machine, et la différence entre compilation et interprétation.",
                        "وصف كيف يتحوّل الكود المصدري إلى تعليمات آلة، والفرق بين التصريف والتفسير.",
                    ),
                    skills=T(
                        "Source code, machine code, compilers, interpreters, processes",
                        "Code source, code machine, compilateurs, interpréteurs, processus",
                        "الكود المصدري، كود الآلة، المصرّفات، المفسّرات، العمليات",
                    ),
                    blocks=[
                        Text(
                            T(
                                "A CPU understands only numbers that stand for very small operations: add these two registers, jump if zero. Your source code is text. Something has to bridge the gap.",
                                "Un processeur ne comprend que des nombres représentant de très petites opérations : additionner ces deux registres, sauter si zéro. Votre code source est du texte. Quelque chose doit combler l'écart.",
                                "لا يفهم المعالج إلّا أرقامًا تمثّل عمليات صغيرة جدًا: اجمع هذين المسجّلين، اقفز إذا كانت النتيجة صفرًا. أما كودك فهو نصّ. لا بدّ من شيء يسدّ الفجوة.",
                            )
                        ),
                        Text(
                            T(
                                "A **compiler** translates the whole program ahead of time into machine code (C, C++, Rust). An **interpreter** reads and carries out the program as it goes (Python, JavaScript). Compiling gives speed; interpreting gives immediacy — you change a line and run it, with no build step.",
                                "Un **compilateur** traduit tout le programme à l'avance en code machine (C, C++, Rust). Un **interpréteur** lit et exécute le programme au fil de l'eau (Python, JavaScript). La compilation donne la vitesse ; l'interprétation donne l'immédiateté — on modifie une ligne et on l'exécute, sans étape de construction.",
                                "**المصرّف** يترجم البرنامج كلّه مسبقًا إلى كود آلة (C وC++ وRust). و**المفسّر** يقرأ البرنامج وينفّذه أثناء سيره (Python وJavaScript). التصريف يمنح السرعة، والتفسير يمنح الفورية — تغيّر سطرًا وتنفّذه دون خطوة بناء.",
                            )
                        ),
                        Code(
                            T(
                                "Python compiles to bytecode first, then interprets it. You can look at the bytecode:",
                                "Python compile d'abord en bytecode, puis l'interprète. On peut regarder ce bytecode :",
                                "يُصرّف بايثون إلى bytecode أوّلًا ثمّ يفسّره. ويمكنك الاطّلاع على ذلك:",
                            ),
                            "import dis\n\n"
                            "def add_tax(price):\n"
                            "    return price * 1.2\n\n"
                            "dis.dis(add_tax)   # the small steps the interpreter will follow",
                        ),
                        Text(
                            T(
                                "When the program starts, the operating system creates a **process**: a private slice of memory plus the right to use the CPU in turns. That is why one crashing program does not take the rest of the machine with it.",
                                "Au démarrage, le système d'exploitation crée un **processus** : une portion privée de mémoire et le droit d'utiliser le processeur à tour de rôle. C'est pourquoi un programme qui plante n'entraîne pas le reste de la machine.",
                                "عند بدء البرنامج ينشئ نظام التشغيل **عملية** (process): جزءًا خاصًا من الذاكرة وحقّ استخدام المعالج بالتناوب. لهذا لا يُسقط انهيار برنامج واحد بقيّة الجهاز.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "Which statement describes an interpreter?",
                                "Quel énoncé décrit un interpréteur ?",
                                "أيّ عبارة تصف المفسّر؟",
                            ),
                            hint=T(
                                "Think about when the translation happens.",
                                "Pensez au moment où la traduction a lieu.",
                                "فكّر في اللحظة التي تحدث فيها الترجمة.",
                            ),
                            explanation=T(
                                "An interpreter executes the program as it reads it, with no separate build step producing a machine-code file.",
                                "Un interpréteur exécute le programme au fur et à mesure de sa lecture, sans étape de construction produisant un fichier en code machine.",
                                "ينفّذ المفسّر البرنامج أثناء قراءته، دون خطوة بناء منفصلة تنتج ملفًا بكود الآلة.",
                            ),
                            options=[
                                Option(
                                    T(
                                        "It reads and runs the program step by step, with no separate build",
                                        "Il lit et exécute le programme pas à pas, sans construction séparée",
                                        "يقرأ البرنامج وينفّذه خطوة بخطوة دون بناء منفصل",
                                    ),
                                    correct=True,
                                ),
                                Option(T("It converts the whole program to machine code before running", "Il convertit tout le programme en code machine avant l'exécution", "يحوّل البرنامج كلّه إلى كود آلة قبل التنفيذ")),
                                Option(T("It stores the program on disk", "Il stocke le programme sur le disque", "يخزّن البرنامج على القرص")),
                                Option(T("It allocates the process's memory", "Il alloue la mémoire du processus", "يخصّص ذاكرة العملية")),
                            ],
                        ),
                        FillBlank(
                            prompt=T(
                                "Complete the sentence about translation strategies.",
                                "Complétez la phrase sur les stratégies de traduction.",
                                "أكمل الجملة عن استراتيجيّتَي الترجمة.",
                            ),
                            hint=T(
                                "One translates everything up front; the other translates as it runs.",
                                "L'une traduit tout d'avance ; l'autre traduit au fil de l'exécution.",
                                "إحداهما تترجم كلّ شيء مسبقًا والأخرى تترجم أثناء التنفيذ.",
                            ),
                            explanation=T(
                                "A compiler translates ahead of time; an interpreter translates during execution.",
                                "Un compilateur traduit à l'avance ; un interpréteur traduit pendant l'exécution.",
                                "المصرّف يترجم مسبقًا، والمفسّر يترجم أثناء التنفيذ.",
                            ),
                            snippet="A ____ translates the whole program before it runs, while an ____ translates and runs it line by line.",
                            answers=["compiler", "interpreter"],
                        ),
                    ],
                ),
            ],
        ),
        # ------------------------------------------------------------------
        Module(
            slug="binary-and-data",
            title=T("Binary and Data Representation", "Binaire et Représentation des Données", "النظام الثنائي وتمثيل البيانات"),
            description=T(
                "Why everything — numbers, text, pictures, sound — ends up as ones and zeros.",
                "Pourquoi tout — nombres, texte, images, son — finit en uns et zéros.",
                "لماذا ينتهي كلّ شيء — الأعداد والنصوص والصور والصوت — إلى أصفار وآحاد.",
            ),
            lessons=[
                Lesson(
                    slug="binary-numbers",
                    minutes=35,
                    xp=60,
                    difficulty=D.beginner,
                    title=T("Binary Numbers", "Les Nombres Binaires", "الأعداد الثنائية"),
                    story=T(
                        "A wire is either carrying current or it is not. From that one fact, everything follows.",
                        "Un fil conduit du courant ou n'en conduit pas. De ce seul fait, tout découle.",
                        "السلك إمّا يحمل تيّارًا أو لا. ومن هذه الحقيقة وحدها ينبع كلّ شيء.",
                    ),
                    objective=T(
                        "Convert between binary and decimal, and explain bits, bytes and place value.",
                        "Convertir entre binaire et décimal, et expliquer bits, octets et valeur de position.",
                        "التحويل بين الثنائي والعشري، وشرح البِت والبايت والقيمة المكانية.",
                    ),
                    skills=T(
                        "Bits, bytes, place value, binary/decimal conversion, overflow",
                        "Bits, octets, valeur de position, conversion binaire/décimal, dépassement",
                        "البتّات، البايتات، القيمة المكانية، التحويل الثنائي/العشري، الفيضان",
                    ),
                    blocks=[
                        Text(
                            T(
                                "A **bit** is one yes-or-no. Eight bits make a **byte**, which can hold 2⁸ = 256 different values. Binary is ordinary place-value arithmetic with two digits instead of ten: each position is worth twice the one to its right.",
                                "Un **bit** est un oui-ou-non. Huit bits font un **octet**, qui peut contenir 2⁸ = 256 valeurs différentes. Le binaire est l'arithmétique de position ordinaire avec deux chiffres au lieu de dix : chaque position vaut le double de celle à sa droite.",
                                "**البِت** هو نعم أو لا. وثمانية بتّات تكوّن **بايتًا** يمكنه حمل 2⁸ = 256 قيمة مختلفة. والنظام الثنائي هو حساب القيمة المكانية المعتاد لكن برقمين بدل عشرة: كلّ خانة تساوي ضِعف التي على يمينها.",
                            )
                        ),
                        Code(
                            T(
                                "Reading a binary number is adding up the positions that hold a 1:",
                                "Lire un nombre binaire, c'est additionner les positions qui portent un 1 :",
                                "قراءة العدد الثنائي هي جمع الخانات التي تحمل 1:",
                            ),
                            "#   1     0     1     1     0     1\n"
                            "#  32    16     8     4     2     1     <- place values\n"
                            "#  32  +  0  +  8  +  4  +  0  +  1  =  45\n\n"
                            "print(0b101101)          # 45  - binary literal\n"
                            "print(bin(45))           # '0b101101'\n"
                            "print(int('101101', 2))  # 45  - parse base 2",
                        ),
                        Text(
                            T(
                                "Fixed-width storage has a ceiling. Eight bits count from 0 to 255; ask for 256 and it wraps around to 0. That wrap-around is **overflow**, and it has crashed rockets and grounded aircraft.",
                                "Un stockage de largeur fixe a un plafond. Huit bits comptent de 0 à 255 ; demandez 256 et on repasse à 0. Ce retour à zéro est le **dépassement**, et il a détruit des fusées et cloué des avions au sol.",
                                "التخزين ذو العرض الثابت له سقف. ثمانية بتّات تعدّ من 0 إلى 255؛ فإذا طلبت 256 عاد العدّاد إلى 0. هذا الالتفاف هو **الفيضان (overflow)**، وقد تسبّب في تحطّم صواريخ ومنع طائرات من الطيران.",
                            )
                        ),
                        ExamTip(
                            T(
                                "n bits give 2ⁿ distinct values, counting from 0 to 2ⁿ − 1. Writing 2ⁿ as the largest value instead of the count is the classic lost mark.",
                                "n bits donnent 2ⁿ valeurs distinctes, de 0 à 2ⁿ − 1. Écrire 2ⁿ comme valeur maximale au lieu du nombre de valeurs est l'erreur classique.",
                                "n بتّات تعطي 2ⁿ قيمة مختلفة تُعدّ من 0 إلى 2ⁿ − 1. وكتابة 2ⁿ كأكبر قيمة بدل عدد القيم خطأ شائع يفقدك الدرجة.",
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
                                "Add the place values where a 1 appears: 8 + 4 + 0 + 1.",
                                "Additionnez les valeurs de position où figure un 1 : 8 + 4 + 0 + 1.",
                                "اجمع القيم المكانية حيث يظهر 1: 8 + 4 + 0 + 1.",
                            ),
                            explanation=T(
                                "1101 in binary is 8 + 4 + 1 = 13, and bin() shows the same value back in base 2.",
                                "1101 en binaire vaut 8 + 4 + 1 = 13, et bin() réaffiche la même valeur en base 2.",
                                "القيمة 1101 ثنائيًا تساوي 8 + 4 + 1 = 13، وتعيد bin() القيمة نفسها بالأساس 2.",
                            ),
                            code="print(int('1101', 2))\nprint(bin(13))",
                            expected_output="13\n0b1101",
                        ),
                        MCQ(
                            prompt=T(
                                "How many different values can 4 bits represent?",
                                "Combien de valeurs différentes 4 bits peuvent-ils représenter ?",
                                "كم قيمة مختلفة يمكن أن تمثّلها 4 بتّات؟",
                            ),
                            hint=T("2 to the power of the number of bits.", "2 à la puissance du nombre de bits.", "2 مرفوعًا لعدد البتّات."),
                            explanation=T(
                                "2⁴ = 16 values, numbered 0 to 15.",
                                "2⁴ = 16 valeurs, numérotées de 0 à 15.",
                                "2⁴ = 16 قيمة، مرقّمة من 0 إلى 15.",
                            ),
                            options=[
                                Option(T("8", "8", "8")),
                                Option(T("15", "15", "15")),
                                Option(T("16", "16", "16"), correct=True),
                                Option(T("32", "32", "32")),
                            ],
                        ),
                    ],
                ),
                Lesson(
                    slug="representing-text-and-media",
                    minutes=30,
                    xp=55,
                    difficulty=D.beginner,
                    title=T("Representing Text, Images and Sound", "Représenter Texte, Images et Son", "تمثيل النصّ والصورة والصوت"),
                    story=T(
                        "The same bits mean a letter, a pixel or a note — the difference is only how you agree to read them.",
                        "Les mêmes bits signifient une lettre, un pixel ou une note — la différence n'est que la convention de lecture.",
                        "البتّات نفسها قد تعني حرفًا أو بكسلًا أو نغمة — والفرق هو الاتفاق على كيفية قراءتها.",
                    ),
                    objective=T(
                        "Explain character encodings, pixels and sampling, and why file size follows from them.",
                        "Expliquer les encodages de caractères, les pixels et l'échantillonnage, et pourquoi la taille des fichiers en découle.",
                        "شرح ترميز المحارف والبكسل وأخذ العيّنات، ولماذا ينتج حجم الملفّ عنها.",
                    ),
                    skills=T(
                        "ASCII, Unicode, UTF-8, pixels, RGB, sampling, file size",
                        "ASCII, Unicode, UTF-8, pixels, RVB, échantillonnage, taille de fichier",
                        "ASCII، يونيكود، UTF-8، البكسل، RGB، أخذ العيّنات، حجم الملفّ",
                    ),
                    blocks=[
                        Text(
                            T(
                                "Text is numbers plus a table. ASCII gave 128 characters — enough for English. **Unicode** gives a number to every character in every writing system, and **UTF-8** stores those numbers using one to four bytes each. This is why 'A' takes one byte and 'ب' takes two.",
                                "Le texte, ce sont des nombres plus une table. ASCII offrait 128 caractères — assez pour l'anglais. **Unicode** attribue un nombre à chaque caractère de chaque système d'écriture, et **UTF-8** stocke ces nombres sur un à quatre octets. C'est pourquoi « A » occupe un octet et « ب » deux.",
                                "النصّ أرقام مع جدول. أعطى ASCII مئة وثمانية وعشرين محرفًا — يكفي الإنجليزية. أما **يونيكود** فيعطي رقمًا لكلّ محرف في كلّ نظام كتابة، و**UTF-8** يخزّن تلك الأرقام في بايت إلى أربعة. لهذا يشغل «A» بايتًا واحدًا و«ب» بايتين.",
                            )
                        ),
                        Code(
                            T(
                                "Every character has a code point, and encoding turns it into bytes:",
                                "Chaque caractère a un point de code, et l'encodage le transforme en octets :",
                                "لكلّ محرف نقطة ترميز، والترميز يحوّلها إلى بايتات:",
                            ),
                            "print(ord('A'))              # 65   - the code point\n"
                            "print(chr(65))               # 'A'\n"
                            "print(len('Hi'.encode()))    # 2 bytes\n"
                            "print(len('مرحبا'.encode())) # 10 bytes - 2 per Arabic letter",
                        ),
                        Text(
                            T(
                                "An image is a grid of **pixels**, each usually three bytes: red, green and blue from 0 to 255. Sound is measured — **sampled** — thousands of times a second, each sample a number. So a 1000×1000 photo is about 3 MB before compression, and a minute of CD audio about 10 MB. File size is not magic; it is arithmetic.",
                                "Une image est une grille de **pixels**, chacun généralement de trois octets : rouge, vert et bleu de 0 à 255. Le son est mesuré — **échantillonné** — des milliers de fois par seconde, chaque échantillon étant un nombre. Ainsi une photo de 1000×1000 pèse environ 3 Mo avant compression, et une minute d'audio CD environ 10 Mo. La taille d'un fichier n'a rien de magique : c'est de l'arithmétique.",
                                "الصورة شبكة من **البكسلات**، كلّ منها غالبًا ثلاثة بايتات: أحمر وأخضر وأزرق من 0 إلى 255. والصوت يُقاس — تُؤخذ منه **عيّنات** — آلاف المرّات في الثانية، وكلّ عيّنة رقم. لذا فصورة 1000×1000 تبلغ نحو 3 ميغابايت قبل الضغط، ودقيقة صوت بجودة القرص المدمج نحو 10 ميغابايت. حجم الملفّ ليس سحرًا، بل حساب.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "Why can UTF-8 represent Arabic, Chinese and English in the same file?",
                                "Pourquoi UTF-8 peut-il représenter l'arabe, le chinois et l'anglais dans un même fichier ?",
                                "لماذا يستطيع UTF-8 تمثيل العربية والصينية والإنجليزية في الملفّ نفسه؟",
                            ),
                            hint=T(
                                "Think about how many bytes one character is allowed to use.",
                                "Pensez au nombre d'octets qu'un caractère peut utiliser.",
                                "فكّر في عدد البايتات المسموح لمحرف واحد باستخدامها.",
                            ),
                            explanation=T(
                                "UTF-8 is a variable-width encoding of Unicode: common characters take one byte, others take two to four, so every writing system fits in one scheme.",
                                "UTF-8 est un encodage à largeur variable d'Unicode : les caractères courants tiennent sur un octet, les autres sur deux à quatre, si bien que tous les systèmes d'écriture tiennent dans un seul schéma.",
                                "UTF-8 ترميز متغيّر العرض ليونيكود: المحارف الشائعة بايت واحد، وغيرها من بايتين إلى أربعة، فيتّسع المخطّط الواحد لكلّ أنظمة الكتابة.",
                            ),
                            options=[
                                Option(T("It stores every character in exactly one byte", "Il stocke chaque caractère sur exactement un octet", "يخزّن كلّ محرف في بايت واحد بالضبط")),
                                Option(
                                    T(
                                        "It uses one to four bytes per character, covering all of Unicode",
                                        "Il utilise un à quatre octets par caractère, couvrant tout Unicode",
                                        "يستخدم من بايت إلى أربعة لكلّ محرف فيغطّي يونيكود كلّه",
                                    ),
                                    correct=True,
                                ),
                                Option(T("It compresses the text", "Il compresse le texte", "يضغط النصّ")),
                                Option(T("It stores a separate file per language", "Il stocke un fichier séparé par langue", "يخزّن ملفًا منفصلًا لكلّ لغة")),
                            ],
                        ),
                        Prediction(
                            prompt=T(
                                "What does this print?",
                                "Qu'affiche ce code ?",
                                "ما الذي يطبعه هذا الكود؟",
                            ),
                            hint=T(
                                "ord() gives the code point; chr() goes back the other way.",
                                "ord() donne le point de code ; chr() fait le chemin inverse.",
                                "تعطي ord() نقطة الترميز، وتعيدها chr() إلى محرف.",
                            ),
                            explanation=T(
                                "'a' is code point 97, and adding 1 then converting back gives 'b'.",
                                "« a » est le point de code 97 ; en ajoutant 1 puis en reconvertissant on obtient « b ».",
                                "المحرف 'a' نقطته 97، وبإضافة 1 ثمّ التحويل نحصل على 'b'.",
                            ),
                            code="print(ord('a'))\nprint(chr(ord('a') + 1))",
                            expected_output="97\nb",
                        ),
                    ],
                ),
            ],
        ),
        # ------------------------------------------------------------------
        Module(
            slug="logic-foundations",
            title=T("Logic and Reasoning", "Logique et Raisonnement", "المنطق والاستدلال"),
            description=T(
                "Boolean values, truth tables and the gates every processor is built from.",
                "Valeurs booléennes, tables de vérité et portes dont sont faits tous les processeurs.",
                "القيم البوليانية وجداول الصدق والبوّابات التي يُبنى منها كلّ معالج.",
            ),
            lessons=[
                Lesson(
                    slug="boolean-logic",
                    minutes=30,
                    xp=55,
                    difficulty=D.beginner,
                    title=T("Boolean Logic", "La Logique Booléenne", "المنطق البولياني"),
                    story=T(
                        "Two values, three operators, and every decision a program will ever make.",
                        "Deux valeurs, trois opérateurs, et toutes les décisions qu'un programme prendra jamais.",
                        "قيمتان وثلاثة معاملات، ومنها كلّ قرار سيتّخذه أيّ برنامج.",
                    ),
                    objective=T(
                        "Evaluate AND, OR and NOT expressions and use them to express real conditions.",
                        "Évaluer des expressions ET, OU et NON et les utiliser pour exprimer des conditions réelles.",
                        "تقييم عبارات AND وOR وNOT واستخدامها للتعبير عن شروط واقعية.",
                    ),
                    skills=T(
                        "AND, OR, NOT, boolean expressions, De Morgan's laws",
                        "ET, OU, NON, expressions booléennes, lois de De Morgan",
                        "AND، OR، NOT، العبارات البوليانية، قانونا دي مورغان",
                    ),
                    blocks=[
                        Text(
                            T(
                                "**AND** is true only when both sides are true. **OR** is true when at least one side is. **NOT** flips a value. That is the whole vocabulary, and it is enough to describe any decision a computer makes.",
                                "**ET** n'est vrai que si les deux côtés le sont. **OU** est vrai si au moins un côté l'est. **NON** inverse une valeur. C'est tout le vocabulaire, et il suffit à décrire toute décision d'un ordinateur.",
                                "**AND** صحيحة فقط إذا كان الطرفان صحيحين. و**OR** صحيحة إذا كان أحدهما على الأقلّ صحيحًا. و**NOT** تعكس القيمة. هذه كلّ المفردات، وهي تكفي لوصف أيّ قرار يتّخذه الحاسوب.",
                            )
                        ),
                        Code(
                            T(
                                "A real condition, written as one boolean expression:",
                                "Une condition réelle, écrite comme une seule expression booléenne :",
                                "شرط واقعي مكتوب كعبارة بوليانية واحدة:",
                            ),
                            "age = 17\n"
                            "has_permission = True\n\n"
                            "can_enrol = age >= 18 or (age >= 16 and has_permission)\n"
                            "print(can_enrol)          # True\n\n"
                            "print(True and False)     # False\n"
                            "print(True or False)      # True\n"
                            "print(not True)           # False",
                        ),
                        Text(
                            T(
                                "**De Morgan's laws** let you push a NOT inwards: `not (A and B)` is `(not A) or (not B)`, and `not (A or B)` is `(not A) and (not B)`. They are how a tangled negative condition gets turned into a readable one.",
                                "Les **lois de De Morgan** permettent de faire entrer un NON : `not (A and B)` équivaut à `(not A) or (not B)`, et `not (A or B)` à `(not A) and (not B)`. C'est ainsi qu'une condition négative embrouillée devient lisible.",
                                "يسمح **قانونا دي مورغان** بإدخال النفي: `not (A and B)` تكافئ `(not A) or (not B)`، و`not (A or B)` تكافئ `(not A) and (not B)`. وبهما يتحوّل الشرط السالب المعقّد إلى شرط مقروء.",
                            )
                        ),
                        ExamTip(
                            T(
                                "When negating a compound condition, the operator flips too: not(A and B) becomes (not A) OR (not B). Forgetting to flip and/or is the most common logic error in exams and in production code alike.",
                                "En niant une condition composée, l'opérateur change aussi : not(A et B) devient (non A) OU (non B). Oublier d'inverser et/ou est l'erreur de logique la plus fréquente, aux examens comme en production.",
                                "عند نفي شرط مركّب يتغيّر المعامل أيضًا: not(A and B) تصبح (not A) OR (not B). ونسيان تبديل and/or أشيع خطأ منطقي في الامتحانات وفي الكود الحقيقي على السواء.",
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
                                "Evaluate the brackets first, then apply not.",
                                "Évaluez d'abord les parenthèses, puis appliquez not.",
                                "قيّم الأقواس أوّلًا ثمّ طبّق not.",
                            ),
                            explanation=T(
                                "(True and False) is False, so not False is True. The second line shows De Morgan's law giving the same answer.",
                                "(True and False) vaut False, donc not False vaut True. La seconde ligne montre la loi de De Morgan donnant la même réponse.",
                                "‏(True and False) تساوي False، فتصبح not False تساوي True. ويبيّن السطر الثاني أنّ قانون دي مورغان يعطي النتيجة نفسها.",
                            ),
                            code="print(not (True and False))\nprint((not True) or (not False))",
                            expected_output="True\nTrue",
                        ),
                        MCQ(
                            prompt=T(
                                "A ticket is refundable if it was bought less than 24 hours ago AND has not been used. Which expression means \"not refundable\"?",
                                "Un billet est remboursable s'il a été acheté il y a moins de 24 heures ET n'a pas été utilisé. Quelle expression signifie « non remboursable » ?",
                                "التذكرة قابلة للاسترداد إذا اشتُريت قبل أقلّ من 24 ساعة ولم تُستخدَم. أيّ عبارة تعني «غير قابلة للاسترداد»؟",
                            ),
                            hint=T("Apply De Morgan's law.", "Appliquez la loi de De Morgan.", "طبّق قانون دي مورغان."),
                            explanation=T(
                                "Negating (recent AND unused) gives (not recent) OR (used) — either condition alone blocks the refund.",
                                "La négation de (récent ET non utilisé) donne (non récent) OU (utilisé) — l'une ou l'autre suffit à bloquer le remboursement.",
                                "نفي (حديثة AND غير مستخدمة) يعطي (ليست حديثة) OR (مستخدمة) — ويكفي أحدهما لمنع الاسترداد.",
                            ),
                            options=[
                                Option(T("not recent and not used", "non récent et non utilisé", "ليست حديثة و غير مستخدمة")),
                                Option(T("not recent or used", "non récent ou utilisé", "ليست حديثة أو مستخدمة"), correct=True),
                                Option(T("recent or not used", "récent ou non utilisé", "حديثة أو غير مستخدمة")),
                                Option(T("recent and used", "récent et utilisé", "حديثة و مستخدمة")),
                            ],
                        ),
                    ],
                ),
                Lesson(
                    slug="truth-tables-and-gates",
                    minutes=30,
                    xp=60,
                    difficulty=D.beginner,
                    title=T("Truth Tables and Logic Gates", "Tables de Vérité et Portes Logiques", "جداول الصدق والبوّابات المنطقية"),
                    story=T(
                        "The gap between a logical rule and a piece of silicon is smaller than you think.",
                        "L'écart entre une règle logique et un morceau de silicium est plus petit qu'on ne le croit.",
                        "الفجوة بين قاعدة منطقية وقطعة سيليكون أصغر ممّا تظنّ.",
                    ),
                    objective=T(
                        "Build a truth table for a compound expression and connect it to the gates in hardware.",
                        "Construire une table de vérité pour une expression composée et la relier aux portes matérielles.",
                        "بناء جدول صدق لعبارة مركّبة وربطه ببوّابات العتاد.",
                    ),
                    skills=T(
                        "Truth tables, logic gates, XOR, half adder",
                        "Tables de vérité, portes logiques, XOR, demi-additionneur",
                        "جداول الصدق، البوّابات المنطقية، XOR، نصف الجامع",
                    ),
                    blocks=[
                        Text(
                            T(
                                "A **truth table** lists every possible combination of inputs and the result for each. Two inputs give four rows, three give eight — 2ⁿ rows for n inputs. It is the exhaustive proof that a condition behaves as intended.",
                                "Une **table de vérité** énumère toutes les combinaisons d'entrées et le résultat de chacune. Deux entrées donnent quatre lignes, trois en donnent huit — 2ⁿ lignes pour n entrées. C'est la preuve exhaustive qu'une condition se comporte comme prévu.",
                                "**جدول الصدق** يعدّد كلّ تركيبات المدخلات ونتيجتها. مدخلان يعطيان أربعة صفوف، وثلاثة تعطي ثمانية — أي 2ⁿ صفًّا لعدد n من المدخلات. وهو البرهان الشامل على أنّ الشرط يتصرّف كما أُريد له.",
                            )
                        ),
                        Code(
                            T(
                                "Printing the truth table for XOR — true when the inputs differ:",
                                "Affichage de la table de vérité du XOR — vrai lorsque les entrées diffèrent :",
                                "طباعة جدول صدق XOR — صحيحة عندما تختلف المدخلات:",
                            ),
                            "print('A      B      A XOR B')\n"
                            "for a in (False, True):\n"
                            "    for b in (False, True):\n"
                            "        print(f'{a!s:<6} {b!s:<6} {a != b}')",
                        ),
                        Text(
                            T(
                                "A **logic gate** is a tiny circuit implementing one of these operators. Combine two of them — an XOR for the digit and an AND for the carry — and you have a **half adder**, the circuit that adds one bit to another. Stack enough half adders and you have arithmetic; stack enough arithmetic and you have a computer.",
                                "Une **porte logique** est un minuscule circuit réalisant l'un de ces opérateurs. Combinez-en deux — un XOR pour le chiffre et un ET pour la retenue — et vous obtenez un **demi-additionneur**, le circuit qui additionne un bit à un autre. Empilez assez de demi-additionneurs et vous avez l'arithmétique ; empilez assez d'arithmétique et vous avez un ordinateur.",
                                "**البوّابة المنطقية** دارة صغيرة تنفّذ أحد هذه المعاملات. اجمع بوّابتين — XOR للرقم وAND للحمل — فتحصل على **نصف الجامع**، وهو الدارة التي تجمع بتًا إلى بت. وبتكديس ما يكفي من أنصاف الجوامع يظهر الحساب، وبتكديس ما يكفي من الحساب يظهر الحاسوب.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "How many rows does the truth table of an expression with 3 inputs have?",
                                "Combien de lignes compte la table de vérité d'une expression à 3 entrées ?",
                                "كم صفًّا في جدول صدق عبارة لها ثلاثة مدخلات؟",
                            ),
                            hint=T("Each input doubles the number of combinations.", "Chaque entrée double le nombre de combinaisons.", "كلّ مدخل يضاعف عدد التركيبات."),
                            explanation=T("2³ = 8 rows, one per combination of the three inputs.", "2³ = 8 lignes, une par combinaison des trois entrées.", "‏2³ = 8 صفوف، صفّ لكلّ تركيبة من المدخلات الثلاثة."),
                            options=[
                                Option(T("3", "3", "3")),
                                Option(T("6", "6", "6")),
                                Option(T("8", "8", "8"), correct=True),
                                Option(T("9", "9", "9")),
                            ],
                        ),
                        ShortAnswer(
                            prompt=T(
                                "When is A XOR B true? Answer in one sentence.",
                                "Quand A XOR B est-il vrai ? Répondez en une phrase.",
                                "متى تكون A XOR B صحيحة؟ أجب بجملة واحدة.",
                            ),
                            hint=T(
                                "Compare the two inputs to each other.",
                                "Comparez les deux entrées entre elles.",
                                "قارن المدخلين ببعضهما.",
                            ),
                            explanation=T(
                                "XOR is true exactly when the two inputs differ — one true and one false.",
                                "XOR est vrai exactement lorsque les deux entrées diffèrent — l'une vraie, l'autre fausse.",
                                "تكون XOR صحيحة تمامًا عندما يختلف المدخلان — أحدهما صحيح والآخر خاطئ.",
                            ),
                            keywords=[["differ", "different", "diffèrent", "différentes", "مختلف", "تختلف"]],
                            reference_answer="A XOR B is true when the two inputs differ, that is when exactly one of them is true.",
                        ),
                    ],
                ),
            ],
        ),
    ],
)


async def seed_cs_foundations(db, order: int) -> int:
    print("Seeding Computer Science Foundations...")
    return await seed_course(db, CS_FOUNDATIONS, order)
