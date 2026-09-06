"""Data Structures & Algorithms — the core course.

Arrays through graphs, sorting and searching: the material every technical
interview and every performance-sensitive program draws on. Combined with the
already-written Tries module (app.seed.expansions.DSA_MODULES) into one course
by app.seed.expansions.seed_data_structures_algorithms.
"""

from app.models import DifficultyEnum as D

from .authoring import (
    Code,
    CodeWriting,
    ExamTip,
    Lesson,
    MCQ,
    Module,
    Option,
    Ordering,
    Prediction,
    T,
    Text,
    asserts,
    prints,
)

CORE_DSA_MODULES = [
    Module(
        slug="arrays-and-linked-lists",
        title=T("Arrays & Linked Lists", "Tableaux et Listes Chaînées", "المصفوفات والقوائم المترابطة"),
        description=T(
            "The two most basic ways to hold a sequence of things, and why the choice between them matters.",
            "Les deux façons les plus basiques de conserver une séquence d'éléments, et pourquoi ce choix compte.",
            "أبسط طريقتين لحفظ سلسلة من العناصر، ولماذا يهمّ الاختيار بينهما.",
        ),
        lessons=[
            Lesson(
                slug="arrays-and-memory",
                minutes=30,
                xp=50,
                difficulty=D.beginner,
                title=T("Arrays and Memory", "Les Tableaux et la Mémoire", "المصفوفات والذاكرة"),
                story=T(
                    "A list in Python looks like magic until you ask why `my_list[0]` is instant no matter how long the list is.",
                    "Une liste en Python semble magique jusqu'à ce qu'on se demande pourquoi `my_list[0]` est instantané peu importe sa longueur.",
                    "تبدو القائمة في Python سحرية إلى أن تسأل لماذا يكون `my_list[0]` فوريًا مهما طال طولها.",
                ),
                objective=T(
                    "Explain why array indexing is O(1), and why inserting at the front of a large array is slow.",
                    "Expliquer pourquoi l'indexation d'un tableau est en O(1), et pourquoi insérer en tête d'un grand tableau est lent.",
                    "شرح سبب كون الوصول للعنصر عبر الفهرس O(1)، ولماذا يكون الإدراج في بداية مصفوفة كبيرة بطيئًا.",
                ),
                skills=T(
                    "Arrays, contiguous memory, indexing, Big-O of access vs. insertion",
                    "Tableaux, mémoire contiguë, indexation, complexité de l'accès vs. de l'insertion",
                    "المصفوفات، الذاكرة المتجاورة، الفهرسة، تعقيد الوصول مقابل الإدراج",
                ),
                blocks=[
                    Text(T(
                        "An array is a block of memory slots sitting right next to each other, all the same size. "
                        "If the array starts at memory address 1000 and each slot holds 8 bytes, the computer finds "
                        "element `i` with pure arithmetic: `1000 + i * 8`. No searching, no walking through the list — "
                        "that's why `array[i]` is O(1): constant time, regardless of how many elements exist.",
                        "Un tableau est un bloc de cases mémoire placées côte à côte, toutes de la même taille. "
                        "Si le tableau commence à l'adresse 1000 et que chaque case fait 8 octets, l'ordinateur trouve "
                        "l'élément `i` par simple arithmétique : `1000 + i * 8`. Aucune recherche, aucun parcours — "
                        "c'est pourquoi `array[i]` est en O(1) : temps constant, quel que soit le nombre d'éléments.",
                        "المصفوفة كتلة من خانات الذاكرة المتجاورة، وكلها بنفس الحجم. إذا بدأت المصفوفة عند العنوان 1000 "
                        "وكانت كل خانة 8 بايت، يجد الحاسوب العنصر `i` بعملية حسابية بسيطة: `1000 + i * 8`. لا بحث ولا "
                        "تصفّح — لهذا يكون `array[i]` بزمن ثابت O(1) بغضّ النظر عن عدد العناصر.",
                    )),
                    Text(T(
                        "That same contiguity is what makes inserting at the *front* expensive: every existing element "
                        "has to shift one slot over to make room, which is O(n) — proportional to the array's length. "
                        "Appending at the *end* is usually O(1), since there's often free space right after the last slot.",
                        "Cette même contiguïté rend l'insertion en *tête* coûteuse : chaque élément existant doit se "
                        "décaler d'une case pour faire de la place, ce qui est en O(n) — proportionnel à la longueur du "
                        "tableau. Ajouter à la *fin* est généralement en O(1), car il y a souvent de la place libre juste après.",
                        "هذا التجاور نفسه يجعل الإدراج في *البداية* مكلفًا: يجب أن يتحرّك كل عنصر موجود خانة واحدة "
                        "لإفساح المجال، وهو ما يكلّف O(n) — يتناسب مع طول المصفوفة. أمّا الإضافة في *النهاية* فعادة "
                        "O(1) لأن هناك غالبًا مساحة فارغة بعد آخر خانة مباشرة.",
                    )),
                    Code(
                        T("Python's list is a dynamic array — it over-allocates so appends are usually O(1).",
                          "La liste de Python est un tableau dynamique — elle sur-alloue pour que l'ajout soit souvent en O(1).",
                          "قائمة Python مصفوفة ديناميكية — تحجز أكثر من اللازم كي تكون الإضافة غالبًا O(1)."),
                        'numbers = [10, 20, 30]\nprint(numbers[0])       # O(1): direct address math\nnumbers.append(40)      # usually O(1): room at the end\nnumbers.insert(0, 5)    # O(n): every element shifts right',
                    ),
                ],
                exercises=[
                    MCQ(
                        T("Why is `array[i]` constant time regardless of array length?",
                          "Pourquoi `array[i]` est-il en temps constant, quelle que soit la longueur du tableau ?",
                          "لماذا يكون `array[i]` بزمن ثابت بغضّ النظر عن طول المصفوفة؟"),
                        T("Think about how the address of element i is computed.",
                          "Pensez à comment l'adresse de l'élément i est calculée.",
                          "فكّر في كيفية حساب عنوان العنصر i."),
                        T("The address is computed directly from the index with arithmetic — no searching is needed.",
                          "L'adresse est calculée directement à partir de l'index par arithmétique — aucune recherche n'est nécessaire.",
                          "يُحسب العنوان مباشرة من الفهرس عبر عملية حسابية — لا حاجة لأي بحث."),
                        [
                            Option(T("The computer checks each element until it finds index i", "L'ordinateur vérifie chaque élément jusqu'à trouver l'index i", "يفحص الحاسوب كل عنصر حتى يجد الفهرس i")),
                            Option(T("The address of element i is computed directly from the start address and i", "L'adresse de l'élément i est calculée directement à partir de l'adresse de départ et de i", "يُحسب عنوان العنصر i مباشرة من عنوان البداية وi"), correct=True),
                            Option(T("Arrays are always small enough to check instantly", "Les tableaux sont toujours assez petits pour être vérifiés instantanément", "المصفوفات صغيرة دائمًا بما يكفي للفحص الفوري")),
                            Option(T("Python caches every possible index", "Python met en cache chaque index possible", "تخزّن Python كل فهرس ممكن مؤقتًا")),
                        ],
                    ),
                    Prediction(
                        T("What does this print?", "Qu'affiche ce code ?", "ماذا يطبع هذا الكود؟"),
                        T("insert(0, ...) shifts everything right by one.",
                          "insert(0, ...) décale tout d'une position vers la droite.",
                          "insert(0, ...) يزيح كل شيء خانة واحدة لليمين."),
                        T("Inserting at index 0 pushes every existing element one slot over.",
                          "Insérer à l'index 0 pousse chaque élément existant d'une case.",
                          "الإدراج عند الفهرس 0 يدفع كل عنصر موجود خانة واحدة."),
                        'nums = [1, 2, 3]\nnums.insert(0, 0)\nprint(nums)',
                        '[0, 1, 2, 3]',
                    ),
                ],
            ),
            Lesson(
                slug="linked-lists",
                minutes=35,
                xp=60,
                difficulty=D.intermediate,
                title=T("Linked Lists", "Les Listes Chaînées", "القوائم المترابطة"),
                story=T(
                    "A linked list gives up instant indexing to get something arrays can't: O(1) insertion anywhere, "
                    "without shifting a single other element.",
                    "Une liste chaînée renonce à l'indexation instantanée pour obtenir ce que les tableaux ne peuvent pas : "
                    "une insertion en O(1) n'importe où, sans décaler le moindre autre élément.",
                    "تتخلّى القائمة المترابطة عن الفهرسة الفورية لتكسب ما لا تقدر عليه المصفوفات: إدراج بزمن O(1) في أي "
                    "مكان، دون إزاحة أي عنصر آخر.",
                ),
                objective=T(
                    "Build a singly linked node structure and traverse it, and explain the arrays-vs-linked-lists trade-off.",
                    "Construire une structure de nœuds chaînés et la parcourir, et expliquer le compromis tableaux vs. listes chaînées.",
                    "بناء بنية عقد مترابطة أحادية الاتجاه والمرور عبرها، وشرح المفاضلة بين المصفوفات والقوائم المترابطة.",
                ),
                skills=T(
                    "Nodes, pointers/references, traversal, arrays vs. linked lists",
                    "Nœuds, pointeurs/références, parcours, tableaux vs. listes chaînées",
                    "العقد، المؤشرات/المراجع، المرور، المصفوفات مقابل القوائم المترابطة",
                ),
                blocks=[
                    Text(T(
                        "A linked list is a chain of separate nodes scattered anywhere in memory. Each node holds a "
                        "value and a reference to the *next* node. There's no arithmetic shortcut to node 50 — you "
                        "have to walk the chain from the start, one link at a time, so indexing is O(n). What you get "
                        "in exchange: inserting a new node anywhere only means rewiring two references, O(1), with "
                        "nothing else in the list touched.",
                        "Une liste chaînée est une chaîne de nœuds séparés, dispersés n'importe où en mémoire. Chaque "
                        "nœud contient une valeur et une référence vers le nœud *suivant*. Il n'y a pas de raccourci "
                        "arithmétique vers le nœud 50 — il faut parcourir la chaîne depuis le début, lien par lien, "
                        "donc l'indexation est en O(n). En échange : insérer un nouveau nœud n'importe où ne demande "
                        "que de rebrancher deux références, en O(1), sans toucher au reste de la liste.",
                        "القائمة المترابطة سلسلة من العقد المنفصلة المبعثرة في أي مكان بالذاكرة. تحمل كل عقدة قيمة "
                        "ومرجعًا إلى العقدة *التالية*. لا يوجد اختصار حسابي للوصول للعقدة رقم 50 — يجب المرور عبر "
                        "السلسلة من البداية، رابطًا رابطًا، فتكون الفهرسة O(n). في المقابل: يتطلّب إدراج عقدة جديدة "
                        "في أي مكان إعادة ربط مرجعين فقط، بزمن O(1)، دون المساس ببقية القائمة.",
                    )),
                    Code(
                        T("A minimal node and a three-node chain built by hand.",
                          "Un nœud minimal et une chaîne de trois nœuds construite manuellement.",
                          "عقدة بسيطة وسلسلة من ثلاث عقد مبنية يدويًا."),
                        'class Node:\n    def __init__(self, value):\n        self.value = value\n        self.next = None\n\nhead = Node("a")\nhead.next = Node("b")\nhead.next.next = Node("c")\n\ncurrent = head\nwhile current is not None:\n    print(current.value)\n    current = current.next',
                    ),
                    ExamTip(T(
                        "If a problem says \"insert/delete frequently, rarely access by position\" — think linked list. "
                        "If it says \"look up by position constantly\" — think array.",
                        "Si un problème dit « insérer/supprimer souvent, accéder par position rarement » — pensez liste chaînée. "
                        "S'il dit « accéder par position constamment » — pensez tableau.",
                        "إذا قالت المسألة «إدراج/حذف متكرر، وصول نادر حسب الموضع» — فكّر بقائمة مترابطة. "
                        "وإذا قالت «وصول متكرر حسب الموضع» — فكّر بمصفوفة.",
                    )),
                ],
                exercises=[
                    CodeWriting(
                        T("Write `to_list(head)` that walks a linked list and returns a Python list of its values.",
                          "Écrivez `to_list(head)` qui parcourt une liste chaînée et renvoie une liste Python de ses valeurs.",
                          "اكتب `to_list(head)` تمرّ عبر قائمة مترابطة وتُعيد قائمة Python بقيمها."),
                        T("Start a plain list, walk with a `current` pointer, append each value, stop at None.",
                          "Commencez avec une liste vide, parcourez avec un pointeur `current`, ajoutez chaque valeur, arrêtez à None.",
                          "ابدأ بقائمة فارغة، امشِ بمؤشر `current`، أضف كل قيمة، وتوقّف عند None."),
                        T("Traversal is always: start at head, follow .next until it's None, collecting as you go.",
                          "Le parcours est toujours : commencer à head, suivre .next jusqu'à None, en collectant au passage.",
                          "المرور دائمًا: ابدأ من head، تابع .next حتى تصل None، وجمّع القيم في الطريق."),
                        'class Node:\n    def __init__(self, value, next=None):\n        self.value = value\n        self.next = next\n\ndef to_list(head):\n    # your code here\n    pass',
                        'class Node:\n    def __init__(self, value, next=None):\n        self.value = value\n        self.next = next\n\ndef to_list(head):\n    result = []\n    current = head\n    while current is not None:\n        result.append(current.value)\n        current = current.next\n    return result',
                        asserts(
                            "chain = Node(1, Node(2, Node(3)))",
                            "assert to_list(chain) == [1, 2, 3]",
                            "assert to_list(Node('only')) == ['only']",
                        ),
                    ),
                ],
            ),
        ],
    ),
    Module(
        slug="stacks-queues-hash-tables",
        title=T("Stacks, Queues & Hash Tables", "Piles, Files et Tables de Hachage", "المكدّسات والطوابير وجداول التجزئة"),
        description=T(
            "Three data structures defined entirely by *which* operations they allow — and why that restriction is the point.",
            "Trois structures de données définies entièrement par les opérations qu'elles autorisent — et pourquoi cette restriction est utile.",
            "ثلاث بنى بيانات تُعرَّف بالكامل بالعمليات التي تسمح بها — ولماذا هذا التقييد مفيد.",
        ),
        lessons=[
            Lesson(
                slug="stacks-and-queues",
                minutes=30,
                xp=50,
                difficulty=D.beginner,
                title=T("Stacks and Queues", "Piles et Files", "المكدّسات والطوابير"),
                story=T(
                    "Undo history and a print queue solve opposite problems with the same idea: restrict how you can add and remove.",
                    "L'historique d'annulation et une file d'impression résolvent des problèmes opposés avec la même idée : restreindre l'ajout et le retrait.",
                    "يحلّ سجلّ التراجع وطابور الطباعة مشكلتين متعاكستين بفكرة واحدة: تقييد كيفية الإضافة والإزالة.",
                ),
                objective=T(
                    "Implement a stack (LIFO) and a queue (FIFO) and pick the right one for a given problem.",
                    "Implémenter une pile (LIFO) et une file (FIFO) et choisir la bonne pour un problème donné.",
                    "تنفيذ مكدّس (LIFO) وطابور (FIFO) واختيار المناسب لمسألة معيّنة.",
                ),
                skills=T(
                    "Stack (LIFO), queue (FIFO), push/pop, enqueue/dequeue",
                    "Pile (LIFO), file (FIFO), push/pop, enqueue/dequeue",
                    "المكدّس (LIFO)، الطابور (FIFO)، push/pop، enqueue/dequeue",
                ),
                blocks=[
                    Text(T(
                        "A **stack** is Last-In-First-Out (LIFO): the last thing you pushed is the first thing that "
                        "comes back out — exactly how a stack of plates works, and exactly how \"undo\" works: your "
                        "most recent action is the first one undone. A **queue** is First-In-First-Out (FIFO): the "
                        "first thing in line is the first one served, like a real queue at a checkout.",
                        "Une **pile** fonctionne en Dernier Entré, Premier Sorti (LIFO) : le dernier élément empilé est "
                        "le premier à ressortir — exactement comme une pile d'assiettes, et exactement comme "
                        "« annuler » : votre action la plus récente est la première annulée. Une **file** fonctionne "
                        "en Premier Entré, Premier Sorti (FIFO) : le premier arrivé est le premier servi, comme une "
                        "vraie file d'attente en caisse.",
                        "**المكدّس** يعمل بمبدأ آخر داخل أول خارج (LIFO): آخر عنصر أضفته هو أول ما يخرج — تمامًا كتكديس "
                        "الصحون، وتمامًا كآلية «تراجع»: أحدث إجراء هو أول ما يُلغى. أمّا **الطابور** فيعمل بمبدأ أول "
                        "داخل أول خارج (FIFO): أول من ينضمّ هو أول من يُخدم، تمامًا كطابور حقيقي عند الصندوق.",
                    )),
                    Code(
                        T("Python's list works as both, with different ends.",
                          "La liste Python fait office des deux, avec des extrémités différentes.",
                          "تعمل قائمة Python كلا البنيتين، باستخدام طرفين مختلفين."),
                        'stack = []\nstack.append("a")\nstack.append("b")\nprint(stack.pop())   # "b" -- LIFO\n\nfrom collections import deque\nqueue = deque()\nqueue.append("a")\nqueue.append("b")\nprint(queue.popleft())  # "a" -- FIFO',
                    ),
                ],
                exercises=[
                    MCQ(
                        T("A browser's \"back\" button behaves like which structure?",
                          "Le bouton « retour » d'un navigateur se comporte comme quelle structure ?",
                          "زرّ «رجوع» في المتصفح يتصرّف مثل أي بنية؟"),
                        T("The page you visited most recently is the one \"back\" returns to first.",
                          "La page visitée le plus récemment est celle où « retour » vous ramène en premier.",
                          "الصفحة التي زرتها مؤخرًا هي أول ما يعيدك إليه زرّ «رجوع»."),
                        T("Most recent visited page comes back first — that's LIFO, a stack.",
                          "La page visitée le plus récemment revient en premier — c'est LIFO, une pile.",
                          "أحدث صفحة تمّت زيارتها تعود أولًا — وهذا LIFO، أي مكدّس."),
                        [
                            Option(T("A queue (FIFO)", "Une file (FIFO)", "طابور (FIFO)")),
                            Option(T("A stack (LIFO)", "Une pile (LIFO)", "مكدّس (LIFO)"), correct=True),
                            Option(T("An array with random access", "Un tableau à accès aléatoire", "مصفوفة بوصول عشوائي")),
                            Option(T("A hash table", "Une table de hachage", "جدول تجزئة")),
                        ],
                    ),
                    CodeWriting(
                        T("Write `is_balanced(s)` that returns True if every `(` in `s` has a matching `)` in the right order.",
                          "Écrivez `is_balanced(s)` qui renvoie True si chaque `(` de `s` a un `)` correspondant dans le bon ordre.",
                          "اكتب `is_balanced(s)` تُعيد True إذا كان لكل `(` في `s` قوسٌ مطابق `)` بالترتيب الصحيح."),
                        T("Push on '(', pop on ')'. If you ever pop an empty stack, or finish with a non-empty stack, it's unbalanced.",
                          "Empilez sur '(', dépilez sur ')'. Si vous dépilez une pile vide, ou terminez avec une pile non vide, c'est déséquilibré.",
                          "أضف عند '('، وأزل عند ')'. إذا حاولت الإزالة من مكدّس فارغ، أو انتهيت بمكدّس غير فارغ، فالنص غير متوازن."),
                        T("This is the classic stack application: matching parentheses is exactly a LIFO problem.",
                          "C'est l'application classique de la pile : faire correspondre des parenthèses est exactement un problème LIFO.",
                          "هذا هو التطبيق الكلاسيكي للمكدّس: مطابقة الأقواس هي بالضبط مسألة LIFO."),
                        'def is_balanced(s):\n    # your code here\n    pass',
                        'def is_balanced(s):\n    stack = []\n    for ch in s:\n        if ch == "(":\n            stack.append(ch)\n        elif ch == ")":\n            if not stack:\n                return False\n            stack.pop()\n    return len(stack) == 0',
                        asserts(
                            "assert is_balanced('(())') == True",
                            "assert is_balanced('(()') == False",
                            "assert is_balanced(')(') == False",
                            "assert is_balanced('') == True",
                        ),
                    ),
                ],
            ),
            Lesson(
                slug="hash-tables",
                minutes=35,
                xp=60,
                difficulty=D.intermediate,
                title=T("Hash Tables", "Tables de Hachage", "جداول التجزئة"),
                story=T(
                    "A Python dict looks up any key in roughly constant time, whether it holds 10 items or 10 million. Here's how.",
                    "Un dict Python retrouve n'importe quelle clé en temps quasi constant, qu'il contienne 10 éléments ou 10 millions. Voici comment.",
                    "يبحث قاموس Python عن أي مفتاح في زمن شبه ثابت، سواء احتوى 10 عناصر أو 10 ملايين. إليك كيف يحدث ذلك.",
                ),
                objective=T(
                    "Explain how a hash function turns a key into a bucket index, and what a collision is.",
                    "Expliquer comment une fonction de hachage transforme une clé en index de compartiment, et ce qu'est une collision.",
                    "شرح كيف تحوّل دالة التجزئة المفتاح إلى فهرس خانة، وما هو التصادم.",
                ),
                skills=T(
                    "Hash functions, buckets, collisions, average-case O(1) lookup",
                    "Fonctions de hachage, compartiments, collisions, recherche en O(1) en moyenne",
                    "دوال التجزئة، الخانات، التصادمات، البحث بمتوسط O(1)",
                ),
                blocks=[
                    Text(T(
                        "A hash table stores key-value pairs in an array of \"buckets\". A **hash function** turns a "
                        "key into a number, and that number (modulo the array size) picks the bucket — so `d[\"alice\"]` "
                        "doesn't search anything, it computes hash(\"alice\") and jumps straight to a bucket, giving "
                        "average O(1) lookup regardless of how many keys exist.",
                        "Une table de hachage stocke des paires clé-valeur dans un tableau de « compartiments ». Une "
                        "**fonction de hachage** transforme une clé en nombre, et ce nombre (modulo la taille du "
                        "tableau) désigne le compartiment — ainsi `d[\"alice\"]` ne recherche rien, elle calcule "
                        "hash(\"alice\") et saute directement à un compartiment, donnant une recherche en O(1) en "
                        "moyenne, quel que soit le nombre de clés.",
                        "يخزّن جدول التجزئة أزواج مفتاح-قيمة في مصفوفة من «الخانات». تحوّل **دالة التجزئة** المفتاح "
                        "إلى رقم، ويحدّد هذا الرقم (باقي قسمته على حجم المصفوفة) الخانة — فـ`d[\"alice\"]` لا تبحث عن "
                        "شيء، بل تحسب hash(\"alice\") وتقفز مباشرة إلى خانة، ما يمنح بحثًا بمتوسط O(1) بغضّ النظر عن "
                        "عدد المفاتيح.",
                    )),
                    Text(T(
                        "Two different keys can hash to the same bucket — a **collision**. A good hash table handles "
                        "this (commonly by keeping a small list per bucket) so lookups stay fast on average, even "
                        "though a single bucket with many collisions would be slow in the worst case.",
                        "Deux clés différentes peuvent se hacher vers le même compartiment — une **collision**. Une "
                        "bonne table de hachage gère cela (souvent en gardant une petite liste par compartiment) pour "
                        "que la recherche reste rapide en moyenne, même si un compartiment avec beaucoup de collisions "
                        "serait lent dans le pire des cas.",
                        "قد يتحوّل مفتاحان مختلفان إلى نفس الخانة — وهذا **تصادم**. يتعامل جدول التجزئة الجيّد مع هذا "
                        "(غالبًا بالاحتفاظ بقائمة صغيرة لكل خانة) كي يبقى البحث سريعًا في المتوسط، رغم أنّ خانة واحدة "
                        "بها تصادمات كثيرة ستكون بطيئة في أسوأ حال.",
                    )),
                ],
                exercises=[
                    MCQ(
                        T("Why is dict lookup average O(1) instead of O(n)?",
                          "Pourquoi la recherche dans un dict est-elle en O(1) en moyenne plutôt qu'en O(n) ?",
                          "لماذا يكون البحث في القاموس بمتوسط O(1) بدلًا من O(n)؟"),
                        T("Think about what the hash function lets the table skip.",
                          "Pensez à ce que la fonction de hachage permet à la table d'éviter.",
                          "فكّر فيما تتيح دالة التجزئة للجدول تخطّيه."),
                        T("The hash function computes the bucket directly, so no scan through the other keys is needed.",
                          "La fonction de hachage calcule directement le compartiment, donc aucun parcours des autres clés n'est nécessaire.",
                          "تحسب دالة التجزئة الخانة مباشرة، فلا حاجة لتصفّح بقية المفاتيح."),
                        [
                            Option(T("Python secretly sorts every dict", "Python trie secrètement chaque dict", "تُرتّب Python كل قاموس سرًّا")),
                            Option(T("The hash function computes the bucket directly instead of scanning", "La fonction de hachage calcule directement le compartiment au lieu de parcourir", "تحسب دالة التجزئة الخانة مباشرة بدل التصفّح"), correct=True),
                            Option(T("Dicts only ever hold a handful of keys", "Les dicts ne contiennent jamais que quelques clés", "لا تحمل القواميس سوى عدد قليل من المفاتيح")),
                            Option(T("Collisions never happen in practice", "Les collisions n'arrivent jamais en pratique", "لا تحدث التصادمات أبدًا عمليًا")),
                        ],
                    ),
                ],
            ),
        ],
    ),
    Module(
        slug="trees-and-graphs",
        title=T("Trees & Graphs", "Arbres et Graphes", "الأشجار والرسوم البيانية"),
        description=T(
            "Data that branches: file systems, org charts, and social networks are all trees or graphs underneath.",
            "Des données qui se ramifient : systèmes de fichiers, organigrammes et réseaux sociaux sont tous, au fond, des arbres ou des graphes.",
            "بيانات تتفرّع: أنظمة الملفات والهياكل التنظيمية والشبكات الاجتماعية كلّها أشجار أو رسوم بيانية في جوهرها.",
        ),
        lessons=[
            Lesson(
                slug="binary-trees",
                minutes=35,
                xp=60,
                difficulty=D.intermediate,
                title=T("Binary Trees", "Les Arbres Binaires", "الأشجار الثنائية"),
                story=T(
                    "A phone book sorted alphabetically lets you binary-search it. A binary search tree keeps that same speed while staying easy to update.",
                    "Un annuaire trié alphabétiquement permet une recherche binaire. Un arbre binaire de recherche garde cette même vitesse tout en restant facile à mettre à jour.",
                    "يتيح لك دليل الهاتف المرتّب أبجديًا البحث الثنائي. تحافظ شجرة البحث الثنائية على السرعة نفسها مع سهولة التحديث.",
                ),
                objective=T(
                    "Describe a binary search tree's shape rule and traverse one in order.",
                    "Décrire la règle de forme d'un arbre binaire de recherche et le parcourir dans l'ordre.",
                    "وصف قاعدة شكل شجرة البحث الثنائية والمرور عبرها بالترتيب.",
                ),
                skills=T(
                    "Nodes and children, binary search tree property, in-order traversal, recursion",
                    "Nœuds et enfants, propriété de l'arbre binaire de recherche, parcours en ordre, récursivité",
                    "العقد والأبناء، خاصية شجرة البحث الثنائية، المرور بالترتيب، الاستدعاء الذاتي",
                ),
                blocks=[
                    Text(T(
                        "A tree is nodes connected so that each has one parent (except the root) and any number of "
                        "children. A **binary** tree caps that at two children, usually called `left` and `right`. A "
                        "**binary search tree (BST)** adds one rule: everything in a node's left subtree is smaller "
                        "than the node, everything on the right is larger. That single rule is what makes searching a "
                        "BST fast — at each node you know instantly which side to continue into.",
                        "Un arbre est un ensemble de nœuds reliés de sorte que chacun ait un seul parent (sauf la "
                        "racine) et un nombre quelconque d'enfants. Un arbre **binaire** limite cela à deux enfants, "
                        "généralement `left` et `right`. Un **arbre binaire de recherche (ABR)** ajoute une règle : "
                        "tout ce qui est dans le sous-arbre gauche d'un nœud est plus petit que lui, tout ce qui est à "
                        "droite est plus grand. C'est cette seule règle qui rend la recherche dans un ABR rapide — à "
                        "chaque nœud, on sait instantanément de quel côté continuer.",
                        "الشجرة عقد مترابطة بحيث لكل عقدة أب واحد (إلا الجذر) وأيّ عدد من الأبناء. تحدّ الشجرة "
                        "**الثنائية** ذلك بابنَين، يُسمّيان عادة `left` و`right`. تضيف **شجرة البحث الثنائية** قاعدة "
                        "واحدة: كل ما في الشجرة الفرعية اليسرى لعقدة أصغر منها، وكل ما في اليمنى أكبر. هذه القاعدة "
                        "الوحيدة هي ما يجعل البحث في شجرة كهذه سريعًا — عند كل عقدة تعرف فورًا أيّ جهة تتابع فيه.",
                    )),
                    Code(
                        T("A tiny BST node and a recursive in-order traversal (prints values sorted).",
                          "Un petit nœud d'ABR et un parcours en ordre récursif (affiche les valeurs triées).",
                          "عقدة صغيرة لشجرة بحث ثنائية ومرور بالترتيب بالاستدعاء الذاتي (يطبع القيم مرتّبة)."),
                        'class Node:\n    def __init__(self, value, left=None, right=None):\n        self.value = value\n        self.left = left\n        self.right = right\n\ndef in_order(node):\n    if node is None:\n        return\n    in_order(node.left)\n    print(node.value)\n    in_order(node.right)\n\ntree = Node(5, Node(3, Node(1), Node(4)), Node(8))\nin_order(tree)  # 1, 3, 4, 5, 8',
                    ),
                    ExamTip(T(
                        "In-order traversal of a BST always visits values in sorted order — that's the property to remember, not the code.",
                        "Le parcours en ordre d'un ABR visite toujours les valeurs dans l'ordre trié — c'est la propriété à retenir, pas le code.",
                        "يزور المرور بالترتيب لشجرة البحث الثنائية القيم دائمًا مرتّبة — هذه هي الخاصية التي يجب تذكّرها لا الكود.",
                    )),
                ],
                exercises=[
                    Prediction(
                        T("What order does in_order() print these values?", "Dans quel ordre in_order() affiche-t-il ces valeurs ?", "بأيّ ترتيب تطبع in_order() هذه القيم؟"),
                        T("A BST's in-order traversal always yields sorted output.", "Le parcours en ordre d'un ABR donne toujours une sortie triée.", "يعطي المرور بالترتيب لشجرة البحث الثنائية دائمًا مخرجات مرتّبة."),
                        T("Left subtree, then node, then right subtree — recursively — always yields ascending order for a valid BST.", "Sous-arbre gauche, puis nœud, puis sous-arbre droit — récursivement — donne toujours un ordre croissant pour un ABR valide.", "الشجرة الفرعية اليسرى ثم العقدة ثم اليمنى — بالاستدعاء الذاتي — تُعطي دائمًا ترتيبًا تصاعديًا لشجرة بحث ثنائية صحيحة."),
                        'class Node:\n    def __init__(self, value, left=None, right=None):\n        self.value = value\n        self.left = left\n        self.right = right\n\ndef in_order(node):\n    if node is None:\n        return\n    in_order(node.left)\n    print(node.value)\n    in_order(node.right)\n\ntree = Node(10, Node(6, Node(4), Node(8)), Node(14))\nin_order(tree)',
                        '4\n6\n8\n10\n14',
                    ),
                ],
            ),
            Lesson(
                slug="graphs",
                minutes=35,
                xp=60,
                difficulty=D.intermediate,
                title=T("Graphs", "Les Graphes", "الرسوم البيانية"),
                story=T(
                    "A road map, a social network, and the internet's routers are all the same shape: a graph.",
                    "Une carte routière, un réseau social et les routeurs d'internet ont tous la même forme : un graphe.",
                    "خريطة الطرق والشبكة الاجتماعية وموجّهات الإنترنت لها الشكل نفسه: رسم بياني.",
                ),
                objective=T(
                    "Represent a graph with an adjacency list and traverse it with breadth-first search.",
                    "Représenter un graphe avec une liste d'adjacence et le parcourir en largeur d'abord.",
                    "تمثيل رسم بياني بقائمة تجاور والمرور عبره بالبحث بالعرض أولًا.",
                ),
                skills=T(
                    "Nodes and edges, adjacency lists, breadth-first search, shortest path in an unweighted graph",
                    "Nœuds et arêtes, listes d'adjacence, parcours en largeur, plus court chemin dans un graphe non pondéré",
                    "العقد والحواف، قوائم التجاور، البحث بالعرض أولًا، أقصر مسار في رسم بياني غير مُرجَّح",
                ),
                blocks=[
                    Text(T(
                        "A graph is nodes (often called vertices) connected by edges — with no restriction on shape: "
                        "a node can connect to any number of others, and cycles are allowed (unlike a tree). A tree "
                        "is actually a special case of a graph. The most common representation in code is an "
                        "**adjacency list**: a dictionary mapping each node to the list of nodes it connects to.",
                        "Un graphe est un ensemble de nœuds (souvent appelés sommets) reliés par des arêtes — sans "
                        "restriction de forme : un nœud peut se connecter à n'importe quel nombre d'autres, et les "
                        "cycles sont permis (contrairement à un arbre). Un arbre est en fait un cas particulier de "
                        "graphe. La représentation la plus courante en code est une **liste d'adjacence** : un "
                        "dictionnaire associant chaque nœud à la liste des nœuds auxquels il se connecte.",
                        "الرسم البياني عقد (تُسمّى غالبًا رؤوسًا) مرتبطة بحواف — دون قيد على الشكل: يمكن لعقدة أن ترتبط "
                        "بأيّ عدد من العقد الأخرى، والدورات مسموحة (خلافًا للشجرة). الشجرة في الواقع حالة خاصة من "
                        "الرسم البياني. أكثر تمثيل شائع في الكود هو **قائمة التجاور**: قاموس يربط كل عقدة بقائمة "
                        "العقد التي ترتبط بها.",
                    )),
                    Code(
                        T("Breadth-first search finds the shortest path (fewest edges) in an unweighted graph.",
                          "Le parcours en largeur trouve le plus court chemin (le moins d'arêtes) dans un graphe non pondéré.",
                          "يجد البحث بالعرض أولًا أقصر مسار (أقل عدد حواف) في رسم بياني غير مُرجَّح."),
                        'from collections import deque\n\ngraph = {\n    "a": ["b", "c"],\n    "b": ["d"],\n    "c": ["d"],\n    "d": [],\n}\n\ndef bfs(graph, start):\n    visited = {start}\n    queue = deque([start])\n    order = []\n    while queue:\n        node = queue.popleft()\n        order.append(node)\n        for neighbor in graph[node]:\n            if neighbor not in visited:\n                visited.add(neighbor)\n                queue.append(neighbor)\n    return order\n\nprint(bfs(graph, "a"))  # [\'a\', \'b\', \'c\', \'d\']',
                    ),
                ],
                exercises=[
                    CodeWriting(
                        T("Write `has_path(graph, start, end)` returning True if end is reachable from start.",
                          "Écrivez `has_path(graph, start, end)` renvoyant True si end est accessible depuis start.",
                          "اكتب `has_path(graph, start, end)` تُعيد True إذا كان end قابلًا للوصول من start."),
                        T("Do a BFS or DFS from start, tracking visited nodes, and check if end ever gets visited.",
                          "Faites un BFS ou DFS depuis start, en suivant les nœuds visités, et vérifiez si end est visité.",
                          "نفّذ BFS أو DFS من start، مع تتبّع العقد التي زرتها، وتحقّق إن كان end قد زُرت."),
                        T("Reachability is exactly what a graph traversal answers: explore everything connected to start and see if end shows up.",
                          "L'accessibilité est exactement ce qu'un parcours de graphe répond : explorer tout ce qui est connecté à start et voir si end apparaît.",
                          "الوصولية هي بالضبط ما يجيب عنه المرور في الرسم البياني: استكشف كل ما يتّصل بـstart وتحقّق إن ظهر end."),
                        'def has_path(graph, start, end):\n    # your code here\n    pass',
                        'def has_path(graph, start, end):\n    visited = {start}\n    stack = [start]\n    while stack:\n        node = stack.pop()\n        if node == end:\n            return True\n        for neighbor in graph.get(node, []):\n            if neighbor not in visited:\n                visited.add(neighbor)\n                stack.append(neighbor)\n    return start == end',
                        asserts(
                            "g = {'a': ['b'], 'b': ['c'], 'c': []}",
                            "assert has_path(g, 'a', 'c') == True",
                            "assert has_path(g, 'c', 'a') == False",
                            "assert has_path(g, 'a', 'a') == True",
                        ),
                    ),
                ],
            ),
        ],
    ),
    Module(
        slug="sorting-and-searching",
        title=T("Sorting & Searching", "Tri et Recherche", "الفرز والبحث"),
        description=T(
            "The algorithms behind every \"sort by\" button, and the search that makes a sorted list worth having.",
            "Les algorithmes derrière chaque bouton « trier par », et la recherche qui justifie d'avoir une liste triée.",
            "الخوارزميات وراء كل زرّ «فرز حسب»، والبحث الذي يجعل القائمة المرتّبة مفيدة.",
        ),
        lessons=[
            Lesson(
                slug="sorting-algorithms",
                minutes=35,
                xp=60,
                difficulty=D.intermediate,
                title=T("Sorting Algorithms", "Les Algorithmes de Tri", "خوارزميات الفرز"),
                story=T(
                    "Every language ships a built-in sort. Understanding how sorting actually works is what lets you reason about performance instead of guessing.",
                    "Chaque langage propose un tri intégré. Comprendre comment le tri fonctionne réellement permet de raisonner sur la performance au lieu de deviner.",
                    "تأتي كل لغة بخوارزمية فرز مدمجة. فهم كيفية عمل الفرز فعليًا هو ما يمكّنك من التفكير في الأداء بدلًا من التخمين.",
                ),
                objective=T(
                    "Trace bubble sort by hand and explain why it's O(n²) while built-in sorts are O(n log n).",
                    "Tracer le tri à bulles à la main et expliquer pourquoi il est en O(n²) alors que les tris intégrés sont en O(n log n).",
                    "تتبّع فرز الفقاعات يدويًا وشرح لماذا هو O(n²) بينما خوارزميات الفرز المدمجة O(n log n).",
                ),
                skills=T(
                    "Bubble sort, comparison-based sorting, O(n²) vs. O(n log n)",
                    "Tri à bulles, tri par comparaison, O(n²) vs. O(n log n)",
                    "فرز الفقاعات، الفرز بالمقارنة، O(n²) مقابل O(n log n)",
                ),
                blocks=[
                    Text(T(
                        "Bubble sort repeatedly walks the list, swapping any two neighbors that are out of order. "
                        "Each full pass \"bubbles\" the largest remaining value to its correct spot. With n elements, "
                        "that's n passes of up to n comparisons each — O(n²). Python's built-in `sorted()` uses "
                        "Timsort, a much smarter O(n log n) algorithm — the same asymptotic class as merge sort — "
                        "which is why it comfortably sorts millions of items where bubble sort would crawl.",
                        "Le tri à bulles parcourt la liste à plusieurs reprises, en échangeant deux voisins mal "
                        "ordonnés. Chaque passe complète fait « remonter » la plus grande valeur restante à sa place "
                        "correcte. Avec n éléments, cela fait n passes d'au plus n comparaisons chacune — O(n²). La "
                        "fonction intégrée `sorted()` de Python utilise Timsort, un algorithme bien plus intelligent "
                        "en O(n log n) — la même classe asymptotique que le tri fusion — ce qui explique pourquoi elle "
                        "trie des millions d'éléments sans effort là où le tri à bulles ramperait.",
                        "يمرّ فرز الفقاعات على القائمة مرارًا، ويبدّل أي جارَين خارج الترتيب. كل مرور كامل «يُصعِد» أكبر "
                        "قيمة متبقّية إلى مكانها الصحيح. مع n عنصر، هذا يعني n مرور بحدّ أقصى n مقارنة لكل منها — "
                        "O(n²). تستخدم دالة `sorted()` المدمجة في Python خوارزمية Timsort، وهي أذكى بكثير وتعمل بزمن "
                        "O(n log n) — نفس الفئة التقاربية لفرز الدمج — ولهذا تفرز ملايين العناصر بسهولة حيث يزحف فرز "
                        "الفقاعات.",
                    )),
                    Code(
                        T("Bubble sort, written out in full.", "Le tri à bulles, écrit en entier.", "فرز الفقاعات، مكتوبًا بالكامل."),
                        'def bubble_sort(items):\n    items = items.copy()\n    n = len(items)\n    for i in range(n):\n        for j in range(n - i - 1):\n            if items[j] > items[j + 1]:\n                items[j], items[j + 1] = items[j + 1], items[j]\n    return items\n\nprint(bubble_sort([5, 2, 4, 1]))  # [1, 2, 4, 5]',
                    ),
                ],
                exercises=[
                    CodeWriting(
                        T("Write `bubble_sort(items)` that returns a new sorted list without mutating the input.",
                          "Écrivez `bubble_sort(items)` qui renvoie une nouvelle liste triée sans modifier l'entrée.",
                          "اكتب `bubble_sort(items)` تُعيد قائمة جديدة مرتّبة دون تعديل المُدخل."),
                        T("Copy the list first. Then repeatedly swap adjacent out-of-order pairs until a full pass makes no swaps.",
                          "Copiez d'abord la liste. Puis échangez répétitivement les paires adjacentes mal ordonnées jusqu'à ce qu'une passe complète ne fasse plus d'échange.",
                          "انسخ القائمة أولًا. ثم بدّل الأزواج المتجاورة الخارجة عن الترتيب مرارًا حتى لا يحدث أي تبديل في مرور كامل."),
                        T("This is exactly the bubble sort shown above — the key detail graders check is that the input list itself isn't mutated.",
                          "C'est exactement le tri à bulles montré ci-dessus — le détail clé vérifié est que la liste d'entrée elle-même n'est pas modifiée.",
                          "هذا هو فرز الفقاعات المعروض أعلاه تمامًا — التفصيل الأساسي الذي يُتحقّق منه هو عدم تعديل قائمة المُدخل نفسها."),
                        'def bubble_sort(items):\n    # your code here\n    pass',
                        'def bubble_sort(items):\n    items = items.copy()\n    n = len(items)\n    for i in range(n):\n        for j in range(n - i - 1):\n            if items[j] > items[j + 1]:\n                items[j], items[j + 1] = items[j + 1], items[j]\n    return items',
                        asserts(
                            "original = [5, 2, 4, 1]",
                            "result = bubble_sort(original)",
                            "assert result == [1, 2, 4, 5]",
                            "assert original == [5, 2, 4, 1]",
                        ),
                    ),
                ],
            ),
            Lesson(
                slug="binary-search",
                minutes=30,
                xp=50,
                difficulty=D.intermediate,
                title=T("Binary Search", "La Recherche Binaire", "البحث الثنائي"),
                story=T(
                    "Guessing a number between 1 and 1000? Halving the range each time finds it in 10 guesses, not 1000.",
                    "Deviner un nombre entre 1 et 1000 ? Diviser l'intervalle par deux à chaque fois le trouve en 10 essais, pas 1000.",
                    "تخمين رقم بين 1 و1000؟ تنصيف المجال في كل مرة يجده خلال 10 محاولات، لا 1000.",
                ),
                objective=T(
                    "Implement binary search on a sorted list and explain why it requires the list to be sorted.",
                    "Implémenter la recherche binaire sur une liste triée et expliquer pourquoi elle exige que la liste soit triée.",
                    "تنفيذ البحث الثنائي في قائمة مرتّبة وشرح سبب اشتراطه أن تكون القائمة مرتّبة.",
                ),
                skills=T(
                    "Binary search, O(log n), the sorted-input precondition",
                    "Recherche binaire, O(log n), la précondition de tri de l'entrée",
                    "البحث الثنائي، O(log n)، شرط ترتيب المُدخل",
                ),
                blocks=[
                    Text(T(
                        "Binary search only works on sorted data, and that's exactly what makes it fast: check the "
                        "middle element, and the sort order tells you the entire other half can be discarded without "
                        "looking at it. Repeat on the remaining half. Each check eliminates half of what's left, so "
                        "the number of checks needed is O(log n) — for a million items, about 20 comparisons, not "
                        "500,000.",
                        "La recherche binaire ne fonctionne que sur des données triées, et c'est exactement ce qui la "
                        "rend rapide : vérifiez l'élément du milieu, et l'ordre de tri vous dit que toute l'autre "
                        "moitié peut être écartée sans même la regarder. Répétez sur la moitié restante. Chaque "
                        "vérification élimine la moitié de ce qui reste, donc le nombre de vérifications nécessaires "
                        "est en O(log n) — pour un million d'éléments, environ 20 comparaisons, pas 500 000.",
                        "يعمل البحث الثنائي فقط على بيانات مرتّبة، وهذا بالضبط ما يجعله سريعًا: تحقّق من العنصر "
                        "الأوسط، ويخبرك ترتيب الفرز أنّ النصف الآخر بأكمله يمكن استبعاده دون النظر إليه. كرّر على "
                        "النصف المتبقّي. كل تحقّق يُلغي نصف ما تبقّى، فيكون عدد الفحوصات اللازمة O(log n) — لمليون "
                        "عنصر، نحو 20 مقارنة فقط، لا 500,000.",
                    )),
                    Code(
                        T("Iterative binary search.", "Recherche binaire itérative.", "بحث ثنائي تكراري."),
                        'def binary_search(items, target):\n    low, high = 0, len(items) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if items[mid] == target:\n            return mid\n        elif items[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    return -1\n\nprint(binary_search([1, 3, 5, 7, 9, 11], 7))  # 3',
                    ),
                    ExamTip(T(
                        "If the input isn't sorted, binary search silently gives wrong answers instead of erroring — always sort first, or confirm it already is.",
                        "Si l'entrée n'est pas triée, la recherche binaire donne silencieusement de mauvaises réponses au lieu d'échouer — triez toujours d'abord, ou confirmez qu'elle l'est déjà.",
                        "إذا لم يكن المُدخل مرتّبًا، يُعطي البحث الثنائي إجابات خاطئة بصمت بدلًا من الفشل — رتّب دائمًا أولًا، أو تأكّد من أنّه مرتّب فعلًا.",
                    )),
                ],
                exercises=[
                    CodeWriting(
                        T("Write `binary_search(items, target)` returning the index of target, or -1 if absent.",
                          "Écrivez `binary_search(items, target)` renvoyant l'index de target, ou -1 si absent.",
                          "اكتب `binary_search(items, target)` تُعيد فهرس target، أو -1 إن لم يوجد."),
                        T("Track low and high bounds, check the midpoint, and narrow the range based on the comparison.",
                          "Suivez les bornes low et high, vérifiez le point milieu, et réduisez l'intervalle selon la comparaison.",
                          "تتبّع حدَّي low وhigh، تحقّق من نقطة المنتصف، وضيّق المجال حسب المقارنة."),
                        T("This is the classic binary search shown above — assumes items is already sorted ascending.",
                          "C'est la recherche binaire classique montrée ci-dessus — suppose que items est déjà trié par ordre croissant.",
                          "هذا هو البحث الثنائي الكلاسيكي المعروض أعلاه — يفترض أن items مرتّبة تصاعديًا مسبقًا."),
                        'def binary_search(items, target):\n    # your code here\n    pass',
                        'def binary_search(items, target):\n    low, high = 0, len(items) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if items[mid] == target:\n            return mid\n        elif items[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    return -1',
                        asserts(
                            "assert binary_search([1, 3, 5, 7, 9], 5) == 2",
                            "assert binary_search([1, 3, 5, 7, 9], 1) == 0",
                            "assert binary_search([1, 3, 5, 7, 9], 10) == -1",
                            "assert binary_search([], 1) == -1",
                        ),
                    ),
                ],
            ),
        ],
    ),
]
