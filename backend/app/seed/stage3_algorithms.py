"""Stage 3 — Algorithms and Complexity.

Data Structures & Algorithms teaches the containers. This course teaches the
*techniques* and the *analysis*: how to measure a solution, and the four design
strategies — brute force, divide and conquer, greedy, dynamic programming —
that most efficient algorithms turn out to be an instance of.
"""

from app.models import DifficultyEnum as D

from .authoring import (
    Code,
    CodeWriting,
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
    asserts,
    seed_course,
)

ALGORITHMS_COMPLEXITY = CourseSpec(
    slug="algorithms-complexity",
    stage=3,
    track="theory",
    icon="⏱️",
    difficulty=D.intermediate,
    estimated_hours=12,
    prerequisite_slug="data-structures-algorithms",
    title=T("Algorithms & Complexity", "Algorithmes et Complexité", "الخوارزميات والتعقيد"),
    description=T(
        "Measure what your code costs, then make it cost less: Big-O, time and space, and the four strategies behind most efficient algorithms.",
        "Mesurez ce que coûte votre code, puis réduisez ce coût : Big-O, temps et espace, et les quatre stratégies derrière la plupart des algorithmes efficaces.",
        "قِس ما يكلّفه كودك ثمّ اجعله يكلّف أقلّ: Big-O، والزمن والمكان، والاستراتيجيات الأربع وراء معظم الخوارزميات الفعّالة.",
    ),
    skills=T(
        "Big-O, time and space complexity, divide and conquer, greedy, dynamic programming, graph algorithms",
        "Big-O, complexité en temps et en espace, diviser pour régner, glouton, programmation dynamique, algorithmes de graphes",
        "‏Big-O، تعقيد الزمن والمكان، فرّق تسُد، الجشع، البرمجة الديناميكية، خوارزميات البيانات",
    ),
    modules=[
        Module(
            slug="analysing-algorithms",
            title=T("Analysing Algorithms", "Analyser les Algorithmes", "تحليل الخوارزميات"),
            description=T(
                "How to say what an algorithm costs without running it.",
                "Comment dire ce que coûte un algorithme sans l'exécuter.",
                "كيف تحدّد كلفة الخوارزمية دون تنفيذها.",
            ),
            lessons=[
                Lesson(
                    slug="measuring-cost",
                    minutes=35,
                    xp=60,
                    difficulty=D.intermediate,
                    title=T("Measuring the Cost of an Algorithm", "Mesurer le Coût d'un Algorithme", "قياس كلفة الخوارزمية"),
                    story=T(
                        "A stopwatch measures your laptop. Big-O measures your algorithm.",
                        "Un chronomètre mesure votre portable. Big-O mesure votre algorithme.",
                        "ساعة الإيقاف تقيس حاسوبك. أمّا Big-O فتقيس خوارزميتك.",
                    ),
                    objective=T(
                        "Count operations as a function of input size and express the result in Big-O.",
                        "Compter les opérations en fonction de la taille de l'entrée et exprimer le résultat en Big-O.",
                        "عدّ العمليات كدالّة في حجم المدخلات والتعبير عن النتيجة بـ Big-O.",
                    ),
                    skills=T(
                        "Operation counting, Big-O, dropping constants, worst case",
                        "Comptage d'opérations, Big-O, suppression des constantes, pire cas",
                        "عدّ العمليات، Big-O، إسقاط الثوابت، أسوأ حالة",
                    ),
                    blocks=[
                        Text(
                            T(
                                "Timing a program tells you about your machine on that day. **Big-O** tells you how the work grows as the input grows, which is a property of the algorithm itself — and it is the one that decides whether the program still works when the data is a thousand times bigger.",
                                "Chronométrer un programme renseigne sur votre machine ce jour-là. **Big-O** dit comment le travail croît avec l'entrée, ce qui est une propriété de l'algorithme lui-même — et c'est elle qui décide si le programme tient encore quand les données sont mille fois plus grosses.",
                                "توقيت البرنامج يخبرك عن جهازك في ذلك اليوم. أمّا **Big-O** فتخبرك كيف ينمو العمل مع نموّ المدخلات، وهذه خاصّية الخوارزمية نفسها — وهي التي تقرّر هل يظلّ البرنامج صالحًا حين تكبر البيانات ألف مرّة.",
                            )
                        ),
                        Text(
                            T(
                                "Two rules do almost all the work. **Drop the constants**: 3n and n/2 are both O(n), because doubling the input doubles both. **Keep only the fastest-growing term**: n² + 1000n is O(n²), because past some size the square dominates everything.",
                                "Deux règles font presque tout. **Supprimez les constantes** : 3n et n/2 sont tous deux O(n), car doubler l'entrée double les deux. **Ne gardez que le terme dominant** : n² + 1000n est O(n²), car passé une certaine taille le carré écrase tout.",
                                "قاعدتان تقومان بالعمل كلّه تقريبًا. **أسقط الثوابت**: فـ 3n وn/2 كلاهما O(n) لأنّ مضاعفة المدخل تضاعفهما. و**أبقِ الحدّ الأسرع نموًّا فقط**: فـ n² + 1000n هي O(n²)، لأنّ المربّع يطغى على كلّ شيء بعد حجم معيّن.",
                            )
                        ),
                        Code(
                            T(
                                "Count the innermost operation, and see how the loops multiply:",
                                "Comptez l'opération la plus interne, et voyez comment les boucles se multiplient :",
                                "عُدّ العملية الداخلية وانظر كيف تتضاعف الحلقات:",
                            ),
                            "def first(items):          # O(1) - one step, whatever n is\n"
                            "    return items[0]\n\n"
                            "def total(items):          # O(n) - one pass\n"
                            "    result = 0\n"
                            "    for item in items:\n"
                            "        result += item\n"
                            "    return result\n\n"
                            "def has_duplicate(items):  # O(n^2) - a pass inside a pass\n"
                            "    for i in range(len(items)):\n"
                            "        for j in range(i + 1, len(items)):\n"
                            "            if items[i] == items[j]:\n"
                            "                return True\n"
                            "    return False\n\n"
                            "def has_duplicate_fast(items):   # O(n) - one pass and a set\n"
                            "    return len(set(items)) != len(items)\n\n"
                            "print(has_duplicate([1, 2, 3, 2]), has_duplicate_fast([1, 2, 3, 2]))",
                        ),
                        ExamTip(
                            T(
                                "Unless told otherwise, Big-O means the **worst case**. Linear search is O(n) even though it sometimes finds the item first try — the guarantee is what matters when you are promising a response time.",
                                "Sauf mention contraire, Big-O désigne le **pire cas**. La recherche linéaire est O(n) même si elle trouve parfois l'élément du premier coup — c'est la garantie qui compte quand on promet un temps de réponse.",
                                "ما لم يُذكر خلاف ذلك، تعني Big-O **أسوأ حالة**. فالبحث الخطّي O(n) حتى لو وجد العنصر أحيانًا من أوّل محاولة — لأنّ الضمان هو ما يهمّ حين تَعِد بزمن استجابة.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "What is the time complexity of a loop nested inside another loop, each over n items?",
                                "Quelle est la complexité temporelle d'une boucle imbriquée dans une autre, chacune sur n éléments ?",
                                "ما التعقيد الزمني لحلقة داخل حلقة، كلّ منهما على n عنصرًا؟",
                            ),
                            hint=T("The inner loop runs completely for each outer step.", "La boucle interne s'exécute entièrement à chaque tour externe.", "الحلقة الداخلية تُنفَّذ كاملة عند كلّ دورة خارجية."),
                            explanation=T(
                                "n outer passes × n inner passes = n² operations, so O(n²).",
                                "n passages externes × n passages internes = n² opérations, soit O(n²).",
                                "‏n دورة خارجية × n دورة داخلية = n² عملية، أي O(n²).",
                            ),
                            options=[
                                Option(T("O(n)", "O(n)", "O(n)")),
                                Option(T("O(n log n)", "O(n log n)", "O(n log n)")),
                                Option(T("O(n²)", "O(n²)", "O(n²)"), correct=True),
                                Option(T("O(2ⁿ)", "O(2ⁿ)", "O(2ⁿ)")),
                            ],
                        ),
                        ShortAnswer(
                            prompt=T(
                                "Why is 3n² + 500n + 12 simply O(n²)? Answer in one sentence.",
                                "Pourquoi 3n² + 500n + 12 est-il simplement O(n²) ? Une phrase.",
                                "لماذا تُعدّ 3n² + 500n + 12 ببساطة O(n²)؟ أجب بجملة.",
                            ),
                            hint=T(
                                "Think about which term wins as n gets very large.",
                                "Pensez au terme qui l'emporte quand n devient très grand.",
                                "فكّر في الحدّ الذي يغلب حين يكبر n كثيرًا.",
                            ),
                            explanation=T(
                                "Constants are dropped and only the fastest-growing term is kept, because for large n the n² term dominates the rest.",
                                "On supprime les constantes et on garde le terme dominant, car pour n grand le terme en n² écrase les autres.",
                                "تُسقَط الثوابت ويُبقى الحدّ الأسرع نموًّا، لأنّ حدّ n² يطغى على البقيّة عند القيم الكبيرة لـ n.",
                            ),
                            keywords=[
                                [
                                    "dominates",
                                    "dominant",
                                    "fastest-growing",
                                    "domine",
                                    "يطغى",
                                    "الأسرع",
                                ],
                                ["constant", "constants", "constante", "ثابت", "ثوابت"],
                            ],
                            reference_answer="Because constants are dropped and only the fastest-growing term matters: for large n the n squared term dominates the rest.",
                        ),
                    ],
                ),
                Lesson(
                    slug="space-complexity",
                    minutes=30,
                    xp=55,
                    difficulty=D.intermediate,
                    title=T("Space Complexity and Trade-Offs", "Complexité en Espace et Compromis", "تعقيد المكان والمقايضات"),
                    story=T(
                        "You can nearly always buy speed with memory. The skill is knowing when the price is worth paying.",
                        "On peut presque toujours acheter de la vitesse avec de la mémoire. Le talent est de savoir quand le prix en vaut la peine.",
                        "يمكنك دائمًا تقريبًا شراء السرعة بالذاكرة. والمهارة أن تعرف متى يستحقّ الثمن.",
                    ),
                    objective=T(
                        "Measure the extra memory an algorithm needs and reason about time–space trade-offs.",
                        "Mesurer la mémoire supplémentaire nécessaire et raisonner sur le compromis temps–espace.",
                        "قياس الذاكرة الإضافية التي تحتاجها الخوارزمية والاستدلال على مقايضة الزمن والمكان.",
                    ),
                    skills=T(
                        "Auxiliary space, in-place algorithms, memoisation, trade-offs",
                        "Espace auxiliaire, algorithmes en place, mémoïsation, compromis",
                        "المساحة الإضافية، الخوارزميات في المكان، الحفظ المؤقّت، المقايضات",
                    ),
                    blocks=[
                        Text(
                            T(
                                "**Space complexity** counts the memory an algorithm needs *beyond its input*. Reversing a list by swapping ends inwards is O(1) extra space; building a reversed copy is O(n). Both are O(n) time, so on a large input the difference is entirely about memory.",
                                "La **complexité en espace** compte la mémoire nécessaire *au-delà de l'entrée*. Inverser une liste par échanges est en O(1) d'espace ; construire une copie inversée est en O(n). Les deux sont en O(n) temps : sur une grande entrée, toute la différence est la mémoire.",
                                "**تعقيد المكان** يحسب الذاكرة التي تحتاجها الخوارزمية *زيادةً على مدخلاتها*. فعكس القائمة بالتبديل من الطرفين يكلّف O(1) مساحة إضافية، أمّا بناء نسخة معكوسة فيكلّف O(n). وكلاهما O(n) زمنًا، فيكون الفرق كلّه في الذاكرة عند المدخلات الكبيرة.",
                            )
                        ),
                        Code(
                            T(
                                "The same result, two very different memory profiles:",
                                "Le même résultat, deux profils mémoire très différents :",
                                "النتيجة نفسها بملمحين مختلفين تمامًا للذاكرة:",
                            ),
                            "def reverse_copy(items):        # O(n) time, O(n) extra space\n"
                            "    return items[::-1]\n\n"
                            "def reverse_in_place(items):    # O(n) time, O(1) extra space\n"
                            "    left, right = 0, len(items) - 1\n"
                            "    while left < right:\n"
                            "        items[left], items[right] = items[right], items[left]\n"
                            "        left += 1\n"
                            "        right -= 1\n"
                            "    return items\n\n"
                            "print(reverse_copy([1, 2, 3]))\n"
                            "print(reverse_in_place([1, 2, 3]))",
                        ),
                        Text(
                            T(
                                "**Memoisation** is the classic trade: remember results you have already computed so you never compute them twice. It turns exponential recursions into linear ones — at the cost of a table that grows with the number of distinct inputs.",
                                "La **mémoïsation** est le compromis classique : retenir les résultats déjà calculés pour ne jamais les recalculer. Elle transforme des récursions exponentielles en récursions linéaires — au prix d'une table qui croît avec le nombre d'entrées distinctes.",
                                "**الحفظ المؤقّت (memoisation)** هو المقايضة الكلاسيكية: تذكّر النتائج المحسوبة كي لا تحسبها مرّتين. وهو يحوّل الاستدعاءات الذاتية الأسّية إلى خطّية — بثمن جدول ينمو بعدد المدخلات المختلفة.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "An algorithm builds a set of every item it has seen. What is its space complexity?",
                                "Un algorithme construit un ensemble de tous les éléments vus. Quelle est sa complexité en espace ?",
                                "خوارزمية تبني مجموعة بكلّ عنصر رأته. ما تعقيدها المكاني؟",
                            ),
                            hint=T("How does the set grow with the input?", "Comment l'ensemble croît-il avec l'entrée ?", "كيف تنمو المجموعة مع المدخلات؟"),
                            explanation=T(
                                "In the worst case every item is distinct, so the set holds n items: O(n) extra space.",
                                "Au pire, tous les éléments sont distincts : l'ensemble contient n éléments, soit O(n) d'espace.",
                                "في أسوأ حالة تكون كلّ العناصر مختلفة فتحوي المجموعة n عنصرًا: مساحة إضافية O(n).",
                            ),
                            options=[
                                Option(T("O(1)", "O(1)", "O(1)")),
                                Option(T("O(log n)", "O(log n)", "O(log n)")),
                                Option(T("O(n)", "O(n)", "O(n)"), correct=True),
                                Option(T("O(n²)", "O(n²)", "O(n²)")),
                            ],
                        ),
                        CodeWriting(
                            prompt=T(
                                "Write `reverse_in_place(items)` that reverses a list using only swaps — no slicing, no new list — and returns it.",
                                "Écrivez `reverse_in_place(items)` qui inverse une liste uniquement par échanges — sans slicing ni nouvelle liste — et la renvoie.",
                                "اكتب `reverse_in_place(items)` تعكس القائمة بالتبديل فقط — بلا تقطيع ولا قائمة جديدة — وتُرجعها.",
                            ),
                            hint=T(
                                "Two indices moving towards each other, swapping as they go.",
                                "Deux indices qui se rapprochent en échangeant au passage.",
                                "مؤشّران يتقاربان ويتبادلان أثناء ذلك.",
                            ),
                            explanation=T(
                                "Swapping from both ends inwards touches each element once and needs only two index variables, so it is O(n) time and O(1) extra space.",
                                "Échanger des deux extrémités vers l'intérieur touche chaque élément une fois et ne demande que deux indices : O(n) temps, O(1) espace.",
                                "التبديل من الطرفين نحو الداخل يمسّ كلّ عنصر مرّة ولا يحتاج إلّا مؤشّرين: O(n) زمنًا وO(1) مساحة.",
                            ),
                            starter_code="def reverse_in_place(items):\n    pass\n\nprint(reverse_in_place([1, 2, 3, 4]))",
                            solution_code="def reverse_in_place(items):\n    left, right = 0, len(items) - 1\n    while left < right:\n        items[left], items[right] = items[right], items[left]\n        left += 1\n        right -= 1\n    return items\n\nprint(reverse_in_place([1, 2, 3, 4]))",
                            test_code=asserts(
                                "original = [1, 2, 3, 4]",
                                "result = reverse_in_place(original)",
                                "assert result == [4, 3, 2, 1], result",
                                "assert original == [4, 3, 2, 1], 'the list must be reversed in place'",
                                "assert reverse_in_place([]) == []",
                                "assert reverse_in_place([7]) == [7]",
                            ),
                        ),
                    ],
                ),
            ],
        ),
        Module(
            slug="design-strategies",
            title=T("Algorithm Design Strategies", "Stratégies de Conception d'Algorithmes", "استراتيجيات تصميم الخوارزميات"),
            description=T(
                "Divide and conquer, greedy choices, and dynamic programming.",
                "Diviser pour régner, choix gloutons et programmation dynamique.",
                "فرّق تسُد، والاختيار الجشع، والبرمجة الديناميكية.",
            ),
            lessons=[
                Lesson(
                    slug="divide-and-conquer",
                    minutes=40,
                    xp=65,
                    difficulty=D.intermediate,
                    title=T("Divide and Conquer", "Diviser pour Régner", "فرّق تسُد"),
                    story=T(
                        "Cut the problem in half, solve both halves, combine. Do that recursively and O(n²) becomes O(n log n).",
                        "Coupez le problème en deux, résolvez les moitiés, combinez. En récursif, O(n²) devient O(n log n).",
                        "قسّم المسألة نصفين، وحُلّ النصفين، ثمّ ادمج. وبتكرار ذلك ذاتيًا تتحوّل O(n²) إلى O(n log n).",
                    ),
                    objective=T(
                        "Recognise the divide-and-conquer shape and explain why it produces a log factor.",
                        "Reconnaître la forme diviser-pour-régner et expliquer pourquoi elle produit un facteur logarithmique.",
                        "التعرّف على شكل «فرّق تسُد» وشرح سبب إنتاجه عاملًا لوغاريتميًا.",
                    ),
                    skills=T(
                        "Recursion, merge sort, binary search, recurrence intuition",
                        "Récursivité, tri fusion, recherche binaire, intuition des récurrences",
                        "الاستدعاء الذاتي، ترتيب الدمج، البحث الثنائي، حدس العلاقات التراجعية",
                    ),
                    blocks=[
                        Text(
                            T(
                                "Divide and conquer has three moves: **divide** the input into smaller pieces, **conquer** each piece by recursion, **combine** the answers. Merge sort divides in half, sorts each half, then merges — and merging two sorted lists is linear, which is where O(n log n) comes from: log n levels, O(n) work per level.",
                                "Diviser pour régner comporte trois gestes : **diviser** l'entrée, **résoudre** chaque partie par récursion, **combiner** les réponses. Le tri fusion divise en deux, trie chaque moitié, puis fusionne — et fusionner deux listes triées est linéaire : d'où O(n log n), soit log n niveaux et O(n) de travail par niveau.",
                                "لـ«فرّق تسُد» ثلاث حركات: **التقسيم** إلى أجزاء أصغر، ثمّ **الحلّ** لكلّ جزء بالاستدعاء الذاتي، ثمّ **الدمج** للإجابات. ترتيب الدمج يقسم إلى نصفين ويرتّب كلّ نصف ثمّ يدمج — ودمج قائمتين مرتّبتين خطّي، ومن هنا تأتي O(n log n): عدد المستويات log n وعمل O(n) في كلّ مستوى.",
                            )
                        ),
                        Code(
                            T(
                                "Merge sort in full — the merge step is where the sorting really happens:",
                                "Le tri fusion complet — l'étape de fusion est là où le tri se produit vraiment :",
                                "ترتيب الدمج كاملًا — وخطوة الدمج هي حيث يحدث الترتيب فعلًا:",
                            ),
                            "def merge(left, right):\n"
                            "    result, i, j = [], 0, 0\n"
                            "    while i < len(left) and j < len(right):\n"
                            "        if left[i] <= right[j]:\n"
                            "            result.append(left[i]); i += 1\n"
                            "        else:\n"
                            "            result.append(right[j]); j += 1\n"
                            "    result.extend(left[i:])\n"
                            "    result.extend(right[j:])\n"
                            "    return result\n\n"
                            "def merge_sort(items):\n"
                            "    if len(items) <= 1:            # base case\n"
                            "        return items\n"
                            "    middle = len(items) // 2\n"
                            "    return merge(merge_sort(items[:middle]), merge_sort(items[middle:]))\n\n"
                            "print(merge_sort([5, 2, 9, 1, 7]))",
                        ),
                        Text(
                            T(
                                "The log factor always comes from the same place: **how many times you can halve n before reaching the base case**. Binary search does one comparison per level and no combining, so it is O(log n); merge sort does O(n) combining per level, so it is O(n log n).",
                                "Le facteur logarithmique vient toujours du même endroit : **combien de fois on peut diviser n par deux avant le cas de base**. La recherche binaire fait une comparaison par niveau sans combinaison : O(log n) ; le tri fusion fait O(n) de combinaison par niveau : O(n log n).",
                                "العامل اللوغاريتمي يأتي دائمًا من المصدر نفسه: **كم مرّة يمكن تنصيف n قبل بلوغ حالة الأساس**. البحث الثنائي يجري مقارنة واحدة لكلّ مستوى بلا دمج، فهو O(log n)؛ وترتيب الدمج يجري دمجًا بكلفة O(n) لكلّ مستوى، فهو O(n log n).",
                            )
                        ),
                    ],
                    exercises=[
                        Ordering(
                            prompt=T(
                                "Put the three steps of divide and conquer in order.",
                                "Remettez les trois étapes de diviser-pour-régner dans l'ordre.",
                                "رتّب خطوات «فرّق تسُد» الثلاث.",
                            ),
                            hint=T("You cannot combine answers you have not produced yet.", "On ne combine pas des réponses qu'on n'a pas encore produites.", "لا تدمج إجابات لم تُنتجها بعد."),
                            explanation=T(
                                "Divide the input, solve each part recursively, then combine the partial answers into one.",
                                "Diviser l'entrée, résoudre chaque partie récursivement, puis combiner les réponses partielles.",
                                "قسّم المدخلات، ثمّ حُلّ كلّ جزء ذاتيًا، ثمّ ادمج الإجابات الجزئية في إجابة واحدة.",
                            ),
                            steps=[
                                T("Divide the input into smaller parts", "Diviser l'entrée en parties plus petites", "قسّم المدخلات إلى أجزاء أصغر"),
                                T("Solve each part recursively", "Résoudre chaque partie récursivement", "حُلّ كلّ جزء بالاستدعاء الذاتي"),
                                T("Combine the partial answers", "Combiner les réponses partielles", "ادمج الإجابات الجزئية"),
                            ],
                        ),
                        MCQ(
                            prompt=T(
                                "Why is merge sort O(n log n) rather than O(n²)?",
                                "Pourquoi le tri fusion est-il en O(n log n) et non en O(n²) ?",
                                "لماذا ترتيب الدمج O(n log n) وليس O(n²)؟",
                            ),
                            hint=T("Count the levels, and the work done at each level.", "Comptez les niveaux et le travail par niveau.", "عُدّ المستويات والعمل في كلّ مستوى."),
                            explanation=T(
                                "There are log n levels of halving, and each level merges every element once, giving O(n) work per level.",
                                "Il y a log n niveaux de division, et chaque niveau fusionne chaque élément une fois : O(n) de travail par niveau.",
                                "توجد log n من مستويات التنصيف، ويدمج كلّ مستوى كلّ عنصر مرّة، أي عمل O(n) لكلّ مستوى.",
                            ),
                            options=[
                                Option(T("Because it never compares elements", "Parce qu'il ne compare jamais d'éléments", "لأنّه لا يقارن العناصر أبدًا")),
                                Option(
                                    T(
                                        "Because there are log n levels and O(n) work per level",
                                        "Parce qu'il y a log n niveaux et O(n) de travail par niveau",
                                        "لأنّ عدد المستويات log n والعمل O(n) في كلّ مستوى",
                                    ),
                                    correct=True,
                                ),
                                Option(T("Because it uses no extra memory", "Parce qu'il n'utilise aucune mémoire supplémentaire", "لأنّه لا يستخدم ذاكرة إضافية")),
                                Option(T("Because the input is already sorted", "Parce que l'entrée est déjà triée", "لأنّ المدخلات مرتّبة أصلًا")),
                            ],
                        ),
                    ],
                ),
                Lesson(
                    slug="greedy-and-dynamic-programming",
                    minutes=40,
                    xp=70,
                    difficulty=D.advanced,
                    title=T("Greedy Algorithms and Dynamic Programming", "Algorithmes Gloutons et Programmation Dynamique", "الخوارزميات الجشعة والبرمجة الديناميكية"),
                    story=T(
                        "Take the best-looking option now, or work out every option once and remember the answers?",
                        "Prendre la meilleure option immédiate, ou calculer chaque option une fois et retenir les réponses ?",
                        "أتأخذ أفضل خيار ظاهر الآن، أم تحسب كلّ خيار مرّة وتتذكّر النتائج؟",
                    ),
                    objective=T(
                        "Tell a greedy problem from one that needs dynamic programming, and implement memoisation.",
                        "Distinguer un problème glouton d'un problème nécessitant la programmation dynamique, et implémenter la mémoïsation.",
                        "التمييز بين المسألة الجشعة والمسألة التي تتطلّب برمجة ديناميكية، وتنفيذ الحفظ المؤقّت.",
                    ),
                    skills=T(
                        "Greedy choice, optimal substructure, overlapping subproblems, memoisation",
                        "Choix glouton, sous-structure optimale, sous-problèmes chevauchants, mémoïsation",
                        "الاختيار الجشع، البنية الجزئية المثلى، المسائل الفرعية المتداخلة، الحفظ المؤقّت",
                    ),
                    blocks=[
                        Text(
                            T(
                                "A **greedy** algorithm takes the locally best option at every step and never reconsiders. It is fast and simple — and only correct for problems where the local best is provably part of the global best. Making change with 1, 5, 10 coins works greedily; with 1, 3, 4 coins it does not: for 6, greedy takes 4+1+1 while 3+3 is better.",
                                "Un algorithme **glouton** prend à chaque étape la meilleure option locale sans jamais revenir dessus. Rapide et simple — et correct uniquement lorsque l'optimum local fait démontrablement partie de l'optimum global. Rendre la monnaie avec des pièces 1, 5, 10 fonctionne ; avec 1, 3, 4 non : pour 6, le glouton prend 4+1+1 alors que 3+3 vaut mieux.",
                                "الخوارزمية **الجشعة** تأخذ أفضل خيار محلّي في كلّ خطوة ولا تعيد النظر أبدًا. وهي سريعة وبسيطة — وصحيحة فقط في المسائل التي يُثبَت أنّ الأفضل المحلّي فيها جزء من الأفضل الكلّي. فردّ الباقي بعملات 1 و5 و10 ينجح بالجشع، أمّا بعملات 1 و3 و4 فلا: عند 6 يأخذ الجشع 4+1+1 بينما 3+3 أفضل.",
                            )
                        ),
                        Text(
                            T(
                                "**Dynamic programming** applies when the same subproblem is solved again and again. Instead of recomputing, you store each answer the first time. The naive Fibonacci recursion is O(2ⁿ) purely because it recomputes; with memoisation it is O(n).",
                                "La **programmation dynamique** s'applique quand le même sous-problème revient sans cesse. Au lieu de recalculer, on stocke chaque réponse la première fois. La récursion naïve de Fibonacci est en O(2ⁿ) uniquement parce qu'elle recalcule ; avec mémoïsation elle est en O(n).",
                                "**البرمجة الديناميكية** تُستخدم حين تُحلّ المسألة الفرعية نفسها مرارًا. فبدل إعادة الحساب تخزّن كلّ إجابة في أوّل مرّة. والاستدعاء الذاتي الساذج لفيبوناتشي O(2ⁿ) لمجرّد أنّه يعيد الحساب؛ ومع الحفظ المؤقّت يصير O(n).",
                            )
                        ),
                        Code(
                            T(
                                "The same function, before and after remembering:",
                                "La même fonction, avant et après mémorisation :",
                                "الدالّة نفسها قبل التذكّر وبعده:",
                            ),
                            "def fib_slow(n):                 # O(2^n): fib(30) is ~1.6M calls\n"
                            "    if n < 2:\n"
                            "        return n\n"
                            "    return fib_slow(n - 1) + fib_slow(n - 2)\n\n"
                            "def fib_fast(n, seen=None):      # O(n): each value computed once\n"
                            "    if seen is None:\n"
                            "        seen = {}\n"
                            "    if n < 2:\n"
                            "        return n\n"
                            "    if n not in seen:\n"
                            "        seen[n] = fib_fast(n - 1, seen) + fib_fast(n - 2, seen)\n"
                            "    return seen[n]\n\n"
                            "print(fib_fast(50))              # instant; fib_slow(50) would not finish",
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "Which condition makes dynamic programming worthwhile?",
                                "Quelle condition rend la programmation dynamique utile ?",
                                "أيّ شرط يجعل البرمجة الديناميكية مجدية؟",
                            ),
                            hint=T(
                                "Think about what memoisation saves you from doing.",
                                "Pensez à ce que la mémoïsation vous évite de faire.",
                                "فكّر فيما يوفّره عليك الحفظ المؤقّت.",
                            ),
                            explanation=T(
                                "DP pays off when the same subproblems recur; storing each answer once removes the repeated work.",
                                "La PD est rentable quand les mêmes sous-problèmes reviennent ; stocker chaque réponse une fois supprime le travail répété.",
                                "تُجدي البرمجة الديناميكية حين تتكرّر المسائل الفرعية نفسها؛ فتخزين كلّ إجابة مرّة يلغي العمل المكرّر.",
                            ),
                            options=[
                                Option(T("The input is already sorted", "L'entrée est déjà triée", "المدخلات مرتّبة أصلًا")),
                                Option(
                                    T(
                                        "The same subproblems are solved repeatedly",
                                        "Les mêmes sous-problèmes sont résolus à répétition",
                                        "تُحلّ المسائل الفرعية نفسها مرارًا",
                                    ),
                                    correct=True,
                                ),
                                Option(T("There is no recursion involved", "Aucune récursivité n'est en jeu", "لا يوجد استدعاء ذاتي")),
                                Option(T("The input is very small", "L'entrée est très petite", "المدخلات صغيرة جدًا")),
                            ],
                        ),
                        CodeWriting(
                            prompt=T(
                                "Write `fib(n)` using memoisation so that `fib(60)` returns instantly. Return the nth Fibonacci number with fib(0)=0 and fib(1)=1.",
                                "Écrivez `fib(n)` avec mémoïsation pour que `fib(60)` réponde instantanément. Renvoyez le n-ième nombre de Fibonacci avec fib(0)=0 et fib(1)=1.",
                                "اكتب `fib(n)` بالحفظ المؤقّت بحيث تُرجع `fib(60)` فورًا. أعِد عدد فيبوناتشي النوني حيث fib(0)=0 وfib(1)=1.",
                            ),
                            hint=T(
                                "Keep a dictionary of results and check it before recursing.",
                                "Gardez un dictionnaire de résultats et consultez-le avant de récurser.",
                                "احتفظ بقاموس للنتائج وافحصه قبل الاستدعاء الذاتي.",
                            ),
                            explanation=T(
                                "Each value is computed once and then read from the table, turning exponential work into linear work.",
                                "Chaque valeur est calculée une fois puis lue dans la table, transformant un travail exponentiel en travail linéaire.",
                                "تُحسَب كلّ قيمة مرّة ثمّ تُقرأ من الجدول، فيتحوّل العمل الأسّي إلى خطّي.",
                            ),
                            starter_code="def fib(n, seen=None):\n    pass\n\nprint(fib(10))",
                            solution_code="def fib(n, seen=None):\n    if seen is None:\n        seen = {}\n    if n < 2:\n        return n\n    if n not in seen:\n        seen[n] = fib(n - 1, seen) + fib(n - 2, seen)\n    return seen[n]\n\nprint(fib(10))",
                            test_code=asserts(
                                "assert fib(0) == 0",
                                "assert fib(1) == 1",
                                "assert fib(10) == 55, fib(10)",
                                "assert fib(60) == 1548008755920, fib(60)",
                            ),
                        ),
                    ],
                ),
            ],
        ),
        Module(
            slug="searching-sorting-graphs",
            title=T("Searching, Sorting and Graph Algorithms", "Recherche, Tri et Algorithmes de Graphes", "البحث والترتيب وخوارزميات البيانات"),
            description=T(
                "The algorithms you will meet most often, and how to choose between them.",
                "Les algorithmes les plus courants, et comment choisir entre eux.",
                "أكثر الخوارزميات شيوعًا، وكيف تختار بينها.",
            ),
            lessons=[
                Lesson(
                    slug="choosing-a-sort",
                    minutes=35,
                    xp=60,
                    difficulty=D.intermediate,
                    title=T("Choosing a Sorting Algorithm", "Choisir un Algorithme de Tri", "اختيار خوارزمية ترتيب"),
                    story=T(
                        "Nobody writes a sort at work. Everybody has to know why the built-in one is the right choice.",
                        "Personne n'écrit un tri en entreprise. Tout le monde doit savoir pourquoi celui du langage est le bon choix.",
                        "لا أحد يكتب خوارزمية ترتيب في العمل. لكن على الجميع معرفة لماذا الخوارزمية المدمجة هي الخيار الصحيح.",
                    ),
                    objective=T(
                        "Compare common sorts by complexity and stability, and explain what a sort key is.",
                        "Comparer les tris courants par complexité et stabilité, et expliquer ce qu'est une clé de tri.",
                        "مقارنة خوارزميات الترتيب الشائعة بالتعقيد والاستقرار، وشرح ما هو مفتاح الترتيب.",
                    ),
                    skills=T(
                        "Bubble/insertion/merge/quick sort, stability, sort keys, comparison lower bound",
                        "Tris à bulles/insertion/fusion/rapide, stabilité, clés de tri, borne inférieure",
                        "الترتيب الفقاعي والإدراجي والدمجي والسريع، الاستقرار، مفاتيح الترتيب، الحدّ الأدنى للمقارنة",
                    ),
                    blocks=[
                        Text(
                            T(
                                "Bubble and insertion sort are O(n²): fine for a dozen items, hopeless for a million. Merge sort and quicksort are O(n log n) — merge sort always, quicksort on average with an O(n²) worst case. No comparison-based sort can beat O(n log n); that is a proven lower bound, not a gap waiting to be closed.",
                                "Les tris à bulles et par insertion sont en O(n²) : acceptables pour une douzaine d'éléments, désespérants pour un million. Tri fusion et tri rapide sont en O(n log n) — le premier toujours, le second en moyenne avec un pire cas en O(n²). Aucun tri par comparaison ne peut faire mieux que O(n log n) : c'est une borne inférieure démontrée, pas un écart à combler.",
                                "الترتيب الفقاعي والإدراجي O(n²): مقبولان لعشرات العناصر، ميؤوس منهما لمليون. أمّا الدمجي والسريع فـ O(n log n) — الدمجي دائمًا، والسريع في المتوسّط مع أسوأ حالة O(n²). ولا يمكن لأيّ ترتيب قائم على المقارنة أن يتجاوز O(n log n)؛ فهذا حدّ أدنى مبرهَن لا فجوة تنتظر السدّ.",
                            )
                        ),
                        Text(
                            T(
                                "A sort is **stable** when equal items keep their original order. It matters more than it sounds: sorting by surname and then by class only works if the second sort is stable, otherwise the first sort's work is destroyed. Python's `sorted()` is stable, and takes a `key` so you never write a comparison by hand.",
                                "Un tri est **stable** quand les éléments égaux conservent leur ordre initial. Cela compte plus qu'il n'y paraît : trier par nom puis par classe ne fonctionne que si le second tri est stable, sinon le premier est détruit. Le `sorted()` de Python est stable et accepte une `key`, si bien qu'on n'écrit jamais de comparaison à la main.",
                                "الترتيب **مستقرّ** إذا حافظت العناصر المتساوية على ترتيبها الأصلي. وهذا أهمّ ممّا يبدو: فالترتيب بالكنية ثمّ بالصفّ لا ينجح إلّا إذا كان الترتيب الثاني مستقرًّا، وإلّا أُتلف عمل الأوّل. ودالّة `sorted()` في بايثون مستقرّة وتقبل `key`، فلا تحتاج لكتابة مقارنة يدويًا.",
                            )
                        ),
                        Code(
                            T(
                                "Sorting by a key, then by a second key, relying on stability:",
                                "Trier par une clé, puis par une seconde, en s'appuyant sur la stabilité :",
                                "الترتيب بمفتاح ثمّ بآخر اعتمادًا على الاستقرار:",
                            ),
                            "students = [\n"
                            "    {'name': 'Sara',    'class': 'B', 'mark': 17},\n"
                            "    {'name': 'Amina',   'class': 'A', 'mark': 14},\n"
                            "    {'name': 'Youssef', 'class': 'A', 'mark': 17},\n"
                            "]\n\n"
                            "# Sort by name first, then by mark: equal marks stay name-ordered.\n"
                            "by_name = sorted(students, key=lambda s: s['name'])\n"
                            "final = sorted(by_name, key=lambda s: s['mark'], reverse=True)\n"
                            "for s in final:\n"
                            "    print(s['mark'], s['name'])",
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "What does it mean for a sort to be stable?",
                                "Que signifie qu'un tri soit stable ?",
                                "ماذا يعني أن يكون الترتيب مستقرًّا؟",
                            ),
                            hint=T("Think about two items that compare as equal.", "Pensez à deux éléments considérés comme égaux.", "فكّر في عنصرين متساويين في المقارنة."),
                            explanation=T(
                                "Items that compare equal appear in the same relative order as in the input, which is what makes multi-pass sorting work.",
                                "Les éléments égaux conservent leur ordre relatif d'entrée, ce qui rend possible le tri en plusieurs passes.",
                                "العناصر المتساوية تظهر بالترتيب النسبي نفسه الذي كانت عليه في المدخلات، وهو ما يجعل الترتيب متعدّد المرّات ممكنًا.",
                            ),
                            options=[
                                Option(T("It never crashes on large inputs", "Il ne plante jamais sur de grandes entrées", "لا ينهار أبدًا مع المدخلات الكبيرة")),
                                Option(
                                    T(
                                        "Equal items keep their original relative order",
                                        "Les éléments égaux gardent leur ordre relatif d'origine",
                                        "العناصر المتساوية تحتفظ بترتيبها النسبي الأصلي",
                                    ),
                                    correct=True,
                                ),
                                Option(T("It uses O(1) extra memory", "Il utilise O(1) de mémoire", "يستخدم ذاكرة إضافية O(1)")),
                                Option(T("It always runs in O(n) time", "Il tourne toujours en O(n)", "يعمل دائمًا بزمن O(n)")),
                            ],
                        ),
                        Prediction(
                            prompt=T("What does this print?", "Qu'affiche ce code ?", "ما الذي يطبعه هذا الكود؟"),
                            hint=T(
                                "sorted() is stable, so the earlier ordering survives among equal keys.",
                                "sorted() est stable : l'ordre antérieur survit entre clés égales.",
                                "‏sorted() مستقرّة، فيبقى الترتيب السابق بين المفاتيح المتساوية.",
                            ),
                            explanation=T(
                                "Both have mark 17, and the name sort put Sara before Youssef, so stability keeps that order.",
                                "Les deux ont 17 ; le tri par nom plaçait Sara avant Youssef, et la stabilité conserve cet ordre.",
                                "كلاهما بدرجة 17، وقد وضع الترتيب بالاسم سارة قبل يوسف، فحافظ الاستقرار على ذلك.",
                            ),
                            code="students = [\n    {'name': 'Sara', 'mark': 17},\n    {'name': 'Amina', 'mark': 14},\n    {'name': 'Youssef', 'mark': 17},\n]\nby_name = sorted(students, key=lambda s: s['name'])\nfinal = sorted(by_name, key=lambda s: s['mark'], reverse=True)\nprint([s['name'] for s in final])",
                            expected_output="['Sara', 'Youssef', 'Amina']",
                        ),
                    ],
                ),
                Lesson(
                    slug="shortest-paths",
                    minutes=40,
                    xp=70,
                    difficulty=D.advanced,
                    title=T("Graph Algorithms: Shortest Paths", "Algorithmes de Graphes : Plus Courts Chemins", "خوارزميات البيانات: أقصر المسارات"),
                    story=T(
                        "Route planning, network routing and dependency resolution are the same question asked three ways.",
                        "Calcul d'itinéraire, routage réseau et résolution de dépendances : une même question posée trois fois.",
                        "تخطيط الطرق وتوجيه الشبكات وحلّ التبعيّات هي السؤال نفسه مطروحًا بثلاث صيغ.",
                    ),
                    objective=T(
                        "Choose between BFS and Dijkstra, and explain why weights change the answer.",
                        "Choisir entre BFS et Dijkstra, et expliquer pourquoi les poids changent la réponse.",
                        "الاختيار بين BFS وديكسترا، وشرح لماذا تغيّر الأوزان الإجابة.",
                    ),
                    skills=T(
                        "BFS, DFS, Dijkstra, weighted graphs, priority queues",
                        "BFS, DFS, Dijkstra, graphes pondérés, files de priorité",
                        "‏BFS، DFS، ديكسترا، البيانات الموزونة، طوابير الأولوية",
                    ),
                    blocks=[
                        Text(
                            T(
                                "**BFS** explores in rings: everything one step away, then everything two steps away. That is exactly why it finds the shortest path when every edge costs the same. **DFS** goes as deep as it can before backing up — the right tool for reachability and cycle detection, but it gives no shortest-path guarantee.",
                                "**BFS** explore par anneaux : tout ce qui est à un pas, puis à deux pas. C'est précisément pourquoi il trouve le plus court chemin quand toutes les arêtes coûtent pareil. **DFS** descend au plus profond avant de revenir — l'outil de l'accessibilité et de la détection de cycles, mais sans garantie de plus court chemin.",
                                "**BFS** يستكشف على شكل حلقات: كلّ ما يبعد خطوة، ثمّ كلّ ما يبعد خطوتين. ولهذا بالضبط يجد أقصر مسار حين تتساوى كلفة الأضلاع. أمّا **DFS** فيتعمّق ما استطاع قبل التراجع — وهو أداة الوصولية وكشف الدورات، لكنّه لا يضمن أقصر مسار.",
                            )
                        ),
                        Text(
                            T(
                                "When edges have different costs — distance, latency, price — BFS is wrong: the path with fewest hops need not be the cheapest. **Dijkstra's algorithm** fixes this by always expanding the cheapest known frontier next, using a priority queue. It requires non-negative weights, which is why it works for road distances and not for problems with refunds or gains.",
                                "Quand les arêtes ont des coûts différents — distance, latence, prix — BFS est faux : le chemin avec le moins de sauts n'est pas forcément le moins cher. L'**algorithme de Dijkstra** corrige cela en étendant toujours la frontière la moins coûteuse, via une file de priorité. Il exige des poids positifs, d'où sa validité pour les distances routières et non pour des problèmes avec gains.",
                                "حين تختلف كلف الأضلاع — مسافة أو زمن أو سعر — يخطئ BFS: فالمسار ذو القفزات الأقلّ ليس بالضرورة الأرخص. و**خوارزمية ديكسترا** تصحّح ذلك بتوسيع أرخص جبهة معروفة دائمًا عبر طابور أولوية. وهي تشترط أوزانًا غير سالبة، ولذلك تصلح لمسافات الطرق لا لمسائل فيها مكاسب.",
                            )
                        ),
                        Code(
                            T(
                                "BFS gives the fewest-hops path on an unweighted graph:",
                                "BFS donne le chemin au moins de sauts sur un graphe non pondéré :",
                                "يعطي BFS المسار ذا القفزات الأقلّ في بيان غير موزون:",
                            ),
                            "from collections import deque\n\n"
                            "graph = {'A': ['B', 'C'], 'B': ['D'], 'C': ['D'], 'D': ['E'], 'E': []}\n\n"
                            "def shortest_hops(graph, start, goal):\n"
                            "    queue = deque([(start, [start])])\n"
                            "    seen = {start}\n"
                            "    while queue:\n"
                            "        node, path = queue.popleft()\n"
                            "        if node == goal:\n"
                            "            return path\n"
                            "        for neighbour in graph[node]:\n"
                            "            if neighbour not in seen:\n"
                            "                seen.add(neighbour)\n"
                            "                queue.append((neighbour, path + [neighbour]))\n"
                            "    return None\n\n"
                            "print(shortest_hops(graph, 'A', 'E'))",
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "Your graph has roads of different lengths. Which algorithm finds the shortest total distance?",
                                "Votre graphe a des routes de longueurs différentes. Quel algorithme trouve la distance totale la plus courte ?",
                                "بيانك فيه طرق بأطوال مختلفة. أيّ خوارزمية تجد أقصر مسافة إجمالية؟",
                            ),
                            hint=T("BFS counts hops, not distance.", "BFS compte les sauts, pas la distance.", "‏BFS يعدّ القفزات لا المسافة."),
                            explanation=T(
                                "With weighted edges, Dijkstra expands the cheapest frontier first and is the correct choice; BFS would return the fewest-hops path instead.",
                                "Avec des arêtes pondérées, Dijkstra étend d'abord la frontière la moins coûteuse : c'est le bon choix ; BFS renverrait le chemin au moins de sauts.",
                                "مع الأضلاع الموزونة توسّع ديكسترا أرخص جبهة أوّلًا وهي الخيار الصحيح؛ أمّا BFS فيُرجع المسار ذا القفزات الأقلّ.",
                            ),
                            options=[
                                Option(T("BFS", "BFS", "BFS")),
                                Option(T("DFS", "DFS", "DFS")),
                                Option(T("Dijkstra's algorithm", "L'algorithme de Dijkstra", "خوارزمية ديكسترا"), correct=True),
                                Option(T("Binary search", "La recherche binaire", "البحث الثنائي")),
                            ],
                        ),
                        Prediction(
                            prompt=T(
                                "What path does this BFS return?",
                                "Quel chemin ce BFS renvoie-t-il ?",
                                "أيّ مسار يُرجعه هذا الـ BFS؟",
                            ),
                            hint=T("Neighbours are explored in the order they are listed.", "Les voisins sont explorés dans l'ordre où ils sont listés.", "يُستكشف الجيران بالترتيب المذكور."),
                            explanation=T(
                                "A reaches B before C, B reaches D first, and D reaches E, so the path found is A→B→D→E.",
                                "A atteint B avant C, B atteint D en premier, et D atteint E : le chemin est A→B→D→E.",
                                "يصل A إلى B قبل C، ويصل B إلى D أوّلًا، ثمّ D إلى E، فيكون المسار A→B→D→E.",
                            ),
                            code="from collections import deque\n\ngraph = {'A': ['B', 'C'], 'B': ['D'], 'C': ['D'], 'D': ['E'], 'E': []}\n\ndef shortest_hops(graph, start, goal):\n    queue = deque([(start, [start])])\n    seen = {start}\n    while queue:\n        node, path = queue.popleft()\n        if node == goal:\n            return path\n        for neighbour in graph[node]:\n            if neighbour not in seen:\n                seen.add(neighbour)\n                queue.append((neighbour, path + [neighbour]))\n    return None\n\nprint(shortest_hops(graph, 'A', 'E'))",
                            expected_output="['A', 'B', 'D', 'E']",
                        ),
                    ],
                ),
            ],
        ),
    ],
)


async def seed_algorithms_complexity(db, order: int) -> int:
    print("Seeding Algorithms & Complexity...")
    return await seed_course(db, ALGORITHMS_COMPLEXITY, order)
