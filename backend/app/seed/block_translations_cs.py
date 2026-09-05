# -*- coding: utf-8 -*-
"""FR/AR lesson-block translations for CS Fundamentals (course 5).

Same contract as the other block_translations modules: keyed by
lesson_block.id, ``en`` repeats the source so the backfill can verify before
writing, and code examples are copied verbatim from the base block.

Established computer-science terms keep their standard rendering: complexity
classes and Big-O notation stay in mathematical form, and Python/OS identifiers
(``super()``, ``__init__``, TCP, UDP, DNS) are never translated.
"""

CS_FUNDAMENTALS_BLOCKS = {
    106: {
        "en": "An algorithm is a finite sequence of precise instructions to solve a problem or perform a computation. Like a recipe: clear steps, defined inputs, guaranteed outputs, terminates eventually.",
        "fr": "Un algorithme est une suite finie d'instructions précises permettant de résoudre un problème ou d'effectuer un calcul. Comme une recette : des étapes claires, des entrées définies, des sorties garanties, et une fin assurée.",
        "ar": "الخوارزمية سلسلة منتهية من التعليمات الدقيقة لحلّ مسألة أو إجراء عملية حسابية. وهي أشبه بوصفة طهي: خطوات واضحة، ومُدخلات محدّدة، ومُخرجات مضمونة، ونهاية أكيدة.",
    },
    107: {
        "en": "Algorithm example - finding maximum:",
        "fr": "Exemple d'algorithme : trouver le maximum",
        "ar": "مثال على خوارزمية: إيجاد القيمة العظمى",
    },
    108: {
        "en": "Algorithms have: input, output, definiteness (clear steps), finiteness (terminates), effectiveness (doable). Same problem, different algorithms = different efficiency.",
        "fr": "Un algorithme possède : une entrée, une sortie, la définitude (des étapes non ambiguës), la finitude (il se termine) et l'effectivité (il est réalisable). Un même problème résolu par des algorithmes différents donne des efficacités différentes.",
        "ar": "تتّصف الخوارزمية بأن لها مُدخلات ومُخرجات، وبالتحديد أي وضوح خطواتها، وبالانتهاء أي أنها تتوقّف، وبالقابلية للتنفيذ. والمسألة الواحدة قد تُحلّ بخوارزميات مختلفة تتفاوت كفاءتها.",
    },
    109: {
        "en": "Big-O describes how runtime/memory grows with input size n. O(1) constant, O(log n) logarithmic, O(n) linear, O(n log n) linearithmic, O(n²) quadratic, O(2ⁿ) exponential. Drop constants and lower terms.",
        "fr": "La notation Big-O décrit la croissance du temps d'exécution ou de la mémoire en fonction de la taille n de l'entrée : O(1) constant, O(log n) logarithmique, O(n) linéaire, O(n log n) quasi-linéaire, O(n²) quadratique, O(2ⁿ) exponentiel. On ignore les constantes et les termes de moindre ordre.",
        "ar": "يصف ترميز Big-O كيف ينمو زمن التنفيذ أو استهلاك الذاكرة مع حجم المُدخل n: فـ O(1) ثابت، وO(log n) لوغاريتمي، وO(n) خطّي، وO(n log n) شبه خطّي، وO(n²) تربيعي، وO(2ⁿ) أسّي. وتُهمَل الثوابت والحدود الأدنى رتبةً.",
    },
    110: {
        "en": "Complexity examples:",
        "fr": "Exemples de complexité :",
        "ar": "أمثلة على التعقيد الحسابي:",
    },
    111: {
        "en": "Best/average/worst case: linear search O(n) worst, O(1) best. Binary search O(log n) worst. Space complexity counts extra memory. Prefer lower complexity for large inputs.",
        "fr": "Cas meilleur, moyen et pire : la recherche linéaire est en O(n) au pire et O(1) au mieux ; la recherche dichotomique en O(log n) au pire. La complexité en espace mesure la mémoire supplémentaire utilisée. Préférez une complexité plus faible pour les grandes entrées.",
        "ar": "الحالات الثلاث هي الأفضل والمتوسّطة والأسوأ: فالبحث الخطّي O(n) في أسوأ الحالات وO(1) في أفضلها، والبحث الثنائي O(log n) في أسوأ الحالات. أما تعقيد المساحة فيقيس الذاكرة الإضافية المستهلكة. وفضّل التعقيد الأدنى كلما كبر حجم المُدخلات.",
    },
    112: {
        "en": "Linear search: check each element O(n). Binary search: repeatedly divide sorted array in half O(log n). Binary search requires sorted data! Use when searching repeatedly in static data.",
        "fr": "Recherche linéaire : on examine chaque élément, en O(n). Recherche dichotomique : on divise en deux un tableau trié, en O(log n). La recherche dichotomique exige des données triées ! Utilisez-la lorsque vous cherchez souvent dans des données stables.",
        "ar": "البحث الخطّي يفحص كل عنصر بتعقيد O(n)، أما البحث الثنائي فيقسم المصفوفة المرتّبة إلى نصفين مرارًا بتعقيد O(log n). ويشترط البحث الثنائي أن تكون البيانات مرتّبة! واستخدمه عند تكرار البحث في بيانات ثابتة.",
    },
    113: {
        "en": "Search algorithms:",
        "fr": "Algorithmes de recherche :",
        "ar": "خوارزميات البحث:",
    },
    114: {
        "en": "Binary search halves the search space each iteration. 1,000,000 items -> max 20 steps! Sorting first O(n log n) pays off if searching many times.",
        "fr": "La recherche dichotomique divise l'espace de recherche par deux à chaque itération : 1 000 000 d'éléments, 20 étapes au maximum ! Trier d'abord en O(n log n) devient rentable si l'on effectue de nombreuses recherches.",
        "ar": "يقلّص البحث الثنائي مجال البحث إلى النصف في كل تكرار، فمليون عنصر لا تحتاج إلا إلى 20 خطوة على الأكثر! ويصبح الترتيب المسبق بتعقيد O(n log n) مُجديًا إذا تكرّر البحث كثيرًا.",
    },
    115: {
        "en": "Bubble sort O(n²): repeatedly swap adjacent if wrong order. Simple but slow. Merge sort O(n log n): divide, sort halves, merge. Stable, not in-place. Quicksort O(n log n) average, O(n²) worst. Python's sort() uses Timsort (hybrid).",
        "fr": "Tri à bulles en O(n²) : on échange les éléments adjacents mal ordonnés, encore et encore. Simple mais lent. Tri fusion en O(n log n) : diviser, trier les moitiés, fusionner ; stable mais non en place. Tri rapide en O(n log n) en moyenne, O(n²) au pire. La méthode sort() de Python utilise Timsort, un algorithme hybride.",
        "ar": "الترتيب الفقاعي بتعقيد O(n²) يبدّل العناصر المتجاورة غير المرتّبة مرارًا، وهو بسيط لكنه بطيء. وترتيب الدمج بتعقيد O(n log n) يقسم ثم يرتّب النصفين ثم يدمجهما، وهو مستقرّ لكنه يحتاج ذاكرة إضافية. أما الترتيب السريع فتعقيده O(n log n) في المتوسط وO(n²) في أسوأ الحالات. وتستخدم الدالة ()sort في Python خوارزمية Timsort الهجينة.",
    },
    116: {
        "en": "Sorting algorithms:",
        "fr": "Algorithmes de tri :",
        "ar": "خوارزميات الترتيب:",
    },
    117: {
        "en": "Stable sort keeps equal elements in original order. In-place uses O(1) extra space. For small/nearly sorted data, insertion sort can beat others. Use built-in sorted() in practice.",
        "fr": "Un tri stable conserve l'ordre initial des éléments égaux. Un tri en place n'utilise que O(1) de mémoire supplémentaire. Sur de petites données ou des données presque triées, le tri par insertion peut surpasser les autres. En pratique, utilisez la fonction native sorted().",
        "ar": "الترتيب المستقرّ يحافظ على الترتيب الأصلي للعناصر المتساوية، والترتيب في المكان لا يستهلك سوى O(1) من الذاكرة الإضافية. وفي البيانات الصغيرة أو شبه المرتّبة قد يتفوّق ترتيب الإدراج على غيره. أما عمليًا فاستخدم الدالة الجاهزة ()sorted.",
    },
    118: {
        "en": "A class is a blueprint. An object is an instance. __init__ initializes attributes. self refers to the current instance. Methods are functions inside a class that operate on the object's data.",
        "fr": "Une classe est un plan, un objet en est une instance. __init__ initialise les attributs et self désigne l'instance courante. Les méthodes sont les fonctions d'une classe qui manipulent les données de l'objet.",
        "ar": "الصنف مخطّط، والكائن نسخة منه. وتُهيّئ __init__ الخصائص، ويشير self إلى الكائن الحالي. أما التوابع فهي دوال داخل الصنف تعمل على بيانات الكائن.",
    },
    119: {
        "en": "Class and object:",
        "fr": "Classe et objet :",
        "ar": "الصنف والكائن:",
    },
    120: {
        "en": "Each object has its own attribute values. Methods access attributes via self. Classes enable modeling real-world entities with both state (attributes) and behavior (methods).",
        "fr": "Chaque objet possède ses propres valeurs d'attributs, auxquelles les méthodes accèdent via self. Les classes permettent de modéliser des entités du monde réel avec à la fois un état (les attributs) et un comportement (les méthodes).",
        "ar": "لكل كائن قيم خصائصه الخاصة، وتصل التوابع إلى هذه الخصائص عبر self. وتتيح الأصناف نمذجة كيانات من العالم الحقيقي بحالتها المتمثّلة في الخصائص وسلوكها المتمثّل في التوابع.",
    },
    121: {
        "en": "Instance attributes (self.x) belong to each object. Class attributes (shared) belong to the class. @classmethod gets class as first arg (cls). @staticmethod gets no implicit first arg. @property makes method act like attribute.",
        "fr": "Les attributs d'instance (self.x) appartiennent à chaque objet ; les attributs de classe sont partagés et appartiennent à la classe. @classmethod reçoit la classe en premier argument (cls), @staticmethod ne reçoit aucun argument implicite, et @property fait qu'une méthode se comporte comme un attribut.",
        "ar": "خصائص النسخة مثل self.x تعود إلى كل كائن على حدة، أما خصائص الصنف فمشتركة وتعود إلى الصنف نفسه. ويتلقّى classmethod@ الصنف كوسيط أول باسم cls، ولا يتلقّى staticmethod@ أي وسيط ضمني، بينما يجعل property@ التابع يتصرّف وكأنه خاصية.",
    },
    122: {
        "en": "Attribute types:",
        "fr": "Types d'attributs :",
        "ar": "أنواع الخصائص:",
    },
    123: {
        "en": "Use class attributes for shared data. @classmethod for factory methods. @staticmethod for utility functions. @property for computed attributes with validation.",
        "fr": "Utilisez les attributs de classe pour les données partagées, @classmethod pour les méthodes de fabrique, @staticmethod pour les fonctions utilitaires et @property pour les attributs calculés avec validation.",
        "ar": "استخدم خصائص الصنف للبيانات المشتركة، وclassmethod@ لتوابع الإنشاء، وstaticmethod@ للدوال المساعدة، وproperty@ للخصائص المحسوبة مع التحقّق من القيم.",
    },
    124: {
        "en": "Encapsulation hides internal details. Python uses _single (convention) and __double (name mangling) for private. Abstraction exposes only what's needed. Properties control access with validation.",
        "fr": "L'encapsulation masque les détails internes. En Python, _simple relève de la convention et __double déclenche le name mangling pour signaler le privé. L'abstraction n'expose que le nécessaire, et les properties contrôlent l'accès en validant les valeurs.",
        "ar": "يُخفي التغليف التفاصيل الداخلية. وفي Python تدلّ الشرطة السفلية المفردة على اصطلاح الخصوصية، بينما تُفعّل الشرطتان السفليتان آلية تشويه الأسماء. أما التجريد فلا يكشف إلا ما يلزم، وتتحكّم الخصائص (properties) في الوصول مع التحقّق من القيم.",
    },
    125: {
        "en": "Encapsulation:",
        "fr": "Encapsulation :",
        "ar": "التغليف:",
    },
    126: {
        "en": "__balance becomes _BankAccount__balance (name mangling). Not truly private but signals intent. Properties enable validation on read/write. Abstraction: user calls deposit(), doesn't know how balance stored.",
        "fr": "__balance devient _BankAccount__balance (name mangling) : ce n'est pas vraiment privé, mais l'intention est claire. Les properties permettent de valider en lecture comme en écriture. Abstraction : l'utilisateur appelle deposit() sans savoir comment le solde est stocké.",
        "ar": "يتحوّل الاسم __balance إلى _BankAccount__balance بفعل تشويه الأسماء، وهو ليس خاصًا حقًا لكنه يوضّح النية. وتتيح الخصائص التحقّق عند القراءة والكتابة. وبفضل التجريد يستدعي المستخدم ()deposit دون أن يعرف كيف يُخزَّن الرصيد.",
    },
    127: {
        "en": "Inheritance: class Child(Parent) gets parent's attributes/methods. Override methods to change behavior. super() calls parent method. Polymorphism: different objects respond to same method call differently. Liskov: subclass usable wherever parent expected.",
        "fr": "Héritage : class Child(Parent) hérite des attributs et méthodes du parent. On redéfinit une méthode pour en changer le comportement, et super() appelle celle du parent. Polymorphisme : des objets différents répondent différemment au même appel de méthode. Principe de Liskov : une sous-classe doit pouvoir remplacer sa classe parente partout.",
        "ar": "الوراثة تعني أن class Child(Parent) يرث خصائص الأب وتوابعه. ويمكن إعادة تعريف التابع لتغيير سلوكه، بينما تستدعي ()super تابع الأب. أما تعدّد الأشكال فيعني أن كائنات مختلفة تستجيب لاستدعاء التابع نفسه بطرق مختلفة. ووفق مبدأ ليسكوف يجب أن يصلح الصنف الفرعي في كل موضع يُتوقَّع فيه الصنف الأب.",
    },
    128: {
        "en": "Inheritance and polymorphism:",
        "fr": "Héritage et polymorphisme :",
        "ar": "الوراثة وتعدّد الأشكال:",
    },
    129: {
        "en": "super().__init__() initializes parent. Abstract base classes (abc) define required methods. Mixins add functionality. Composition often better than deep inheritance hierarchies.",
        "fr": "super().__init__() initialise la classe parente. Les classes de base abstraites (module abc) imposent les méthodes à implémenter. Les mixins ajoutent des fonctionnalités. La composition vaut souvent mieux que des hiérarchies d'héritage profondes.",
        "ar": "يُهيّئ ()super().__init__ الصنف الأب. وتُحدّد الأصناف الأساسية المجرّدة عبر وحدة abc التوابع الواجب تنفيذها، بينما تضيف الـ mixins وظائف إضافية. والتركيب غالبًا أفضل من تسلسلات الوراثة العميقة.",
    },
    130: {
        "en": "Computers use binary (0 and 1). Bit = binary digit. Byte = 8 bits. Integers use two's complement for negatives. Text uses ASCII (128 chars) or Unicode (millions). Floats use IEEE 754.",
        "fr": "Les ordinateurs travaillent en binaire (0 et 1). Un bit est un chiffre binaire, un octet vaut 8 bits. Les entiers négatifs sont codés en complément à deux. Le texte utilise ASCII (128 caractères) ou Unicode (des millions). Les nombres à virgule flottante suivent la norme IEEE 754.",
        "ar": "تعمل الحواسيب بالنظام الثنائي المكوّن من 0 و1. والبِت هو الرقم الثنائي، والبايت يساوي 8 بِتات. وتُرمَّز الأعداد الصحيحة السالبة بالمتمّم الثنائي، ويُرمَّز النص بترميز ASCII الذي يضمّ 128 محرفًا أو بترميز Unicode الذي يضمّ الملايين. أما الأعداد العشرية فتتّبع معيار IEEE 754.",
    },
    131: {
        "en": "Data representation in Python:",
        "fr": "Représentation des données en Python :",
        "ar": "تمثيل البيانات في Python:",
    },
    132: {
        "en": "Two's complement: invert bits, add 1. Unicode uses variable-width (UTF-8). Floats are approximate - avoid == for equality. Use decimal module for exact money.",
        "fr": "Complément à deux : inverser les bits, puis ajouter 1. Unicode utilise un codage à largeur variable (UTF-8). Les flottants sont approximatifs : évitez == pour tester l'égalité. Utilisez le module decimal pour les montants monétaires exacts.",
        "ar": "يُحسب المتمّم الثنائي بعكس البِتات ثم إضافة 1. ويستخدم Unicode ترميزًا متغيّر العرض مثل UTF-8. والأعداد العشرية تقريبية، لذا تجنّب استخدام == لاختبار التساوي، واستعمل وحدة decimal للتعامل الدقيق مع المبالغ المالية.",
    },
    133: {
        "en": "Memory hierarchy: Registers (fastest, tiny) -> L1/L2/L3 Cache (fast, small) -> RAM (fast, volatile) -> SSD/HDD (slow, persistent). Volatile loses data on power off. Cache bridges CPU-RAM speed gap.",
        "fr": "Hiérarchie mémoire : registres (les plus rapides, minuscules) -> caches L1/L2/L3 (rapides, petits) -> RAM (rapide, volatile) -> SSD/HDD (lents, persistants). Une mémoire volatile perd ses données à l'extinction. Le cache comble l'écart de vitesse entre le processeur et la RAM.",
        "ar": "التسلسل الهرمي للذاكرة: المسجّلات وهي الأسرع والأصغر، ثم الذاكرة المخبّأة L1 وL2 وL3 وهي سريعة وصغيرة، ثم ذاكرة الوصول العشوائي RAM وهي سريعة ومتطايرة، ثم أقراص SSD وHDD وهي بطيئة لكنها دائمة. والذاكرة المتطايرة تفقد بياناتها عند انقطاع الطاقة، بينما تسدّ الذاكرة المخبّأة فجوة السرعة بين المعالج وRAM.",
    },
    134: {
        "en": "Memory concepts:",
        "fr": "Notions de mémoire :",
        "ar": "مفاهيم الذاكرة:",
    },
    135: {
        "en": "Variables reference objects in memory. id() gives address. Python manages memory automatically (garbage collection). Memory leaks possible with circular references.",
        "fr": "Les variables référencent des objets en mémoire ; id() en donne l'adresse. Python gère la mémoire automatiquement grâce au ramasse-miettes. Des fuites mémoire restent possibles en cas de références circulaires.",
        "ar": "تشير المتغيّرات إلى كائنات في الذاكرة، وتُعطي ()id عنوان الكائن. وتدير Python الذاكرة تلقائيًا عبر جامع النفايات، غير أن تسرّب الذاكرة يبقى ممكنًا مع المراجع الدائرية.",
    },
    136: {
        "en": "OS manages hardware resources. Process = running program with own memory space. Thread = lightweight unit within process, shares memory. Scheduler decides which runs. System calls (syscalls) request OS services. Virtual memory gives each process illusion of full memory.",
        "fr": "Le système d'exploitation gère les ressources matérielles. Un processus est un programme en cours d'exécution avec son propre espace mémoire ; un thread est une unité légère à l'intérieur d'un processus, qui partage cette mémoire. L'ordonnanceur décide qui s'exécute. Les appels système demandent les services de l'OS. La mémoire virtuelle donne à chaque processus l'illusion de disposer de toute la mémoire.",
        "ar": "يدير نظام التشغيل موارد العتاد. والعملية برنامج قيد التنفيذ له مساحة ذاكرة خاصة به، أما الخيط فوحدة تنفيذ خفيفة داخل العملية تتشارك معها الذاكرة. ويقرّر المُجدوِل أيّها يعمل، بينما تطلب استدعاءات النظام خدمات نظام التشغيل. وتمنح الذاكرة الافتراضية كل عملية وهمَ امتلاك الذاكرة كاملة.",
    },
    137: {
        "en": "Process concepts:",
        "fr": "Notions de processus :",
        "ar": "مفاهيم العمليات:",
    },
    138: {
        "en": "Context switch: save state, load another. Preemptive vs cooperative scheduling. Deadlock: circular wait. Virtual memory uses pages. Page fault: data not in RAM, loaded from disk.",
        "fr": "Changement de contexte : sauvegarder un état, en charger un autre. Ordonnancement préemptif ou coopératif. Interblocage : attente circulaire. La mémoire virtuelle fonctionne par pages ; un défaut de page survient lorsque la donnée n'est pas en RAM et doit être chargée depuis le disque.",
        "ar": "تبديل السياق يعني حفظ حالة عملية وتحميل أخرى. والجدولة إمّا استباقية وإمّا تعاونية. ويقع الجمود عند الانتظار الدائري. وتعمل الذاكرة الافتراضية بالصفحات، ويحدث خطأ الصفحة عندما لا تكون البيانات في RAM فتُحمَّل من القرص.",
    },
    139: {
        "en": "Networks connect computers. IP addresses identify devices (IPv4: 32-bit, IPv6: 128-bit). DNS translates names to IPs. TCP: reliable, ordered. UDP: fast, no guarantees. HTTP/HTTPS on port 80/443. OSI model: Physical, Data Link, Network, Transport, Session, Presentation, Application.",
        "fr": "Les réseaux relient les ordinateurs. Les adresses IP identifient les appareils (IPv4 sur 32 bits, IPv6 sur 128 bits). Le DNS traduit les noms en adresses IP. TCP est fiable et ordonné ; UDP est rapide mais sans garantie. HTTP et HTTPS utilisent les ports 80 et 443. Modèle OSI : physique, liaison de données, réseau, transport, session, présentation, application.",
        "ar": "تربط الشبكات الحواسيب ببعضها. وتُعرِّف عناوين IP الأجهزة، فـ IPv4 بطول 32 بِتًا وIPv6 بطول 128 بِتًا. ويترجم DNS الأسماء إلى عناوين IP. وبروتوكول TCP موثوق ويحفظ الترتيب، أما UDP فسريع بلا ضمانات. ويعمل HTTP وHTTPS على المنفذين 80 و443. وطبقات نموذج OSI هي: المادية، وربط البيانات، والشبكة، والنقل، والجلسة، والعرض، والتطبيق.",
    },
    140: {
        "en": "Network basics:",
        "fr": "Bases des réseaux :",
        "ar": "أساسيات الشبكات:",
    },
    141: {
        "en": "Ports identify services (80=HTTP, 443=HTTPS, 22=SSH, 53=DNS). Public vs private IPs. NAT translates private to public. Firewalls filter traffic. HTTPS encrypts with TLS.",
        "fr": "Les ports identifient les services (80 = HTTP, 443 = HTTPS, 22 = SSH, 53 = DNS). On distingue les adresses IP publiques des privées ; le NAT traduit les privées en publiques. Les pare-feu filtrent le trafic et HTTPS le chiffre grâce à TLS.",
        "ar": "تُحدِّد المنافذ الخدمات، فالمنفذ 80 لـ HTTP و443 لـ HTTPS و22 لـ SSH و53 لـ DNS. وتنقسم عناوين IP إلى عامة وخاصة، ويترجم NAT العناوين الخاصة إلى عامة. وتُصفّي الجدران النارية حركة البيانات، بينما يُشفّرها HTTPS باستخدام TLS.",
    },
}
