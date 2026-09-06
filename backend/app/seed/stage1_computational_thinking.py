"""Stage 1 — Computational Thinking for Problem Solving.

The habit that makes programming learnable: break a problem down, spot what
repeats, hide what does not matter yet, and write the steps out before writing
any code. Taught with tiny Python snippets, but the skill is language-neutral.
"""

from app.models import DifficultyEnum as D

from .authoring import (
    Code,
    CourseSpec,
    ExamTip,
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

COMPUTATIONAL_THINKING = CourseSpec(
    slug="computational-thinking",
    stage=1,
    track="foundations",
    icon="🧩",
    difficulty=D.beginner,
    estimated_hours=6,
    prerequisite_slug="cs-foundations",
    title=T(
        "Computational Thinking",
        "Pensée Computationnelle",
        "التفكير الحاسوبي",
    ),
    description=T(
        "Turn messy real-world problems into something a computer can solve: decomposition, pattern recognition, abstraction and algorithm design.",
        "Transformez des problèmes réels et flous en quelque chose qu'un ordinateur peut résoudre : décomposition, reconnaissance de motifs, abstraction et conception d'algorithmes.",
        "حوّل المسائل الواقعية المتشابكة إلى ما يستطيع الحاسوب حلّه: التفكيك، وتمييز الأنماط، والتجريد، وتصميم الخوارزميات.",
    ),
    skills=T(
        "Decomposition, pattern recognition, abstraction, algorithm design, tracing",
        "Décomposition, reconnaissance de motifs, abstraction, conception d'algorithmes, traçage",
        "التفكيك، تمييز الأنماط، التجريد، تصميم الخوارزميات، التتبّع",
    ),
    modules=[
        Module(
            slug="decomposition-abstraction",
            title=T("Decomposition and Abstraction", "Décomposition et Abstraction", "التفكيك والتجريد"),
            description=T(
                "Cut a big problem into parts, and decide what you are allowed to ignore.",
                "Découper un grand problème en parties et décider de ce qu'on peut ignorer.",
                "قسّم المسألة الكبيرة إلى أجزاء، وقرّر ما يمكنك تجاهله.",
            ),
            lessons=[
                Lesson(
                    slug="breaking-problems-down",
                    minutes=30,
                    xp=55,
                    difficulty=D.beginner,
                    title=T("Breaking Problems Down", "Décomposer les Problèmes", "تفكيك المسائل"),
                    story=T(
                        "\"Build a school timetable\" is not a problem you can solve. Six smaller problems are.",
                        "« Construire un emploi du temps » n'est pas un problème qu'on peut résoudre. Six problèmes plus petits, si.",
                        "«ابنِ جدولًا دراسيًا» ليست مسألة يمكن حلّها. أمّا ستّ مسائل أصغر فنعم.",
                    ),
                    objective=T(
                        "Split a large problem into independent sub-problems, each small enough to solve and test on its own.",
                        "Diviser un grand problème en sous-problèmes indépendants, chacun assez petit pour être résolu et testé seul.",
                        "تقسيم المسألة الكبيرة إلى مسائل فرعية مستقلّة، كلّ منها صغير بما يكفي لحلّه واختباره وحده.",
                    ),
                    skills=T(
                        "Decomposition, sub-problems, single responsibility, testability",
                        "Décomposition, sous-problèmes, responsabilité unique, testabilité",
                        "التفكيك، المسائل الفرعية، المسؤولية الواحدة، قابلية الاختبار",
                    ),
                    blocks=[
                        Hook(
                            T(
                                "A shop owner asks you for \"a program that manages my stock\". You could stare at that sentence for a week. A developer's first move is not to open an editor — it is to ask what the program must actually be able to do, one capability at a time.",
                                "Un commerçant vous demande « un programme qui gère mon stock ». On peut fixer cette phrase une semaine entière. Le premier réflexe d'un développeur n'est pas d'ouvrir un éditeur, mais de demander ce que le programme doit savoir faire, capacité par capacité.",
                                "يطلب منك صاحب متجر «برنامجًا يدير مخزوني». يمكنك التحديق في هذه الجملة أسبوعًا. أوّل خطوة عند المطوّر ليست فتح المحرّر، بل السؤال عمّا يجب أن يفعله البرنامج، قدرةً بعد قدرة.",
                            ),
                            T(
                                "List five things \"manage my stock\" actually means.",
                                "Énumérez cinq choses que « gérer mon stock » signifie réellement.",
                                "عدّد خمسة أشياء تعنيها فعلًا عبارة «إدارة المخزون».",
                            ),
                        ),
                        Text(
                            T(
                                "**Decomposition** is splitting one problem you cannot solve into several you can. A good split has two properties: each piece can be described in a single sentence, and each piece can be checked on its own without the others being finished.",
                                "La **décomposition** consiste à diviser un problème insoluble en plusieurs problèmes solubles. Une bonne division a deux propriétés : chaque morceau se décrit en une phrase, et chaque morceau se vérifie seul, sans attendre les autres.",
                                "**التفكيك** هو تقسيم مسألة لا تستطيع حلّها إلى مسائل تستطيعها. والتقسيم الجيّد له خاصّيتان: يمكن وصف كلّ جزء بجملة واحدة، ويمكن التحقّق من كلّ جزء وحده دون انتظار البقيّة.",
                            )
                        ),
                        Code(
                            T(
                                "\"Report the class average\" decomposed into three checkable pieces:",
                                "« Calculer la moyenne de la classe » décomposé en trois morceaux vérifiables :",
                                "«احسب معدّل الصفّ» مفكّكة إلى ثلاثة أجزاء قابلة للتحقّق:",
                            ),
                            "def parse_marks(lines):\n"
                            "    \"\"\"Piece 1: text -> numbers.\"\"\"\n"
                            "    return [float(line) for line in lines if line.strip()]\n\n"
                            "def mean(values):\n"
                            "    \"\"\"Piece 2: numbers -> one number.\"\"\"\n"
                            "    return sum(values) / len(values) if values else None\n\n"
                            "def format_report(average):\n"
                            "    \"\"\"Piece 3: one number -> a sentence.\"\"\"\n"
                            "    if average is None:\n"
                            "        return 'No marks recorded.'\n"
                            "    return f'Class average: {average:.2f}'\n\n"
                            "print(format_report(mean(parse_marks(['12', '15', '18']))))",
                        ),
                        ExamTip(
                            T(
                                "A piece that needs another piece to be finished before it can be tested has been split in the wrong place. Move the boundary until each part has a clear input and a clear output.",
                                "Un morceau qui exige qu'un autre soit terminé pour être testé a été découpé au mauvais endroit. Déplacez la frontière jusqu'à ce que chaque partie ait une entrée et une sortie claires.",
                                "الجزء الذي يحتاج إلى اكتمال جزء آخر كي يُختبَر قُسّم في المكان الخطأ. حرّك الحدّ حتى يصبح لكلّ جزء مدخل واضح ومخرج واضح.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "Which is the best sign that a problem has been decomposed well?",
                                "Quel est le meilleur signe qu'un problème a été bien décomposé ?",
                                "ما أفضل دليل على أنّ المسألة فُكّكت جيّدًا؟",
                            ),
                            hint=T(
                                "Think about what you can do with one piece before the others exist.",
                                "Pensez à ce que vous pouvez faire d'un morceau avant que les autres existent.",
                                "فكّر فيما يمكنك فعله بجزء واحد قبل وجود البقيّة.",
                            ),
                            explanation=T(
                                "Independence is the test: if a part can be written and checked on its own, the boundary is in the right place.",
                                "L'indépendance est le critère : si une partie peut être écrite et vérifiée seule, la frontière est bien placée.",
                                "الاستقلال هو المعيار: إذا أمكن كتابة جزء والتحقّق منه وحده، فالحدّ في مكانه الصحيح.",
                            ),
                            options=[
                                Option(T("There are more than five pieces", "Il y a plus de cinq morceaux", "عدد الأجزاء أكثر من خمسة")),
                                Option(
                                    T(
                                        "Each piece can be written and tested on its own",
                                        "Chaque morceau peut être écrit et testé séparément",
                                        "يمكن كتابة كلّ جزء واختباره وحده",
                                    ),
                                    correct=True,
                                ),
                                Option(T("Every piece uses the same variables", "Chaque morceau utilise les mêmes variables", "كلّ جزء يستخدم المتغيّرات نفسها")),
                                Option(T("The pieces are all the same length", "Les morceaux ont tous la même longueur", "الأجزاء كلّها بالطول نفسه")),
                            ],
                        ),
                        Prediction(
                            prompt=T(
                                "What does this decomposed program print?",
                                "Qu'affiche ce programme décomposé ?",
                                "ما الذي يطبعه هذا البرنامج المفكّك؟",
                            ),
                            hint=T(
                                "Work from the innermost call outwards.",
                                "Travaillez de l'appel le plus interne vers l'extérieur.",
                                "اعمل من الاستدعاء الداخلي نحو الخارج.",
                            ),
                            explanation=T(
                                "parse_marks gives [12.0, 15.0, 18.0], mean gives 15.0, and format_report prints it to two decimals.",
                                "parse_marks donne [12.0, 15.0, 18.0], mean donne 15.0, et format_report l'affiche à deux décimales.",
                                "تعطي parse_marks القيم [12.0, 15.0, 18.0]، وتعطي mean القيمة 15.0، وتطبعها format_report بمنزلتين عشريّتين.",
                            ),
                            code="def parse_marks(lines):\n    return [float(line) for line in lines if line.strip()]\n\ndef mean(values):\n    return sum(values) / len(values) if values else None\n\ndef format_report(average):\n    if average is None:\n        return 'No marks recorded.'\n    return f'Class average: {average:.2f}'\n\nprint(format_report(mean(parse_marks(['12', '15', '18']))))\nprint(format_report(mean(parse_marks([]))))",
                            expected_output="Class average: 15.00\nNo marks recorded.",
                        ),
                    ],
                ),
                Lesson(
                    slug="abstraction",
                    minutes=30,
                    xp=55,
                    difficulty=D.beginner,
                    title=T("Abstraction: Choosing What to Ignore", "L'Abstraction : Choisir Ce Qu'on Ignore", "التجريد: اختيار ما تتجاهله"),
                    story=T(
                        "A metro map is a lie about geography, and that is exactly why it works.",
                        "Un plan de métro est un mensonge géographique, et c'est précisément pour cela qu'il fonctionne.",
                        "خريطة المترو كذبة جغرافية، ولهذا بالضبط تنفع.",
                    ),
                    objective=T(
                        "Decide which details a solution must keep and which it can drop, and express that as an interface.",
                        "Décider quels détails une solution doit conserver et lesquels elle peut abandonner, et l'exprimer comme une interface.",
                        "تحديد التفاصيل التي يجب أن يحتفظ بها الحلّ وتلك التي يمكن إسقاطها، والتعبير عن ذلك كواجهة.",
                    ),
                    skills=T(
                        "Abstraction, interfaces, information hiding, modelling",
                        "Abstraction, interfaces, masquage d'information, modélisation",
                        "التجريد، الواجهات، إخفاء المعلومات، النمذجة",
                    ),
                    blocks=[
                        Text(
                            T(
                                "**Abstraction** is deciding what matters for the question you are answering. A metro map throws away distance, scale and street layout, and keeps only order and connections — because that is all a passenger needs. Keeping more would make it worse, not better.",
                                "L'**abstraction**, c'est décider de ce qui compte pour la question posée. Un plan de métro jette la distance, l'échelle et le tracé des rues, et ne garde que l'ordre et les correspondances — car c'est tout ce dont un passager a besoin. En garder plus le rendrait pire, pas meilleur.",
                                "**التجريد** هو تحديد ما يهمّ بالنسبة للسؤال الذي تجيب عنه. خريطة المترو تتخلّص من المسافة والمقياس وتخطيط الشوارع، وتبقي على الترتيب والتقاطعات فقط — لأنّ هذا كلّ ما يحتاجه الراكب. والاحتفاظ بأكثر من ذلك يجعلها أسوأ لا أفضل.",
                            )
                        ),
                        Code(
                            T(
                                "The same student, modelled twice, for two different questions:",
                                "Le même élève, modélisé deux fois, pour deux questions différentes :",
                                "الطالب نفسه، مُنمذَج مرّتين، لسؤالين مختلفين:",
                            ),
                            "# For computing averages, a student IS a list of marks.\n"
                            "marks_by_student = {'Amina': [14, 17, 12], 'Youssef': [11, 9, 16]}\n\n"
                            "# For printing ID cards, a student IS a name and a photo path.\n"
                            "id_cards = [\n"
                            "    {'name': 'Amina', 'photo': 'amina.jpg'},\n"
                            "    {'name': 'Youssef', 'photo': 'youssef.jpg'},\n"
                            "]\n\n"
                            "# Neither model is 'the truth'. Each keeps only what its job needs.\n"
                            "for name, marks in marks_by_student.items():\n"
                            "    print(name, round(sum(marks) / len(marks), 1))",
                        ),
                        Text(
                            T(
                                "In code, abstraction shows up as an **interface**: a name, its inputs and its outputs, with the method hidden behind it. `sorted(names)` tells you what you get, not how it is done — so the how can change without a single caller noticing.",
                                "En code, l'abstraction prend la forme d'une **interface** : un nom, ses entrées et ses sorties, la méthode restant cachée derrière. `sorted(names)` dit ce que vous obtenez, pas comment — de sorte que le comment peut changer sans qu'aucun appelant s'en aperçoive.",
                                "في الكود يظهر التجريد على شكل **واجهة**: اسم ومدخلات ومخرجات، والطريقة مخفيّة خلفها. تخبرك `sorted(names)` بما تحصل عليه لا بكيفيّته — فيمكن أن تتغيّر الكيفيّة دون أن يلاحظ أيّ مستدعٍ.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "You are writing a program that finds the nearest pharmacy. Which detail is safe to abstract away?",
                                "Vous écrivez un programme qui trouve la pharmacie la plus proche. Quel détail peut-on abstraire sans risque ?",
                                "تكتب برنامجًا يجد أقرب صيدلية. أيّ تفصيل يمكن تجريده بأمان؟",
                            ),
                            hint=T(
                                "Which fact could never change the answer?",
                                "Quel fait ne pourrait jamais changer la réponse ?",
                                "أيّ معلومة لا يمكن أن تغيّر الإجابة أبدًا؟",
                            ),
                            explanation=T(
                                "The colour of the shopfront cannot affect which pharmacy is nearest. Coordinates, opening hours and distance all can.",
                                "La couleur de la devanture ne peut pas affecter quelle pharmacie est la plus proche. Les coordonnées, les horaires et la distance, si.",
                                "لون واجهة المحلّ لا يمكن أن يؤثّر في أيّ صيدلية هي الأقرب. أمّا الإحداثيات وساعات العمل والمسافة فتؤثّر.",
                            ),
                            options=[
                                Option(T("The pharmacy's coordinates", "Les coordonnées de la pharmacie", "إحداثيات الصيدلية")),
                                Option(T("The colour of its shopfront", "La couleur de sa devanture", "لون واجهة المحلّ"), correct=True),
                                Option(T("Whether it is open now", "Si elle est ouverte maintenant", "هل هي مفتوحة الآن")),
                                Option(T("The distance from the user", "La distance depuis l'utilisateur", "المسافة من المستخدم")),
                            ],
                        ),
                        ShortAnswer(
                            prompt=T(
                                "Why is a metro map more useful to a passenger than a satellite photo of the same city? Answer in one sentence.",
                                "Pourquoi un plan de métro est-il plus utile à un passager qu'une photo satellite de la même ville ? Répondez en une phrase.",
                                "لماذا خريطة المترو أنفع للراكب من صورة قمر صناعي للمدينة نفسها؟ أجب بجملة واحدة.",
                            ),
                            hint=T(
                                "Say what the map removes and what it keeps.",
                                "Dites ce que le plan supprime et ce qu'il conserve.",
                                "قل ما الذي تحذفه الخريطة وما الذي تُبقيه.",
                            ),
                            explanation=T(
                                "The map abstracts away geography and keeps only the connections and order of stations — the only information the passenger's decision depends on.",
                                "Le plan fait abstraction de la géographie et ne garde que les correspondances et l'ordre des stations — la seule information dont dépend la décision du passager.",
                                "الخريطة تجرّد الجغرافيا وتُبقي على التقاطعات وترتيب المحطّات فقط — وهي المعلومة الوحيدة التي يتوقّف عليها قرار الراكب.",
                            ),
                            keywords=[
                                ["abstract", "abstracts", "abstraction", "abstrait", "تجريد", "تجرّد"],
                                ["station", "stations", "connection", "connections", "correspondance", "محطّ", "تقاطع"],
                            ],
                            reference_answer="The map abstracts away geography and distance and keeps only the stations, their order and the connections between lines, which is the only information a passenger needs.",
                        ),
                    ],
                ),
            ],
        ),
        Module(
            slug="patterns-and-algorithms",
            title=T("Patterns and Algorithm Design", "Motifs et Conception d'Algorithmes", "الأنماط وتصميم الخوارزميات"),
            description=T(
                "Notice what repeats, then write the steps down before writing code.",
                "Repérer ce qui se répète, puis écrire les étapes avant d'écrire du code.",
                "لاحظ ما يتكرّر، ثمّ اكتب الخطوات قبل كتابة الكود.",
            ),
            lessons=[
                Lesson(
                    slug="pattern-recognition",
                    minutes=30,
                    xp=55,
                    difficulty=D.beginner,
                    title=T("Pattern Recognition", "Reconnaissance de Motifs", "تمييز الأنماط"),
                    story=T(
                        "Every loop you will ever write started as someone noticing a repetition.",
                        "Toute boucle que vous écrirez a commencé par quelqu'un remarquant une répétition.",
                        "كلّ حلقة ستكتبها يومًا بدأت بشخصٍ لاحظ تكرارًا.",
                    ),
                    objective=T(
                        "Spot repetition and near-repetition in a problem and turn it into a loop or a reusable function.",
                        "Repérer la répétition et la quasi-répétition dans un problème et la transformer en boucle ou en fonction réutilisable.",
                        "اكتشاف التكرار وشبه التكرار في المسألة وتحويله إلى حلقة أو دالّة قابلة لإعادة الاستخدام.",
                    ),
                    skills=T(
                        "Pattern recognition, loops, parameterisation, DRY",
                        "Reconnaissance de motifs, boucles, paramétrage, DRY",
                        "تمييز الأنماط، الحلقات، التمرير بالمعاملات، مبدأ DRY",
                    ),
                    blocks=[
                        Text(
                            T(
                                "Two kinds of pattern matter. **Exact repetition** — the same thing done to many items — becomes a loop. **Near repetition** — almost the same thing, differing in one detail — becomes a function with that detail as a parameter.",
                                "Deux types de motifs comptent. La **répétition exacte** — la même chose faite à plusieurs éléments — devient une boucle. La **quasi-répétition** — presque la même chose, à un détail près — devient une fonction avec ce détail en paramètre.",
                                "نوعان من الأنماط يهمّان. **التكرار التامّ** — الشيء نفسه يُطبَّق على عناصر كثيرة — يصبح حلقة. و**شبه التكرار** — الشيء نفسه تقريبًا مع اختلاف في تفصيل واحد — يصبح دالّة ذلك التفصيل معاملها.",
                            )
                        ),
                        Code(
                            T(
                                "The same code three times is a pattern asking to be named:",
                                "Le même code trois fois est un motif qui demande à être nommé :",
                                "الكود نفسه ثلاث مرّات نمطٌ يطلب أن يُسمّى:",
                            ),
                            "# Before - near repetition, differing only in the rate\n"
                            "price_fr = 100 * 1.20\n"
                            "price_ma = 100 * 1.20\n"
                            "price_uk = 100 * 1.20\n\n"
                            "# After - the difference becomes a parameter\n"
                            "def with_tax(price, rate):\n"
                            "    return price * (1 + rate)\n\n"
                            "for country, rate in [('FR', 0.20), ('MA', 0.20), ('UK', 0.20)]:\n"
                            "    print(country, with_tax(100, rate))",
                        ),
                        Text(
                            T(
                                "Naming a pattern is not only about typing less. It gives the idea one home, so a change happens once, and it gives the reader a word for what the code is doing.",
                                "Nommer un motif ne sert pas seulement à taper moins. Cela donne à l'idée un seul foyer, donc un changement se fait une seule fois, et cela donne au lecteur un mot pour ce que fait le code.",
                                "تسمية النمط ليست فقط لتقليل الكتابة. إنّها تمنح الفكرة موطنًا واحدًا فيحدث التغيير مرّة واحدة، وتمنح القارئ كلمةً تصف ما يفعله الكود.",
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
                            hint=T("The function is called once per pair in the list.", "La fonction est appelée une fois par paire de la liste.", "تُستدعى الدالّة مرّة لكلّ زوج في القائمة."),
                            explanation=T(
                                "Each loop pass applies the same rule with a different rate: 100×1.2 = 120.0 and 100×1.1 = 110.00000000000001 is avoided by rounding.",
                                "Chaque passage applique la même règle avec un taux différent : 100×1,2 = 120.0 et l'arrondi évite 110.00000000000001.",
                                "كلّ دورة تطبّق القاعدة نفسها بنسبة مختلفة: 100×1.2 = 120.0، والتقريب يتفادى 110.00000000000001.",
                            ),
                            code="def with_tax(price, rate):\n    return round(price * (1 + rate), 2)\n\nfor label, rate in [('A', 0.20), ('B', 0.10)]:\n    print(label, with_tax(100, rate))",
                            expected_output="A 120.0\nB 110.0",
                        ),
                        MCQ(
                            prompt=T(
                                "You see the same six lines repeated four times, each differing only in a filename. What should you do?",
                                "Vous voyez les mêmes six lignes répétées quatre fois, ne différant que par un nom de fichier. Que faire ?",
                                "ترى الأسطر الستّة نفسها مكرّرة أربع مرّات، ولا تختلف إلّا في اسم الملفّ. ماذا تفعل؟",
                            ),
                            hint=T("The varying part is a clue about the parameter.", "La partie variable indique le paramètre.", "الجزء المتغيّر يدلّ على المعامل."),
                            explanation=T(
                                "Near repetition becomes one function whose parameter is the part that varies — here the filename.",
                                "La quasi-répétition devient une fonction dont le paramètre est la partie qui varie — ici le nom de fichier.",
                                "شبه التكرار يصبح دالّة واحدة معاملها هو الجزء المتغيّر — وهنا اسم الملفّ.",
                            ),
                            options=[
                                Option(T("Copy them a fifth time for the next file", "Les copier une cinquième fois pour le fichier suivant", "انسخها مرّة خامسة للملفّ التالي")),
                                Option(
                                    T(
                                        "Write one function that takes the filename as a parameter",
                                        "Écrire une fonction qui prend le nom de fichier en paramètre",
                                        "اكتب دالّة واحدة تأخذ اسم الملفّ معاملًا",
                                    ),
                                    correct=True,
                                ),
                                Option(T("Put the six lines in a comment", "Mettre les six lignes en commentaire", "ضع الأسطر الستّة في تعليق")),
                                Option(T("Rename the variables so they look different", "Renommer les variables pour qu'elles paraissent différentes", "غيّر أسماء المتغيّرات لتبدو مختلفة")),
                            ],
                        ),
                    ],
                ),
                Lesson(
                    slug="designing-algorithms",
                    minutes=35,
                    xp=60,
                    difficulty=D.beginner,
                    title=T("Designing an Algorithm", "Concevoir un Algorithme", "تصميم خوارزمية"),
                    story=T(
                        "Write the steps in plain words first. If you cannot, you do not understand the problem yet.",
                        "Écrivez d'abord les étapes en mots simples. Si vous n'y arrivez pas, c'est que le problème n'est pas encore compris.",
                        "اكتب الخطوات بكلمات بسيطة أوّلًا. فإن لم تستطع، فأنت لم تفهم المسألة بعد.",
                    ),
                    objective=T(
                        "Write pseudocode for a problem and translate it into working code.",
                        "Rédiger le pseudocode d'un problème et le traduire en code fonctionnel.",
                        "كتابة شبه كود لمسألة وترجمته إلى كود يعمل.",
                    ),
                    skills=T(
                        "Pseudocode, algorithm design, step-by-step reasoning",
                        "Pseudocode, conception d'algorithmes, raisonnement par étapes",
                        "شبه الكود، تصميم الخوارزميات، التفكير خطوة بخطوة",
                    ),
                    blocks=[
                        Text(
                            T(
                                "**Pseudocode** is the algorithm written in ordinary language, precise enough to follow but free of syntax. It lets you get the thinking right while mistakes are still cheap to fix.",
                                "Le **pseudocode** est l'algorithme écrit en langage ordinaire, assez précis pour être suivi mais sans syntaxe. Il permet de bien penser tant que les erreurs sont encore peu coûteuses à corriger.",
                                "**شبه الكود** هو الخوارزمية مكتوبة بلغة عادية، دقيقة بما يكفي لاتّباعها لكن بلا صياغة لغة برمجة. يتيح لك ضبط التفكير بينما تصحيح الأخطاء ما يزال رخيصًا.",
                            )
                        ),
                        Code(
                            T(
                                "Pseudocode first, code second — the second is a translation of the first:",
                                "Pseudocode d'abord, code ensuite — le second est une traduction du premier :",
                                "شبه الكود أوّلًا ثمّ الكود — والثاني ترجمة للأوّل:",
                            ),
                            "# ALGORITHM: count how many marks are passing (>= 10)\n"
                            "#   1. set count to 0\n"
                            "#   2. for each mark in the list:\n"
                            "#   3.     if the mark is 10 or more, add 1 to count\n"
                            "#   4. give back count\n\n"
                            "def count_passing(marks):\n"
                            "    count = 0\n"
                            "    for mark in marks:\n"
                            "        if mark >= 10:\n"
                            "            count += 1\n"
                            "    return count\n\n"
                            "print(count_passing([14, 8, 10, 3, 17]))",
                        ),
                        Text(
                            T(
                                "Then **trace** it: pick one small input and walk through the steps on paper, writing down every variable after every line. Tracing finds logic errors that reading never will, because reading shows you what you meant, and tracing shows you what you wrote.",
                                "Ensuite, **tracez-le** : prenez une petite entrée et déroulez les étapes sur papier, en notant chaque variable après chaque ligne. Le traçage révèle des erreurs de logique que la lecture ne montre jamais, car la lecture montre ce que vous vouliez dire et le traçage ce que vous avez écrit.",
                                "ثمّ **تتبّعه**: خذ مدخلًا صغيرًا وسِر في الخطوات على الورق، مسجّلًا كلّ متغيّر بعد كلّ سطر. التتبّع يكشف أخطاء منطقية لا تكشفها القراءة أبدًا، لأنّ القراءة تريك ما قصدته، والتتبّع يريك ما كتبته.",
                            )
                        ),
                    ],
                    exercises=[
                        Ordering(
                            prompt=T(
                                "Put the steps of the counting algorithm in the right order.",
                                "Remettez les étapes de l'algorithme de comptage dans le bon ordre.",
                                "رتّب خطوات خوارزمية العدّ ترتيبًا صحيحًا.",
                            ),
                            hint=T(
                                "The counter has to exist before anything is added to it.",
                                "Le compteur doit exister avant qu'on y ajoute quoi que ce soit.",
                                "يجب أن يوجد العدّاد قبل أن يُضاف إليه شيء.",
                            ),
                            explanation=T(
                                "Initialise, then loop, then test inside the loop, then return once the loop is finished.",
                                "Initialiser, puis boucler, puis tester dans la boucle, puis renvoyer une fois la boucle terminée.",
                                "التهيئة ثمّ الحلقة ثمّ الاختبار داخل الحلقة ثمّ الإرجاع بعد انتهاء الحلقة.",
                            ),
                            steps=[
                                T("Set the counter to zero", "Mettre le compteur à zéro", "اضبط العدّاد على صفر"),
                                T("Look at each mark in turn", "Examiner chaque note à tour de rôle", "افحص كلّ درجة بالتتابع"),
                                T("If the mark is 10 or more, add one to the counter", "Si la note est ≥ 10, ajouter un au compteur", "إذا كانت الدرجة 10 أو أكثر، أضف واحدًا للعدّاد"),
                                T("After the last mark, return the counter", "Après la dernière note, renvoyer le compteur", "بعد آخر درجة، أرجِع العدّاد"),
                            ],
                        ),
                        Prediction(
                            prompt=T(
                                "Trace this code by hand. What does it print?",
                                "Tracez ce code à la main. Qu'affiche-t-il ?",
                                "تتبّع هذا الكود يدويًا. ماذا يطبع؟",
                            ),
                            hint=T(
                                "Only marks of 10 or more are counted — 10 itself counts.",
                                "Seules les notes ≥ 10 sont comptées — 10 compte.",
                                "تُحسب الدرجات 10 فأكثر — والعشرة نفسها تُحسب.",
                            ),
                            explanation=T(
                                "14, 10 and 17 pass the test; 8 and 3 do not. That is three.",
                                "14, 10 et 17 passent le test ; 8 et 3 non. Cela fait trois.",
                                "الدرجات 14 و10 و17 تجتاز الاختبار، أمّا 8 و3 فلا. أي ثلاث درجات.",
                            ),
                            code="def count_passing(marks):\n    count = 0\n    for mark in marks:\n        if mark >= 10:\n            count += 1\n    return count\n\nprint(count_passing([14, 8, 10, 3, 17]))",
                            expected_output="3",
                        ),
                    ],
                ),
            ],
        ),
        Module(
            slug="modelling-and-checking",
            title=T("From Real World to Code", "Du Monde Réel au Code", "من العالم الواقعي إلى الكود"),
            description=T(
                "Turning a described situation into data and rules, and checking that it holds.",
                "Transformer une situation décrite en données et en règles, et vérifier que cela tient.",
                "تحويل موقف موصوف إلى بيانات وقواعد، والتحقّق من صحّته.",
            ),
            lessons=[
                Lesson(
                    slug="modelling-a-situation",
                    minutes=30,
                    xp=55,
                    difficulty=D.beginner,
                    title=T("Modelling a Situation", "Modéliser une Situation", "نمذجة موقف"),
                    story=T(
                        "Half of programming is choosing how to store the thing you are talking about.",
                        "La moitié de la programmation consiste à choisir comment stocker ce dont on parle.",
                        "نصف البرمجة هو اختيار طريقة تخزين ما تتحدّث عنه.",
                    ),
                    objective=T(
                        "Choose a data shape that makes the required question easy to answer.",
                        "Choisir une forme de données qui rend facile la réponse à la question posée.",
                        "اختيار شكل بيانات يجعل الإجابة عن السؤال المطلوب سهلة.",
                    ),
                    skills=T(
                        "Data modelling, lists vs dictionaries, choosing representations",
                        "Modélisation des données, listes vs dictionnaires, choix de représentation",
                        "نمذجة البيانات، القوائم مقابل القواميس، اختيار التمثيل",
                    ),
                    blocks=[
                        Text(
                            T(
                                "The right data shape is the one that makes your main question cheap. If you constantly ask \"what is this student's mark?\", store a dictionary keyed by name. If you constantly ask \"who came first?\", store a sorted list. The question decides the shape, not the other way round.",
                                "La bonne forme de données est celle qui rend votre question principale peu coûteuse. Si vous demandez sans cesse « quelle est la note de cet élève ? », stockez un dictionnaire indexé par nom. Si vous demandez sans cesse « qui est premier ? », stockez une liste triée. C'est la question qui décide de la forme, pas l'inverse.",
                                "شكل البيانات الصحيح هو ما يجعل سؤالك الرئيسي رخيصًا. إن كنت تسأل دائمًا «ما درجة هذا الطالب؟» فخزّن قاموسًا مفتاحه الاسم. وإن كنت تسأل دائمًا «من الأوّل؟» فخزّن قائمة مرتّبة. السؤال هو ما يحدّد الشكل لا العكس.",
                            )
                        ),
                        Code(
                            T(
                                "Two models of one class, each good at a different question:",
                                "Deux modèles d'une même classe, chacun bon pour une question différente :",
                                "نموذجان للصفّ نفسه، كلّ منهما جيّد لسؤال مختلف:",
                            ),
                            "# Question: 'what did Amina get?'  -> dictionary is O(1)\n"
                            "by_name = {'Amina': 14, 'Youssef': 11, 'Sara': 17}\n"
                            "print(by_name['Amina'])\n\n"
                            "# Question: 'who is top of the class?' -> sorted list is direct\n"
                            "ranking = sorted(by_name.items(), key=lambda pair: pair[1], reverse=True)\n"
                            "print(ranking[0])",
                        ),
                        Text(
                            T(
                                "Write down the rules of the situation as sentences before coding them: \"a mark is between 0 and 20\", \"a student appears once\". Each sentence becomes either a check in the code or an assumption you have chosen to trust — but now it is a choice, not an accident.",
                                "Écrivez les règles de la situation sous forme de phrases avant de les coder : « une note est entre 0 et 20 », « un élève apparaît une seule fois ». Chaque phrase devient soit une vérification dans le code, soit une hypothèse assumée — mais c'est désormais un choix, pas un hasard.",
                                "اكتب قواعد الموقف كجُمل قبل برمجتها: «الدرجة بين 0 و20»، «يظهر الطالب مرّة واحدة». كلّ جملة تصبح إمّا تحقّقًا في الكود أو افتراضًا اخترت الوثوق به — لكنّه الآن اختيار لا مصادفة.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "Your program must answer \"is this ID already registered?\" thousands of times. Which structure fits best?",
                                "Votre programme doit répondre des milliers de fois à « cet identifiant est-il déjà enregistré ? ». Quelle structure convient le mieux ?",
                                "على برنامجك أن يجيب آلاف المرّات عن «هل هذا المعرّف مسجّل من قبل؟». أيّ بنية أنسب؟",
                            ),
                            hint=T(
                                "Which one answers membership without scanning everything?",
                                "Laquelle répond à l'appartenance sans tout parcourir ?",
                                "أيّها يجيب عن الانتماء دون مسح كلّ شيء؟",
                            ),
                            explanation=T(
                                "A set answers membership in roughly constant time; scanning a list gets slower with every ID added.",
                                "Un ensemble répond à l'appartenance en temps quasi constant ; parcourir une liste devient plus lent à chaque identifiant ajouté.",
                                "المجموعة (set) تجيب عن الانتماء بزمن شبه ثابت، بينما مسح القائمة يزداد بطئًا مع كلّ معرّف يُضاف.",
                            ),
                            options=[
                                Option(T("A list, searched from the start each time", "Une liste, parcourue depuis le début à chaque fois", "قائمة تُبحث من البداية في كلّ مرّة")),
                                Option(T("A set of IDs", "Un ensemble d'identifiants", "مجموعة من المعرّفات"), correct=True),
                                Option(T("A single string of all IDs joined together", "Une seule chaîne contenant tous les identifiants", "سلسلة نصّية واحدة تجمع كلّ المعرّفات")),
                                Option(T("A list of lists", "Une liste de listes", "قائمة من القوائم")),
                            ],
                        ),
                        Prediction(
                            prompt=T(
                                "What does this print?",
                                "Qu'affiche ce code ?",
                                "ما الذي يطبعه هذا الكود؟",
                            ),
                            hint=T(
                                "sorted() with reverse=True puts the highest mark first.",
                                "sorted() avec reverse=True place la meilleure note en premier.",
                                "‏sorted() مع reverse=True تضع أعلى درجة أوّلًا.",
                            ),
                            explanation=T(
                                "Sara has the highest mark, so the first pair of the ranking is ('Sara', 17).",
                                "Sara a la meilleure note, donc la première paire du classement est ('Sara', 17).",
                                "سارة صاحبة أعلى درجة، لذا أوّل زوج في الترتيب هو ('Sara', 17).",
                            ),
                            code="by_name = {'Amina': 14, 'Youssef': 11, 'Sara': 17}\nranking = sorted(by_name.items(), key=lambda pair: pair[1], reverse=True)\nprint(ranking[0])",
                            expected_output="('Sara', 17)",
                        ),
                    ],
                ),
            ],
        ),
    ],
)


async def seed_computational_thinking(db, order: int) -> int:
    print("Seeding Computational Thinking...")
    return await seed_course(db, COMPUTATIONAL_THINKING, order)
