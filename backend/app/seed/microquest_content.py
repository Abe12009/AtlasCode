# -*- coding: utf-8 -*-
"""Micro-Quest block content for the reference lessons that came after lesson 9.

Lesson 9's blocks live inline in ``python_foundations.py`` (and, duplicated for
the migration, in ``microquest_lesson9.py``). Adding two more lessons that way
would have meant three more walls of escaped JSON, so from here the blocks are
authored once, as Python data, and both consumers read them from this module:

  * the seed functions, which build a fresh database (and the test database);
  * ``migrations/add_microquest_lessons_12_36.py``, which inserts the same rows
    into the live ``atlascode.db`` without touching anything already there.

The three block types are the ones lesson 9 established:

  hook       a short real-world scenario, the challenge it raises, and what the
             student will learn. The scenario is prose and goes through
             lesson_block_translations like any other block; the challenge and
             "what you'll learn" lines are structured data and live in
             ``config`` with their own per-language values.

  blueprint  an interactive warm-up. ``config.kind`` picks the interaction:
             ``order_steps`` arranges plain-language steps, ``match_pairs``
             connects a concept to what it does. Neither is graded by the
             backend and neither awards XP — they teach the logic the exercise
             then asks the student to apply.

  exam_tip   one short callout about a mechanic the student can verify inside
             this very lesson. No claim is made about any official exam paper,
             because this repository has no source for such a claim.

WHY THESE TWO LESSONS
---------------------
Lesson 36, "What Is an Algorithm?" (course 5, CS Fundamentals) has exactly one
exercise, #47, a four-option multiple choice worth 10 XP with exactly one
correct option — so it grades through the ``option`` strategy, and solving it
completes the lesson. Its subject is literally "a precise sequence of steps",
which an ``order_steps`` blueprint teaches without giving the question away:
the question asks which listed item is *not* a property of an algorithm, and
the blueprint never lists the properties.

Lesson 12, "Scope and Function Design" (course 1, Python Foundations) has
exactly one exercise, #22, a prediction worth 10 XP graded by exact
``expected_output`` — deterministic, and reachable by a student who understood
the lesson. Its subject is a vocabulary of places a name can live, which is
exactly what ``match_pairs`` is for. The blueprint teaches the local/global
rule; the exercise still requires the student to apply it and write the two
lines the program prints.

WHY LESSON 38 (PHASE 10 — THE DEBUGGING REFERENCE QUEST)
----------------------------------------------------------
Three lessons in the curriculum have a ``debugging`` exercise: 6 (Conditions,
two exercises — ruled out, since a Micro-Quest ends in exactly one), 33
(Branches and Merging, a fill-in-the-command Git exercise graded by
``expected_keywords`` — not really *debugging* code, more "recall the right
syntax"), and 38, "Searching Algorithms" (course 5, CS Fundamentals). Lesson
38 has exactly one exercise, #49: a genuinely broken ``binary_search`` with a
real off-by-one bug, graded by the actual sandbox running real assertions
against real input — the richest and most natural fit for a debugging quest.

Its blueprint uses the third interaction, ``spot_the_bug`` (see
``app/seed/microquest_authoring.py`` and the frontend's
``SpotTheBugBlueprint.tsx``): four claims about how binary search behaves,
exactly one of which is false. The false one names the *general* shape of the
bug — an off-by-one search boundary — without stating the exercise's specific
fix (the exercise has two further, separate off-by-one mistakes in how
``left``/``right`` are updated that the blueprint never mentions), so solving
the blueprint still leaves real work for the sandbox-graded exercise.
"""

from .microquest_authoring import exam_tip_block, hook_block, spot_the_bug_blueprint

# --------------------------------------------------------------------------
# Lesson 36 — "What Is an Algorithm?"  (multiple_choice + order_steps)
# --------------------------------------------------------------------------
#: Lesson 36's existing blocks are at orders 1, 2 and 3, so 0, 4 and 5 are free
#: and nothing has to be renumbered — same shape as lesson 9.
ALGORITHM_BLOCKS = [
    {
        "block_type": "hook",
        "order": 0,
        "content": (
            "Ask ten students to find the tallest person in a classroom and you get ten "
            "different methods, and sometimes ten different answers. A computer cannot "
            "improvise: it needs one method, written down, that anyone would follow the "
            "same way."
        ),
        "translations": {
            "en": (
                "Ask ten students to find the tallest person in a classroom and you get ten "
                "different methods, and sometimes ten different answers. A computer cannot "
                "improvise: it needs one method, written down, that anyone would follow the "
                "same way."
            ),
            "fr": (
                "Demandez à dix élèves de trouver la personne la plus grande d'une classe et "
                "vous obtenez dix méthodes différentes, et parfois dix réponses différentes. "
                "Un ordinateur ne peut pas improviser : il lui faut une seule méthode, écrite, "
                "que n'importe qui suivrait de la même façon."
            ),
            "ar": (
                "اطلب من عشرة تلاميذ أن يجدوا أطول شخص في القسم فتحصل على عشر طرق مختلفة، "
                "وأحيانًا على عشر إجابات مختلفة. الحاسوب لا يرتجل: فهو يحتاج إلى طريقة واحدة "
                "مكتوبة، يتبعها أي شخص بالكيفية نفسها."
            ),
        },
        "config": {
            "kind": "hook",
            "challenge": {
                "en": "What has to be true of a method before a machine can follow it without ever guessing?",
                "fr": "Que doit vérifier une méthode pour qu'une machine puisse la suivre sans jamais deviner ?",
                "ar": "ما الذي يجب أن يتوفّر في طريقة ما حتى تستطيع الآلة اتّباعها دون أن تخمّن أبدًا؟",
            },
            "learn": {
                "en": "You will take an everyday method apart into the exact ordered steps a program runs — the habit behind every algorithm you will write.",
                "fr": "Vous allez décomposer une méthode du quotidien en étapes ordonnées précises, celles qu'un programme exécute — l'habitude qui sous-tend tout algorithme que vous écrirez.",
                "ar": "ستفكّك طريقة من الحياة اليومية إلى الخطوات المرتّبة الدقيقة التي ينفّذها البرنامج، وهي العادة التي تقوم عليها كل خوارزمية ستكتبها.",
            },
        },
    },
    {
        "block_type": "blueprint",
        "order": 4,
        "content": (
            "The lesson's find_max is five steps in a fixed order. Put them back in the order "
            "the program runs them."
        ),
        "translations": {
            "en": (
                "The lesson's find_max is five steps in a fixed order. Put them back in the "
                "order the program runs them."
            ),
            "fr": (
                "Le find_max de la leçon tient en cinq étapes dans un ordre fixe. Remettez-les "
                "dans l'ordre où le programme les exécute."
            ),
            "ar": (
                "دالة find_max في هذا الدرس هي خمس خطوات بترتيب ثابت. أعد ترتيبها كما ينفّذها "
                "البرنامج."
            ),
        },
        "config": {
            "kind": "order_steps",
            # Deliberately syntax-free: the student orders the *method*, not code.
            "steps": [
                {
                    "id": "input",
                    "label": {
                        "en": "Receive the list of numbers to search",
                        "fr": "Recevoir la liste de nombres à parcourir",
                        "ar": "استقبل قائمة الأعداد المراد البحث فيها",
                    },
                },
                {
                    "id": "assume",
                    "label": {
                        "en": "Take the first number as the biggest so far",
                        "fr": "Prendre le premier nombre comme le plus grand jusqu'ici",
                        "ar": "اعتبر العدد الأول هو الأكبر حتى الآن",
                    },
                },
                {
                    "id": "compare",
                    "label": {
                        "en": "Compare the next number with the biggest so far",
                        "fr": "Comparer le nombre suivant au plus grand jusqu'ici",
                        "ar": "قارن العدد التالي بالأكبر حتى الآن",
                    },
                },
                {
                    "id": "replace",
                    "label": {
                        "en": "Replace the biggest so far whenever a larger number appears",
                        "fr": "Remplacer le plus grand jusqu'ici dès qu'un nombre plus grand apparaît",
                        "ar": "استبدل الأكبر حتى الآن كلّما ظهر عدد أكبر منه",
                    },
                },
                {
                    "id": "output",
                    "label": {
                        "en": "Hand back the biggest number once the list is finished",
                        "fr": "Renvoyer le plus grand nombre une fois la liste terminée",
                        "ar": "أعِد العدد الأكبر بعد الانتهاء من القائمة",
                    },
                },
            ],
            "correct_order": ["input", "assume", "compare", "replace", "output"],
            "success": {
                "en": "Something to read, a starting guess, a comparison, an update, a result. Nothing is left to the reader's imagination — that is what separates an algorithm from a rough idea.",
                "fr": "Quelque chose à lire, une supposition de départ, une comparaison, une mise à jour, un résultat. Rien n'est laissé à l'imagination du lecteur : voilà ce qui sépare un algorithme d'une idée vague.",
                "ar": "شيء يُقرأ، وتخمين ابتدائي، ومقارنة، وتحديث، ونتيجة. لا شيء متروك لخيال القارئ، وهذا ما يفصل الخوارزمية عن الفكرة المبهمة.",
            },
            "hint": {
                "en": "Nothing can be compared until there is both a list to read and something to compare against.",
                "fr": "Rien ne peut être comparé tant qu'il n'y a pas à la fois une liste à lire et un élément de comparaison.",
                "ar": "لا يمكن إجراء أي مقارنة قبل أن تتوفّر قائمة تُقرأ وقيمة تُقارَن بها معًا.",
            },
        },
    },
    {
        "block_type": "exam_tip",
        "order": 5,
        "content": (
            "find_max starts with 'if not numbers: return None'. Delete that line and an empty "
            "list makes numbers[0] raise IndexError — the method stops being correct for one "
            "perfectly legal input. Say what your algorithm does with the empty case before you "
            "claim it works."
        ),
        "translations": {
            "en": (
                "find_max starts with 'if not numbers: return None'. Delete that line and an "
                "empty list makes numbers[0] raise IndexError — the method stops being correct "
                "for one perfectly legal input. Say what your algorithm does with the empty "
                "case before you claim it works."
            ),
            "fr": (
                "find_max commence par « if not numbers: return None ». Supprimez cette ligne "
                "et une liste vide fait lever IndexError à numbers[0] : la méthode cesse d'être "
                "correcte pour une entrée pourtant parfaitement valide. Dites ce que fait votre "
                "algorithme du cas vide avant d'affirmer qu'il fonctionne."
            ),
            "ar": (
                "تبدأ find_max بالسطر «if not numbers: return None». احذف هذا السطر فتُطلق "
                "numbers[0] الخطأ IndexError عند إعطائها قائمة فارغة، فتتوقّف الطريقة عن كونها "
                "صحيحة لمُدخل مشروع تمامًا. حدّد ما تفعله خوارزميتك في حالة القائمة الفارغة قبل "
                "أن تقول إنها تعمل."
            ),
        },
        "config": {"kind": "exam_tip"},
    },
]


# --------------------------------------------------------------------------
# Lesson 12 — "Scope and Function Design"  (prediction + match_pairs)
# --------------------------------------------------------------------------
#: Lesson 12's existing blocks are at orders 1, 2 and 3, so 0, 4 and 5 are free.
SCOPE_BLOCKS = [
    {
        "block_type": "hook",
        "order": 0,
        "content": (
            "A classmate adds a total inside a function to fix one bug, and the rest of the "
            "program keeps reading the old value. Nothing crashes and nothing is underlined in "
            "red — the numbers are simply, quietly wrong."
        ),
        "translations": {
            "en": (
                "A classmate adds a total inside a function to fix one bug, and the rest of the "
                "program keeps reading the old value. Nothing crashes and nothing is underlined "
                "in red — the numbers are simply, quietly wrong."
            ),
            "fr": (
                "Un camarade ajoute un total à l'intérieur d'une fonction pour corriger un bug, "
                "et le reste du programme continue de lire l'ancienne valeur. Rien ne plante et "
                "rien n'est souligné en rouge : les chiffres sont simplement faux, en silence."
            ),
            "ar": (
                "يضيف زميل لك متغيّر total داخل دالة لإصلاح خلل واحد، فيظل بقية البرنامج يقرأ "
                "القيمة القديمة. لا شيء يتعطّل ولا شيء يُسطَّر بالأحمر، لكن الأرقام تصبح خاطئة "
                "في صمت."
            ),
        },
        "config": {
            "kind": "hook",
            "challenge": {
                "en": "When two variables share a name, how does Python decide which one a line of code is talking about?",
                "fr": "Quand deux variables portent le même nom, comment Python décide-t-il de laquelle une ligne de code parle ?",
                "ar": "حين يحمل متغيّران الاسم نفسه، كيف تقرّر Python أيّهما يقصده سطر معيّن من الشيفرة؟",
            },
            "learn": {
                "en": "You will learn where a name lives — inside a function or outside it — so you can predict which value a line will actually read.",
                "fr": "Vous allez apprendre où vit un nom — dans une fonction ou en dehors — pour prédire quelle valeur une ligne va réellement lire.",
                "ar": "ستتعلّم أين يعيش الاسم، داخل الدالة أم خارجها، حتى تتوقّع أي قيمة سيقرأها السطر فعليًا.",
            },
        },
    },
    {
        "block_type": "blueprint",
        "order": 4,
        "content": (
            "Before predicting anything, connect each way of naming a value to where that value "
            "actually lives."
        ),
        "translations": {
            "en": (
                "Before predicting anything, connect each way of naming a value to where that "
                "value actually lives."
            ),
            "fr": (
                "Avant de prédire quoi que ce soit, reliez chaque façon de nommer une valeur à "
                "l'endroit où cette valeur vit réellement."
            ),
            "ar": (
                "قبل أن تتوقّع أي شيء، صِل كل طريقة لتسمية قيمة بالمكان الذي تعيش فيه تلك القيمة "
                "فعلًا."
            ),
        },
        "config": {
            "kind": "match_pairs",
            "pairs": [
                {
                    "id": "local",
                    "left": {
                        "en": "Local variable",
                        "fr": "Variable locale",
                        "ar": "متغيّر محلي",
                    },
                    "right": {
                        "en": "Exists only while its own function is running",
                        "fr": "N'existe que pendant l'exécution de sa propre fonction",
                        "ar": "لا يوجد إلا أثناء تنفيذ الدالة التي يخصّها",
                    },
                },
                {
                    "id": "global",
                    "left": {
                        "en": "Global variable",
                        "fr": "Variable globale",
                        "ar": "متغيّر عام",
                    },
                    "right": {
                        "en": "Created outside every function, and lasts for the whole run",
                        "fr": "Créée en dehors de toute fonction, et dure pendant toute l'exécution",
                        "ar": "يُنشَأ خارج كل الدوال، ويبقى طوال تشغيل البرنامج",
                    },
                },
                {
                    "id": "parameter",
                    "left": {
                        "en": "Parameter",
                        "fr": "Paramètre",
                        "ar": "معامِل",
                    },
                    "right": {
                        "en": "A name that receives a value at the moment of the call",
                        "fr": "Un nom qui reçoit une valeur au moment de l'appel",
                        "ar": "اسم يتلقّى قيمة في لحظة استدعاء الدالة",
                    },
                },
                {
                    "id": "return",
                    "left": {
                        "en": "Return value",
                        "fr": "Valeur de retour",
                        "ar": "القيمة المُعادة",
                    },
                    "right": {
                        "en": "The result a function hands back to whoever called it",
                        "fr": "Le résultat qu'une fonction renvoie à celui qui l'a appelée",
                        "ar": "النتيجة التي تعيدها الدالة إلى من استدعاها",
                    },
                },
            ],
            "success": {
                "en": "Assigning to a name inside a function creates a new local name; the outer one is left alone. Now use that rule to predict what the program prints.",
                "fr": "Affecter un nom à l'intérieur d'une fonction crée un nouveau nom local ; celui de l'extérieur n'est pas touché. Utilisez maintenant cette règle pour prédire ce qu'affiche le programme.",
                "ar": "الإسناد إلى اسم داخل الدالة يُنشئ اسمًا محليًا جديدًا، ويترك الاسم الخارجي كما هو. استعمل هذه القاعدة الآن لتتوقّع ما سيطبعه البرنامج.",
            },
            "hint": {
                "en": "Ask where the name was created, not where it is being used.",
                "fr": "Demandez-vous où le nom a été créé, pas où il est utilisé.",
                "ar": "اسأل أين أُنشئ الاسم، لا أين يُستعمل.",
            },
        },
    },
    {
        "block_type": "exam_tip",
        "order": 5,
        "content": (
            "Reading a global inside a function works; assigning to it does not — the "
            "assignment quietly creates a local instead. Python only lets you change the outer "
            "name after you write 'global x', and needing that is usually a sign the value "
            "should have been a parameter or a return value."
        ),
        "translations": {
            "en": (
                "Reading a global inside a function works; assigning to it does not — the "
                "assignment quietly creates a local instead. Python only lets you change the "
                "outer name after you write 'global x', and needing that is usually a sign the "
                "value should have been a parameter or a return value."
            ),
            "fr": (
                "Lire une variable globale dans une fonction fonctionne ; lui affecter une "
                "valeur non — l'affectation crée discrètement une variable locale à la place. "
                "Python ne vous laisse modifier le nom extérieur qu'après avoir écrit « global "
                "x », et en avoir besoin est généralement le signe que la valeur aurait dû être "
                "un paramètre ou une valeur de retour."
            ),
            "ar": (
                "قراءة متغيّر عام داخل دالة تعمل، أما الإسناد إليه فلا: إذ يُنشئ الإسناد متغيّرًا "
                "محليًا في صمت. ولا تسمح لك Python بتغيير الاسم الخارجي إلا بعد كتابة «global x»، "
                "والحاجة إلى ذلك عادةً دليل على أن القيمة كان ينبغي أن تكون معامِلًا أو قيمة "
                "مُعادة."
            ),
        },
        "config": {"kind": "exam_tip"},
    },
]


# --------------------------------------------------------------------------
# Lesson 38 — "Searching Algorithms"  (debugging + spot_the_bug)
# --------------------------------------------------------------------------
# Authored with the microquest_authoring builders (Phase 10's authoring
# improvement) instead of the raw block dicts above: the English text is
# written once, as part of each localized dict, and `content` is derived from
# it rather than typed a second time.
#: Lesson 38's existing blocks are at orders 1, 2 and 3, so 0, 4 and 5 are free.
DEBUGGING_BLOCKS = [
    hook_block(
        order=0,
        prose={
            "en": (
                "A phone book with 2,000 names, sorted alphabetically. Flipping through "
                "it one page at a time to find one name would take forever — you jump to "
                "the middle, then decide which half to keep searching. Get that boundary "
                "wrong by a single position and the search misses the very last name in "
                "the book, or never stops."
            ),
            "fr": (
                "Un annuaire de 2 000 noms, trié par ordre alphabétique. Le feuilleter page "
                "par page pour trouver un nom prendrait une éternité — on saute au milieu, "
                "puis on décide dans quelle moitié continuer à chercher. Si cette limite est "
                "décalée d'une seule position, la recherche rate le tout dernier nom de "
                "l'annuaire, ou ne s'arrête jamais."
            ),
            "ar": (
                "دفتر هاتف يحتوي على 2000 اسم، مرتّب أبجديًا. تصفّحه صفحة بصفحة للعثور على "
                "اسم واحد سيستغرق وقتًا طويلاً جدًا — لذا تقفز إلى المنتصف، ثم تقرر في أي "
                "نصف تواصل البحث. إذا كانت هذه الحدود مُزاحة بموضع واحد فقط، يفوت البحث آخر "
                "اسم في الدفتر، أو لا يتوقف أبدًا."
            ),
        },
        challenge={
            "en": "What exact rule decides which half to search next, and exactly where the search space ends?",
            "fr": "Quelle règle précise décide de la moitié à explorer ensuite, et où s'arrête exactement l'espace de recherche ?",
            "ar": "ما القاعدة الدقيقة التي تحدد أي نصف يُبحث فيه لاحقًا، وأين تنتهي مساحة البحث بالضبط؟",
        },
        learn={
            "en": (
                "You will pin down the exact boundaries binary search depends on — the "
                "difference between including and excluding the middle element decides "
                "whether the algorithm is correct or subtly broken."
            ),
            "fr": (
                "Vous allez déterminer précisément les limites dont dépend la recherche "
                "binaire — la différence entre inclure et exclure l'élément du milieu "
                "décide si l'algorithme est correct ou subtilement cassé."
            ),
            "ar": (
                "ستحدد بدقة الحدود التي يعتمد عليها البحث الثنائي — فالفرق بين تضمين "
                "واستبعاد العنصر الأوسط يقرر ما إذا كانت الخوارزمية صحيحة أم معطوبة بشكل "
                "خفي."
            ),
        },
    ),
    spot_the_bug_blueprint(
        order=4,
        prose={
            "en": "Read these claims about the binary search above. Exactly one of them is wrong.",
            "fr": "Lisez ces affirmations sur la recherche binaire ci-dessus. Une seule d'entre elles est fausse.",
            "ar": "اقرأ هذه العبارات حول البحث الثنائي أعلاه. واحدة منها فقط خاطئة.",
        },
        # The lesson's own reading block (order 2) already shows this exact,
        # correct snippet — repeating it here reveals nothing new about the
        # exercise's separate, buggy version.
        snippet="left, right = 0, len(arr) - 1\nwhile left <= right:\n    mid = (left + right) // 2",
        statements=[
            (
                "sorted",
                {
                    "en": "Binary search requires the array to already be sorted.",
                    "fr": "La recherche binaire exige que le tableau soit déjà trié.",
                    "ar": "يتطلب البحث الثنائي أن تكون المصفوفة مرتّبة مسبقًا.",
                },
            ),
            (
                "halves",
                {
                    "en": "Each comparison discards half of the remaining search space.",
                    "fr": "Chaque comparaison élimine la moitié de l'espace de recherche restant.",
                    "ar": "كل مقارنة تستبعد نصف مساحة البحث المتبقية.",
                },
            ),
            (
                "bound",
                {
                    "en": "The initial right boundary should be len(arr), the length of the array.",
                    "fr": "La limite droite initiale doit être len(arr), la longueur du tableau.",
                    "ar": "يجب أن يكون الحد الأيمن الابتدائي هو len(arr)، أي طول المصفوفة.",
                },
            ),
            (
                "logn",
                {
                    "en": "Binary search runs in O(log n) time.",
                    "fr": "La recherche binaire s'exécute en temps O(log n).",
                    "ar": "يعمل البحث الثنائي في زمن O(log n).",
                },
            ),
        ],
        buggy_id="bound",
        success={
            "en": (
                "Exactly — the initial right boundary has to be the last valid index, "
                "len(arr) - 1, not len(arr) itself. Off-by-one boundaries like this are the "
                "most common way a correct-looking search silently breaks."
            ),
            "fr": (
                "Exactement — la limite droite initiale doit être le dernier index valide, "
                "len(arr) - 1, et non len(arr) lui-même. Ce genre de décalage d'un cran est "
                "la façon la plus courante dont une recherche qui semble correcte se casse "
                "en silence."
            ),
            "ar": (
                "بالضبط — يجب أن يكون الحد الأيمن الابتدائي هو آخر فهرس صالح، len(arr) - 1، "
                "وليس len(arr) نفسه. أخطاء الإزاحة بمقدار واحد كهذه هي الطريقة الأكثر شيوعًا "
                "التي ينكسر بها بحث يبدو صحيحًا في صمت."
            ),
        },
        hint={
            "en": "Which one describes an index that is one position past the last real element?",
            "fr": "Laquelle décrit un index qui se trouve une position après le dernier élément réel ?",
            "ar": "أيّها يصف فهرسًا يقع بموضع واحد بعد آخر عنصر حقيقي؟",
        },
    ),
    exam_tip_block(
        order=5,
        prose={
            "en": (
                "'(left + right) // 2' uses integer floor division, so it always rounds "
                "down: for left=2, right=3, mid is 2, not 2.5. That rounding is why left "
                "must move to mid + 1 and right must move to mid - 1 — moving either one to "
                "mid instead would search the same middle position forever."
            ),
            "fr": (
                "« (left + right) // 2 » utilise la division entière, donc arrondit toujours "
                "vers le bas : pour left=2, right=3, mid vaut 2, pas 2,5. C'est cet arrondi "
                "qui impose que left passe à mid + 1 et right à mid - 1 — déplacer l'un des "
                "deux vers mid reviendrait à examiner indéfiniment la même position centrale."
            ),
            "ar": (
                "تستخدم «(left + right) // 2» القسمة الصحيحة، فتُقرّب دائمًا لأسفل: عندما "
                "left=2 وright=3، تكون mid تساوي 2 لا 2.5. هذا التقريب هو سبب وجوب انتقال "
                "left إلى mid + 1 وright إلى mid - 1 — فنقل أيّهما إلى mid فقط يجعل البحث "
                "يفحص الموضع الأوسط نفسه إلى الأبد."
            ),
        },
    ),
]


from .microquest_content_phase11 import MICROQUEST_BY_SLUG_PHASE11  # noqa: E402

#: Every Micro-Quest this module owns, keyed by the lesson slug it belongs to.
#: The migration and the audit script both walk this, so a new reference lesson
#: is one entry here plus one call in its seed function. Phase 11's ten lessons
#: live in their own sibling module (microquest_content_phase11.py) to keep
#: this file from growing without bound; they are merged into this single
#: registry so every consumer keeps reading from one place.
MICROQUEST_BY_SLUG = {
    "what-is-algorithm": ALGORITHM_BLOCKS,
    "scope-and-function-design": SCOPE_BLOCKS,
    "searching-algorithms": DEBUGGING_BLOCKS,
    **MICROQUEST_BY_SLUG_PHASE11,
}


def seed_blocks(slug: str) -> list[dict]:
    """The blocks for one Micro-Quest, in the shape ``get_or_create_lesson`` wants.

    The seed helper takes ``type``/``config``-as-JSON-text and LanguageEnum
    keys; this module stores plain data so the migration and the audit can read
    it without importing the ORM. Converting here keeps that single source.
    """
    import json

    from app.models import LanguageEnum

    return [
        {
            "type": block["block_type"],
            "order": block["order"],
            "content": block["content"],
            "config": json.dumps(block["config"], ensure_ascii=False),
            "translations": [
                {"language": LanguageEnum(language), "content": text}
                for language, text in block["translations"].items()
            ],
        }
        for block in MICROQUEST_BY_SLUG[slug]
    ]
