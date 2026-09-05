# -*- coding: utf-8 -*-
"""Micro-Quest content for the 10 lessons Phase 11 adds.

Written with the ``microquest_authoring`` builders throughout (Phase 10's
authoring improvement) — no raw block dicts, so English prose is typed once
per field and ``content`` is derived from it, never hand-duplicated.

WHY THESE 10, AND WHY ONLY FROM 5 COURSES
------------------------------------------
The curriculum has 15 courses, but only 5 of them -- Python Foundations,
Web Fundamentals, SQL & Databases, Git & GitHub, CS Fundamentals -- are built
by ``app/seed/seed_all()``, which is what populates the *test* database
(``test_atlascode.db``) that every backend test runs against. The other 10
courses (JavaScript, Frontend Development, Networking, and so on) exist only
in the live ``atlascode.db``, seeded once by the standalone
``seed_curriculum_expansion.py``, which ``seed_all()`` never calls.

A Micro-Quest lesson chosen from one of those other 10 courses would work
fine against the live database but could never be exercised by a real,
passing backend test -- there would be no lesson row for the test client to
even fetch. Given this phase's explicit requirement for real, verified
backend test coverage of all 10 new quests, every lesson below was chosen
from the 5 courses ``seed_all()`` actually builds, even where that meant
picking "Web Fundamentals" over a topically closer but untestable
"JavaScript" or "Networking" lesson. Each lesson was verified, before writing
a line of content, to: exist with exactly one exercise, carry blocks only at
orders 1-3 (leaving 0/4/5 free the same way lesson 9 did), not already have
Micro-Quest blocks, and not be a project's prerequisite lesson.

THE 10 LESSONS
---------------
  16  Dictionaries                        code_writing     match_pairs
  13  Decomposition and Problem Solving   code_writing     order_steps
  15  Tuples and Sets                     fill_blank       spot_the_bug
  18  How the Web Works                   multiple_choice  order_steps
  23  Selectors and Properties            multiple_choice  match_pairs
  26  Databases and Tables                multiple_choice  match_pairs
  29  Sorting, Grouping and Aggregation   code_writing     spot_the_bug
  45  Memory and Storage                  multiple_choice  order_steps
  47  Networks and the Internet           multiple_choice  spot_the_bug
  32  Commits and History                 ordering         match_pairs

Distribution: match_pairs=4, order_steps=3, spot_the_bug=3 -- a deliberate mix
across all three interactions (see ``check_microquests.py`` for the blueprint
kinds it currently recognises).

Every blueprint teaches the *concept* a lesson's reading blocks already state,
never the exercise's specific values -- e.g. lesson 16's match_pairs is about
dict operations in general, never the product/name/price the exercise asks
for; lesson 29's spot_the_bug is about GROUP BY/HAVING ordering, never the
exercise's own WHERE-clause values. See the inline comment on each lesson
for the specific reasoning about why its blueprint does not leak that
lesson's exercise answer.
"""

from .microquest_authoring import (
    exam_tip_block,
    hook_block,
    match_pairs_blueprint,
    order_steps_blueprint,
    spot_the_bug_blueprint,
)

# --------------------------------------------------------------------------
# Lesson 16 -- "Dictionaries"  (code_writing + match_pairs)
# --------------------------------------------------------------------------
# The exercise asks the student to build one specific product dictionary
# (name/price/in_stock) and update its price. The blueprint pairs are about
# dictionary *operations in general* (assignment, .get(), del, `in`) and never
# mention a product, a name, or a price -- so solving it teaches the syntax
# family the exercise needs without touching the exercise's own content.
DICTIONARIES_BLOCKS = [
    hook_block(
        order=0,
        prose={
            "en": (
                "A school's contact list has 800 students. Looking up one student's "
                "phone number by scanning the list from the top would take forever. A "
                "dictionary finds it instantly -- because it looks things up by name, "
                "not by position."
            ),
            "fr": (
                "Le carnet d'adresses d'une école contient 800 élèves. Chercher le "
                "numéro de téléphone d'un élève en parcourant la liste depuis le début "
                "prendrait une éternité. Un dictionnaire le trouve instantanément -- "
                "parce qu'il recherche par nom, pas par position."
            ),
            "ar": (
                "يحتوي دفتر عناوين إحدى المدارس على 800 تلميذ. البحث عن رقم هاتف تلميذ "
                "واحد بتصفّح القائمة من البداية سيستغرق وقتًا طويلاً جدًا. القاموس "
                "(dictionary) يجده فورًا -- لأنه يبحث بالاسم، لا بالموضع."
            ),
        },
        challenge={
            "en": "How can a program find one piece of information among thousands, instantly, without checking every single one?",
            "fr": "Comment un programme peut-il trouver une information parmi des milliers, instantanément, sans toutes les vérifier une par une ?",
            "ar": "كيف يمكن لبرنامج أن يجد معلومة واحدة من بين الآلاف فورًا، دون التحقق من كل واحدة منها؟",
        },
        learn={
            "en": "You will use a dictionary to store information as key-value pairs, so any value can be looked up directly by its key instead of being searched for.",
            "fr": "Vous allez stocker des informations sous forme de paires clé-valeur dans un dictionnaire, afin de retrouver directement une valeur par sa clé plutôt que de la chercher.",
            "ar": "ستخزّن المعلومات على شكل أزواج مفتاح-قيمة داخل قاموس، بحيث يمكن الوصول إلى أي قيمة مباشرة عبر مفتاحها بدل البحث عنها.",
        },
    ),
    match_pairs_blueprint(
        order=4,
        prose={
            "en": "Connect each dictionary operation to what it actually does.",
            "fr": "Reliez chaque opération sur un dictionnaire à ce qu'elle fait réellement.",
            "ar": "صِل كل عملية على القاموس بما تفعله فعليًا.",
        },
        pairs=[
            (
                "assign",
                {"en": "d[key] = value", "fr": "d[cle] = valeur", "ar": "d[key] = value"},
                {
                    "en": "Adds a new entry, or updates it if the key already exists",
                    "fr": "Ajoute une nouvelle entrée, ou la met à jour si la clé existe déjà",
                    "ar": "يضيف إدخالًا جديدًا، أو يحدّثه إذا كان المفتاح موجودًا مسبقًا",
                },
            ),
            (
                "get_safe",
                {"en": "d.get(key, default)", "fr": "d.get(cle, defaut)", "ar": "d.get(key, default)"},
                {
                    "en": "Looks up a key safely, returning a fallback instead of crashing if it's missing",
                    "fr": "Recherche une clé en toute sécurité, en renvoyant une valeur de repli au lieu de planter si elle est absente",
                    "ar": "يبحث عن مفتاح بأمان، ويعيد قيمة بديلة بدل التوقف عن العمل إذا كان المفتاح غير موجود",
                },
            ),
            (
                "delete",
                {"en": "del d[key]", "fr": "del d[cle]", "ar": "del d[key]"},
                {
                    "en": "Removes an entry by its key",
                    "fr": "Supprime une entrée grâce à sa clé",
                    "ar": "يحذف إدخالًا باستخدام مفتاحه",
                },
            ),
            (
                "membership",
                {"en": "key in d", "fr": "cle in d", "ar": "key in d"},
                {
                    "en": "Checks whether a key exists, without looking up its value",
                    "fr": "Vérifie si une clé existe, sans récupérer sa valeur",
                    "ar": "يتحقّق مما إذا كان المفتاح موجودًا، دون جلب قيمته",
                },
            ),
        ],
        success={
            "en": "Exactly -- each operation reads a key first, then acts. That is the whole idea behind a dictionary.",
            "fr": "Exactement -- chaque opération lit d'abord une clé, puis agit. C'est toute l'idée d'un dictionnaire.",
            "ar": "بالضبط -- كل عملية تقرأ المفتاح أولًا، ثم تتصرّف بناءً عليه. هذه هي الفكرة الكاملة وراء القاموس.",
        },
        hint={
            "en": "Which of these is the one that never raises an error, even if the key is missing?",
            "fr": "Laquelle de ces opérations ne lève jamais d'erreur, même si la clé est absente ?",
            "ar": "أيّ من هذه العمليات لا يُطلق خطأً أبدًا، حتى لو كان المفتاح غير موجود؟",
        },
    ),
    exam_tip_block(
        order=5,
        prose={
            "en": (
                "d[key] raises KeyError if the key does not exist; d.get(key) returns "
                "None instead. Reach for .get() whenever a missing key should not crash "
                "the program."
            ),
            "fr": (
                "d[cle] lève une erreur KeyError si la clé n'existe pas ; d.get(cle) "
                "renvoie None à la place. Utilisez .get() dès qu'une clé manquante ne "
                "doit pas faire planter le programme."
            ),
            "ar": (
                "يُطلق d[key] الخطأ KeyError إذا لم يكن المفتاح موجودًا؛ بينما تعيد "
                "d.get(key) القيمة None بدلًا من ذلك. استخدم .get() كلما كان يجب ألا "
                "يتسبّب مفتاح مفقود في توقّف البرنامج."
            ),
        },
    ),
]

# --------------------------------------------------------------------------
# Lesson 13 -- "Decomposition and Problem Solving"  (code_writing + order_steps)
# --------------------------------------------------------------------------
# The exercise asks for two specific functions (is_even, count_evens). The
# blueprint's steps are the *generic method* of decomposition -- state, split,
# write, combine -- and never mention evenness, counting, or a list, so
# solving it teaches the method, not the exercise's two functions.
DECOMPOSITION_BLOCKS = [
    hook_block(
        order=0,
        prose={
            "en": (
                "A single 40-line function that reads input, validates it, computes a "
                "result and prints a report is nearly impossible to fix when something "
                "goes wrong -- one typo anywhere breaks the whole thing, and there is no "
                "way to test one part on its own."
            ),
            "fr": (
                "Une seule fonction de 40 lignes qui lit une entrée, la valide, calcule "
                "un résultat et affiche un rapport est presque impossible à corriger en "
                "cas de problème -- une seule faute de frappe casse tout, et impossible "
                "de tester une partie isolément."
            ),
            "ar": (
                "دالة واحدة من 40 سطرًا تقرأ مُدخلًا وتتحقّق منه وتحسب نتيجة وتطبع تقريرًا "
                "يكاد يكون من المستحيل إصلاحها عند حدوث خلل -- خطأ إملائي واحد في أي "
                "مكان يُعطّل كل شيء، ولا توجد طريقة لاختبار جزء واحد بمفرده."
            ),
        },
        challenge={
            "en": "How can a big, messy problem be turned into something a programmer can actually reason about?",
            "fr": "Comment transformer un problème vaste et confus en quelque chose qu'un programmeur peut vraiment raisonner ?",
            "ar": "كيف يمكن تحويل مشكلة كبيرة ومعقّدة إلى شيء يمكن للمبرمج أن يفكّر فيه فعلًا؟",
        },
        learn={
            "en": "You will break one large problem into small functions, each responsible for exactly one part, so every piece can be written, tested and fixed on its own.",
            "fr": "Vous allez décomposer un grand problème en petites fonctions, chacune responsable d'une seule partie, afin que chaque morceau puisse être écrit, testé et corrigé séparément.",
            "ar": "ستقسّم مشكلة كبيرة إلى دوال صغيرة، كل واحدة مسؤولة عن جزء واحد فقط، بحيث يمكن كتابة كل جزء واختباره وإصلاحه بمفرده.",
        },
    ),
    order_steps_blueprint(
        order=4,
        prose={
            "en": "Put these steps of solving a problem by decomposition in the order a programmer would actually do them.",
            "fr": "Remettez ces étapes de résolution d'un problème par décomposition dans l'ordre où un programmeur les suivrait réellement.",
            "ar": "رتّب خطوات حل مشكلة عبر التفكيك بالترتيب الذي يتّبعه المبرمج فعليًا.",
        },
        steps=[
            (
                "state",
                {
                    "en": "Describe the overall problem in one sentence",
                    "fr": "Décrire le problème global en une seule phrase",
                    "ar": "صِف المشكلة الكاملة في جملة واحدة",
                },
            ),
            (
                "split",
                {
                    "en": "Break that sentence into smaller, separate sub-tasks",
                    "fr": "Décomposer cette phrase en sous-tâches plus petites et séparées",
                    "ar": "قسّم تلك الجملة إلى مهام فرعية أصغر ومنفصلة",
                },
            ),
            (
                "write",
                {
                    "en": "Write one small function for each sub-task",
                    "fr": "Écrire une petite fonction pour chaque sous-tâche",
                    "ar": "اكتب دالة صغيرة واحدة لكل مهمة فرعية",
                },
            ),
            (
                "combine",
                {
                    "en": "Call those functions together in a main() to produce the final result",
                    "fr": "Appeler ces fonctions ensemble dans une fonction main() pour produire le résultat final",
                    "ar": "استدعِ تلك الدوال معًا داخل دالة main() لإنتاج النتيجة النهائية",
                },
            ),
        ],
        correct_order=["state", "split", "write", "combine"],
        success={
            "en": "That is decomposition: state the problem, split it, solve each small piece, then combine the pieces.",
            "fr": "Voilà la décomposition : énoncer le problème, le diviser, résoudre chaque petite partie, puis les combiner.",
            "ar": "هذا هو التفكيك: صِغ المشكلة، قسّمها، حلّ كل جزء صغير، ثم اجمع الأجزاء.",
        },
        hint={
            "en": "Nothing can be split into sub-tasks before the overall problem itself is clearly stated.",
            "fr": "Rien ne peut être divisé en sous-tâches avant que le problème global lui-même soit clairement énoncé.",
            "ar": "لا يمكن تقسيم أي شيء إلى مهام فرعية قبل صياغة المشكلة الكاملة بوضوح.",
        },
    ),
    exam_tip_block(
        order=5,
        prose={
            "en": (
                "A function that does two unrelated things is a sign the problem was "
                "not decomposed enough -- if you cannot describe what a function does "
                "in one short sentence without the word 'and', split it."
            ),
            "fr": (
                "Une fonction qui fait deux choses sans rapport est le signe que le "
                "problème n'a pas été assez décomposé -- si vous ne pouvez pas décrire "
                "ce que fait une fonction en une phrase courte sans le mot « et », "
                "divisez-la."
            ),
            "ar": (
                "دالة تقوم بأمرين غير مرتبطين ببعضهما علامة على أن المشكلة لم تُفكَّك "
                "بما فيه الكفاية -- إذا لم تستطع وصف ما تفعله دالة في جملة قصيرة دون "
                "استخدام كلمة «و»، فقسّمها."
            ),
        },
    ),
]

# --------------------------------------------------------------------------
# Lesson 15 -- "Tuples and Sets"  (fill_blank + spot_the_bug)
# --------------------------------------------------------------------------
# The exercise fills in a tuple's two values and a set's missing element
# (10, 20, "blue"). The blueprint's four statements are about general
# tuple/set *properties* (immutability, deduplication, mixed types) and never
# mention a coordinate or a color, so the blank answers are never touched.
TUPLES_SETS_BLOCKS = [
    hook_block(
        order=0,
        prose={
            "en": (
                "A student stores a list of exam dates as a tuple, and a friend's code "
                "that tries to fix a typo in one of the dates crashes instantly. "
                "Meanwhile, a class attendance sheet stored as a set never lists the "
                "same name twice -- even when the teacher enters it by mistake."
            ),
            "fr": (
                "Un élève stocke une liste de dates d'examen dans un tuple, et le code "
                "d'un ami qui tente de corriger une faute de frappe dans une des dates "
                "plante instantanément. Pendant ce temps, une feuille de présence "
                "stockée dans un set ne liste jamais deux fois le même nom -- même si "
                "l'enseignant le saisit par erreur."
            ),
            "ar": (
                "يخزّن تلميذ قائمة تواريخ الامتحانات في صف (tuple)، وعندما يحاول صديقه "
                "إصلاح خطأ إملائي في أحد التواريخ يتوقف البرنامج فورًا عن العمل. في "
                "المقابل، ورقة حضور القسم المخزّنة في مجموعة (set) لا تُدرج الاسم نفسه "
                "مرتين أبدًا -- حتى لو أدخله الأستاذ بالخطأ."
            ),
        },
        challenge={
            "en": "Why does one collection refuse to be changed at all, while another refuses to hold duplicates?",
            "fr": "Pourquoi une collection refuse-t-elle d'être modifiée, tandis qu'une autre refuse de contenir des doublons ?",
            "ar": "لماذا ترفض إحدى المجموعات أي تغيير على الإطلاق، بينما ترفض أخرى الاحتفاظ بقيم مكرّرة؟",
        },
        learn={
            "en": "You will pin down exactly what makes a tuple different from a set, so you can predict which one will crash and which one will quietly clean up your data.",
            "fr": "Vous allez déterminer précisément ce qui distingue un tuple d'un set, afin de prédire lequel plantera et lequel nettoiera vos données en silence.",
            "ar": "ستحدد بدقة ما الذي يميّز الصف (tuple) عن المجموعة (set)، لتتوقّع أيّهما سيتسبّب في خطأ وأيّهما سينظّف بياناتك بصمت.",
        },
    ),
    spot_the_bug_blueprint(
        order=4,
        prose={
            "en": "Read these claims about tuples and sets. Exactly one of them is wrong.",
            "fr": "Lisez ces affirmations sur les tuples et les sets. Une seule d'entre elles est fausse.",
            "ar": "اقرأ هذه العبارات حول الصفوف (tuples) والمجموعات (sets). واحدة منها فقط خاطئة.",
        },
        statements=[
            (
                "immutable",
                {
                    "en": "A tuple's contents cannot be changed after it is created",
                    "fr": "Le contenu d'un tuple ne peut pas être modifié après sa création",
                    "ar": "لا يمكن تغيير محتوى الصف (tuple) بعد إنشائه",
                },
            ),
            (
                "dedup",
                {
                    "en": "A set automatically removes duplicate values",
                    "fr": "Un set supprime automatiquement les valeurs en double",
                    "ar": "تحذف المجموعة (set) القيم المكررة تلقائيًا",
                },
            ),
            (
                "mixed",
                {
                    "en": 'A tuple can hold values of different types, like (1, "two", 3.0)',
                    "fr": 'Un tuple peut contenir des valeurs de types différents, comme (1, "deux", 3.0)',
                    "ar": 'يمكن أن يحتوي الصف على قيم من أنواع مختلفة، مثل (1, "اثنان", 3.0)',
                },
            ),
            (
                "editable",
                {
                    "en": "A tuple can be modified in place, the same way a list can",
                    "fr": "Un tuple peut être modifié sur place, de la même façon qu'une liste",
                    "ar": "يمكن تعديل الصف في مكانه، تمامًا كما تُعدَّل القائمة",
                },
            ),
        ],
        buggy_id="editable",
        success={
            "en": "Right -- a tuple can never be modified in place. If you need to change a fixed collection, you need a list instead.",
            "fr": "Exact -- un tuple ne peut jamais être modifié sur place. Si vous devez modifier une collection, il vous faut une liste à la place.",
            "ar": "صحيح -- لا يمكن تعديل الصف أبدًا في مكانه. إذا احتجت إلى تغيير مجموعة، فعليك استخدام قائمة بدلًا منه.",
        },
        hint={
            "en": "Which one directly contradicts the word 'immutable'?",
            "fr": "Laquelle contredit directement le mot « immuable » ?",
            "ar": "أيّها يناقض مباشرة كلمة «غير قابل للتغيير»؟",
        },
    ),
    exam_tip_block(
        order=5,
        prose={
            "en": (
                "Parentheses () make a tuple, curly braces {} make a set (or a dict, if "
                "it has colons) -- a single-item tuple still needs a trailing comma, "
                "like (5,), or Python reads it as just the number 5 in parentheses."
            ),
            "fr": (
                "Les parenthèses () créent un tuple, les accolades {} créent un set (ou "
                "un dict, s'il y a des deux-points) -- un tuple à un seul élément a "
                "quand même besoin d'une virgule finale, comme (5,), sinon Python le lit "
                "comme le simple nombre 5 entre parenthèses."
            ),
            "ar": (
                "الأقواس () تُنشئ صفًا (tuple)، والأقواس المعقوفة {} تُنشئ مجموعة (set) "
                "(أو قاموسًا dict إن وُجدت نقطتان رأسيتان) -- الصف بعنصر واحد يحتاج "
                "فاصلة في النهاية، مثل (5,)، وإلا تقرأه Python كمجرّد الرقم 5 بين "
                "قوسين."
            ),
        },
    ),
]

# --------------------------------------------------------------------------
# Lesson 18 -- "How the Web Works"  (multiple_choice + order_steps)
# --------------------------------------------------------------------------
# The exercise asks a single-role question ("what does the browser do"). The
# blueprint orders the full four-step cycle -- send, process, respond, render
# -- which never states which single answer the MCQ wants, only the order
# each side acts in.
HOW_WEB_WORKS_BLOCKS = [
    hook_block(
        order=0,
        prose={
            "en": (
                "Typing a web address and pressing Enter feels instant, but behind that "
                "one second, a message crosses the internet to a server, and an entire "
                "web page travels back -- in a very specific order that never changes."
            ),
            "fr": (
                "Taper une adresse web et appuyer sur Entrée semble instantané, mais "
                "derrière cette seconde, un message traverse Internet jusqu'à un "
                "serveur, et une page web entière revient -- dans un ordre bien précis "
                "qui ne change jamais."
            ),
            "ar": (
                "كتابة عنوان موقع والضغط على زر الإدخال يبدو فوريًا، لكن خلف تلك "
                "الثانية الواحدة، تعبر رسالة الإنترنت إلى خادم، وتعود صفحة ويب كاملة -- "
                "بترتيب محدد جدًا لا يتغيّر أبدًا."
            ),
        },
        challenge={
            "en": "What actually happens, step by step, between pressing Enter and seeing a page appear?",
            "fr": "Que se passe-t-il réellement, étape par étape, entre l'appui sur Entrée et l'apparition de la page ?",
            "ar": "ماذا يحدث فعليًا، خطوة بخطوة، بين الضغط على زر الإدخال وظهور الصفحة؟",
        },
        learn={
            "en": "You will put the request-response cycle in its real order, so you know exactly which side -- browser or server -- is responsible at each step.",
            "fr": "Vous allez remettre le cycle requête-réponse dans son ordre réel, afin de savoir exactement quel côté -- navigateur ou serveur -- est responsable à chaque étape.",
            "ar": "ستضع دورة الطلب-الاستجابة في ترتيبها الحقيقي، لتعرف بالضبط أي طرف -- المتصفح أم الخادم -- هو المسؤول في كل خطوة.",
        },
    ),
    order_steps_blueprint(
        order=4,
        prose={
            "en": "Put these steps of loading a web page in the order they really happen.",
            "fr": "Remettez ces étapes du chargement d'une page web dans l'ordre où elles se produisent réellement.",
            "ar": "رتّب خطوات تحميل صفحة ويب بالترتيب الذي تحدث به فعليًا.",
        },
        steps=[
            (
                "send",
                {
                    "en": "The browser sends an HTTP request for the page",
                    "fr": "Le navigateur envoie une requête HTTP pour la page",
                    "ar": "يرسل المتصفح طلب HTTP للحصول على الصفحة",
                },
            ),
            (
                "process",
                {
                    "en": "The server receives the request and processes it",
                    "fr": "Le serveur reçoit la requête et la traite",
                    "ar": "يستقبل الخادم الطلب ويعالجه",
                },
            ),
            (
                "respond",
                {
                    "en": "The server sends back an HTTP response containing HTML",
                    "fr": "Le serveur renvoie une réponse HTTP contenant du HTML",
                    "ar": "يرسل الخادم استجابة HTTP تحتوي على HTML",
                },
            ),
            (
                "render",
                {
                    "en": "The browser reads the HTML and renders the page on screen",
                    "fr": "Le navigateur lit le HTML et affiche la page à l'écran",
                    "ar": "يقرأ المتصفح HTML ويعرض الصفحة على الشاشة",
                },
            ),
        ],
        correct_order=["send", "process", "respond", "render"],
        success={
            "en": "That is the request-response cycle: ask, process, answer, display -- the same four steps for every website you visit.",
            "fr": "Voilà le cycle requête-réponse : demander, traiter, répondre, afficher -- les quatre mêmes étapes pour chaque site que vous visitez.",
            "ar": "هذه هي دورة الطلب-الاستجابة: اطلب، عالج، أجب، اعرض -- الخطوات الأربع نفسها لكل موقع تزوره.",
        },
        hint={
            "en": "Nothing can be processed by the server before the browser has actually asked for it.",
            "fr": "Rien ne peut être traité par le serveur avant que le navigateur ne l'ait réellement demandé.",
            "ar": "لا يمكن للخادم معالجة أي شيء قبل أن يطلبه المتصفح فعليًا.",
        },
    ),
    exam_tip_block(
        order=5,
        prose={
            "en": (
                "The browser is the client -- it always makes the first move by sending "
                "the request. The server never sends anything until it has received "
                "one."
            ),
            "fr": (
                "Le navigateur est le client -- il fait toujours le premier pas en "
                "envoyant la requête. Le serveur n'envoie jamais rien avant d'en avoir "
                "reçu une."
            ),
            "ar": (
                "المتصفح هو العميل (client) -- وهو الذي يبادر دائمًا بإرسال الطلب. لا "
                "يرسل الخادم أي شيء أبدًا قبل أن يستقبل طلبًا."
            ),
        },
    ),
]

# --------------------------------------------------------------------------
# Lesson 23 -- "Selectors and Properties"  (multiple_choice + match_pairs)
# --------------------------------------------------------------------------
# The exercise asks which selector targets links inside <nav>, contrasting
# four *combinator* symbols (space, >, +, ~). The blueprint's descendant pair
# only teaches that a space means "nested anywhere inside", without
# mentioning the other three combinators the exercise actually compares.
SELECTORS_BLOCKS = [
    hook_block(
        order=0,
        prose={
            "en": (
                "A stylesheet has one rule for '.card' and another for '#header', and "
                "changing colors in one never accidentally changes the other -- because "
                "each selector targets a very specific, different part of the page."
            ),
            "fr": (
                "Une feuille de style a une règle pour « .card » et une autre pour "
                "« #header », et changer les couleurs de l'une ne modifie jamais l'autre "
                "par erreur -- parce que chaque sélecteur cible une partie précise et "
                "différente de la page."
            ),
            "ar": (
                "تحتوي ورقة الأنماط على قاعدة لـ '.card' وأخرى لـ '#header'، وتغيير "
                "الألوان في إحداهما لا يغيّر الأخرى أبدًا بالخطأ -- لأن كل مُحدِّد "
                "(selector) يستهدف جزءًا محددًا ومختلفًا من الصفحة."
            ),
        },
        challenge={
            "en": "How does a single stylesheet manage to style a menu, a button and a paragraph completely differently, all at once?",
            "fr": "Comment une seule feuille de style parvient-elle à styliser un menu, un bouton et un paragraphe de façon totalement différente, en même temps ?",
            "ar": "كيف تتمكّن ورقة أنماط واحدة من تنسيق قائمة وزر وفقرة بشكل مختلف تمامًا، في آن واحد؟",
        },
        learn={
            "en": "You will connect each kind of CSS selector to exactly what it targets, so you can predict which elements a rule will actually style.",
            "fr": "Vous allez relier chaque type de sélecteur CSS à ce qu'il cible exactement, afin de prédire quels éléments une règle va réellement styliser.",
            "ar": "ستصل كل نوع من مُحدِّدات CSS بما يستهدفه بالضبط، لتتوقّع أي عناصر ستُنسِّقها قاعدة معينة فعليًا.",
        },
    ),
    match_pairs_blueprint(
        order=4,
        prose={
            "en": "Connect each CSS selector to what it actually selects.",
            "fr": "Reliez chaque sélecteur CSS à ce qu'il sélectionne réellement.",
            "ar": "صِل كل مُحدِّد CSS بما يحدّده فعليًا.",
        },
        pairs=[
            (
                "class_sel",
                {"en": ".card", "fr": ".card", "ar": ".card"},
                {
                    "en": 'Every element that has the class "card"',
                    "fr": 'Tous les éléments qui ont la classe « card »',
                    "ar": 'كل عنصر يحمل الصنف "card"',
                },
            ),
            (
                "id_sel",
                {"en": "#header", "fr": "#header", "ar": "#header"},
                {
                    "en": 'The one single element with the id "header"',
                    "fr": 'L\'unique élément portant l\'id « header »',
                    "ar": 'العنصر الوحيد الذي يحمل المعرّف "header"',
                },
            ),
            (
                "hover_sel",
                {"en": "a:hover", "fr": "a:hover", "ar": "a:hover"},
                {
                    "en": "A link, only while the mouse is over it",
                    "fr": "Un lien, uniquement pendant que la souris est dessus",
                    "ar": "رابط، فقط أثناء مرور الفأرة فوقه",
                },
            ),
            (
                "descendant_sel",
                {"en": "div p", "fr": "div p", "ar": "div p"},
                {
                    "en": "Every p element nested anywhere inside a div",
                    "fr": "Tout élément p imbriqué n'importe où à l'intérieur d'un div",
                    "ar": "كل عنصر p متداخل في أي مكان داخل عنصر div",
                },
            ),
        ],
        success={
            "en": "Exactly -- a class can repeat everywhere, an id names one element, a pseudo-class reacts to a state, and a space nests one selector inside another.",
            "fr": "Exactement -- une classe peut se répéter partout, un id nomme un seul élément, une pseudo-classe réagit à un état, et une espace imbrique un sélecteur dans un autre.",
            "ar": "بالضبط -- يمكن أن يتكرر الصنف في كل مكان، والمعرّف يسمّي عنصرًا واحدًا، والصنف الزائف يستجيب لحالة معيّنة، والمسافة تُدخل مُحدِّدًا داخل آخر.",
        },
        hint={
            "en": "Which one can only ever match exactly one element on the whole page?",
            "fr": "Lequel ne peut correspondre qu'à un seul élément sur toute la page ?",
            "ar": "أيّها لا يمكن أن يطابق سوى عنصر واحد بالضبط في الصفحة كلها؟",
        },
    ),
    exam_tip_block(
        order=5,
        prose={
            "en": (
                "An id (#) should be used at most once per page; a class (.) is meant "
                "to be reused on many elements. Mixing them up is a common source of "
                "styles that unexpectedly apply everywhere -- or nowhere."
            ),
            "fr": (
                "Un id (#) doit être utilisé au plus une fois par page ; une classe (.) "
                "est faite pour être réutilisée sur plusieurs éléments. Les confondre "
                "est une cause fréquente de styles qui s'appliquent partout -- ou nulle "
                "part -- de façon inattendue."
            ),
            "ar": (
                "يجب استخدام المعرّف (#) مرة واحدة على الأكثر في كل صفحة؛ بينما الصنف "
                "(.) مُصمَّم لإعادة استخدامه على عدة عناصر. الخلط بينهما سبب شائع لأنماط "
                "تُطبَّق في كل مكان -- أو لا تُطبَّق في أي مكان -- بشكل غير متوقع."
            ),
        },
    ),
]

# --------------------------------------------------------------------------
# Lesson 26 -- "Databases and Tables"  (multiple_choice + match_pairs)
# --------------------------------------------------------------------------
# The exercise asks what a primary key is -- a definition the lesson's own
# reading block already states plainly. The blueprint reinforces that
# definition alongside three OTHER terms (row, column, foreign key), so
# solving it teaches the whole vocabulary, not a hidden fact invented for
# the exercise.
DATABASES_TABLES_BLOCKS = [
    hook_block(
        order=0,
        prose={
            "en": (
                "A school's student records live in one table, their course "
                "enrollments in another -- and a single foreign key is what lets the "
                "database know which student belongs to which course, without ever "
                "copying a student's whole record into the enrollments table."
            ),
            "fr": (
                "Les dossiers des élèves d'une école vivent dans une table, leurs "
                "inscriptions aux cours dans une autre -- et c'est une simple clé "
                "étrangère qui permet à la base de données de savoir quel élève "
                "appartient à quel cours, sans jamais copier tout le dossier d'un élève "
                "dans la table des inscriptions."
            ),
            "ar": (
                "تعيش سجلات تلاميذ مدرسة في جدول واحد، وتسجيلاتهم في المقررات في جدول "
                "آخر -- ومفتاح أجنبي واحد (foreign key) هو ما يجعل قاعدة البيانات تعرف "
                "أي تلميذ ينتمي إلى أي مقرر، دون نسخ سجل التلميذ كاملًا إلى جدول "
                "التسجيلات."
            ),
        },
        challenge={
            "en": "How can two separate tables stay connected to each other without duplicating all their data?",
            "fr": "Comment deux tables séparées peuvent-elles rester connectées l'une à l'autre sans dupliquer toutes leurs données ?",
            "ar": "كيف يمكن لجدولين منفصلين أن يبقيا مترابطين دون تكرار كل بياناتهما؟",
        },
        learn={
            "en": "You will connect each core relational-database term to what it actually means, so a table's structure stops looking like a wall of unfamiliar words.",
            "fr": "Vous allez relier chaque terme fondamental des bases de données relationnelles à ce qu'il signifie réellement, pour que la structure d'une table cesse d'être un mur de mots inconnus.",
            "ar": "ستصل كل مصطلح أساسي في قواعد البيانات العلائقية بمعناه الحقيقي، حتى لا يبدو هيكل الجدول جدارًا من الكلمات الغريبة.",
        },
    ),
    match_pairs_blueprint(
        order=4,
        prose={
            "en": "Connect each database term to its definition.",
            "fr": "Reliez chaque terme de base de données à sa définition.",
            "ar": "صِل كل مصطلح في قواعد البيانات بتعريفه.",
        },
        pairs=[
            (
                "row",
                {"en": "Row", "fr": "Ligne", "ar": "صف (Row)"},
                {
                    "en": "One single record in a table, like one student",
                    "fr": "Un seul enregistrement dans une table, comme un élève",
                    "ar": "سجل واحد في الجدول، مثل تلميذ واحد",
                },
            ),
            (
                "column",
                {"en": "Column", "fr": "Colonne", "ar": "عمود (Column)"},
                {
                    "en": 'One field shared by every row, like "email"',
                    "fr": 'Un champ partagé par toutes les lignes, comme « email »',
                    "ar": 'حقل مشترك بين كل الصفوف، مثل "email"',
                },
            ),
            (
                "pk",
                {"en": "Primary Key", "fr": "Clé primaire", "ar": "المفتاح الأساسي (Primary Key)"},
                {
                    "en": "The value that uniquely identifies each row in a table",
                    "fr": "La valeur qui identifie de façon unique chaque ligne d'une table",
                    "ar": "القيمة التي تُعرِّف كل صف في الجدول بشكل فريد",
                },
            ),
            (
                "fk",
                {"en": "Foreign Key", "fr": "Clé étrangère", "ar": "المفتاح الأجنبي (Foreign Key)"},
                {
                    "en": "A value that points to a primary key in another table",
                    "fr": "Une valeur qui pointe vers une clé primaire d'une autre table",
                    "ar": "قيمة تشير إلى مفتاح أساسي في جدول آخر",
                },
            ),
        ],
        success={
            "en": "Exactly -- a primary key identifies a row in its own table; a foreign key links that row to a row in another table.",
            "fr": "Exactement -- une clé primaire identifie une ligne dans sa propre table ; une clé étrangère relie cette ligne à une ligne d'une autre table.",
            "ar": "بالضبط -- المفتاح الأساسي يُعرِّف صفًا في جدوله الخاص؛ والمفتاح الأجنبي يربط ذلك الصف بصف في جدول آخر.",
        },
        hint={
            "en": "Which one lives inside the SAME table it identifies, and which one points OUT to a different table?",
            "fr": "Lequel vit dans la MÊME table qu'il identifie, et lequel pointe VERS une autre table ?",
            "ar": "أيّهما موجود داخل الجدول نفسه الذي يعرّفه، وأيّهما يشير إلى جدول آخر؟",
        },
    ),
    exam_tip_block(
        order=5,
        prose={
            "en": (
                "A primary key can never be NULL and can never repeat within its table "
                "-- if a column could have two rows sharing the same value, it cannot "
                "be the primary key."
            ),
            "fr": (
                "Une clé primaire ne peut jamais être NULL et ne peut jamais se répéter "
                "dans sa table -- si une colonne peut avoir deux lignes partageant la "
                "même valeur, elle ne peut pas être la clé primaire."
            ),
            "ar": (
                "لا يمكن أن يكون المفتاح الأساسي فارغًا (NULL) أبدًا ولا يمكن أن يتكرر "
                "داخل جدوله -- فإذا كان عمود ما يمكن أن يحمل صفان فيه القيمة نفسها، "
                "فلا يمكن أن يكون هو المفتاح الأساسي."
            ),
        },
    ),
]

# --------------------------------------------------------------------------
# Lesson 29 -- "Sorting, Grouping and Aggregation"  (code_writing + spot_the_bug)
# --------------------------------------------------------------------------
# The exercise asks for a specific GROUP BY / HAVING query (grouping by city,
# a COUNT(*) threshold). The blueprint's four claims are about the general
# *order of operations* between WHERE, GROUP BY and HAVING -- never about a
# city, a count threshold, or any of the exercise's specific values.
SORTING_GROUPING_BLOCKS = [
    hook_block(
        order=0,
        prose={
            "en": (
                "A school wants the average grade per class, not per student -- one "
                "query that groups hundreds of individual grade rows into just a "
                "handful of class averages, calculated automatically."
            ),
            "fr": (
                "Une école veut la moyenne des notes par classe, pas par élève -- une "
                "seule requête qui regroupe des centaines de lignes de notes "
                "individuelles en une poignée de moyennes par classe, calculées "
                "automatiquement."
            ),
            "ar": (
                "تريد مدرسة معدّل النقط لكل قسم، وليس لكل تلميذ -- استعلام واحد يجمّع "
                "مئات صفوف النقط الفردية في عدد قليل من معدّلات الأقسام، محسوبة "
                "تلقائيًا."
            ),
        },
        challenge={
            "en": "How does a single query turn hundreds of individual rows into one summary row per group?",
            "fr": "Comment une seule requête transforme-t-elle des centaines de lignes individuelles en une seule ligne de résumé par groupe ?",
            "ar": "كيف يحوّل استعلام واحد مئات الصفوف الفردية إلى صف ملخّص واحد لكل مجموعة؟",
        },
        learn={
            "en": "You will pin down exactly when GROUP BY and HAVING run, so you can predict which rows survive and which get filtered out.",
            "fr": "Vous allez déterminer précisément quand s'exécutent GROUP BY et HAVING, afin de prédire quelles lignes survivent et lesquelles sont filtrées.",
            "ar": "ستحدد بدقة متى تُنفَّذ GROUP BY وHAVING، لتتوقّع أي الصفوف تبقى وأيّها يُستبعد.",
        },
    ),
    spot_the_bug_blueprint(
        order=4,
        prose={
            "en": "Read these claims about GROUP BY and HAVING. Exactly one of them is wrong.",
            "fr": "Lisez ces affirmations sur GROUP BY et HAVING. Une seule d'entre elles est fausse.",
            "ar": "اقرأ هذه العبارات حول GROUP BY وHAVING. واحدة منها فقط خاطئة.",
        },
        statements=[
            (
                "where_first",
                {
                    "en": "WHERE filters individual rows before they are grouped",
                    "fr": "WHERE filtre les lignes individuelles avant qu'elles ne soient regroupées",
                    "ar": "تُصفّي WHERE الصفوف الفردية قبل تجميعها",
                },
            ),
            (
                "having_after",
                {
                    "en": "HAVING filters whole groups, after GROUP BY has combined the rows",
                    "fr": "HAVING filtre des groupes entiers, après que GROUP BY a combiné les lignes",
                    "ar": "تُصفّي HAVING مجموعات كاملة، بعد أن تكون GROUP BY قد جمّعت الصفوف",
                },
            ),
            (
                "select_rule",
                {
                    "en": "A column in SELECT must either be grouped or wrapped in an aggregate function like COUNT()",
                    "fr": "Une colonne dans SELECT doit soit être regroupée, soit être enveloppée dans une fonction d'agrégation comme COUNT()",
                    "ar": "يجب أن يكون العمود في SELECT إما مُجمَّعًا أو داخل دالة تجميع مثل COUNT()",
                },
            ),
            (
                "having_before",
                {
                    "en": "HAVING runs before GROUP BY has grouped anything",
                    "fr": "HAVING s'exécute avant que GROUP BY n'ait regroupé quoi que ce soit",
                    "ar": "تُنفَّذ HAVING قبل أن تجمّع GROUP BY أي شيء",
                },
            ),
        ],
        buggy_id="having_before",
        success={
            "en": "Right -- GROUP BY always runs first to form the groups; HAVING only filters after those groups already exist.",
            "fr": "Exact -- GROUP BY s'exécute toujours en premier pour former les groupes ; HAVING ne filtre qu'une fois ces groupes déjà formés.",
            "ar": "صحيح -- تُنفَّذ GROUP BY دائمًا أولًا لتكوين المجموعات؛ وتُصفّي HAVING فقط بعد أن تكون تلك المجموعات موجودة.",
        },
        hint={
            "en": "Which one gets the order of GROUP BY and HAVING backwards?",
            "fr": "Laquelle inverse l'ordre entre GROUP BY et HAVING ?",
            "ar": "أيّها يعكس ترتيب GROUP BY وHAVING؟",
        },
    ),
    exam_tip_block(
        order=5,
        prose={
            "en": (
                "WHERE cannot filter on an aggregate like COUNT(*) -- because WHERE "
                "runs before the aggregate is even calculated. Use HAVING for any "
                "condition on a group's total, count or average."
            ),
            "fr": (
                "WHERE ne peut pas filtrer sur un agrégat comme COUNT(*) -- parce que "
                "WHERE s'exécute avant même que l'agrégat soit calculé. Utilisez HAVING "
                "pour toute condition sur un total, un count ou une moyenne de groupe."
            ),
            "ar": (
                "لا يمكن لـ WHERE أن تُصفّي بناءً على دالة تجميع مثل COUNT(*) -- لأن "
                "WHERE تُنفَّذ قبل حساب دالة التجميع أصلًا. استخدم HAVING لأي شرط على "
                "مجموع أو عدد أو متوسط مجموعة."
            ),
        },
    ),
]

# --------------------------------------------------------------------------
# Lesson 45 -- "Memory and Storage"  (multiple_choice + order_steps)
# --------------------------------------------------------------------------
# The exercise asks which kind of memory is volatile. Ordering the hierarchy
# by speed/proximity to the CPU is a different fact than volatility, and
# never states which layer loses its data when power is cut.
MEMORY_STORAGE_BLOCKS = [
    hook_block(
        order=0,
        prose={
            "en": (
                "A CPU can read from its own registers in under a nanosecond, but "
                "reading the same amount of data from a hard drive can take ten million "
                "times longer -- that gap is exactly why computers use several layers "
                "of memory instead of just one."
            ),
            "fr": (
                "Un CPU peut lire dans ses propres registres en moins d'une "
                "nanoseconde, mais lire la même quantité de données depuis un disque "
                "dur peut prendre dix millions de fois plus de temps -- c'est "
                "exactement pour cet écart que les ordinateurs utilisent plusieurs "
                "niveaux de mémoire plutôt qu'un seul."
            ),
            "ar": (
                "يمكن للمعالج (CPU) أن يقرأ من سجلاته الخاصة في أقل من نانوثانية، لكن "
                "قراءة الكمية نفسها من البيانات من قرص صلب قد تستغرق أطول بعشرة "
                "ملايين مرة -- وهذا الفارق بالضبط هو سبب استخدام الحواسيب عدة طبقات "
                "من الذاكرة بدل طبقة واحدة."
            ),
        },
        challenge={
            "en": "Why does a computer bother with several different kinds of memory instead of just one big, fast one?",
            "fr": "Pourquoi un ordinateur se donne-t-il la peine d'utiliser plusieurs types de mémoire différents au lieu d'une seule grande mémoire rapide ?",
            "ar": "لماذا يستخدم الحاسوب عدة أنواع مختلفة من الذاكرة بدل ذاكرة كبيرة وسريعة واحدة؟",
        },
        learn={
            "en": "You will order the memory hierarchy from fastest to slowest, so you understand why cache and RAM both exist for different jobs.",
            "fr": "Vous allez ordonner la hiérarchie mémoire de la plus rapide à la plus lente, pour comprendre pourquoi le cache et la RAM existent tous deux, pour des rôles différents.",
            "ar": "سترتّب هرم الذاكرة من الأسرع إلى الأبطأ، لتفهم لماذا توجد كل من الذاكرة المخبّئة (cache) والذاكرة العشوائية (RAM) لأداء مهام مختلفة.",
        },
    ),
    order_steps_blueprint(
        order=4,
        prose={
            "en": "Order these kinds of memory from fastest and closest to the CPU, to slowest and furthest away.",
            "fr": "Classez ces types de mémoire du plus rapide et le plus proche du CPU, au plus lent et le plus éloigné.",
            "ar": "رتّب أنواع الذاكرة هذه من الأسرع والأقرب إلى المعالج، إلى الأبطأ والأبعد عنه.",
        },
        steps=[
            (
                "registers",
                {
                    "en": "CPU registers -- a handful of values, ready instantly",
                    "fr": "Registres du CPU -- une poignée de valeurs, prêtes instantanément",
                    "ar": "سجلات المعالج -- عدد قليل من القيم، جاهزة فورًا",
                },
            ),
            (
                "cache",
                {
                    "en": "Cache (L1/L2/L3) -- small, very fast memory next to the CPU",
                    "fr": "Cache (L1/L2/L3) -- mémoire petite et très rapide, juste à côté du CPU",
                    "ar": "الذاكرة المخبّئة (L1/L2/L3) -- ذاكرة صغيرة وسريعة جدًا بجانب المعالج",
                },
            ),
            (
                "ram",
                {
                    "en": "RAM -- larger, fast, but cleared when the power turns off",
                    "fr": "RAM -- plus grande, rapide, mais effacée à la coupure de courant",
                    "ar": "الذاكرة العشوائية (RAM) -- أكبر وسريعة، لكنها تُمسح عند انقطاع الكهرباء",
                },
            ),
            (
                "disk",
                {
                    "en": "SSD / HDD -- huge, slow, but keeps data without power",
                    "fr": "SSD / HDD -- énorme, lent, mais garde les données sans électricité",
                    "ar": "القرص الصلب (SSD/HDD) -- ضخم وبطيء، لكنه يحتفظ بالبيانات دون كهرباء",
                },
            ),
        ],
        correct_order=["registers", "cache", "ram", "disk"],
        success={
            "en": "That is the memory hierarchy: the closer to the CPU, the faster and smaller; the further away, the slower and larger.",
            "fr": "Voilà la hiérarchie mémoire : plus c'est proche du CPU, plus c'est rapide et petit ; plus c'est loin, plus c'est lent et grand.",
            "ar": "هذا هو هرم الذاكرة: كلما اقتربت من المعالج، كانت أسرع وأصغر؛ وكلما ابتعدت، كانت أبطأ وأكبر.",
        },
        hint={
            "en": "The fastest kind of memory is also, by far, the smallest.",
            "fr": "Le type de mémoire le plus rapide est aussi, de loin, le plus petit.",
            "ar": "أسرع أنواع الذاكرة هو أيضًا الأصغر بفارق كبير.",
        },
    ),
    exam_tip_block(
        order=5,
        prose={
            "en": (
                '"Volatile" means data is lost when power is cut. Registers, cache and '
                "RAM are all volatile; only storage like an SSD or HDD keeps data with "
                "the power off."
            ),
            "fr": (
                "« Volatile » signifie que les données sont perdues à la coupure de "
                "courant. Les registres, le cache et la RAM sont tous volatils ; seul un "
                "stockage comme un SSD ou un HDD garde les données une fois éteint."
            ),
            "ar": (
                'تعني كلمة "متطايرة" (volatile) أن البيانات تُفقد عند انقطاع الكهرباء. '
                "السجلات والذاكرة المخبّئة والذاكرة العشوائية كلها متطايرة؛ فقط وسائط "
                "التخزين مثل SSD أو HDD تحتفظ بالبيانات بعد إيقاف التشغيل."
            ),
        },
    ),
]

# --------------------------------------------------------------------------
# Lesson 47 -- "Networks and the Internet"  (multiple_choice + spot_the_bug)
# --------------------------------------------------------------------------
# The exercise asks which protocol delivers reliably and in order (TCP). The
# blueprint's bug is about NAT and private addresses -- a different fact the
# lesson also teaches -- so it never states the TCP/UDP answer the exercise
# actually grades.
NETWORKS_INTERNET_BLOCKS = [
    hook_block(
        order=0,
        prose={
            "en": (
                "A phone on a school's WiFi and the school's own web server both have "
                "IP addresses -- but the phone's address only makes sense inside that "
                "WiFi network, while the server's address must be reachable from "
                "anywhere on the internet."
            ),
            "fr": (
                "Un téléphone sur le WiFi d'une école et le serveur web de cette école "
                "ont tous deux une adresse IP -- mais l'adresse du téléphone n'a de sens "
                "qu'à l'intérieur de ce réseau WiFi, tandis que l'adresse du serveur "
                "doit être accessible depuis n'importe où sur Internet."
            ),
            "ar": (
                "لكل من هاتف متّصل بشبكة WiFi تابعة لمدرسة وخادم الويب الخاص بتلك "
                "المدرسة عنوان IP -- لكن عنوان الهاتف له معنى فقط داخل تلك الشبكة، بينما "
                "يجب أن يكون عنوان الخادم قابلًا للوصول إليه من أي مكان على الإنترنت."
            ),
        },
        challenge={
            "en": "How can a device be identified on a network at all, and why can't every device just use any address it wants?",
            "fr": "Comment un appareil peut-il seulement être identifié sur un réseau, et pourquoi chaque appareil ne peut-il pas simplement utiliser l'adresse qu'il veut ?",
            "ar": "كيف يمكن لجهاز أن يُعرَّف أصلًا على شبكة ما، ولماذا لا يستطيع كل جهاز استخدام أي عنوان يريده؟",
        },
        learn={
            "en": "You will pin down what a few core networking facts actually mean, so terms like DNS, TCP and NAT stop being just letters.",
            "fr": "Vous allez déterminer ce que signifient réellement quelques faits fondamentaux sur les réseaux, pour que des termes comme DNS, TCP et NAT cessent d'être de simples lettres.",
            "ar": "ستحدد المعنى الحقيقي لبعض الحقائق الأساسية في الشبكات، حتى لا تبقى مصطلحات مثل DNS وTCP وNAT مجرد حروف.",
        },
    ),
    spot_the_bug_blueprint(
        order=4,
        prose={
            "en": "Read these claims about networks. Exactly one of them is wrong.",
            "fr": "Lisez ces affirmations sur les réseaux. Une seule d'entre elles est fausse.",
            "ar": "اقرأ هذه العبارات حول الشبكات. واحدة منها فقط خاطئة.",
        },
        statements=[
            (
                "dns",
                {
                    "en": "DNS translates a domain name into an IP address",
                    "fr": "Le DNS traduit un nom de domaine en adresse IP",
                    "ar": "يترجم DNS اسم النطاق إلى عنوان IP",
                },
            ),
            (
                "tcp",
                {
                    "en": "TCP delivers data reliably and in the correct order",
                    "fr": "TCP livre les données de manière fiable et dans le bon ordre",
                    "ar": "يوصل TCP البيانات بشكل موثوق وبالترتيب الصحيح",
                },
            ),
            (
                "https_port",
                {
                    "en": "HTTPS traffic normally travels over port 443",
                    "fr": "Le trafic HTTPS transite normalement par le port 443",
                    "ar": "تنتقل حركة بيانات HTTPS عادة عبر المنفذ 443",
                },
            ),
            (
                "private_direct",
                {
                    "en": "A device with a private IP address can be reached directly from the public internet, without NAT",
                    "fr": "Un appareil avec une adresse IP privée peut être atteint directement depuis Internet, sans NAT",
                    "ar": "يمكن الوصول إلى جهاز يحمل عنوان IP خاصًا مباشرة من الإنترنت العام، دون NAT",
                },
            ),
        ],
        buggy_id="private_direct",
        success={
            "en": "Right -- a private IP is only valid inside its own network; NAT is exactly what translates it to a public address to reach the internet.",
            "fr": "Exact -- une IP privée n'est valable qu'à l'intérieur de son propre réseau ; c'est précisément le NAT qui la traduit en adresse publique pour atteindre Internet.",
            "ar": "صحيح -- عنوان IP الخاص صالح فقط داخل شبكته الخاصة؛ وNAT هو بالضبط ما يترجمه إلى عنوان عام للوصول إلى الإنترنت.",
        },
        hint={
            "en": "Which one forgets that a private address only means something inside its own local network?",
            "fr": "Laquelle oublie qu'une adresse privée n'a de sens qu'à l'intérieur de son propre réseau local ?",
            "ar": "أيّها ينسى أن العنوان الخاص له معنى فقط داخل شبكته المحلية؟",
        },
    ),
    exam_tip_block(
        order=5,
        prose={
            "en": (
                "Port numbers identify a service, not a device: 80 is plain HTTP, 443 "
                "is HTTPS, 53 is DNS. The same device can run several services at once, "
                "each on its own port."
            ),
            "fr": (
                "Les numéros de port identifient un service, pas un appareil : 80 pour "
                "HTTP, 443 pour HTTPS, 53 pour DNS. Le même appareil peut exécuter "
                "plusieurs services à la fois, chacun sur son propre port."
            ),
            "ar": (
                "أرقام المنافذ تحدّد خدمة، لا جهازًا: 80 لبروتوكول HTTP العادي، و443 "
                "لبروتوكول HTTPS، و53 لـ DNS. يمكن للجهاز نفسه تشغيل عدة خدمات في آن "
                "واحد، كل واحدة على منفذها الخاص."
            ),
        },
    ),
]

# --------------------------------------------------------------------------
# Lesson 32 -- "Commits and History"  (ordering + match_pairs)
# --------------------------------------------------------------------------
# The exercise orders four DIFFERENT commands (init, add, commit, log). The
# blueprint pairs a different set of commands (log, diff, show, HEAD~1) with
# their MEANING, never their order -- so it teaches vocabulary the exercise's
# ordering puzzle does not test, and never states the exercise's sequence.
COMMITS_HISTORY_BLOCKS = [
    hook_block(
        order=0,
        prose={
            "en": (
                "A project has 200 commits, and something broke three weeks ago -- "
                "nobody remembers editing the file that is now failing. Being able to "
                "inspect exactly what changed, and when, is the only way to actually "
                "find out."
            ),
            "fr": (
                "Un projet compte 200 commits, et quelque chose s'est cassé il y a "
                "trois semaines -- personne ne se souvient avoir modifié le fichier qui "
                "échoue maintenant. Pouvoir inspecter exactement ce qui a changé, et "
                "quand, est le seul moyen de le découvrir réellement."
            ),
            "ar": (
                "يحتوي مشروع على 200 تسجيلة (commit)، وتعطّل شيء ما قبل ثلاثة أسابيع -- "
                "لا أحد يتذكر تعديل الملف الذي أصبح الآن معطلًا. القدرة على معاينة ما "
                "تغيّر بالضبط، ومتى، هي الطريقة الوحيدة لمعرفة ذلك فعلًا."
            ),
        },
        challenge={
            "en": "Once a project has hundreds of commits, how do you find out what changed and when, without guessing?",
            "fr": "Une fois qu'un projet compte des centaines de commits, comment savoir ce qui a changé et quand, sans deviner ?",
            "ar": "عندما يحتوي المشروع على مئات التسجيلات، كيف تعرف ما الذي تغيّر ومتى، دون تخمين؟",
        },
        learn={
            "en": "You will connect the everyday Git history commands to what each one actually shows you, so you know which one to reach for.",
            "fr": "Vous allez relier les commandes Git courantes de l'historique à ce que chacune montre réellement, afin de savoir laquelle utiliser.",
            "ar": "ستصل أوامر تاريخ Git اليومية بما تعرضه كل واحدة منها فعليًا، لتعرف أيّها تستخدم.",
        },
    ),
    match_pairs_blueprint(
        order=4,
        prose={
            "en": "Connect each Git command to what it actually shows you.",
            "fr": "Reliez chaque commande Git à ce qu'elle vous montre réellement.",
            "ar": "صِل كل أمر Git بما يعرضه لك فعليًا.",
        },
        pairs=[
            (
                "log",
                {"en": "git log", "fr": "git log", "ar": "git log"},
                {
                    "en": "The full commit history of the project",
                    "fr": "L'historique complet des commits du projet",
                    "ar": "تاريخ تسجيلات المشروع كاملًا",
                },
            ),
            (
                "diff",
                {"en": "git diff", "fr": "git diff", "ar": "git diff"},
                {
                    "en": "What has changed but has not been committed yet",
                    "fr": "Ce qui a changé mais n'a pas encore été commité",
                    "ar": "ما تغيّر ولم يُسجَّل بعد",
                },
            ),
            (
                "show",
                {"en": "git show HEAD", "fr": "git show HEAD", "ar": "git show HEAD"},
                {
                    "en": "Exactly what the most recent commit changed",
                    "fr": "Exactement ce qu'a changé le commit le plus récent",
                    "ar": "بالضبط ما غيّرته آخر تسجيلة",
                },
            ),
            (
                "head_parent",
                {"en": "HEAD~1", "fr": "HEAD~1", "ar": "HEAD~1"},
                {
                    "en": "The commit right before the current one",
                    "fr": "Le commit juste avant l'actuel",
                    "ar": "التسجيلة التي تسبق التسجيلة الحالية مباشرة",
                },
            ),
        ],
        success={
            "en": "Exactly -- git log lists history, git diff shows pending changes, and git show / HEAD~1 both look at one specific commit.",
            "fr": "Exactement -- git log liste l'historique, git diff montre les changements en attente, et git show / HEAD~1 regardent tous deux un commit précis.",
            "ar": "بالضبط -- يسرد git log التاريخ، وتُظهر git diff التغييرات المعلّقة، وينظر كل من git show وHEAD~1 إلى تسجيلة محددة واحدة.",
        },
        hint={
            "en": "Which one looks at UNCOMMITTED changes, and which ones look at commits that already exist?",
            "fr": "Laquelle regarde les changements NON commités, et lesquelles regardent des commits déjà existants ?",
            "ar": "أيّها ينظر إلى تغييرات غير مسجَّلة، وأيّها ينظر إلى تسجيلات موجودة بالفعل؟",
        },
    ),
    exam_tip_block(
        order=5,
        prose={
            "en": (
                'HEAD always means "the current commit" -- HEAD~1 is its parent, '
                "HEAD~2 is its grandparent, and so on. It is a relative pointer, not a "
                "fixed commit."
            ),
            "fr": (
                "HEAD signifie toujours « le commit actuel » -- HEAD~1 est son parent, "
                "HEAD~2 son grand-parent, et ainsi de suite. C'est un pointeur relatif, "
                "pas un commit fixe."
            ),
            "ar": (
                'يعني HEAD دائمًا "التسجيلة الحالية" -- وHEAD~1 هي التسجيلة الأم لها، '
                "وHEAD~2 هي تسجيلة الجد، وهكذا. إنه مؤشر نسبي، لا تسجيلة ثابتة."
            ),
        },
    ),
]

#: Every Micro-Quest this module owns, keyed by the lesson slug it belongs to.
#: Merged into ``microquest_content.MICROQUEST_BY_SLUG`` so the migration, the
#: seed functions and the audit script all read from the one registry.
MICROQUEST_BY_SLUG_PHASE11 = {
    "dictionaries": DICTIONARIES_BLOCKS,
    "decomposition-problem-solving": DECOMPOSITION_BLOCKS,
    "tuples-and-sets": TUPLES_SETS_BLOCKS,
    "how-web-works": HOW_WEB_WORKS_BLOCKS,
    "selectors-properties": SELECTORS_BLOCKS,
    "databases-and-tables": DATABASES_TABLES_BLOCKS,
    "sorting-grouping-aggregation": SORTING_GROUPING_BLOCKS,
    "memory-and-storage": MEMORY_STORAGE_BLOCKS,
    "networks-internet": NETWORKS_INTERNET_BLOCKS,
    "commits-and-history": COMMITS_HISTORY_BLOCKS,
}
