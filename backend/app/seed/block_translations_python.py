# -*- coding: utf-8 -*-
"""French and Arabic lesson-block translations for Python Foundations (course 1).

Keyed by lesson_block.id. ``en`` repeats the English source verbatim so the
backfill can verify it is writing against the block it was authored for; a block
whose English text has changed is skipped rather than mistranslated.

Code examples are intentionally absent here: they are copied verbatim from the
base block by the backfill, matching how courses 6-15 store them (identical code
in all three languages, identifiers and comments untouched).
"""

PYTHON_FOUNDATIONS_BLOCKS = {
    1: {
        "en": "Programming is giving instructions to a computer to perform tasks. Python is a popular programming language because it reads like English.",
        "fr": "Programmer, c'est donner à un ordinateur des instructions pour accomplir des tâches. Python est un langage très répandu parce qu'il se lit presque comme de l'anglais.",
        "ar": "البرمجة هي إعطاء الحاسوب تعليمات لتنفيذ مهام معينة. وتُعدّ لغة Python من أكثر اللغات انتشارًا لأنها تُقرأ وكأنها لغة إنجليزية.",
    },
    2: {
        "en": "Your first Python program:",
        "fr": "Votre premier programme Python :",
        "ar": "أول برنامج لك بلغة Python:",
    },
    3: {
        "en": "The print() function displays text on the screen. Each print() starts on a new line.",
        "fr": "La fonction print() affiche du texte à l'écran. Chaque print() commence sur une nouvelle ligne.",
        "ar": "تعرض الدالة ()print نصًا على الشاشة، وكل استدعاء لـ ()print يبدأ في سطر جديد.",
    },
    4: {
        "en": "Variables are named containers that store values. Think of them like labeled boxes where you can put data.",
        "fr": "Les variables sont des conteneurs nommés qui stockent des valeurs. Imaginez des boîtes étiquetées dans lesquelles vous rangez vos données.",
        "ar": "المتغيّرات هي حاويات لها أسماء تُخزّن القيم. تخيّلها صناديق مُعنونة تضع فيها بياناتك.",
    },
    5: {
        "en": "Creating variables in Python:",
        "fr": "Créer des variables en Python :",
        "ar": "إنشاء المتغيّرات في Python:",
    },
    6: {
        "en": "Variable names can contain letters, numbers, and underscores, but cannot start with a number.",
        "fr": "Un nom de variable peut contenir des lettres, des chiffres et des tirets bas, mais ne peut pas commencer par un chiffre.",
        "ar": "يمكن أن يتضمّن اسم المتغيّر حروفًا وأرقامًا وشرطات سفلية، لكنه لا يمكن أن يبدأ برقم.",
    },
    7: {
        "en": "Every value in Python has a type. The main types are: int (whole numbers), float (decimals), str (text), and bool (True/False).",
        "fr": "Chaque valeur en Python possède un type. Les principaux sont : int (nombres entiers), float (nombres décimaux), str (texte) et bool (True/False).",
        "ar": "لكل قيمة في Python نوع. والأنواع الأساسية هي: int للأعداد الصحيحة، وfloat للأعداد العشرية، وstr للنصوص، وbool للقيم True/False.",
    },
    8: {
        "en": "Checking types:",
        "fr": "Vérifier les types :",
        "ar": "التحقّق من الأنواع:",
    },
    9: {
        "en": "Use type() to check what type a value is. Python automatically chooses the type based on the value.",
        "fr": "Utilisez type() pour connaître le type d'une valeur. Python choisit automatiquement le type en fonction de la valeur.",
        "ar": "استخدم ()type لمعرفة نوع أي قيمة. وتختار Python النوع تلقائيًا بحسب القيمة نفسها.",
    },
    10: {
        "en": "Python supports arithmetic operators (+, -, *, /, //, %, **), comparison operators (==, !=, <, >, <=, >=), and logical operators (and, or, not).",
        "fr": "Python propose des opérateurs arithmétiques (+, -, *, /, //, %, **), de comparaison (==, !=, <, >, <=, >=) et logiques (and, or, not).",
        "ar": "تدعم Python المعاملات الحسابية (+, -, *, /, //, %, **)، ومعاملات المقارنة (==, !=, <, >, <=, >=)، والمعاملات المنطقية (and, or, not).",
    },
    11: {
        "en": "Arithmetic operations:",
        "fr": "Opérations arithmétiques :",
        "ar": "العمليات الحسابية:",
    },
    12: {
        "en": "Operator precedence: ** first, then *, /, //, %, then +, -. Use parentheses to control order.",
        "fr": "Priorité des opérateurs : ** d'abord, puis *, /, //, %, puis + et -. Utilisez des parenthèses pour imposer l'ordre voulu.",
        "ar": "أولوية المعاملات: ** أولًا، ثم *, /, //, %، ثم + و-. واستخدم الأقواس لفرض الترتيب الذي تريده.",
    },
    13: {
        "en": "Programs often need to get information from users. Use input() to ask for information and print() to show results. input() always returns a string, so you may need to convert it.",
        "fr": "Un programme a souvent besoin d'informations venant de l'utilisateur. Utilisez input() pour les demander et print() pour afficher les résultats. input() renvoie toujours une chaîne de caractères : pensez à la convertir si nécessaire.",
        "ar": "كثيرًا ما يحتاج البرنامج إلى معلومات من المستخدم. استخدم ()input لطلبها و()print لعرض النتائج. تُرجع ()input نصًا دائمًا، لذا قد تحتاج إلى تحويله.",
    },
    14: {
        "en": "Getting user input:",
        "fr": "Récupérer une saisie utilisateur :",
        "ar": "قراءة مُدخلات المستخدم:",
    },
    15: {
        "en": "input() always returns a string. Use int() to convert to integer, float() for decimals. f-strings let you embed variables in strings with {variable}.",
        "fr": "input() renvoie toujours une chaîne. Utilisez int() pour convertir en entier et float() pour les décimaux. Les f-strings permettent d'insérer des variables dans un texte avec {variable}.",
        "ar": "تُرجع ()input نصًا دائمًا. استخدم ()int للتحويل إلى عدد صحيح و()float للأعداد العشرية. وتتيح لك f-strings إدراج المتغيّرات داخل النص بالصيغة {variable}.",
    },
    16: {
        "en": "Conditions let your program choose different paths. Use if for a condition, elif for additional conditions, and else for everything else.",
        "fr": "Les conditions permettent à votre programme de suivre des chemins différents. Utilisez if pour une condition, elif pour les conditions supplémentaires et else pour tous les autres cas.",
        "ar": "تتيح الشروط لبرنامجك أن يسلك مسارات مختلفة. استخدم if لشرط أول، وelif لشروط إضافية، وelse لكل ما تبقّى.",
    },
    17: {
        "en": "Basic if-elif-else:",
        "fr": "if-elif-else de base :",
        "ar": "الشكل الأساسي لـ if-elif-else:",
    },
    18: {
        "en": "Only one branch executes. Conditions are checked in order from top to bottom.",
        "fr": "Une seule branche s'exécute. Les conditions sont évaluées dans l'ordre, de haut en bas.",
        "ar": "يُنفَّذ فرع واحد فقط، وتُفحص الشروط بالترتيب من الأعلى إلى الأسفل.",
    },
    19: {
        "en": "Loops repeat code multiple times. for loops iterate over a sequence, while loops repeat while a condition is true.",
        "fr": "Les boucles répètent du code plusieurs fois. La boucle for parcourt une séquence, la boucle while répète tant qu'une condition reste vraie.",
        "ar": "تكرّر الحلقات تنفيذ الشيفرة عدة مرات. تمرّ حلقة for على عناصر متتالية، بينما تكرّر حلقة while ما دام الشرط صحيحًا.",
    },
    20: {
        "en": "For loop with range:",
        "fr": "Boucle for avec range :",
        "ar": "حلقة for مع range:",
    },
    21: {
        "en": "range(n) creates numbers 0 to n-1. range(start, stop) creates numbers from start to stop-1. Always update your counter in while loops!",
        "fr": "range(n) produit les nombres de 0 à n-1. range(start, stop) produit les nombres de start à stop-1. Pensez toujours à mettre à jour votre compteur dans une boucle while !",
        "ar": "تُنتج (range(n الأعداد من 0 إلى n-1، وتُنتج (range(start, stop الأعداد من start إلى stop-1. واحرص دائمًا على تحديث العدّاد داخل حلقة while!",
    },
    22: {
        "en": "break exits a loop immediately. continue skips to the next iteration. Nested loops are loops inside other loops.",
        "fr": "break quitte immédiatement la boucle. continue passe directement à l'itération suivante. Les boucles imbriquées sont des boucles à l'intérieur d'autres boucles.",
        "ar": "تُنهي break الحلقة فورًا، بينما تنتقل continue إلى التكرار التالي. أما الحلقات المتداخلة فهي حلقات داخل حلقات أخرى.",
    },
    23: {
        "en": "Loop control examples:",
        "fr": "Exemples de contrôle de boucle :",
        "ar": "أمثلة على التحكّم في الحلقات:",
    },
    24: {
        "en": "Use break to exit early when you find what you're looking for. Use continue to skip unwanted iterations.",
        "fr": "Utilisez break pour sortir dès que vous avez trouvé ce que vous cherchiez, et continue pour ignorer les itérations qui ne vous intéressent pas.",
        "ar": "استخدم break للخروج مبكرًا بمجرد أن تجد ما تبحث عنه، واستخدم continue لتخطّي التكرارات غير المرغوبة.",
    },
    25: {
        "en": "Real programming problems often need both decisions and repetition. Break the problem into steps, then code each step.",
        "fr": "Les vrais problèmes de programmation demandent souvent à la fois des décisions et des répétitions. Décomposez le problème en étapes, puis codez chaque étape.",
        "ar": "تحتاج المسائل البرمجية الحقيقية غالبًا إلى اتخاذ قرارات وتكرار معًا. جزّئ المسألة إلى خطوات، ثم اكتب شيفرة كل خطوة.",
    },
    26: {
        "en": "Finding the largest number:",
        "fr": "Trouver le plus grand nombre :",
        "ar": "إيجاد أكبر عدد:",
    },
    27: {
        "en": "This pattern (initialize, loop, compare, update) works for finding max, min, sum, average, and more.",
        "fr": "Ce schéma (initialiser, parcourir, comparer, mettre à jour) fonctionne pour trouver un maximum, un minimum, une somme, une moyenne, et bien d'autres.",
        "ar": "هذا النمط (التهيئة، ثم المرور، ثم المقارنة، ثم التحديث) صالح لإيجاد القيمة العظمى والصغرى والمجموع والمتوسط وغيرها.",
    },
    28: {
        "en": "Functions let you group code that does one thing, give it a name, and reuse it. They can take inputs (parameters) and give back outputs (return values).",
        "fr": "Les fonctions permettent de regrouper du code qui fait une seule chose, de lui donner un nom et de le réutiliser. Elles acceptent des entrées (paramètres) et renvoient des sorties (valeurs de retour).",
        "ar": "تتيح لك الدوال تجميع شيفرة تؤدي مهمة واحدة، وتسميتها، وإعادة استخدامها. وهي تقبل مُدخلات (وسائط) وتُعيد مُخرجات (قيم إرجاع).",
    },
    29: {
        "en": "Defining and calling functions:",
        "fr": "Définir et appeler des fonctions :",
        "ar": "تعريف الدوال واستدعاؤها:",
    },
    30: {
        "en": "def defines a function. The code inside only runs when you call the function. return sends a value back to the caller.",
        "fr": "def définit une fonction. Le code qu'elle contient ne s'exécute qu'au moment de l'appel. return renvoie une valeur à l'appelant.",
        "ar": "تُعرِّف def دالةً، ولا تُنفَّذ الشيفرة بداخلها إلا عند استدعائها. أما return فتُعيد قيمة إلى الجهة التي استدعت الدالة.",
    },
    31: {
        "en": "Functions can take multiple parameters. You can also give parameters default values so they're optional when calling.",
        "fr": "Une fonction peut accepter plusieurs paramètres. Vous pouvez aussi leur donner des valeurs par défaut : ils deviennent alors facultatifs à l'appel.",
        "ar": "يمكن للدالة أن تقبل عدة وسائط. ويمكنك كذلك منح الوسائط قيمًا افتراضية لتصبح اختيارية عند الاستدعاء.",
    },
    32: {
        "en": "Multiple parameters and defaults:",
        "fr": "Paramètres multiples et valeurs par défaut :",
        "ar": "وسائط متعددة وقيم افتراضية:",
    },
    33: {
        "en": "Default parameters must come after required parameters. Keyword arguments let you specify parameters by name in any order.",
        "fr": "Les paramètres par défaut doivent venir après les paramètres obligatoires. Les arguments nommés permettent de désigner les paramètres par leur nom, dans n'importe quel ordre.",
        "ar": "يجب أن تأتي الوسائط ذات القيم الافتراضية بعد الوسائط الإلزامية. وتتيح لك الوسائط المُسمّاة تحديد الوسائط بأسمائها وبأي ترتيب.",
    },
    34: {
        "en": "Variables created inside a function are local - they only exist inside that function. Variables outside are global. Prefer local variables and pass data through parameters.",
        "fr": "Les variables créées dans une fonction sont locales : elles n'existent qu'à l'intérieur de cette fonction. Celles définies à l'extérieur sont globales. Privilégiez les variables locales et faites circuler les données par les paramètres.",
        "ar": "المتغيّرات المُنشأة داخل دالة تكون محلّية، أي لا وجود لها خارجها، أما المُعرَّفة خارجها فهي عامة. فضّل المتغيّرات المحلّية ومرّر البيانات عبر الوسائط.",
    },
    35: {
        "en": "Scope example:",
        "fr": "Exemple de portée :",
        "ar": "مثال على نطاق المتغيّرات:",
    },
    36: {
        "en": "Good functions do one thing well, have clear names, and don't rely on global variables. This makes them easier to test and reuse.",
        "fr": "Une bonne fonction fait une seule chose et la fait bien, porte un nom explicite et ne dépend pas de variables globales. Elle en devient plus facile à tester et à réutiliser.",
        "ar": "الدالة الجيدة تؤدي مهمة واحدة على أكمل وجه، ويكون اسمها واضحًا، ولا تعتمد على متغيّرات عامة. وهذا يجعل اختبارها وإعادة استخدامها أسهل.",
    },
    37: {
        "en": "Complex problems become manageable when broken into smaller functions. Each function should do one thing well.",
        "fr": "Les problèmes complexes deviennent gérables lorsqu'on les découpe en petites fonctions. Chaque fonction doit faire une seule chose, et bien.",
        "ar": "تصبح المسائل المعقّدة قابلة للمعالجة حين تُجزّأ إلى دوال أصغر، على أن تؤدي كل دالة مهمة واحدة على أكمل وجه.",
    },
    38: {
        "en": "Decomposing a grade calculator:",
        "fr": "Décomposer un calculateur de notes :",
        "ar": "تجزئة برنامج لحساب الدرجات:",
    },
    39: {
        "en": "Each function has a single responsibility. This makes code easier to read, test, and modify.",
        "fr": "Chaque fonction a une seule responsabilité, ce qui rend le code plus facile à lire, à tester et à modifier.",
        "ar": "لكل دالة مسؤولية واحدة فقط، وهو ما يجعل الشيفرة أسهل في القراءة والاختبار والتعديل.",
    },
    40: {
        "en": "Lists are ordered collections that can hold any type of data. They're created with square brackets and can be modified after creation.",
        "fr": "Les listes sont des collections ordonnées pouvant contenir n'importe quel type de données. On les crée avec des crochets et on peut les modifier après leur création.",
        "ar": "القوائم مجموعات مرتّبة يمكنها أن تضمّ أي نوع من البيانات. تُنشأ بالأقواس المربّعة ويمكن تعديلها بعد إنشائها.",
    },
    41: {
        "en": "List operations:",
        "fr": "Opérations sur les listes :",
        "ar": "العمليات على القوائم:",
    },
    42: {
        "en": "Index 0 is the first item. Negative indices count from the end. append() adds to the end. for loops iterate over each item.",
        "fr": "L'indice 0 désigne le premier élément. Les indices négatifs se comptent depuis la fin. append() ajoute à la fin. La boucle for parcourt chaque élément.",
        "ar": "الفهرس 0 يشير إلى العنصر الأول، والفهارس السالبة تُحسب من النهاية. تضيف ()append عنصرًا في النهاية، وتمرّ حلقة for على كل عنصر.",
    },
    43: {
        "en": "Tuples are like lists but immutable (cannot be changed). Sets are unordered collections with no duplicates. Use tuples for fixed data, sets when you need uniqueness.",
        "fr": "Les tuples ressemblent aux listes mais sont immuables (on ne peut pas les modifier). Les ensembles (sets) sont des collections non ordonnées sans doublons. Utilisez les tuples pour des données figées et les ensembles quand l'unicité compte.",
        "ar": "الصفوف (tuples) تشبه القوائم لكنها غير قابلة للتغيير، أما المجموعات (sets) فهي مجموعات غير مرتّبة لا تقبل التكرار. استخدم الصفوف للبيانات الثابتة، والمجموعات حين تحتاج إلى تفرّد العناصر.",
    },
    44: {
        "en": "Tuples and sets:",
        "fr": "Tuples et ensembles :",
        "ar": "الصفوف والمجموعات:",
    },
    45: {
        "en": "Tuples use parentheses, sets use curly braces. Sets automatically remove duplicates. The in operator checks membership efficiently.",
        "fr": "Les tuples s'écrivent avec des parenthèses, les ensembles avec des accolades. Les ensembles suppriment automatiquement les doublons. L'opérateur in teste l'appartenance de façon efficace.",
        "ar": "تُكتب الصفوف بالأقواس المستديرة والمجموعات بالأقواس المعقوفة. وتحذف المجموعات القيم المكرّرة تلقائيًا. ويتحقّق المعامل in من الانتماء بكفاءة عالية.",
    },
    46: {
        "en": "Dictionaries map keys to values. Keys must be unique and immutable. Use square brackets or get() to access values. get() returns None if key missing instead of error.",
        "fr": "Les dictionnaires associent des clés à des valeurs. Les clés doivent être uniques et immuables. Utilisez les crochets ou get() pour accéder aux valeurs : get() renvoie None si la clé est absente, au lieu de lever une erreur.",
        "ar": "تربط القواميس بين المفاتيح والقيم، ويجب أن تكون المفاتيح فريدة وغير قابلة للتغيير. استخدم الأقواس المربّعة أو ()get للوصول إلى القيم، وتُرجع ()get القيمة None عند غياب المفتاح بدل إطلاق خطأ.",
    },
    47: {
        "en": "Dictionary operations:",
        "fr": "Opérations sur les dictionnaires :",
        "ar": "العمليات على القواميس:",
    },
    48: {
        "en": "Use items() to iterate over key-value pairs. Dictionaries are perfect for lookup tables, configurations, and structured data.",
        "fr": "Utilisez items() pour parcourir les paires clé-valeur. Les dictionnaires sont parfaits pour les tables de correspondance, les configurations et les données structurées.",
        "ar": "استخدم ()items للمرور على أزواج المفتاح والقيمة. والقواميس مثالية لجداول البحث والإعدادات والبيانات المُهيكلة.",
    },
    49: {
        "en": "Lists for ordered sequences, dictionaries for key-value lookups, sets for uniqueness. Real problems often need a combination.",
        "fr": "Les listes pour les séquences ordonnées, les dictionnaires pour les recherches clé-valeur, les ensembles pour l'unicité. Les problèmes réels demandent souvent de les combiner.",
        "ar": "القوائم للتسلسلات المرتّبة، والقواميس للبحث بالمفتاح والقيمة، والمجموعات لضمان التفرّد. وغالبًا ما تتطلّب المسائل الحقيقية الجمع بينها.",
    },
    50: {
        "en": "Student grade tracker:",
        "fr": "Suivi des notes des étudiants :",
        "ar": "متابعة درجات الطلبة:",
    },
    51: {
        "en": "Lists hold multiple students (order matters). Each student is a dictionary (named fields). Grades are a list (multiple values).",
        "fr": "La liste contient plusieurs étudiants (l'ordre compte). Chaque étudiant est un dictionnaire (champs nommés). Les notes forment une liste (plusieurs valeurs).",
        "ar": "تضمّ القائمة عدة طلبة (والترتيب مهم)، وكل طالب قاموس بحقول مُسمّاة، أما الدرجات فهي قائمة تحتوي عدة قيم.",
    },
}
