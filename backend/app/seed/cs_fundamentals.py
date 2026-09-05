from .base import (
    get_or_create_course, get_or_create_module, get_or_create_lesson,
    LanguageEnum, DifficultyEnum, ExerciseTypeEnum
)
from .microquest_content import seed_blocks


async def seed_cs_fundamentals(db):
    print("Seeding CS Fundamentals...")
    
    course_id = await get_or_create_course(db, "cs-fundamentals", 5, [
        {"language": LanguageEnum.en, "title": "CS Fundamentals", "description": "Core computer science concepts every programmer should know", "skills": "Algorithms, OOP, Systems, Complexity, Data representation"},
        {"language": LanguageEnum.fr, "title": "Fondamentaux de l'Informatique", "description": "Concepts de base de l'informatique que tout programmeur doit connaître", "skills": "Algorithmes, POO, Systèmes, Complexité, Représentation des données"},
        {"language": LanguageEnum.ar, "title": "أساسيات علوم الحاسوب", "description": "مفاهيم أساسية في علوم الحاسوب يجب أن يعرفها كل مبرمج", "skills": "الخوارزميات، البرمجة الكائنية، الأنظمة، التعقيد، تمثيل البيانات"},
    ])
    
    # Module 1: Algorithms
    module1_id = await get_or_create_module(db, course_id, "algorithms", 1, [
        {"language": LanguageEnum.en, "title": "Algorithms", "description": "Design and analyze efficient algorithms"},
        {"language": LanguageEnum.fr, "title": "Algorithmes", "description": "Concevoir et analyser des algorithmes efficaces"},
        {"language": LanguageEnum.ar, "title": "الخوارزميات", "description": "تصميم وتحليل خوارزميات فعالة"},
    ])
    
    # Lesson 35: What Is an Algorithm?
    await get_or_create_lesson(db, module1_id, "what-is-algorithm", 1,
        DifficultyEnum.beginner, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "What Is an Algorithm?", "story": "Understand the concept of algorithms in computing", "objective": "Define algorithms, recognize them in daily life and code", "skills": "Algorithm definition, step-by-step thinking, problem specification"},
            {"language": LanguageEnum.fr, "title": "Qu'est-ce qu'un Algorithme ?", "story": "Comprenez le concept d'algorithme en informatique", "objective": "Définir les algorithmes, les reconnaître dans la vie quotidienne et le code", "skills": "Définition d'algorithme, pensée par étapes, spécification de problème"},
            {"language": LanguageEnum.ar, "title": "ما هي الخوارزمية؟", "story": "افهم مفهوم الخوارزميات في الحاسوب", "objective": "تعريف الخوارزميات، التعرف عليها في الحياة اليومية والكود", "skills": "تعريف الخوارزمية، التفكير خطوة بخطوة، مواصفات المشكلة"},
        ],
        [
            {"type": "text", "order": 1, "content": "An algorithm is a finite sequence of precise instructions to solve a problem or perform a computation. Like a recipe: clear steps, defined inputs, guaranteed outputs, terminates eventually."},
            {"type": "code", "order": 2, "content": "Algorithm example - finding maximum:", "code_example": 'def find_max(numbers):\n    if not numbers:\n        return None\n    max_val = numbers[0]\n    for n in numbers:\n        if n > max_val:\n            max_val = n\n    return max_val\n\nprint(find_max([3, 1, 4, 1, 5, 9]))  # 9'},
            {"type": "text", "order": 3, "content": "Algorithms have: input, output, definiteness (clear steps), finiteness (terminates), effectiveness (doable). Same problem, different algorithms = different efficiency."},
            # Micro-Quest blocks (hook 0, blueprint 4, exam_tip 5). The blueprint
            # is the order_steps interaction. Lessons without these render as before.
            *seed_blocks("what-is-algorithm"),
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
                    {"language": LanguageEnum.en, "prompt": "Which is NOT a property of an algorithm?", "hint": "Algorithms must terminate", "explanation": "Algorithms must be finite (terminate), definite (clear steps), have input/output, and be effective. Running forever is not a property."},
                    {"language": LanguageEnum.fr, "prompt": "Lequel n'est PAS une propriété d'un algorithme ?", "hint": "Les algorithmes doivent terminer", "explanation": "Les algorithmes doivent être finis (terminer), définis (étapes claires), avoir entrée/sortie, et être effectifs. Tourner indéfiniment n'est pas une propriété."},
                    {"language": LanguageEnum.ar, "prompt": "أي مما يلي ليس خاصية للخوارزمية؟", "hint": "الخوارزميات يجب أن تنتهي", "explanation": "يجب أن تكون الخوارزميات محدودة (تنتهي)، محددة (خطوات واضحة)، لها مدخلات/مخرجات، وفعالة. التشغيل للأبد ليس خاصية."},
                ],
                "options": [
                    {"order": 1, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "Finiteness"}, {"language": LanguageEnum.fr, "text": "Finitude"}, {"language": LanguageEnum.ar, "text": "النهاية"}]},
                    {"order": 2, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "Definiteness"}, {"language": LanguageEnum.fr, "text": "Définition"}, {"language": LanguageEnum.ar, "text": "التحديد"}]},
                    {"order": 3, "is_correct": True, "translations": [{"language": LanguageEnum.en, "text": "Runs forever"}, {"language": LanguageEnum.fr, "text": "Tourne indéfiniment"}, {"language": LanguageEnum.ar, "text": "تعمل للأبد"}]},
                    {"order": 4, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "Has input and output"}, {"language": LanguageEnum.fr, "text": "A une entrée et sortie"}, {"language": LanguageEnum.ar, "text": "لها مدخلات ومخرجات"}]},
                ]
            }
        ]
    )
    
    # Lesson 36: Complexity and Big-O
    await get_or_create_lesson(db, module1_id, "complexity-big-o", 2,
        DifficultyEnum.intermediate, 40, 60,
        [
            {"language": LanguageEnum.en, "title": "Complexity and Big-O", "story": "Measure and compare algorithm efficiency", "objective": "Analyze time and space complexity using Big-O notation", "skills": "Big-O, time complexity, space complexity, best/average/worst case"},
            {"language": LanguageEnum.fr, "title": "Complexité et Big-O", "story": "Mesurez et comparez l'efficacité des algorithmes", "objective": "Analyser la complexité temporelle et spatiale avec la notation Big-O", "skills": "Big-O, complexité temporelle, complexité spatiale, meilleur/moyen/pire cas"},
            {"language": LanguageEnum.ar, "title": "التعقيد و Big-O", "story": "قاسِ وقارن كفاءة الخوارزميات", "objective": "تحليل تعقيد الوقت والمكان باستخدام تدوين Big-O", "skills": "Big-O، تعقيد الوقت، تعقيد المساحة، أفضل/متوسط/أسوأ حالة"},
        ],
        [
            {"type": "text", "order": 1, "content": "Big-O describes how runtime/memory grows with input size n. O(1) constant, O(log n) logarithmic, O(n) linear, O(n log n) linearithmic, O(n²) quadratic, O(2ⁿ) exponential. Drop constants and lower terms."},
            {"type": "code", "order": 2, "content": "Complexity examples:", "code_example": '# O(1) - constant\ndef get_first(lst):\n    return lst[0]\n\n# O(n) - linear\ndef find_max(lst):\n    max_v = lst[0]\n    for v in lst:\n        if v > max_v:\n            max_v = v\n    return max_v\n\n# O(n²) - quadratic\ndef all_pairs(lst):\n    for i in lst:\n        for j in lst:\n            print(i, j)'},
            {"type": "text", "order": 3, "content": "Best/average/worst case: linear search O(n) worst, O(1) best. Binary search O(log n) worst. Space complexity counts extra memory. Prefer lower complexity for large inputs."},
        ],
        [
            {
                "type": ExerciseTypeEnum.code_writing,
                "order": 1,
                "xp_reward": 15,
                "starter_code": '# What is the time complexity of this function?\ndef sum_pairs(numbers):\n    total = 0\n    for i in range(len(numbers)):\n        for j in range(len(numbers)):\n            total += numbers[i] + numbers[j]\n    return total\n\n# Answer: O(____)',
                "solution_code": '# O(n²)\ndef sum_pairs(numbers):\n    total = 0\n    for i in range(len(numbers)):\n        for j in range(len(numbers)):\n            total += numbers[i] + numbers[j]\n    return total\n\n# Answer: O(n²)',
                "test_code": '',
                "validation_config": '{"expected_keywords": [["n²", "n^2", "n*n", "quadratic"]]}',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Determine the time complexity of the nested loop function.", "hint": "Outer loop runs n times, inner runs n times for each outer iteration", "explanation": "Nested loops: n * n = n² operations. Quadratic time complexity."},
                    {"language": LanguageEnum.fr, "prompt": "Déterminez la complexité temporelle de la fonction à boucles imbriquées.", "hint": "Boucle externe n fois, interne n fois pour chaque itération externe", "explanation": "Boucles imbriquées : n * n = n² opérations. Complexité temporelle quadratique."},
                    {"language": LanguageEnum.ar, "prompt": "حدد تعقيد وقت الدالة ذات الحلقات المتداخلة.", "hint": "الحلقة الخارجية n مرة، الداخلية n مرة لكل تكرار خارجي", "explanation": "الحلقات المتداخلة: n * n = n² عملية. تعقيد زمني تربيعي."},
                ]
            }
        ]
    )
    
    # Lesson 37: Searching Algorithms
    await get_or_create_lesson(db, module1_id, "searching-algorithms", 3,
        DifficultyEnum.intermediate, 40, 60,
        [
            {"language": LanguageEnum.en, "title": "Searching Algorithms", "story": "Find items efficiently in collections", "objective": "Implement linear search and binary search", "skills": "Linear search, binary search, sorted data requirement"},
            {"language": LanguageEnum.fr, "title": "Algorithmes de Recherche", "story": "Trouvez des éléments efficacement dans des collections", "objective": "Implémenter la recherche linéaire et binaire", "skills": "Recherche linéaire, recherche binaire, données triées requises"},
            {"language": LanguageEnum.ar, "title": "خوارزميات البحث", "story": "ابحث عن العناصر بكفاءة في المجموعات", "objective": "تنفيذ البحث الخطي والبحث الثنائي", "skills": "البحث الخطي، البحث الثنائي، شرط البيانات المرتبة"},
        ],
        [
            {"type": "text", "order": 1, "content": "Linear search: check each element O(n). Binary search: repeatedly divide sorted array in half O(log n). Binary search requires sorted data! Use when searching repeatedly in static data."},
            {"type": "code", "order": 2, "content": "Search algorithms:", "code_example": '# Linear search O(n)\ndef linear_search(arr, target):\n    for i, val in enumerate(arr):\n        if val == target:\n            return i\n    return -1\n\n# Binary search O(log n) - requires sorted array\ndef binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1'},
            {"type": "text", "order": 3, "content": "Binary search halves the search space each iteration. 1,000,000 items -> max 20 steps! Sorting first O(n log n) pays off if searching many times."},
            # Micro-Quest blocks (hook 0, blueprint 4, exam_tip 5). The blueprint
            # is the spot_the_bug interaction. Lessons without these render as before.
            *seed_blocks("searching-algorithms"),
        ],
        [
            {
                "type": ExerciseTypeEnum.debugging,
                "order": 1,
                "xp_reward": 15,
                "starter_code": '# Binary search has a bug - fix it\ndef binary_search(arr, target):\n    left, right = 0, len(arr)\n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid\n        else:\n            right = mid\n    return -1',
                "solution_code": 'def binary_search(arr, target):\n    left, right = 0, len(arr) - 1\n    while left <= right:\n        mid = (left + right) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid + 1\n        else:\n            right = mid - 1\n    return -1',
                "test_code": 'import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; arr = [1,3,5,7,9]; assert binary_search(arr, 5) == 2 and binary_search(arr, 2) == -1',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Fix the binary search: right bound off by one, and left/right updates don't exclude mid.", "hint": "right should be len(arr)-1, left=mid+1, right=mid-1", "explanation": "Initial right must be last index. When target > mid, search right half excluding mid (mid+1). When target < mid, search left half excluding mid (mid-1)."},
                    {"language": LanguageEnum.fr, "prompt": "Corrigez la recherche binaire : borne droite décalée, et mises à jour left/right n'excluent pas mid.", "hint": "right doit être len(arr)-1, left=mid+1, right=mid-1", "explanation": "right initial doit être le dernier index. Si target > mid, chercher moitié droite en excluant mid (mid+1). Si target < mid, chercher moitié gauche en excluant mid (mid-1)."},
                    {"language": LanguageEnum.ar, "prompt": "أصلح البحث الثنائي: الحد الأيمن خاطئ بواحد، وتحديثات left/right لا تستثني mid.", "hint": "يجب أن يكون right = len(arr)-1، left=mid+1، right=mid-1", "explanation": "يجب أن يكون right الابتدائي هو الفهرس الأخير. إذا كان target > mid، ابحث في النصف الأيمن مستثنياً mid (mid+1). إذا كان target < mid، ابحث في النصف الأيسر مستثنياً mid (mid-1)."},
                ]
            }
        ]
    )
    
    # Lesson 38: Sorting Algorithms
    await get_or_create_lesson(db, module1_id, "sorting-algorithms", 4,
        DifficultyEnum.intermediate, 45, 60,
        [
            {"language": LanguageEnum.en, "title": "Sorting Algorithms", "story": "Arrange data in order efficiently", "objective": "Understand bubble sort, merge sort, and when to use each", "skills": "Bubble sort, merge sort, quicksort concepts, stability, in-place"},
            {"language": LanguageEnum.fr, "title": "Algorithmes de Tri", "story": "Rangez les données dans l'ordre efficacement", "objective": "Comprendre le tri à bulles, tri fusion, et quand utiliser chacun", "skills": "Tri à bulles, tri fusion, concepts tri rapide, stabilité, sur place"},
            {"language": LanguageEnum.ar, "title": "خوارزميات الترتيب", "story": "رتب البيانات بالترتيب بكفاءة", "objective": "فهم ترتيب الفقاعات، الترتيب بالدمج، ومتى تستخدم كل منها", "skills": "ترتيب الفقاعات، الترتيب بالدمج، مفاهيم الترتيب السريع، الاستقرار، في المكان"},
        ],
        [
            {"type": "text", "order": 1, "content": "Bubble sort O(n²): repeatedly swap adjacent if wrong order. Simple but slow. Merge sort O(n log n): divide, sort halves, merge. Stable, not in-place. Quicksort O(n log n) average, O(n²) worst. Python's sort() uses Timsort (hybrid)."},
            {"type": "code", "order": 2, "content": "Sorting algorithms:", "code_example": '# Bubble sort O(n²)\ndef bubble_sort(arr):\n    n = len(arr)\n    for i in range(n):\n        for j in range(0, n-i-1):\n            if arr[j] > arr[j+1]:\n                arr[j], arr[j+1] = arr[j+1], arr[j]\n    return arr\n\n# Merge sort O(n log n)\ndef merge_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    mid = len(arr) // 2\n    left = merge_sort(arr[:mid])\n    right = merge_sort(arr[mid:])\n    return merge(left, right)\n\ndef merge(left, right):\n    result = []\n    i = j = 0\n    while i < len(left) and j < len(right):\n        if left[i] <= right[j]:\n            result.append(left[i])\n            i += 1\n        else:\n            result.append(right[j])\n            j += 1\n    result.extend(left[i:])\n    result.extend(right[j:])\n    return result'},
            {"type": "text", "order": 3, "content": "Stable sort keeps equal elements in original order. In-place uses O(1) extra space. For small/nearly sorted data, insertion sort can beat others. Use built-in sorted() in practice."},
        ],
        [
            {
                "type": ExerciseTypeEnum.ordering,
                "order": 1,
                "xp_reward": 10,
                "starter_code": "",
                "solution_code": "",
                "validation_config": "",
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Order these sorting algorithms from fastest to slowest average case.", "hint": "O(n log n) beats O(n²)", "explanation": "Merge sort and Quicksort are O(n log n). Bubble sort is O(n²). For large n, O(n log n) is much faster."},
                    {"language": LanguageEnum.fr, "prompt": "Ordonnez ces algorithmes de tri du plus rapide au plus lent en cas moyen.", "hint": "O(n log n) bat O(n²)", "explanation": "Tri fusion et tri rapide sont O(n log n). Tri à bulles est O(n²). Pour grand n, O(n log n) est bien plus rapide."},
                    {"language": LanguageEnum.ar, "prompt": "رتب خوارزميات الترتيب هذه من الأسرع إلى الأبطأ في الحالة المتوسطة.", "hint": "O(n log n) يتفوق على O(n²)", "explanation": "الترتيب بالدمج والترتيب السريع O(n log n). ترتيب الفقاعات O(n²). لـ n كبير، O(n log n) أسرع بكثير."},
                ],
                "options": [
                    {"order": 1, "is_correct": True, "translations": [{"language": LanguageEnum.en, "text": "Merge Sort"}, {"language": LanguageEnum.fr, "text": "Tri fusion"}, {"language": LanguageEnum.ar, "text": "الترتيب بالدمج"}]},
                    {"order": 2, "is_correct": True, "translations": [{"language": LanguageEnum.en, "text": "Quicksort"}, {"language": LanguageEnum.fr, "text": "Tri rapide"}, {"language": LanguageEnum.ar, "text": "الترتيب السريع"}]},
                    {"order": 3, "is_correct": True, "translations": [{"language": LanguageEnum.en, "text": "Bubble Sort"}, {"language": LanguageEnum.fr, "text": "Tri à bulles"}, {"language": LanguageEnum.ar, "text": "ترتيب الفقاعات"}]},
                ]
            }
        ]
    )
    
    # Module 2: Object-Oriented Programming
    module2_id = await get_or_create_module(db, course_id, "oop", 2, [
        {"language": LanguageEnum.en, "title": "Object-Oriented Programming", "description": "Model real-world concepts with classes and objects"},
        {"language": LanguageEnum.fr, "title": "Programmation Orientée Objet", "description": "Modélisez des concepts du monde réel avec classes et objets"},
        {"language": LanguageEnum.ar, "title": "البرمجة الكائنية", "description": "نمذجة مفاهيم العالم الحقيقي بالكائنات والفئات"},
    ])
    
    # Lesson 39: Objects and Classes
    await get_or_create_lesson(db, module2_id, "objects-and-classes", 1,
        DifficultyEnum.beginner, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "Objects and Classes", "story": "Bundle data and behavior together", "objective": "Define classes, create objects, use attributes and methods", "skills": "class, __init__, self, attributes, methods"},
            {"language": LanguageEnum.fr, "title": "Objets et Classes", "story": "Regroupez données et comportements ensemble", "objective": "Définir des classes, créer des objets, utiliser attributs et méthodes", "skills": "class, __init__, self, attributs, méthodes"},
            {"language": LanguageEnum.ar, "title": "الكائنات والفئات", "story": "اجمع البيانات والسلوك معاً", "objective": "تعريف الفئات، إنشاء الكائنات، استخدام السمات والطرق", "skills": "class، __init__، self، السمات، الطرق"},
        ],
        [
            {"type": "text", "order": 1, "content": "A class is a blueprint. An object is an instance. __init__ initializes attributes. self refers to the current instance. Methods are functions inside a class that operate on the object's data."},
            {"type": "code", "order": 2, "content": "Class and object:", "code_example": 'class Student:\n    def __init__(self, name, age):\n        self.name = name\n        self.age = age\n    \n    def greet(self):\n        return f"Hi, I\'m {self.name}"\n\ns = Student("Amine", 20)\nprint(s.greet())  # Hi, I\'m Amine\nprint(s.age)      # 20'},
            {"type": "text", "order": 3, "content": "Each object has its own attribute values. Methods access attributes via self. Classes enable modeling real-world entities with both state (attributes) and behavior (methods)."},
        ],
        [
            {
                "type": ExerciseTypeEnum.code_writing,
                "order": 1,
                "xp_reward": 10,
                "starter_code": '# Create a Rectangle class\nclass Rectangle:\n    def __init__(self, width, height):\n        ____\n        ____\n    \n    def area(self):\n        return self.width * self.height\n\nr = Rectangle(5, 3)\nprint(r.area())  # Should print 15',
                "solution_code": 'class Rectangle:\n    def __init__(self, width, height):\n        self.width = width\n        self.height = height\n    \n    def area(self):\n        return self.width * self.height\n\nr = Rectangle(5, 3)\nprint(r.area())',
                "test_code": 'import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "15" in output',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Complete the Rectangle class with width and height attributes and an area method.", "hint": "Use self.width = width in __init__", "explanation": "__init__ sets up initial state. self stores instance-specific data. Methods use self to access attributes."},
                    {"language": LanguageEnum.fr, "prompt": "Complétez la classe Rectangle avec les attributs width, height et la méthode area.", "hint": "Utilisez self.width = width dans __init__", "explanation": "__init__ initialise l'état. self stocke les données propres à l'instance. Les méthodes utilisent self pour accéder aux attributs."},
                    {"language": LanguageEnum.ar, "prompt": "أكمل فئة Rectangle مع سمتي width و height وطريقة area.", "hint": "استخدم self.width = width في __init__", "explanation": "__init__ تضبط الحالة الأولية. self تخزن البيانات الخاصة بالمثيل. الطرق تستخدم self للوصول للسمات."},
                ]
            }
        ]
    )
    
    # Lesson 40: Attributes and Methods
    await get_or_create_lesson(db, module2_id, "attributes-and-methods", 2,
        DifficultyEnum.beginner, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "Attributes and Methods", "story": "Deepen your understanding of object structure", "objective": "Use class attributes, instance attributes, and method types", "skills": "Class vs instance attributes, @classmethod, @staticmethod, @property"},
            {"language": LanguageEnum.fr, "title": "Attributs et Méthodes", "story": "Approfondissez votre compréhension de la structure des objets", "objective": "Utiliser les attributs de classe, d'instance, et types de méthodes", "skills": "Attributs classe vs instance, @classmethod, @staticmethod, @property"},
            {"language": LanguageEnum.ar, "title": "السمات والطرق", "story": "عمق فهمك لهيكل الكائنات", "objective": "استخدام سمات الفئة، سمات المثيل، وأنواع الطرق", "skills": "سمات الفئة مقابل المثيل، @classmethod، @staticmethod، @property"},
        ],
        [
            {"type": "text", "order": 1, "content": "Instance attributes (self.x) belong to each object. Class attributes (shared) belong to the class. @classmethod gets class as first arg (cls). @staticmethod gets no implicit first arg. @property makes method act like attribute."},
            {"type": "code", "order": 2, "content": "Attribute types:", "code_example": 'class Counter:\n    count = 0  # class attribute\n    \n    def __init__(self):\n        Counter.count += 1\n        self.id = Counter.count  # instance attribute\n    \n    @classmethod\n    def get_count(cls):\n        return cls.count\n    \n    @property\n    def is_first(self):\n        return self.id == 1\n\nc1 = Counter()\nc2 = Counter()\nprint(Counter.get_count())  # 2\nprint(c1.is_first)  # True'},
            {"type": "text", "order": 3, "content": "Use class attributes for shared data. @classmethod for factory methods. @staticmethod for utility functions. @property for computed attributes with validation."},
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
                    {"language": LanguageEnum.en, "prompt": "Which decorator makes a method accessible like an attribute?", "hint": "Use it like obj.attr not obj.attr()", "explanation": "@property lets you call a method without parentheses, like an attribute."},
                    {"language": LanguageEnum.fr, "prompt": "Quel décorateur rend une méthode accessible comme un attribut ?", "hint": "Utilisez-la comme obj.attr pas obj.attr()", "explanation": "@property permet d'appeler une méthode sans parenthèses, comme un attribut."},
                    {"language": LanguageEnum.ar, "prompt": "أي مزين يجعل الطريقة قابلة للوصول كسمة؟", "hint": "استخدمها مثل obj.attr لا obj.attr()", "explanation": "@property تتيح استدعاء طريقة بدون أقواس، كسمة."},
                ],
                "options": [
                    {"order": 1, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "@classmethod"}, {"language": LanguageEnum.fr, "text": "@classmethod"}, {"language": LanguageEnum.ar, "text": "@classmethod"}]},
                    {"order": 2, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "@staticmethod"}, {"language": LanguageEnum.fr, "text": "@staticmethod"}, {"language": LanguageEnum.ar, "text": "@staticmethod"}]},
                    {"order": 3, "is_correct": True, "translations": [{"language": LanguageEnum.en, "text": "@property"}, {"language": LanguageEnum.fr, "text": "@property"}, {"language": LanguageEnum.ar, "text": "@property"}]},
                    {"order": 4, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "@abstractmethod"}, {"language": LanguageEnum.fr, "text": "@abstractmethod"}, {"language": LanguageEnum.ar, "text": "@abstractmethod"}]},
                ]
            }
        ]
    )
    
    # Lesson 41: Encapsulation and Abstraction
    await get_or_create_lesson(db, module2_id, "encapsulation-abstraction", 3,
        DifficultyEnum.intermediate, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "Encapsulation and Abstraction", "story": "Hide complexity and protect object integrity", "objective": "Use private attributes, properties, and design clean interfaces", "skills": "Private attributes, name mangling, properties, abstraction, interface design"},
            {"language": LanguageEnum.fr, "title": "Encapsulation et Abstraction", "story": "Cachez la complexité et protégez l'intégrité des objets", "objective": "Utiliser attributs privés, properties, et concevoir des interfaces propres", "skills": "Attributs privés, name mangling, properties, abstraction, design d'interface"},
            {"language": LanguageEnum.ar, "title": "التغليف والتجريد", "story": "اخفِ التعقيد واحمِ سلامة الكائنات", "objective": "استخدام السمات الخاصة، الخصائص، وتصميم واجهات نظيفة", "skills": "السمات الخاصة، تلاعب الأسماء، الخصائص، التجريد، تصميم الواجهات"},
        ],
        [
            {"type": "text", "order": 1, "content": "Encapsulation hides internal details. Python uses _single (convention) and __double (name mangling) for private. Abstraction exposes only what's needed. Properties control access with validation."},
            {"type": "code", "order": 2, "content": "Encapsulation:", "code_example": 'class BankAccount:\n    def __init__(self, owner, balance=0):\n        self.owner = owner\n        self.__balance = balance  # private\n    \n    @property\n    def balance(self):\n        return self.__balance\n    \n    def deposit(self, amount):\n        if amount > 0:\n            self.__balance += amount\n    \n    def withdraw(self, amount):\n        if 0 < amount <= self.__balance:\n            self.__balance -= amount\n            return True\n        return False\n\nacc = BankAccount("Youssef", 1000)\nacc.deposit(500)\nprint(acc.balance)  # 1500\nacc.withdraw(200)\nprint(acc.balance)  # 1300'},
            {"type": "text", "order": 3, "content": "__balance becomes _BankAccount__balance (name mangling). Not truly private but signals intent. Properties enable validation on read/write. Abstraction: user calls deposit(), doesn't know how balance stored."},
        ],
        [
            {
                "type": ExerciseTypeEnum.code_writing,
                "order": 1,
                "xp_reward": 15,
                "starter_code": '# Create a Temperature class with encapsulation\nclass Temperature:\n    def __init__(self, celsius):\n        self.__celsius = celsius\n    \n    @property\n    def celsius(self):\n        return ____\n    \n    @celsius.setter\n    def celsius(self, value):\n        if value < -273.15:\n            raise ValueError("Below absolute zero")\n        self.__celsius = value\n    \n    @property\n    def fahrenheit(self):\n        return self.__celsius * 9/5 + 32\n\nt = Temperature(25)\nprint(t.celsius)      # 25\nprint(t.fahrenheit)   # 77.0\nt.celsius = 30\nprint(t.fahrenheit)   # 86.0',
                "solution_code": 'class Temperature:\n    def __init__(self, celsius):\n        self.__celsius = celsius\n    \n    @property\n    def celsius(self):\n        return self.__celsius\n    \n    @celsius.setter\n    def celsius(self, value):\n        if value < -273.15:\n            raise ValueError("Below absolute zero")\n        self.__celsius = value\n    \n    @property\n    def fahrenheit(self):\n        return self.__celsius * 9/5 + 32\n\nt = Temperature(25)\nprint(t.celsius)\nprint(t.fahrenheit)\nt.celsius = 30\nprint(t.fahrenheit)',
                "test_code": 'import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "25" in output and "77.0" in output and "86.0" in output',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Complete the Temperature class with encapsulated celsius and computed fahrenheit.", "hint": "return self.__celsius for getter, use @property and @celsius.setter", "explanation": "Private __celsius hides storage. Property controls access. Setter validates. Fahrenheit computed on demand."},
                    {"language": LanguageEnum.fr, "prompt": "Complétez la classe Temperature avec celsius encapsulé et fahrenheit calculé.", "hint": "return self.__celsius pour getter, utilisez @property et @celsius.setter", "explanation": "__celsius privé cache le stockage. Property contrôle l'accès. Setter valide. Fahrenheit calculé à la demande."},
                    {"language": LanguageEnum.ar, "prompt": "أكمل فئة Temperature مع celsius المغلف و fahrenheit المحسوب.", "hint": "return self.__celsius لـ getter، استخدم @property و @celsius.setter", "explanation": "__celsius خاص يخزن التخزين. Property تتحكم في الوصول. Setter تتحقق من الصحة. Fahrenheit يحسب عند الطلب."},
                ]
            }
        ]
    )
    
    # Lesson 42: Inheritance and Polymorphism
    await get_or_create_lesson(db, module2_id, "inheritance-polymorphism", 4,
        DifficultyEnum.intermediate, 40, 60,
        [
            {"language": LanguageEnum.en, "title": "Inheritance and Polymorphism", "story": "Reuse and extend code with class hierarchies", "objective": "Create subclasses, override methods, use super(), understand polymorphism", "skills": "Inheritance, super(), method overriding, polymorphism, Liskov substitution"},
            {"language": LanguageEnum.fr, "title": "Héritage et Polymorphisme", "story": "Réutilisez et étendez le code avec des hiérarchies de classes", "objective": "Créer des sous-classes, redéfinir méthodes, utiliser super(), comprendre polymorphisme", "skills": "Héritage, super(), redéfinition de méthodes, polymorphisme, substitution de Liskov"},
            {"language": LanguageEnum.ar, "title": "الوراثة والتعدد الأشكال", "story": "أعد استخدام الكود ومده مع تسلسلات الفئات", "objective": "إنشاء فئات فرعية، تجاوز الطرق، استخدام super()، فهم التعدد الأشكال", "skills": "الوراثة، super()، تجاوز الطرق، التعدد الأشكال، استبدال ليسكوف"},
        ],
        [
            {"type": "text", "order": 1, "content": "Inheritance: class Child(Parent) gets parent's attributes/methods. Override methods to change behavior. super() calls parent method. Polymorphism: different objects respond to same method call differently. Liskov: subclass usable wherever parent expected."},
            {"type": "code", "order": 2, "content": "Inheritance and polymorphism:", "code_example": 'class Animal:\n    def __init__(self, name):\n        self.name = name\n    def speak(self):\n        return "..."\n\nclass Dog(Animal):\n    def speak(self):\n        return "Woof!"\n\nclass Cat(Animal):\n    def speak(self):\n        return "Meow!"\n\nanimals = [Dog("Rex"), Cat("Whiskers")]\nfor a in animals:\n    print(a.name, "says", a.speak())'},
            {"type": "text", "order": 3, "content": "super().__init__() initializes parent. Abstract base classes (abc) define required methods. Mixins add functionality. Composition often better than deep inheritance hierarchies."},
        ],
        [
            {
                "type": ExerciseTypeEnum.visual_programming,
                "order": 1,
                "xp_reward": 15,
                "starter_code": '{"nodes": [{"id": "1", "type": "start", "config": {}}, {"id": "2", "type": "variable", "config": {"name": "animals", "value": "[Dog(\"Rex\"), Cat(\"Whiskers\")]"}}, {"id": "3", "type": "loop", "config": {"var": "a", "times": "len(animals)"}}, {"id": "4", "type": "output", "config": {"value": "a.name + \" says \" + a.speak()"}}, {"id": "5", "type": "end", "config": {}}], "edges": [{"source": "1", "target": "2"}, {"source": "2", "target": "3"}, {"source": "3", "target": "4"}, {"source": "4", "target": "5"}]}',
                "solution_code": 'class Animal:\n    def __init__(self, name):\n        self.name = name\n    def speak(self):\n        return "..."\n\nclass Dog(Animal):\n    def speak(self):\n        return "Woof!"\n\nclass Cat(Animal):\n    def speak(self):\n        return "Meow!"\n\nanimals = [Dog("Rex"), Cat("Whiskers")]\nfor a in animals:\n    print(a.name, "says", a.speak())',
                "test_code": 'import sys, io; stdout = sys.stdout; sys.stdout = io.StringIO(); exec(compile(code, "<string>", "exec")); output = sys.stdout.getvalue(); sys.stdout = stdout; assert "Woof" in output and "Meow" in output',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Build a visual program demonstrating polymorphism with Animal, Dog, and Cat classes.", "hint": "Create list of animals, loop through, call speak() on each", "explanation": "Polymorphism: same method call (speak()) produces different results based on actual object type."},
                    {"language": LanguageEnum.fr, "prompt": "Construisez un programme visuel démontrant le polymorphisme avec Animal, Dog, Cat.", "hint": "Créez liste d'animaux, parcourez, appelez speak() sur chacun", "explanation": "Polymorphisme: même appel de méthode (speak()) produit résultats différents selon le type réel de l'objet."},
                    {"language": LanguageEnum.ar, "prompt": "ابنِ برنامجاً مرئياً يوضح التعدد الأشكال مع فئات Animal، Dog، Cat.", "hint": "أنشئ قائمة حيوانات، مرر عليها، استدعي speak() على كل منها", "explanation": "التعدد الأشكال: نفس استدعاء الطريقة (speak()) ينتج نتائج مختلفة حسب نوع الكائن الفعلي."},
                ]
            }
        ]
    )
    
    # Module 3: Systems
    module3_id = await get_or_create_module(db, course_id, "systems", 3, [
        {"language": LanguageEnum.en, "title": "Systems", "description": "How computers work at the hardware and OS level"},
        {"language": LanguageEnum.fr, "title": "Systèmes", "description": "Comment les ordinateurs fonctionnent au niveau matériel et OS"},
        {"language": LanguageEnum.ar, "title": "الأنظمة", "description": "كيف تعمل أجهزة الكمبيوتر على مستوى العتاد ونظام التشغيل"},
    ])
    
    # Lesson 43: How Computers Represent Data
    await get_or_create_lesson(db, module3_id, "data-representation", 1,
        DifficultyEnum.beginner, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "How Computers Represent Data", "story": "Understand binary, encoding, and data storage", "objective": "Explain bits, bytes, binary, character encoding, and number representation", "skills": "Bits, bytes, binary, ASCII, Unicode, two's complement"},
            {"language": LanguageEnum.fr, "title": "Comment les Ordinateurs Représentent les Données", "story": "Comprenez le binaire, l'encodage et le stockage des données", "objective": "Expliquer bits, octets, binaire, encodage caractères, représentation nombres", "skills": "Bits, octets, binaire, ASCII, Unicode, complément à deux"},
            {"language": LanguageEnum.ar, "title": "كيف تمثل الحواسيب البيانات", "story": "افهم الثنائي، الترميز، وتخزين البيانات", "objective": "شرح البتات، البايتات، الثنائي، ترميز الحروف، تمثيل الأرقام", "skills": "البتات، البايتات، الثنائي، ASCII، Unicode، مكمل الاثنين"},
        ],
        [
            {"type": "text", "order": 1, "content": "Computers use binary (0 and 1). Bit = binary digit. Byte = 8 bits. Integers use two's complement for negatives. Text uses ASCII (128 chars) or Unicode (millions). Floats use IEEE 754."},
            {"type": "code", "order": 2, "content": "Data representation in Python:", "code_example": '# Binary representation\nprint(bin(10))      # 0b1010\nprint(bin(-10))     # -0b1010 (two\'s complement)\n\n# Character encoding\nprint(ord("A"))       # 65\nprint(chr(65))        # A\nprint("مرحبا".encode("utf-8"))  # bytes\n\n# Float precision\nprint(0.1 + 0.2)     # 0.30000000000000004'},
            {"type": "text", "order": 3, "content": "Two's complement: invert bits, add 1. Unicode uses variable-width (UTF-8). Floats are approximate - avoid == for equality. Use decimal module for exact money."},
        ],
        [
            {
                "type": ExerciseTypeEnum.prediction,
                "order": 1,
                "xp_reward": 10,
                "starter_code": 'print(ord("A"))\nprint(chr(97))\nprint(bin(13))',
                "solution_code": "65\na\n0b1101",
                "validation_config": '{"expected_output": "65\\na\\n0b1101"}',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "What will this code print? ord() gives code point, chr() gives character, bin() gives binary.", "hint": "A=65, a=97, 13=1101 binary", "explanation": "ord() returns Unicode code point. chr() is inverse. bin() shows binary with 0b prefix."},
                    {"language": LanguageEnum.fr, "prompt": "Qu'affichera ce code ? ord() donne le point de code, chr() le caractère, bin() le binaire.", "hint": "A=65, a=97, 13=1101 binaire", "explanation": "ord() retourne le point de code Unicode. chr() est l'inverse. bin() montre le binaire avec préfixe 0b."},
                    {"language": LanguageEnum.ar, "prompt": "ماذا سيطبع هذا الكود؟ ord() تعطي نقطة الكود، chr() تعطي الحرف، bin() تعطي الثنائي.", "hint": "A=65، a=97، 13=1101 ثنائي", "explanation": "ord() ترجع نقطة كود Unicode. chr() عكسها. bin() تظهر الثنائي ببادئة 0b."},
                ]
            }
        ]
    )
    
    # Lesson 44: Memory and Storage
    await get_or_create_lesson(db, module3_id, "memory-and-storage", 2,
        DifficultyEnum.beginner, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "Memory and Storage", "story": "Distinguish between RAM, cache, disk, and their trade-offs", "objective": "Explain memory hierarchy, volatility, and storage technologies", "skills": "RAM, cache, SSD/HDD, volatility, memory hierarchy"},
            {"language": LanguageEnum.fr, "title": "Mémoire et Stockage", "story": "Différenciez RAM, cache, disque et leurs compromis", "objective": "Expliquer la hiérarchie mémoire, volatilité, technologies stockage", "skills": "RAM, cache, SSD/HDD, volatilité, hiérarchie mémoire"},
            {"language": LanguageEnum.ar, "title": "الذاكرة والتخزين", "story": "اميز بين RAM، الكاش، القرص، ومفاضلاتهم", "objective": "شرح هرمية الذاكرة، التطاير، وتقنيات التخزين", "skills": "RAM، الكاش، SSD/HDD، التطاير، هرمية الذاكرة"},
        ],
        [
            {"type": "text", "order": 1, "content": "Memory hierarchy: Registers (fastest, tiny) -> L1/L2/L3 Cache (fast, small) -> RAM (fast, volatile) -> SSD/HDD (slow, persistent). Volatile loses data on power off. Cache bridges CPU-RAM speed gap."},
            {"type": "code", "order": 2, "content": "Memory concepts:", "code_example": '# Python memory (simplified)\nimport sys\n\nx = 42\nprint(sys.getsizeof(x))  # 28 bytes for small int\n\nlst = [1, 2, 3]\nprint(sys.getsizeof(lst))  # list overhead + pointers\n\n# Memory addresses\nprint(hex(id(x)))  # object location in memory'},
            {"type": "text", "order": 3, "content": "Variables reference objects in memory. id() gives address. Python manages memory automatically (garbage collection). Memory leaks possible with circular references."},
            # Micro-Quest blocks (hook 0, blueprint 4, exam_tip 5). The blueprint
            # is the order_steps interaction. Lessons without these render as before.
            *seed_blocks("memory-and-storage"),
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
                    {"language": LanguageEnum.en, "prompt": "Which is volatile (loses data when power off)?", "hint": "RAM needs power", "explanation": "RAM is volatile - requires constant power. SSD/HDD are non-volatile (persistent)."},
                    {"language": LanguageEnum.fr, "prompt": "Lequel est volatil (perd les données à l'arrêt) ?", "hint": "RAM a besoin d'alimentation", "explanation": "RAM est volatile - nécessite alimentation constante. SSD/HDD non-volatils (persistants)."},
                    {"language": LanguageEnum.ar, "prompt": "أيهما متطاير (يفقد البيانات عند انقطاع الطاقة)؟", "hint": "RAM تحتاج طاقة دائمة", "explanation": "RAM متطاير - يتطلب طاقة مستمرة. SSD/HDD غير متطايرين (ثابتين)."},
                ],
                "options": [
                    {"order": 1, "is_correct": True, "translations": [{"language": LanguageEnum.en, "text": "RAM"}, {"language": LanguageEnum.fr, "text": "RAM"}, {"language": LanguageEnum.ar, "text": "RAM"}]},
                    {"order": 2, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "SSD"}, {"language": LanguageEnum.fr, "text": "SSD"}, {"language": LanguageEnum.ar, "text": "SSD"}]},
                    {"order": 3, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "HDD"}, {"language": LanguageEnum.fr, "text": "HDD"}, {"language": LanguageEnum.ar, "text": "HDD"}]},
                    {"order": 4, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "USB drive"}, {"language": LanguageEnum.fr, "text": "Clé USB"}, {"language": LanguageEnum.ar, "text": "محرك USB"}]},
                ]
            }
        ]
    )
    
    # Lesson 45: Operating Systems and Processes
    await get_or_create_lesson(db, module3_id, "os-processes", 3,
        DifficultyEnum.intermediate, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "Operating Systems and Processes", "story": "Understand how OS manages resources and runs programs", "objective": "Explain processes, threads, scheduling, system calls, and virtual memory", "skills": "Processes, threads, scheduling, system calls, virtual memory, context switching"},
            {"language": LanguageEnum.fr, "title": "Systèmes d'Exploitation et Processus", "story": "Comprenez comment l'OS gère les ressources et exécute les programmes", "objective": "Expliquer processus, threads, ordonnancement, appels système, mémoire virtuelle", "skills": "Processus, threads, ordonnancement, appels système, mémoire virtuelle, commutation contexte"},
            {"language": LanguageEnum.ar, "title": "أنظمة التشغيل والعمليات", "story": "افهم كيف يدير نظام التشغيل الموارد وينفذ البرامج", "objective": "شرح العمليات، الخيوط، الجدولة، استدعاءات النظام، الذاكرة الافتراضية", "skills": "العمليات، الخيوط، الجدولة، استدعاءات النظام، الذاكرة الافتراضية، تبديل السياق"},
        ],
        [
            {"type": "text", "order": 1, "content": "OS manages hardware resources. Process = running program with own memory space. Thread = lightweight unit within process, shares memory. Scheduler decides which runs. System calls (syscalls) request OS services. Virtual memory gives each process illusion of full memory."},
            {"type": "code", "order": 2, "content": "Process concepts:", "code_example": '# Python process/thread example\nimport multiprocessing\nimport threading\nimport os\n\nprint(f"Process ID: {os.getpid()}")\nprint(f"Thread: {threading.current_thread().name}")\n\n# Process - separate memory\ndef worker():\n    print("In child process")\n\np = multiprocessing.Process(target=worker)\np.start()\np.join()'},
            {"type": "text", "order": 3, "content": "Context switch: save state, load another. Preemptive vs cooperative scheduling. Deadlock: circular wait. Virtual memory uses pages. Page fault: data not in RAM, loaded from disk."},
        ],
        [
            {
                "type": ExerciseTypeEnum.fill_blank,
                "order": 1,
                "xp_reward": 10,
                "starter_code": '# Fill in the blanks about OS concepts\n# A ____ is a running program with its own memory space\n# A ____ is a lightweight unit within a process\n# The OS ____ decides which process runs next\n# ____ memory gives each process the illusion of full memory',
                "solution_code": 'A process is a running program with its own memory space\nA thread is a lightweight unit within a process\nThe OS scheduler decides which process runs next\nVirtual memory gives each process the illusion of full memory',
                "validation_config": '{"blanks": [{"answer": "process"}, {"answer": "thread"}, {"answer": "scheduler"}, {"answer": "Virtual"}]}',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Fill in the OS concepts: process, thread, scheduler, virtual.", "hint": "Process=running program, Thread=lightweight unit, Scheduler=decides, Virtual=memory illusion", "explanation": "Process has own memory. Thread shares process memory. Scheduler picks next process. Virtual memory abstracts physical RAM."},
                    {"language": LanguageEnum.fr, "prompt": "Remplissez les concepts OS : processus, thread, ordonnanceur, virtuel.", "hint": "Processus=prog en cours, Thread=unité légère, Ordonnanceur=décide, Virtuel=illusion mémoire", "explanation": "Processus a sa mémoire. Thread partage mémoire processus. Ordonnanceur choisit prochain processus. Mémoire virtuelle abstrait RAM physique."},
                    {"language": LanguageEnum.ar, "prompt": "املأ مفاهيم نظام التشغيل: عملية، خيط، مجدول، افتراضي.", "hint": "عملية=برنامج يعمل، خيط=وحدة خفيفة، مجدول=يقرر، افتراضي=وهم ذاكرة", "explanation": "العملية لها ذاكرة خاصة. الخيط يشارك ذاكرة العملية. المجدول يختار العملية التالية. الذاكرة الافتراضية تجرد RAM الفيزيائية."},
                ]
            }
        ]
    )
    
    # Lesson 46: Networks and the Internet
    await get_or_create_lesson(db, module3_id, "networks-internet", 4,
        DifficultyEnum.intermediate, 40, 60,
        [
            {"language": LanguageEnum.en, "title": "Networks and the Internet", "story": "How computers communicate across the globe", "objective": "Explain IP, DNS, HTTP, TCP/UDP, and the layered network model", "skills": "IP addresses, DNS, HTTP, TCP/UDP, OSI model, ports"},
            {"language": LanguageEnum.fr, "title": "Réseaux et Internet", "story": "Comment les ordinateurs communiquent à travers le monde", "objective": "Expliquer IP, DNS, HTTP, TCP/UDP, et le modèle réseau en couches", "skills": "Adresses IP, DNS, HTTP, TCP/UDP, modèle OSI, ports"},
            {"language": LanguageEnum.ar, "title": "الشبكات والإنترنت", "story": "كيف تتواصل أجهزة الكمبيوتر حول العالم", "objective": "شرح IP، DNS، HTTP، TCP/UDP، ونموذج الشبكة الطبقي", "skills": "عناوين IP، DNS، HTTP، TCP/UDP، نموذج OSI، المنافذ"},
        ],
        [
            {"type": "text", "order": 1, "content": "Networks connect computers. IP addresses identify devices (IPv4: 32-bit, IPv6: 128-bit). DNS translates names to IPs. TCP: reliable, ordered. UDP: fast, no guarantees. HTTP/HTTPS on port 80/443. OSI model: Physical, Data Link, Network, Transport, Session, Presentation, Application."},
            {"type": "code", "order": 2, "content": "Network basics:", "code_example": '# Python socket (educational only - not for production)\nimport socket\n\n# TCP server\nserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\nserver.bind(("localhost", 8080))\nserver.listen()\nconn, addr = server.accept()\ndata = conn.recv(1024)\nconn.send(b"Hello from server!")\nconn.close()'},
            {"type": "text", "order": 3, "content": "Ports identify services (80=HTTP, 443=HTTPS, 22=SSH, 53=DNS). Public vs private IPs. NAT translates private to public. Firewalls filter traffic. HTTPS encrypts with TLS."},
            # Micro-Quest blocks (hook 0, blueprint 4, exam_tip 5). The blueprint
            # is the spot_the_bug interaction. Lessons without these render as before.
            *seed_blocks("networks-internet"),
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
                    {"language": LanguageEnum.en, "prompt": "Which protocol provides reliable, ordered delivery?", "hint": "TCP vs UDP", "explanation": "TCP guarantees delivery and order. UDP is faster but doesn't guarantee either."},
                    {"language": LanguageEnum.fr, "prompt": "Quel protocole fournit une livraison fiable et ordonnée ?", "hint": "TCP vs UDP", "explanation": "TCP garantit la livraison et l'ordre. UDP est plus rapide mais ne garantit ni l'un ni l'autre."},
                    {"language": LanguageEnum.ar, "prompt": "أي بروتوكول يوفر تسليماً موثوقاً ومرتباً؟", "hint": "TCP مقابل UDP", "explanation": "TCP يضمن التسليم والترتيب. UDP أسرع لكن لا يضمن أياً منهما."},
                ],
                "options": [
                    {"order": 1, "is_correct": True, "translations": [{"language": LanguageEnum.en, "text": "TCP"}, {"language": LanguageEnum.fr, "text": "TCP"}, {"language": LanguageEnum.ar, "text": "TCP"}]},
                    {"order": 2, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "UDP"}, {"language": LanguageEnum.fr, "text": "UDP"}, {"language": LanguageEnum.ar, "text": "UDP"}]},
                    {"order": 3, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "IP"}, {"language": LanguageEnum.fr, "text": "IP"}, {"language": LanguageEnum.ar, "text": "IP"}]},
                    {"order": 4, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "HTTP"}, {"language": LanguageEnum.fr, "text": "HTTP"}, {"language": LanguageEnum.ar, "text": "HTTP"}]},
                ]
            }
        ]
    )
    
    print("CS Fundamentals seeded successfully!")