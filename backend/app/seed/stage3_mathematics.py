"""Stage 3 — Mathematics for Computer Science.

Two courses. *Discrete Mathematics* is the language the rest of computer
science is written in: sets, relations, logic, proof, counting and graphs.
*Mathematics for Computer Science* is the applied half a programmer reaches for
daily: logarithms, growth, probability and reading statistics honestly.

Every idea is anchored to something the student has already met in code.
"""

from app.models import DifficultyEnum as D

from .authoring import (
    Code,
    CourseSpec,
    ExamTip,
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

DISCRETE_MATHEMATICS = CourseSpec(
    slug="discrete-mathematics",
    stage=3,
    track="theory",
    icon="∑",
    difficulty=D.intermediate,
    estimated_hours=10,
    prerequisite_slug="computational-thinking",
    title=T("Discrete Mathematics", "Mathématiques Discrètes", "الرياضيات المتقطّعة"),
    description=T(
        "The mathematics computers are actually made of: sets, relations, functions, logic, proof, counting and graphs.",
        "Les mathématiques dont les ordinateurs sont faits : ensembles, relations, fonctions, logique, preuve, dénombrement et graphes.",
        "الرياضيات التي تُبنى منها الحواسيب فعلًا: المجموعات والعلاقات والدوالّ والمنطق والبرهان والعدّ والبيانات.",
    ),
    skills=T(
        "Sets, relations, functions, propositional logic, proof, combinatorics, graphs",
        "Ensembles, relations, fonctions, logique propositionnelle, preuve, combinatoire, graphes",
        "المجموعات، العلاقات، الدوالّ، منطق القضايا، البرهان، التوافيق، البيانات",
    ),
    modules=[
        Module(
            slug="sets-relations-functions",
            title=T("Sets, Relations and Functions", "Ensembles, Relations et Fonctions", "المجموعات والعلاقات والدوالّ"),
            description=T(
                "The three structures every data model is built on.",
                "Les trois structures sur lesquelles repose tout modèle de données.",
                "البنى الثلاث التي يُبنى عليها كلّ نموذج بيانات.",
            ),
            lessons=[
                Lesson(
                    slug="sets-and-operations",
                    minutes=35,
                    xp=60,
                    difficulty=D.intermediate,
                    title=T("Sets and Their Operations", "Les Ensembles et Leurs Opérations", "المجموعات وعملياتها"),
                    story=T(
                        "\"Which students take both maths and physics?\" is a set intersection, whether you call it that or not.",
                        "« Quels élèves suivent à la fois maths et physique ? » est une intersection d'ensembles, qu'on l'appelle ainsi ou non.",
                        "«أيّ الطلبة يدرسون الرياضيات والفيزياء معًا؟» هي تقاطع مجموعات، سمّيتها كذلك أم لا.",
                    ),
                    objective=T(
                        "Use union, intersection, difference and subset to express queries precisely.",
                        "Utiliser union, intersection, différence et inclusion pour exprimer des requêtes avec précision.",
                        "استخدام الاتّحاد والتقاطع والفرق والاحتواء للتعبير عن الاستعلامات بدقّة.",
                    ),
                    skills=T(
                        "Sets, union, intersection, difference, subsets, cardinality",
                        "Ensembles, union, intersection, différence, sous-ensembles, cardinalité",
                        "المجموعات، الاتّحاد، التقاطع، الفرق، المجموعات الجزئية، عدد العناصر",
                    ),
                    blocks=[
                        Text(
                            T(
                                "A **set** is an unordered collection with no duplicates. That is the whole definition, and it is exactly why sets answer membership questions so fast — there is nothing to search through in order.",
                                "Un **ensemble** est une collection non ordonnée sans doublons. C'est toute la définition, et c'est précisément pourquoi les ensembles répondent si vite aux questions d'appartenance — il n'y a rien à parcourir dans l'ordre.",
                                "**المجموعة** تجميعة غير مرتّبة بلا تكرار. هذا كلّ التعريف، وهو بالضبط سبب سرعة المجموعات في الإجابة عن أسئلة الانتماء — إذ لا يوجد ما يُبحث فيه بالترتيب.",
                            )
                        ),
                        Code(
                            T(
                                "The four operations, in notation and in Python:",
                                "Les quatre opérations, en notation et en Python :",
                                "العمليات الأربع، بالرمز وفي بايثون:",
                            ),
                            "maths   = {'Amina', 'Youssef', 'Sara'}\n"
                            "physics = {'Sara', 'Karim'}\n\n"
                            "print(maths | physics)   # union  A ∪ B  - either subject\n"
                            "print(maths & physics)   # inter. A ∩ B  - both subjects\n"
                            "print(maths - physics)   # diff.  A \\\\ B  - maths only\n"
                            "print(maths ^ physics)   # symmetric difference - exactly one\n\n"
                            "print({'Sara'} <= maths) # subset  ⊆\n"
                            "print(len(maths))        # cardinality |A|",
                        ),
                        Text(
                            T(
                                "Two counting facts you will use constantly. The **inclusion–exclusion principle**: |A ∪ B| = |A| + |B| − |A ∩ B|, because adding the two sizes counts the overlap twice. And the **power set** of a set with n elements has 2ⁿ members — one choice of in-or-out per element.",
                                "Deux faits de dénombrement que vous utiliserez sans cesse. Le **principe d'inclusion–exclusion** : |A ∪ B| = |A| + |B| − |A ∩ B|, car additionner les deux tailles compte deux fois le chevauchement. Et l'**ensemble des parties** d'un ensemble à n éléments compte 2ⁿ membres — un choix dedans/dehors par élément.",
                                "حقيقتان في العدّ ستستخدمهما باستمرار. **مبدأ الضمّ والاستبعاد**: |A ∪ B| = |A| + |B| − |A ∩ B|، لأنّ جمع الحجمين يعدّ التقاطع مرّتين. و**مجموعة القوى** لمجموعة من n عنصرًا فيها 2ⁿ عنصرًا — اختيار «داخل أو خارج» لكلّ عنصر.",
                            )
                        ),
                    ],
                    exercises=[
                        Prediction(
                            prompt=T("What does this print?", "Qu'affiche ce code ?", "ما الذي يطبعه هذا الكود؟"),
                            hint=T("Intersection keeps only what is in both.", "L'intersection ne garde que ce qui est dans les deux.", "التقاطع يُبقي ما هو في الاثنين فقط."),
                            explanation=T(
                                "Only 3 is in both sets, and the difference keeps the elements of A that are not in B.",
                                "Seul 3 est dans les deux ensembles, et la différence garde les éléments de A absents de B.",
                                "العنصر 3 وحده موجود في المجموعتين، والفرق يُبقي عناصر A غير الموجودة في B.",
                            ),
                            code="a = {1, 2, 3}\nb = {3, 4}\nprint(sorted(a & b))\nprint(sorted(a - b))",
                            expected_output="[3]\n[1, 2]",
                        ),
                        MCQ(
                            prompt=T(
                                "30 students take maths, 20 take physics, 8 take both. How many take at least one?",
                                "30 élèves suivent les maths, 20 la physique, 8 les deux. Combien en suivent au moins une ?",
                                "‏30 طالبًا يدرسون الرياضيات، و20 الفيزياء، و8 كليهما. كم عدد من يدرس واحدة على الأقلّ؟",
                            ),
                            hint=T("Inclusion–exclusion: do not count the overlap twice.", "Inclusion–exclusion : ne comptez pas deux fois le chevauchement.", "الضمّ والاستبعاد: لا تعدّ التقاطع مرّتين."),
                            explanation=T(
                                "|A ∪ B| = 30 + 20 − 8 = 42.",
                                "|A ∪ B| = 30 + 20 − 8 = 42.",
                                "‏|A ∪ B| = 30 + 20 − 8 = 42.",
                            ),
                            options=[
                                Option(T("50", "50", "50")),
                                Option(T("42", "42", "42"), correct=True),
                                Option(T("38", "38", "38")),
                                Option(T("58", "58", "58")),
                            ],
                        ),
                    ],
                ),
                Lesson(
                    slug="relations-and-functions",
                    minutes=35,
                    xp=60,
                    difficulty=D.intermediate,
                    title=T("Relations and Functions", "Relations et Fonctions", "العلاقات والدوالّ"),
                    story=T(
                        "A database table is a relation. A dictionary is a function. The maths came first.",
                        "Une table de base de données est une relation. Un dictionnaire est une fonction. Les maths sont venues avant.",
                        "جدول قاعدة البيانات علاقة. والقاموس دالّة. والرياضيات سبقت كليهما.",
                    ),
                    objective=T(
                        "Define relations and functions, and classify a function as injective, surjective or bijective.",
                        "Définir relations et fonctions, et classer une fonction comme injective, surjective ou bijective.",
                        "تعريف العلاقات والدوالّ، وتصنيف الدالّة إلى متباينة أو شاملة أو تقابلية.",
                    ),
                    skills=T(
                        "Cartesian product, relations, functions, injective/surjective/bijective",
                        "Produit cartésien, relations, fonctions, injective/surjective/bijective",
                        "الجداء الديكارتي، العلاقات، الدوالّ، التباين والشمول والتقابل",
                    ),
                    blocks=[
                        Text(
                            T(
                                "A **relation** from A to B is any set of pairs (a, b) — exactly what a two-column table holds. A **function** is a relation with one extra rule: every a appears at most once. That rule is why a dictionary can have one value per key.",
                                "Une **relation** de A vers B est un ensemble de paires (a, b) — exactement ce que contient une table à deux colonnes. Une **fonction** est une relation avec une règle en plus : chaque a apparaît au plus une fois. C'est cette règle qui fait qu'un dictionnaire a une valeur par clé.",
                                "**العلاقة** من A إلى B أيّ مجموعة من الأزواج (a, b) — وهو بالضبط ما يحويه جدول بعمودين. و**الدالّة** علاقة بقاعدة إضافية: كلّ a يظهر مرّة واحدة على الأكثر. وهذه القاعدة هي سبب امتلاك القاموس قيمة واحدة لكلّ مفتاح.",
                            )
                        ),
                        Code(
                            T(
                                "The same idea, twice — once as pairs, once as a dictionary:",
                                "La même idée, deux fois — en paires puis en dictionnaire :",
                                "الفكرة نفسها مرّتين — مرّة كأزواج ومرّة كقاموس:",
                            ),
                            "# A relation: any set of pairs\n"
                            "enrolled = {('Amina', 'maths'), ('Amina', 'physics'), ('Sara', 'maths')}\n\n"
                            "# A function: each input appears once\n"
                            "capital = {'Morocco': 'Rabat', 'France': 'Paris', 'Japan': 'Tokyo'}\n"
                            "print(capital['Morocco'])\n\n"
                            "# 'enrolled' is NOT a function: Amina maps to two subjects.",
                        ),
                        Text(
                            T(
                                "**Injective** (one-to-one): different inputs never share an output — this is what a good hash function tries hard to approximate. **Surjective** (onto): every possible output is produced. **Bijective**: both, so the function can be reversed — which is exactly what makes lossless encoding and decryption possible.",
                                "**Injective** : des entrées différentes ne partagent jamais une sortie — c'est ce qu'une bonne fonction de hachage cherche à approcher. **Surjective** : toute sortie possible est atteinte. **Bijective** : les deux, donc la fonction est inversible — ce qui rend possibles l'encodage sans perte et le déchiffrement.",
                                "**متباينة** (واحد لواحد): المدخلات المختلفة لا تتشارك مخرجًا أبدًا — وهذا ما تسعى دالّة التجزئة الجيّدة لمقاربته. و**شاملة**: كلّ مخرج ممكن يتحقّق. و**تقابلية**: الاثنان معًا، فتصبح الدالّة قابلة للعكس — وهو بالضبط ما يجعل الترميز بلا فقد وفكّ التشفير ممكنين.",
                            )
                        ),
                        ExamTip(
                            T(
                                "Only a bijection has an inverse. If a function loses information — like taking the remainder, or hashing — no inverse exists, no matter how clever the algorithm.",
                                "Seule une bijection possède un inverse. Si une fonction perd de l'information — comme le reste d'une division ou un hachage — aucun inverse n'existe, aussi ingénieux soit l'algorithme.",
                                "التقابل وحده له معكوس. فإذا فقدت الدالّة معلومات — كأخذ الباقي أو التجزئة — فلا وجود لمعكوس مهما بلغت براعة الخوارزمية.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "Why can a hash function not be inverted?",
                                "Pourquoi une fonction de hachage n'est-elle pas inversible ?",
                                "لماذا لا يمكن عكس دالّة التجزئة؟",
                            ),
                            hint=T("Compare the size of the input space with the output space.", "Comparez la taille de l'espace d'entrée et de sortie.", "قارن حجم فضاء المدخلات بفضاء المخرجات."),
                            explanation=T(
                                "Many inputs map to the same fixed-size output, so it is not injective, and only a bijection can be inverted.",
                                "De nombreuses entrées donnent la même sortie de taille fixe : elle n'est pas injective, et seule une bijection est inversible.",
                                "مدخلات كثيرة تُنتج المخرج نفسه ذا الحجم الثابت، فهي ليست متباينة، ولا يُعكس إلّا التقابل.",
                            ),
                            options=[
                                Option(T("It is too slow to reverse", "Elle est trop lente à inverser", "عكسها بطيء جدًا")),
                                Option(
                                    T(
                                        "Many inputs share one output, so it is not injective",
                                        "Plusieurs entrées partagent une sortie : elle n'est pas injective",
                                        "مدخلات كثيرة تتشارك مخرجًا واحدًا، فهي ليست متباينة",
                                    ),
                                    correct=True,
                                ),
                                Option(T("It uses a secret key", "Elle utilise une clé secrète", "تستخدم مفتاحًا سرّيًا")),
                                Option(T("It is not a function at all", "Ce n'est pas une fonction", "ليست دالّة أصلًا")),
                            ],
                        ),
                        MCQ(
                            prompt=T(
                                "Which set of pairs is a function from {1,2,3} to {a,b}?",
                                "Quel ensemble de paires est une fonction de {1,2,3} vers {a,b} ?",
                                "أيّ مجموعة أزواج تمثّل دالّة من {1,2,3} إلى {a,b}؟",
                            ),
                            hint=T("Each input may appear only once.", "Chaque entrée ne peut apparaître qu'une fois.", "كلّ مدخل يظهر مرّة واحدة فقط."),
                            explanation=T(
                                "A function assigns exactly one output per input; repeating 1 with two outputs breaks that.",
                                "Une fonction associe exactement une sortie par entrée ; répéter 1 avec deux sorties viole cette règle.",
                                "الدالّة تسند مخرجًا واحدًا بالضبط لكلّ مدخل، وتكرار 1 بمخرجين يخالف ذلك.",
                            ),
                            options=[
                                Option(T("{(1,a), (1,b), (2,a)}", "{(1,a), (1,b), (2,a)}", "{(1,a), (1,b), (2,a)}")),
                                Option(T("{(1,a), (2,b), (3,a)}", "{(1,a), (2,b), (3,a)}", "{(1,a), (2,b), (3,a)}"), correct=True),
                                Option(T("{(a,1), (b,2)}", "{(a,1), (b,2)}", "{(a,1), (b,2)}")),
                                Option(T("{(1,a), (2,b), (2,a)}", "{(1,a), (2,b), (2,a)}", "{(1,a), (2,b), (2,a)}")),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        Module(
            slug="logic-and-proof",
            title=T("Logic and Proof", "Logique et Preuve", "المنطق والبرهان"),
            description=T(
                "Saying precisely what is true, and showing that it must be.",
                "Dire précisément ce qui est vrai, et montrer que cela doit l'être.",
                "قول ما هو صحيح بدقّة، وإثبات أنّه لا بدّ أن يكون كذلك.",
            ),
            lessons=[
                Lesson(
                    slug="propositional-logic",
                    minutes=35,
                    xp=60,
                    difficulty=D.intermediate,
                    title=T("Propositional Logic", "Logique Propositionnelle", "منطق القضايا"),
                    story=T(
                        "\"If the file exists then read it\" is a claim with a precise truth value, and it is not what most people think.",
                        "« Si le fichier existe alors le lire » est une affirmation à valeur de vérité précise, et ce n'est pas celle qu'on croit.",
                        "«إن كان الملفّ موجودًا فاقرأه» عبارة لها قيمة صدق دقيقة، وهي ليست ما يظنّه معظم الناس.",
                    ),
                    objective=T(
                        "Read and negate implications, and use quantifiers correctly.",
                        "Lire et nier des implications, et utiliser correctement les quantificateurs.",
                        "قراءة الاقتضاءات ونفيها، واستخدام المُسوِّرات بشكل صحيح.",
                    ),
                    skills=T(
                        "Implication, contrapositive, converse, quantifiers, negation",
                        "Implication, contraposée, réciproque, quantificateurs, négation",
                        "الاقتضاء، النقيض المعاكس، العكس، المُسوِّرات، النفي",
                    ),
                    blocks=[
                        Text(
                            T(
                                "**P → Q** (\"if P then Q\") is false in exactly one case: P true and Q false. When P is false the whole claim is true, however odd that feels — which is why a loop body that never runs never violates its condition.",
                                "**P → Q** (« si P alors Q ») est fausse dans un seul cas : P vraie et Q fausse. Quand P est fausse, l'affirmation entière est vraie, aussi étrange que cela paraisse — c'est pourquoi un corps de boucle jamais exécuté ne viole jamais sa condition.",
                                "**P → Q** («إن كان P فإنّ Q») تكون خاطئة في حالة واحدة فقط: P صحيحة وQ خاطئة. وعندما تكون P خاطئة تكون العبارة كلّها صحيحة مهما بدا ذلك غريبًا — ولهذا فإنّ جسم حلقة لا يُنفَّذ أبدًا لا يخالف شرطه أبدًا.",
                            )
                        ),
                        Text(
                            T(
                                "Three statements are easy to confuse. The **contrapositive** of P → Q is ¬Q → ¬P, and it is *always* equivalent. The **converse** Q → P is a different claim entirely. The **inverse** ¬P → ¬Q is likewise unrelated. \"If it rains the ground is wet\" does not mean a wet ground implies rain.",
                                "Trois énoncés sont faciles à confondre. La **contraposée** de P → Q est ¬Q → ¬P, et elle est *toujours* équivalente. La **réciproque** Q → P est une affirmation totalement différente. L'**inverse** ¬P → ¬Q ne l'est pas moins. « S'il pleut, le sol est mouillé » ne signifie pas qu'un sol mouillé implique la pluie.",
                                "ثلاث عبارات يسهل الخلط بينها. **النقيض المعاكس** لـ P → Q هو ¬Q → ¬P، وهو *دائمًا* مكافئ. أمّا **العكس** Q → P فعبارة مختلفة تمامًا. وكذلك **النقيض** ¬P → ¬Q. فقولك «إن أمطرت فالأرض مبتلّة» لا يعني أنّ الأرض المبتلّة تعني المطر.",
                            )
                        ),
                        Code(
                            T(
                                "An implication is only ever false in one row of its truth table:",
                                "Une implication n'est fausse que dans une seule ligne de sa table de vérité :",
                                "الاقتضاء لا يكون خاطئًا إلّا في صفّ واحد من جدول صدقه:",
                            ),
                            "def implies(p, q):\n"
                            "    return (not p) or q\n\n"
                            "for p in (True, False):\n"
                            "    for q in (True, False):\n"
                            "        print(p, q, implies(p, q))",
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "What is the contrapositive of \"if a number is divisible by 4, it is even\"?",
                                "Quelle est la contraposée de « si un nombre est divisible par 4, il est pair » ?",
                                "ما النقيض المعاكس لعبارة «إذا كان العدد قابلًا للقسمة على 4 فهو زوجي»؟",
                            ),
                            hint=T("Negate both parts and swap them.", "Niez les deux parties et échangez-les.", "انفِ الطرفين وبدّل بينهما."),
                            explanation=T(
                                "The contrapositive of P → Q is ¬Q → ¬P, which is always logically equivalent to the original.",
                                "La contraposée de P → Q est ¬Q → ¬P, toujours logiquement équivalente à l'originale.",
                                "النقيض المعاكس لـ P → Q هو ¬Q → ¬P، وهو دائمًا مكافئ منطقيًا للأصل.",
                            ),
                            options=[
                                Option(T("If a number is even, it is divisible by 4", "Si un nombre est pair, il est divisible par 4", "إذا كان العدد زوجيًا فهو قابل للقسمة على 4")),
                                Option(
                                    T(
                                        "If a number is not even, it is not divisible by 4",
                                        "Si un nombre n'est pas pair, il n'est pas divisible par 4",
                                        "إذا لم يكن العدد زوجيًا فهو غير قابل للقسمة على 4",
                                    ),
                                    correct=True,
                                ),
                                Option(T("If a number is not divisible by 4, it is not even", "Si un nombre n'est pas divisible par 4, il n'est pas pair", "إذا لم يكن العدد قابلًا للقسمة على 4 فهو ليس زوجيًا")),
                                Option(T("Every even number is divisible by 4", "Tout nombre pair est divisible par 4", "كلّ عدد زوجي قابل للقسمة على 4")),
                            ],
                        ),
                        ShortAnswer(
                            prompt=T(
                                "What is the negation of \"every student passed\"? Answer in one short sentence.",
                                "Quelle est la négation de « tous les élèves ont réussi » ? Une phrase courte.",
                                "ما نفي عبارة «كلّ الطلبة نجحوا»؟ أجب بجملة قصيرة.",
                            ),
                            hint=T(
                                "The negation of \"for all\" is \"there exists at least one that does not\".",
                                "La négation de « pour tout » est « il existe au moins un qui ne… pas ».",
                                "نفي «لكلّ» هو «يوجد واحد على الأقلّ لا…».",
                            ),
                            explanation=T(
                                "¬∀x P(x) is ∃x ¬P(x): at least one student did not pass. One counter-example is enough.",
                                "¬∀x P(x) équivaut à ∃x ¬P(x) : au moins un élève n'a pas réussi. Un contre-exemple suffit.",
                                "‏¬∀x P(x) تكافئ ∃x ¬P(x): طالب واحد على الأقلّ لم ينجح. ويكفي مثال مضادّ واحد.",
                            ),
                            keywords=[
                                ["at least one", "one student", "au moins un", "un élève", "طالب واحد", "على الأقل"],
                                ["not pass", "did not", "failed", "n'a pas", "échoué", "لم ينجح", "رسب"],
                            ],
                            reference_answer="At least one student did not pass.",
                        ),
                    ],
                ),
                Lesson(
                    slug="proof-and-induction",
                    minutes=40,
                    xp=65,
                    difficulty=D.advanced,
                    title=T("Proof and Induction", "Preuve et Récurrence", "البرهان والاستقراء"),
                    story=T(
                        "Testing shows a program works on the cases you tried. A proof shows it works on the ones you did not.",
                        "Les tests montrent qu'un programme marche sur les cas essayés. Une preuve montre qu'il marche sur les autres.",
                        "الاختبار يبيّن أنّ البرنامج يعمل على الحالات التي جرّبتها. أمّا البرهان فيبيّن أنّه يعمل على ما لم تجرّبه.",
                    ),
                    objective=T(
                        "Use direct proof, proof by contradiction and induction, and connect induction to recursion.",
                        "Utiliser la preuve directe, par l'absurde et par récurrence, et relier la récurrence à la récursivité.",
                        "استخدام البرهان المباشر والبرهان بالخلف والاستقراء، وربط الاستقراء بالاستدعاء الذاتي.",
                    ),
                    skills=T(
                        "Direct proof, contradiction, counter-examples, induction, loop invariants",
                        "Preuve directe, absurde, contre-exemples, récurrence, invariants de boucle",
                        "البرهان المباشر، البرهان بالخلف، الأمثلة المضادّة، الاستقراء، ثوابت الحلقة",
                    ),
                    blocks=[
                        Text(
                            T(
                                "**Direct proof** argues from the definitions to the conclusion. **Proof by contradiction** assumes the opposite and derives something impossible. **A counter-example** disproves a universal claim outright — one is enough, and finding one is often faster than proving anything.",
                                "La **preuve directe** part des définitions pour aller à la conclusion. La **preuve par l'absurde** suppose le contraire et en tire une impossibilité. Un **contre-exemple** réfute d'un coup une affirmation universelle — un seul suffit, et en trouver un est souvent plus rapide que de prouver quoi que ce soit.",
                                "**البرهان المباشر** ينطلق من التعاريف إلى النتيجة. و**البرهان بالخلف** يفترض النقيض ويستنتج منه مستحيلًا. و**المثال المضادّ** يُبطل العبارة الكلّية دفعةً واحدة — يكفي مثال واحد، وإيجاده غالبًا أسرع من إثبات أيّ شيء.",
                            )
                        ),
                        Text(
                            T(
                                "**Induction** proves a claim for every natural number in two steps: show it holds for the smallest case (the **base case**), then show that if it holds for n it must hold for n+1 (the **inductive step**). It is the same shape as recursion — base case and recursive call — which is not a coincidence.",
                                "La **récurrence** prouve une affirmation pour tout entier en deux étapes : la montrer au plus petit cas (**cas de base**), puis montrer que si elle vaut pour n elle vaut pour n+1 (**pas de récurrence**). C'est la forme même de la récursivité — cas de base et appel récursif — et ce n'est pas un hasard.",
                                "**الاستقراء** يثبت العبارة لكلّ عدد طبيعي في خطوتين: إثباتها لأصغر حالة (**حالة الأساس**)، ثمّ إثبات أنّها إن صحّت عند n صحّت عند n+1 (**خطوة الاستقراء**). وهو الشكل نفسه للاستدعاء الذاتي — حالة أساس واستدعاء — وليست تلك مصادفة.",
                            )
                        ),
                        Code(
                            T(
                                "The classic: 1 + 2 + … + n = n(n+1)/2. Induction proves it; code only checks it.",
                                "Le classique : 1 + 2 + … + n = n(n+1)/2. La récurrence le prouve ; le code ne fait que vérifier.",
                                "المثال الكلاسيكي: 1 + 2 + … + n = n(n+1)/2. الاستقراء يبرهنها، والكود يتحقّق منها فقط.",
                            ),
                            "def sum_to(n):\n"
                            "    return n * (n + 1) // 2\n\n"
                            "# Base case: n = 1 -> 1*2//2 = 1. Correct.\n"
                            "# Step: assume true for n. Then for n+1:\n"
                            "#   sum_to(n) + (n+1) = n(n+1)/2 + (n+1) = (n+1)(n+2)/2. Correct.\n\n"
                            "for n in range(1, 6):\n"
                            "    assert sum_to(n) == sum(range(1, n + 1))\n"
                            "print(sum_to(100))",
                        ),
                    ],
                    exercises=[
                        Ordering(
                            prompt=T(
                                "Put a proof by induction in order.",
                                "Remettez une preuve par récurrence dans l'ordre.",
                                "رتّب خطوات البرهان بالاستقراء.",
                            ),
                            hint=T("You cannot assume the claim before stating it.", "On ne peut pas supposer l'affirmation avant de l'énoncer.", "لا يمكنك افتراض العبارة قبل صياغتها."),
                            explanation=T(
                                "State the claim, prove the base case, assume it for n, then derive it for n+1.",
                                "Énoncer l'affirmation, prouver le cas de base, la supposer pour n, puis la déduire pour n+1.",
                                "صِغ العبارة، ثمّ أثبت حالة الأساس، ثمّ افترضها عند n، ثمّ استنتجها عند n+1.",
                            ),
                            steps=[
                                T("State the claim for every n", "Énoncer l'affirmation pour tout n", "صِغ العبارة لكلّ n"),
                                T("Prove the base case, n = 1", "Prouver le cas de base, n = 1", "أثبت حالة الأساس، n = 1"),
                                T("Assume the claim holds for n", "Supposer l'affirmation vraie pour n", "افترض صحّة العبارة عند n"),
                                T("Deduce that it holds for n + 1", "En déduire qu'elle vaut pour n + 1", "استنتج صحّتها عند n + 1"),
                            ],
                        ),
                        MCQ(
                            prompt=T(
                                "What is enough to disprove \"every prime number is odd\"?",
                                "Que suffit-il pour réfuter « tout nombre premier est impair » ?",
                                "ما الذي يكفي لدحض عبارة «كلّ عدد أوّلي فردي»؟",
                            ),
                            hint=T("Think of the smallest prime.", "Pensez au plus petit nombre premier.", "فكّر في أصغر عدد أوّلي."),
                            explanation=T(
                                "2 is prime and even, and one counter-example disproves a universal claim completely.",
                                "2 est premier et pair, et un seul contre-exemple réfute totalement une affirmation universelle.",
                                "العدد 2 أوّلي وزوجي، ومثال مضادّ واحد يدحض العبارة الكلّية تمامًا.",
                            ),
                            options=[
                                Option(T("Checking the first 1000 primes", "Vérifier les 1000 premiers nombres premiers", "فحص أوّل ألف عدد أوّلي")),
                                Option(T("The single counter-example 2", "Le seul contre-exemple 2", "المثال المضادّ الواحد: 2"), correct=True),
                                Option(T("A proof by induction", "Une preuve par récurrence", "برهان بالاستقراء")),
                                Option(T("Showing most primes are odd", "Montrer que la plupart sont impairs", "إظهار أنّ معظم الأعداد الأوّلية فردية")),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        Module(
            slug="counting-and-graphs",
            title=T("Counting and Graphs", "Dénombrement et Graphes", "العدّ والبيانات"),
            description=T(
                "How many possibilities are there, and how are things connected?",
                "Combien y a-t-il de possibilités, et comment les choses sont-elles reliées ?",
                "كم عدد الاحتمالات، وكيف ترتبط الأشياء؟",
            ),
            lessons=[
                Lesson(
                    slug="combinatorics",
                    minutes=35,
                    xp=60,
                    difficulty=D.intermediate,
                    title=T("Combinatorics: Counting Possibilities", "Combinatoire : Compter les Possibilités", "التوافيق: عدّ الاحتمالات"),
                    story=T(
                        "How long would it take to try every 8-character password? Counting answers that.",
                        "Combien de temps pour essayer tous les mots de passe de 8 caractères ? Le dénombrement répond.",
                        "كم يستغرق تجريب كلّ كلمات المرور المكوّنة من 8 محارف؟ العدّ يجيب.",
                    ),
                    objective=T(
                        "Apply the product rule, permutations and combinations, and reason about search-space size.",
                        "Appliquer la règle du produit, les permutations et les combinaisons, et raisonner sur la taille d'un espace de recherche.",
                        "تطبيق قاعدة الجداء والتباديل والتوافيق، والاستدلال على حجم فضاء البحث.",
                    ),
                    skills=T(
                        "Product rule, permutations, combinations, search space, pigeonhole",
                        "Règle du produit, permutations, combinaisons, espace de recherche, tiroirs",
                        "قاعدة الجداء، التباديل، التوافيق، فضاء البحث، مبدأ الحمام",
                    ),
                    blocks=[
                        Text(
                            T(
                                "**Product rule**: if one choice has m options and the next has n, together they have m × n. Everything else in counting is built from this. An 8-character password from 62 symbols has 62⁸ ≈ 2.2 × 10¹⁴ possibilities — which is exactly why length matters more than punctuation.",
                                "**Règle du produit** : si un choix a m options et le suivant n, ensemble ils en ont m × n. Tout le reste en découle. Un mot de passe de 8 caractères sur 62 symboles offre 62⁸ ≈ 2,2 × 10¹⁴ possibilités — c'est pourquoi la longueur compte plus que la ponctuation.",
                                "**قاعدة الجداء**: إذا كان لخيارٍ m احتمالًا وللذي يليه n، فلهما معًا m × n. وكلّ ما سواه في العدّ يُبنى على هذا. فكلمة مرور من 8 محارف من 62 رمزًا لها 62⁸ ≈ 2.2 × 10¹⁴ احتمالًا — ولهذا يهمّ الطول أكثر من علامات الترقيم.",
                            )
                        ),
                        Text(
                            T(
                                "**Permutations** count arrangements, where order matters: n!/(n−k)!. **Combinations** count selections, where it does not: C(n,k) = n!/(k!(n−k)!). The question to ask is simply: would swapping two of my chosen items give a different answer?",
                                "Les **permutations** comptent les arrangements, où l'ordre compte : n!/(n−k)!. Les **combinaisons** comptent les sélections, où il ne compte pas : C(n,k) = n!/(k!(n−k)!). La question est simple : échanger deux éléments choisis donnerait-il une réponse différente ?",
                                "**التباديل** تعدّ الترتيبات حيث يهمّ الترتيب: n!/(n−k)!. و**التوافيق** تعدّ الاختيارات حيث لا يهمّ: C(n,k) = n!/(k!(n−k)!). والسؤال ببساطة: هل تبديل عنصرين مختارين يعطي إجابة مختلفة؟",
                            )
                        ),
                        Code(
                            T(
                                "Growth you can feel: adding one character multiplies the work by 62.",
                                "Une croissance qu'on ressent : un caractère de plus multiplie le travail par 62.",
                                "نموّ تلمسه: إضافة محرف واحد تضاعف العمل 62 مرّة.",
                            ),
                            "from math import comb, perm, factorial\n\n"
                            "print(perm(5, 3))       # arrangements of 3 from 5: 60\n"
                            "print(comb(5, 3))       # selections of 3 from 5:   10\n"
                            "print(factorial(5))     # all orderings of 5:      120\n\n"
                            "for length in (6, 8, 10, 12):\n"
                            "    print(length, f'{62 ** length:.2e}')",
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "A team of 3 is chosen from 10 students. Order does not matter. How many teams?",
                                "Une équipe de 3 est choisie parmi 10 élèves. L'ordre n'importe pas. Combien d'équipes ?",
                                "يُختار فريق من 3 من بين 10 طلبة، والترتيب لا يهمّ. كم عدد الفرق؟",
                            ),
                            hint=T("Order does not matter, so this is a combination.", "L'ordre n'importe pas : c'est une combinaison.", "الترتيب لا يهمّ، إذن هي توافيق."),
                            explanation=T(
                                "C(10,3) = 10!/(3!·7!) = 120.",
                                "C(10,3) = 10!/(3!·7!) = 120.",
                                "‏C(10,3) = 10!/(3!·7!) = 120.",
                            ),
                            options=[
                                Option(T("30", "30", "30")),
                                Option(T("120", "120", "120"), correct=True),
                                Option(T("720", "720", "720")),
                                Option(T("1000", "1000", "1000")),
                            ],
                        ),
                        Prediction(
                            prompt=T("What does this print?", "Qu'affiche ce code ?", "ما الذي يطبعه هذا الكود؟"),
                            hint=T("perm counts ordered arrangements, comb unordered selections.", "perm compte les arrangements ordonnés, comb les sélections non ordonnées.", "‏perm تعدّ الترتيبات وcomb تعدّ الاختيارات."),
                            explanation=T(
                                "perm(4,2) = 4×3 = 12 ordered pairs; comb(4,2) = 6 unordered pairs.",
                                "perm(4,2) = 4×3 = 12 paires ordonnées ; comb(4,2) = 6 paires non ordonnées.",
                                "‏perm(4,2) = 4×3 = 12 زوجًا مرتّبًا، وcomb(4,2) = 6 أزواج غير مرتّبة.",
                            ),
                            code="from math import comb, perm\nprint(perm(4, 2))\nprint(comb(4, 2))",
                            expected_output="12\n6",
                        ),
                    ],
                ),
                Lesson(
                    slug="graph-theory-basics",
                    minutes=35,
                    xp=60,
                    difficulty=D.intermediate,
                    title=T("Graph Theory Basics", "Bases de la Théorie des Graphes", "أساسيات نظرية البيانات"),
                    story=T(
                        "Friend networks, road maps, package dependencies and web links are all the same object.",
                        "Réseaux d'amis, cartes routières, dépendances de paquets et liens web sont un seul et même objet.",
                        "شبكات الأصدقاء وخرائط الطرق وتبعيّات الحزم وروابط الويب كلّها الشيء نفسه.",
                    ),
                    objective=T(
                        "Model a situation as a graph and use degree, path and cycle correctly.",
                        "Modéliser une situation en graphe et utiliser correctement degré, chemin et cycle.",
                        "نمذجة موقف كبيان واستخدام الدرجة والمسار والدورة بشكل صحيح.",
                    ),
                    skills=T(
                        "Vertices, edges, degree, paths, cycles, directed graphs, trees",
                        "Sommets, arêtes, degré, chemins, cycles, graphes orientés, arbres",
                        "الرؤوس، الأضلاع، الدرجة، المسارات، الدورات، البيانات الموجّهة، الأشجار",
                    ),
                    blocks=[
                        Text(
                            T(
                                "A **graph** is vertices joined by edges. Edges may be **directed** (a follows b, but not the reverse) or not. The **degree** of a vertex is how many edges touch it. A **path** is a walk with no repeated vertex; a **cycle** is a path that returns to its start.",
                                "Un **graphe** est un ensemble de sommets reliés par des arêtes. Les arêtes peuvent être **orientées** (a suit b, sans réciprocité) ou non. Le **degré** d'un sommet est le nombre d'arêtes qui le touchent. Un **chemin** ne répète aucun sommet ; un **cycle** est un chemin qui revient à son point de départ.",
                                "**البيان** رؤوس تصلها أضلاع. وقد تكون الأضلاع **موجّهة** (a يتابع b دون العكس) أو غير موجّهة. و**درجة** الرأس هي عدد الأضلاع التي تمسّه. و**المسار** تجوال لا يكرّر رأسًا، و**الدورة** مسار يعود إلى نقطة انطلاقه.",
                            )
                        ),
                        Code(
                            T(
                                "An adjacency list is the usual representation — one entry per vertex:",
                                "Une liste d'adjacence est la représentation habituelle — une entrée par sommet :",
                                "قائمة الجوار هي التمثيل المعتاد — مدخل واحد لكلّ رأس:",
                            ),
                            "graph = {\n"
                            "    'A': ['B', 'C'],\n"
                            "    'B': ['A', 'D'],\n"
                            "    'C': ['A', 'D'],\n"
                            "    'D': ['B', 'C'],\n"
                            "}\n\n"
                            "print(len(graph['A']))                      # degree of A\n"
                            "print(sum(len(n) for n in graph.values()))   # 2 x number of edges",
                        ),
                        Text(
                            T(
                                "A **tree** is a connected graph with no cycles, and it always has exactly n−1 edges for n vertices — file systems, HTML documents and decision structures are all trees. A directed graph with no cycles (a **DAG**) is how build systems and package managers decide what must be done before what.",
                                "Un **arbre** est un graphe connexe sans cycle, et il a toujours exactement n−1 arêtes pour n sommets — systèmes de fichiers, documents HTML et structures de décision sont des arbres. Un graphe orienté sans cycle (**DAG**) est ce qui permet aux systèmes de build et gestionnaires de paquets de décider quoi faire avant quoi.",
                                "**الشجرة** بيان متّصل بلا دورات، ولها دائمًا n−1 ضلعًا لعدد n من الرؤوس — أنظمة الملفّات ووثائق HTML وبنى القرار كلّها أشجار. والبيان الموجّه بلا دورات (**DAG**) هو ما يتيح لأنظمة البناء ومديري الحزم تحديد ما يجب فعله قبل ماذا.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "A tree has 12 vertices. How many edges does it have?",
                                "Un arbre a 12 sommets. Combien d'arêtes a-t-il ?",
                                "شجرة فيها 12 رأسًا. كم ضلعًا فيها؟",
                            ),
                            hint=T("A tree is connected and has no cycles.", "Un arbre est connexe et sans cycle.", "الشجرة متّصلة وبلا دورات."),
                            explanation=T(
                                "A tree on n vertices always has exactly n − 1 edges: one more would create a cycle, one fewer would disconnect it.",
                                "Un arbre à n sommets a toujours exactement n − 1 arêtes : une de plus créerait un cycle, une de moins le déconnecterait.",
                                "الشجرة ذات n رأسًا لها دائمًا n − 1 ضلعًا: ضلع إضافي يُنشئ دورة، وضلع أقلّ يفصلها.",
                            ),
                            options=[
                                Option(T("11", "11", "11"), correct=True),
                                Option(T("12", "12", "12")),
                                Option(T("13", "13", "13")),
                                Option(T("24", "24", "24")),
                            ],
                        ),
                        MCQ(
                            prompt=T(
                                "Why must a package manager's dependency graph be acyclic?",
                                "Pourquoi le graphe de dépendances d'un gestionnaire de paquets doit-il être acyclique ?",
                                "لماذا يجب أن يكون بيان تبعيّات مدير الحزم بلا دورات؟",
                            ),
                            hint=T("What would it mean for A to require B which requires A?", "Que signifierait A exigeant B exigeant A ?", "ماذا يعني أن يتطلّب A الحزمة B التي تتطلّب A؟"),
                            explanation=T(
                                "A cycle means each package must be installed before the other, so no valid install order exists.",
                                "Un cycle signifie que chaque paquet doit être installé avant l'autre : aucun ordre d'installation valide n'existe.",
                                "الدورة تعني أنّ كلّ حزمة يجب تثبيتها قبل الأخرى، فلا يوجد ترتيب تثبيت صحيح.",
                            ),
                            options=[
                                Option(T("Cycles use more memory", "Les cycles consomment plus de mémoire", "الدورات تستهلك ذاكرة أكثر")),
                                Option(
                                    T(
                                        "A cycle means no valid installation order exists",
                                        "Un cycle signifie qu'aucun ordre d'installation valide n'existe",
                                        "الدورة تعني عدم وجود ترتيب تثبيت صحيح",
                                    ),
                                    correct=True,
                                ),
                                Option(T("Cycles cannot be stored in a dictionary", "Les cycles ne peuvent pas être stockés dans un dictionnaire", "لا يمكن تخزين الدورات في قاموس")),
                                Option(T("Acyclic graphs are always trees", "Les graphes acycliques sont toujours des arbres", "البيانات بلا دورات أشجار دائمًا")),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)


MATH_FOR_CS = CourseSpec(
    slug="math-for-cs",
    stage=3,
    track="theory",
    icon="📐",
    difficulty=D.intermediate,
    estimated_hours=8,
    prerequisite_slug="discrete-mathematics",
    title=T(
        "Mathematics for Computer Science",
        "Mathématiques pour l'Informatique",
        "الرياضيات لعلوم الحاسوب",
    ),
    description=T(
        "The applied maths a programmer really uses: algebra, logarithms and growth, probability, and reading statistics without being fooled.",
        "Les mathématiques qu'un programmeur utilise vraiment : algèbre, logarithmes et croissance, probabilités, et lecture honnête des statistiques.",
        "الرياضيات التي يستخدمها المبرمج فعلًا: الجبر، واللوغاريتمات والنموّ، والاحتمالات، وقراءة الإحصاء دون انخداع.",
    ),
    skills=T(
        "Algebra, exponentials, logarithms, growth rates, probability, statistics",
        "Algèbre, exponentielles, logarithmes, taux de croissance, probabilités, statistiques",
        "الجبر، الأسّيات، اللوغاريتمات، معدّلات النموّ، الاحتمالات، الإحصاء",
    ),
    modules=[
        Module(
            slug="growth-and-logarithms",
            title=T("Growth, Exponentials and Logarithms", "Croissance, Exponentielles et Logarithmes", "النموّ والأسّيات واللوغاريتمات"),
            description=T(
                "Why halving a problem is so much better than shrinking it by one.",
                "Pourquoi diviser un problème par deux vaut bien mieux que le réduire de un.",
                "لماذا تنصيف المسألة أفضل بكثير من إنقاصها بواحد.",
            ),
            lessons=[
                Lesson(
                    slug="exponentials-and-logarithms",
                    minutes=35,
                    xp=60,
                    difficulty=D.intermediate,
                    title=T("Exponentials and Logarithms", "Exponentielles et Logarithmes", "الأسّيات واللوغاريتمات"),
                    story=T(
                        "Twenty questions is enough to find one person in a million. Logarithms explain why.",
                        "Vingt questions suffisent pour trouver une personne parmi un million. Les logarithmes expliquent pourquoi.",
                        "عشرون سؤالًا تكفي للعثور على شخص من بين مليون. واللوغاريتمات تفسّر السبب.",
                    ),
                    objective=T(
                        "Read log₂ n as \"how many halvings\", and connect it to binary search and tree height.",
                        "Lire log₂ n comme « combien de divisions par deux », et le relier à la recherche binaire et à la hauteur d'un arbre.",
                        "قراءة log₂ n بمعنى «كم تنصيفًا»، وربطها بالبحث الثنائي وارتفاع الشجرة.",
                    ),
                    skills=T(
                        "Powers, log₂, doubling, halving, growth comparison",
                        "Puissances, log₂, doublement, division par deux, comparaison de croissance",
                        "القوى، log₂، المضاعفة، التنصيف، مقارنة النموّ",
                    ),
                    blocks=[
                        Text(
                            T(
                                "**log₂ n answers one question: how many times can I halve n before reaching 1?** That is the whole intuition. log₂ 1 000 000 ≈ 20, so twenty halvings — twenty yes/no questions — is enough to pinpoint one item in a million.",
                                "**log₂ n répond à une seule question : combien de fois puis-je diviser n par deux avant d'atteindre 1 ?** C'est toute l'intuition. log₂ 1 000 000 ≈ 20 : vingt divisions — vingt questions oui/non — suffisent à isoler un élément parmi un million.",
                                "**‏log₂ n تجيب عن سؤال واحد: كم مرّة أستطيع تنصيف n قبل الوصول إلى 1؟** هذا كلّ الحدس. فـ log₂ 1 000 000 ≈ 20، أي أنّ عشرين تنصيفًا — عشرين سؤالًا بنعم/لا — تكفي لتحديد عنصر من بين مليون.",
                            )
                        ),
                        Code(
                            T(
                                "The gap between linear and logarithmic is not a detail:",
                                "L'écart entre linéaire et logarithmique n'est pas un détail :",
                                "الفرق بين الخطّي واللوغاريتمي ليس تفصيلًا:",
                            ),
                            "from math import log2\n\n"
                            "print(f\"{'n':>12} {'n steps':>12} {'log2 n steps':>14}\")\n"
                            "for n in (1_000, 1_000_000, 1_000_000_000):\n"
                            "    print(f'{n:>12,} {n:>12,} {log2(n):>14.1f}')",
                        ),
                        Text(
                            T(
                                "Exponentials are the mirror image. Doubling something 30 times multiplies it by more than a billion, which is why an algorithm costing 2ⁿ is unusable at n = 60 no matter how fast the computer. **The base of the logarithm never matters for growth comparisons** — changing base only multiplies by a constant.",
                                "Les exponentielles sont l'image inverse. Doubler trente fois multiplie par plus d'un milliard, d'où l'inutilisabilité d'un algorithme en 2ⁿ dès n = 60, quelle que soit la machine. **La base du logarithme n'a aucune importance pour comparer des croissances** — changer de base ne fait que multiplier par une constante.",
                                "الأسّيات هي الصورة المعاكسة. فمضاعفة شيء ثلاثين مرّة تضربه بأكثر من مليار، ولذلك تصبح خوارزمية بكلفة 2ⁿ غير قابلة للاستعمال عند n = 60 مهما بلغت سرعة الحاسوب. و**أساس اللوغاريتم لا يهمّ أبدًا عند مقارنة النموّ** — فتغيير الأساس مجرّد ضرب بثابت.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "Roughly how many steps does binary search need on a sorted list of one million items?",
                                "Combien d'étapes environ pour une recherche binaire sur une liste triée d'un million d'éléments ?",
                                "كم خطوة يحتاج البحث الثنائي تقريبًا في قائمة مرتّبة من مليون عنصر؟",
                            ),
                            hint=T("How many times can you halve a million?", "Combien de fois peut-on diviser un million par deux ?", "كم مرّة يمكنك تنصيف المليون؟"),
                            explanation=T(
                                "log₂(1 000 000) ≈ 20, so about twenty halvings are enough.",
                                "log₂(1 000 000) ≈ 20 : une vingtaine de divisions suffisent.",
                                "‏log₂(1 000 000) ≈ 20، أي أنّ نحو عشرين تنصيفًا تكفي.",
                            ),
                            options=[
                                Option(T("About 20", "Environ 20", "نحو 20"), correct=True),
                                Option(T("About 1000", "Environ 1000", "نحو 1000")),
                                Option(T("About 500 000", "Environ 500 000", "نحو 500000")),
                                Option(T("About 1 000 000", "Environ 1 000 000", "نحو 1000000")),
                            ],
                        ),
                        Prediction(
                            prompt=T("What does this print?", "Qu'affiche ce code ?", "ما الذي يطبعه هذا الكود؟"),
                            hint=T("Count how many halvings reach 1.", "Comptez les divisions par deux jusqu'à 1.", "عُدّ عدد التنصيفات حتى الوصول إلى 1."),
                            explanation=T(
                                "1024 halves to 1 in exactly 10 steps, which is log₂ 1024.",
                                "1024 atteint 1 en exactement 10 divisions, soit log₂ 1024.",
                                "العدد 1024 يصل إلى 1 في عشر خطوات بالضبط، وهي log₂ 1024.",
                            ),
                            code="n = 1024\nsteps = 0\nwhile n > 1:\n    n = n // 2\n    steps += 1\nprint(steps)",
                            expected_output="10",
                        ),
                    ],
                ),
            ],
        ),
        Module(
            slug="probability",
            title=T("Probability", "Probabilités", "الاحتمالات"),
            description=T(
                "Reasoning about uncertainty, from hash collisions to machine learning.",
                "Raisonner sur l'incertitude, des collisions de hachage à l'apprentissage automatique.",
                "الاستدلال في ظلّ عدم اليقين، من تصادمات التجزئة إلى تعلّم الآلة.",
            ),
            lessons=[
                Lesson(
                    slug="probability-basics",
                    minutes=35,
                    xp=60,
                    difficulty=D.intermediate,
                    title=T("Probability Basics", "Bases des Probabilités", "أساسيات الاحتمال"),
                    story=T(
                        "In a room of 23 people, there is a better-than-even chance two share a birthday. Intuition is not enough.",
                        "Dans une salle de 23 personnes, il y a plus d'une chance sur deux que deux partagent un anniversaire. L'intuition ne suffit pas.",
                        "في غرفة فيها 23 شخصًا، احتمال أن يتشارك اثنان تاريخ الميلاد يفوق النصف. الحدس لا يكفي.",
                    ),
                    objective=T(
                        "Compute simple and conditional probabilities and explain why rare events become likely at scale.",
                        "Calculer des probabilités simples et conditionnelles et expliquer pourquoi les événements rares deviennent probables à grande échelle.",
                        "حساب الاحتمالات البسيطة والشرطية، وشرح لماذا تصبح الأحداث النادرة مرجّحة عند الحجم الكبير.",
                    ),
                    skills=T(
                        "Sample space, independence, conditional probability, complement rule",
                        "Univers, indépendance, probabilité conditionnelle, règle du complémentaire",
                        "فضاء العيّنة، الاستقلال، الاحتمال الشرطي، قاعدة المتمّمة",
                    ),
                    blocks=[
                        Text(
                            T(
                                "A probability is the fraction of outcomes in which something happens: favourable ÷ total, always between 0 and 1. For **independent** events, multiply: P(A and B) = P(A) × P(B). For events that cannot both happen, add.",
                                "Une probabilité est la fraction des issues où quelque chose se produit : favorables ÷ total, toujours entre 0 et 1. Pour des événements **indépendants**, on multiplie : P(A et B) = P(A) × P(B). Pour des événements incompatibles, on additionne.",
                                "الاحتمال هو نسبة النواتج التي يقع فيها الحدث: المواتية ÷ الكلّية، وهو دائمًا بين 0 و1. وللأحداث **المستقلّة** نضرب: P(A و B) = P(A) × P(B). وللأحداث التي لا تقع معًا نجمع.",
                            )
                        ),
                        Code(
                            T(
                                "The complement trick: \"at least one\" is easiest as 1 − \"none\".",
                                "L'astuce du complémentaire : « au moins un » se calcule mieux comme 1 − « aucun ».",
                                "حيلة المتمّمة: «واحد على الأقلّ» أسهل حسابًا بصيغة 1 − «لا أحد».",
                            ),
                            "def shared_birthday(people):\n"
                            "    all_different = 1.0\n"
                            "    for i in range(people):\n"
                            "        all_different *= (365 - i) / 365\n"
                            "    return 1 - all_different\n\n"
                            "for n in (10, 23, 50):\n"
                            "    print(n, f'{shared_birthday(n):.1%}')",
                        ),
                        Text(
                            T(
                                "**Conditional probability** P(A | B) is the chance of A once B is known. This is the reason a very accurate medical test can still be wrong most of the time it says \"positive\": when the condition is rare, the false positives outnumber the true ones. The same arithmetic governs security alerts and spam filters.",
                                "La **probabilité conditionnelle** P(A | B) est la chance de A sachant B. C'est pourquoi un test médical très précis peut se tromper la plupart du temps quand il annonce « positif » : si la maladie est rare, les faux positifs dépassent les vrais. La même arithmétique gouverne les alertes de sécurité et les filtres anti-spam.",
                                "**الاحتمال الشرطي** P(A | B) هو احتمال A بعد معرفة B. ولهذا قد يخطئ اختبار طبّي دقيق جدًا في معظم الحالات التي يقول فيها «إيجابي»: فحين يكون المرض نادرًا تفوق الإيجابيات الكاذبة الصادقةَ. والحساب نفسه يحكم تنبيهات الأمن ومرشّحات البريد المزعج.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "You flip a fair coin three times. What is the probability of three heads?",
                                "Vous lancez une pièce équilibrée trois fois. Quelle est la probabilité de trois faces ?",
                                "ترمي قطعة نقدية عادلة ثلاث مرّات. ما احتمال ظهور ثلاث صور؟",
                            ),
                            hint=T("Independent events multiply.", "Les événements indépendants se multiplient.", "الأحداث المستقلّة تُضرب."),
                            explanation=T(
                                "½ × ½ × ½ = 1/8.",
                                "½ × ½ × ½ = 1/8.",
                                "½ × ½ × ½ = 1/8.",
                            ),
                            options=[
                                Option(T("1/2", "1/2", "1/2")),
                                Option(T("1/3", "1/3", "1/3")),
                                Option(T("1/6", "1/6", "1/6")),
                                Option(T("1/8", "1/8", "1/8"), correct=True),
                            ],
                        ),
                        ShortAnswer(
                            prompt=T(
                                "Why is it easier to compute \"at least one collision\" as 1 minus the probability of none?",
                                "Pourquoi est-il plus simple de calculer « au moins une collision » comme 1 moins la probabilité d'aucune ?",
                                "لماذا يسهل حساب «تصادم واحد على الأقلّ» بصيغة 1 ناقص احتمال عدم وقوع أيّ تصادم؟",
                            ),
                            hint=T(
                                "How many separate cases does \"at least one\" cover?",
                                "Combien de cas distincts couvre « au moins un » ?",
                                "كم حالة منفصلة تغطّيها عبارة «واحد على الأقلّ»؟",
                            ),
                            explanation=T(
                                "\"At least one\" covers many overlapping cases (exactly one, exactly two, …), while \"none\" is a single case, so the complement is far less work.",
                                "« Au moins un » couvre de nombreux cas qui se chevauchent (exactement un, exactement deux, …), alors que « aucun » est un cas unique : le complémentaire demande bien moins de travail.",
                                "عبارة «واحد على الأقلّ» تغطّي حالات كثيرة متداخلة (واحد بالضبط، اثنان بالضبط، …)، أمّا «لا أحد» فحالة واحدة، فتكون المتمّمة أقلّ عملًا بكثير.",
                            ),
                            keywords=[
                                ["one case", "single case", "un seul cas", "cas unique", "حالة واحدة"],
                                ["many", "several", "plusieurs", "nombreux", "كثير", "حالات"],
                            ],
                            reference_answer="Because none is a single case to compute, while at least one covers many overlapping cases that would each have to be counted separately.",
                        ),
                    ],
                ),
                Lesson(
                    slug="statistics-basics",
                    minutes=35,
                    xp=60,
                    difficulty=D.intermediate,
                    title=T("Reading Statistics Honestly", "Lire les Statistiques Honnêtement", "قراءة الإحصاء بأمانة"),
                    story=T(
                        "The mean salary at a company with one billionaire is a true number and a useless one.",
                        "Le salaire moyen d'une entreprise comptant un milliardaire est un chiffre vrai et inutile.",
                        "متوسّط الرواتب في شركة فيها ملياردير رقم صحيح وعديم الفائدة.",
                    ),
                    objective=T(
                        "Choose between mean and median, read spread, and spot the difference between correlation and causation.",
                        "Choisir entre moyenne et médiane, lire la dispersion, et distinguer corrélation et causalité.",
                        "الاختيار بين المتوسّط والوسيط، وقراءة التشتّت، والتمييز بين الارتباط والسببية.",
                    ),
                    skills=T(
                        "Mean, median, outliers, variance, correlation vs causation, sampling bias",
                        "Moyenne, médiane, valeurs aberrantes, variance, corrélation vs causalité, biais d'échantillonnage",
                        "المتوسّط، الوسيط، القيم الشاذّة، التباين، الارتباط مقابل السببية، تحيّز العيّنة",
                    ),
                    blocks=[
                        Text(
                            T(
                                "The **mean** is pulled by extreme values; the **median** is not. When a distribution has outliers — salaries, response times, file sizes — the median describes a typical case and the mean does not. This is why engineers report p50 and p99 latency rather than an average.",
                                "La **moyenne** est tirée par les valeurs extrêmes ; la **médiane** non. Quand une distribution a des valeurs aberrantes — salaires, temps de réponse, tailles de fichiers — la médiane décrit un cas typique, pas la moyenne. C'est pourquoi les ingénieurs publient les latences p50 et p99 plutôt qu'une moyenne.",
                                "**المتوسّط** تجذبه القيم المتطرّفة، بخلاف **الوسيط**. وحين يحوي التوزيع قيمًا شاذّة — الرواتب وأزمنة الاستجابة وأحجام الملفّات — فالوسيط يصف الحالة النمطية والمتوسّط لا يفعل. ولهذا يعرض المهندسون زمن الاستجابة عند p50 وp99 بدل المتوسّط.",
                            )
                        ),
                        Code(
                            T(
                                "One outlier is enough to make the mean lie:",
                                "Une seule valeur aberrante suffit à faire mentir la moyenne :",
                                "قيمة شاذّة واحدة تكفي لجعل المتوسّط يكذب:",
                            ),
                            "from statistics import mean, median, pstdev\n\n"
                            "salaries = [2200, 2400, 2500, 2600, 90000]\n\n"
                            "print('mean  ', round(mean(salaries)))\n"
                            "print('median', median(salaries))\n"
                            "print('spread', round(pstdev(salaries)))",
                        ),
                        Text(
                            T(
                                "Two habits protect you from most bad conclusions. **Correlation is not causation**: ice-cream sales and drownings rise together because both follow the weather. And **ask who was measured**: a survey of your own users cannot tell you why other people left.",
                                "Deux réflexes protègent de la plupart des mauvaises conclusions. **Corrélation n'est pas causalité** : ventes de glaces et noyades augmentent ensemble parce que toutes deux suivent la météo. Et **demandez qui a été mesuré** : un sondage auprès de vos propres utilisateurs ne dira jamais pourquoi les autres sont partis.",
                                "عادتان تحميانك من معظم الاستنتاجات الخاطئة. **الارتباط ليس سببية**: مبيعات المثلّجات وحوادث الغرق ترتفعان معًا لأنّ كليهما يتبع الطقس. و**اسأل: من الذي قيس؟** فاستطلاع بين مستخدميك لن يخبرك أبدًا لماذا رحل الآخرون.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "Response times are mostly 100 ms but a few requests take 30 s. Which statistic best describes the typical experience?",
                                "Les temps de réponse sont surtout de 100 ms mais quelques requêtes prennent 30 s. Quelle statistique décrit le mieux l'expérience typique ?",
                                "أزمنة الاستجابة غالبًا 100 مللي ثانية لكن بعض الطلبات تستغرق 30 ثانية. أيّ مقياس يصف التجربة النمطية أفضل؟",
                            ),
                            hint=T("Which one ignores the extreme values?", "Laquelle ignore les valeurs extrêmes ?", "أيّها يتجاهل القيم المتطرّفة؟"),
                            explanation=T(
                                "The median is unaffected by a handful of very slow requests, so it reflects what most users actually experience.",
                                "La médiane n'est pas affectée par quelques requêtes très lentes : elle reflète ce que vivent réellement la plupart des utilisateurs.",
                                "الوسيط لا تتأثّر به حفنة من الطلبات البطيئة جدًا، فيعكس ما يعيشه معظم المستخدمين فعلًا.",
                            ),
                            options=[
                                Option(T("The mean", "La moyenne", "المتوسّط")),
                                Option(T("The median", "La médiane", "الوسيط"), correct=True),
                                Option(T("The maximum", "Le maximum", "القيمة العظمى")),
                                Option(T("The sum", "La somme", "المجموع")),
                            ],
                        ),
                        MCQ(
                            prompt=T(
                                "Users who enable dark mode stay longer. What does this show?",
                                "Les utilisateurs qui activent le mode sombre restent plus longtemps. Qu'est-ce que cela montre ?",
                                "المستخدمون الذين يفعّلون الوضع الداكن يبقون مدّة أطول. ماذا يثبت ذلك؟",
                            ),
                            hint=T("Could a third factor explain both?", "Un troisième facteur pourrait-il expliquer les deux ?", "هل يمكن لعامل ثالث أن يفسّر الاثنين؟"),
                            explanation=T(
                                "It shows an association. Engaged users are more likely to explore settings at all, so the cause may run the other way, or from a third factor.",
                                "Cela montre une association. Les utilisateurs engagés explorent davantage les réglages, donc la cause peut être inverse ou venir d'un troisième facteur.",
                                "يثبت وجود ارتباط. فالمستخدمون المنخرطون أميل أصلًا لاستكشاف الإعدادات، وقد يكون الاتّجاه معكوسًا أو ناتجًا عن عامل ثالث.",
                            ),
                            options=[
                                Option(T("Dark mode causes longer sessions", "Le mode sombre cause des sessions plus longues", "الوضع الداكن يسبّب جلسات أطول")),
                                Option(
                                    T(
                                        "A correlation, which may have another explanation entirely",
                                        "Une corrélation, qui peut avoir une tout autre explication",
                                        "ارتباطًا قد يكون له تفسير آخر تمامًا",
                                    ),
                                    correct=True,
                                ),
                                Option(T("Nothing at all", "Rien du tout", "لا شيء إطلاقًا")),
                                Option(T("That light mode is broken", "Que le mode clair est défectueux", "أنّ الوضع الفاتح معطّل")),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)


async def seed_discrete_mathematics(db, order: int) -> int:
    print("Seeding Discrete Mathematics...")
    return await seed_course(db, DISCRETE_MATHEMATICS, order)


async def seed_math_for_cs(db, order: int) -> int:
    print("Seeding Mathematics for Computer Science...")
    return await seed_course(db, MATH_FOR_CS, order)
