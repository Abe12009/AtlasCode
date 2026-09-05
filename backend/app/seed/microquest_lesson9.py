# -*- coding: utf-8 -*-
"""Micro-Quest content for lesson 9, "Problem Solving with Control Flow".

The Micro-Quest adds three block types on top of the existing "text" and
"code" blocks:

  hook       a short real-world scenario, the challenge it raises, and what the
             student will learn. Prose lives in the translation rows like any
             other block; the challenge and "what you'll learn" lines live in
             ``config`` with their own per-language values.

  blueprint  an interactive step-ordering puzzle. ``config`` carries the steps
             (each with per-language labels) and the correct order. The student
             arranges the pattern before writing a single line of syntax.

  exam_tip   one short, optional callout. It is deliberately about Python
             mechanics the student can verify in this very lesson -- no claim
             is made about what appears on any official exam, because this
             repository has no source for such a claim.

``config`` holds per-language labels inline because those are structured data,
not prose; the block's main paragraph still goes through
lesson_block_translations so the existing translation-coverage checks apply.
"""

#: Order 0 is free on lesson 9 (its existing blocks are 1, 2, 3), so the hook
#: slots in front without renumbering or touching a single existing row.
MICROQUEST_BLOCKS = [
    {
        "block_type": "hook",
        "order": 0,
        "content": (
            "A school needs the total of every even-numbered locker in a corridor. "
            "Counting them one by one works, but it is slow and easy to get wrong."
        ),
        "translations": {
            "en": (
                "A school needs the total of every even-numbered locker in a corridor. "
                "Counting them one by one works, but it is slow and easy to get wrong."
            ),
            "fr": (
                "Une école a besoin du total de tous les casiers portant un numéro pair "
                "dans un couloir. Les compter un par un fonctionne, mais c'est lent et on "
                "se trompe facilement."
            ),
            "ar": (
                "تحتاج مدرسة إلى مجموع أرقام كل الخزانات ذات الأرقام الزوجية في ممرّ واحد. "
                "عدّها واحدة تلو الأخرى ممكن، لكنه بطيء ويسهل الوقوع فيه في الخطأ."
            ),
        },
        "config": {
            "kind": "hook",
            "challenge": {
                "en": "How can a program look at every number, keep only the ones it wants, and add them up on its own?",
                "fr": "Comment un programme peut-il parcourir chaque nombre, ne garder que ceux qui l'intéressent et les additionner tout seul ?",
                "ar": "كيف يمكن لبرنامج أن يمرّ على كل عدد، ويحتفظ بما يهمّه منها فقط، ثم يجمعها من تلقاء نفسه؟",
            },
            "learn": {
                "en": "You will combine a loop with a condition to build a running total — the pattern behind counting, summing and finding a maximum.",
                "fr": "Vous allez combiner une boucle et une condition pour construire un total cumulé — le schéma qui sert à compter, additionner et trouver un maximum.",
                "ar": "ستجمع بين حلقة وشرط لبناء مجموع تراكمي، وهو النمط نفسه المستخدم في العدّ والجمع وإيجاد القيمة العظمى.",
            },
        },
    },
    {
        "block_type": "blueprint",
        "order": 4,
        "content": (
            "Before writing any code, put the four steps of the pattern in the order a "
            "program would run them."
        ),
        "translations": {
            "en": (
                "Before writing any code, put the four steps of the pattern in the order a "
                "program would run them."
            ),
            "fr": (
                "Avant d'écrire la moindre ligne de code, remettez les quatre étapes du "
                "schéma dans l'ordre où un programme les exécuterait."
            ),
            "ar": (
                "قبل كتابة أي شيفرة، رتّب خطوات النمط الأربع بالترتيب الذي ينفّذها به البرنامج."
            ),
        },
        "config": {
            "kind": "order_steps",
            # Deliberately syntax-free: the student orders the *idea*, not code.
            "steps": [
                {
                    "id": "init",
                    "label": {
                        "en": "Start a total at zero",
                        "fr": "Démarrer un total à zéro",
                        "ar": "ابدأ بمجموع قيمته صفر",
                    },
                },
                {
                    "id": "visit",
                    "label": {
                        "en": "Look at the next number in the range",
                        "fr": "Passer au nombre suivant de l'intervalle",
                        "ar": "انتقل إلى العدد التالي في المجال",
                    },
                },
                {
                    "id": "decide",
                    "label": {
                        "en": "Ask: is this number even?",
                        "fr": "Se demander : ce nombre est-il pair ?",
                        "ar": "اسأل: هل هذا العدد زوجي؟",
                    },
                },
                {
                    "id": "update",
                    "label": {
                        "en": "If it is, add it to the total",
                        "fr": "Si oui, l'ajouter au total",
                        "ar": "إذا كان كذلك، أضفه إلى المجموع",
                    },
                },
            ],
            "correct_order": ["init", "visit", "decide", "update"],
            "success": {
                "en": "That is the pattern: initialise, visit, decide, update. Now write it in Python.",
                "fr": "Voilà le schéma : initialiser, parcourir, décider, mettre à jour. À vous de l'écrire en Python.",
                "ar": "هذا هو النمط: التهيئة، ثم المرور، ثم القرار، ثم التحديث. والآن اكتبه بلغة Python.",
            },
            "hint": {
                "en": "The total has to exist before the loop can add anything to it.",
                "fr": "Le total doit exister avant que la boucle puisse y ajouter quoi que ce soit.",
                "ar": "يجب أن يوجد المجموع قبل أن تتمكّن الحلقة من إضافة أي شيء إليه.",
            },
        },
    },
    {
        "block_type": "exam_tip",
        "order": 5,
        "content": (
            "Everything indented under a for or if line belongs to it. Put the line that "
            "adds to your total one level too far left and it runs after the loop instead "
            "of inside it — the total will be wrong, with no error message."
        ),
        "translations": {
            "en": (
                "Everything indented under a for or if line belongs to it. Put the line that "
                "adds to your total one level too far left and it runs after the loop instead "
                "of inside it — the total will be wrong, with no error message."
            ),
            "fr": (
                "Tout ce qui est indenté sous une ligne for ou if lui appartient. Placez la "
                "ligne qui ajoute au total un niveau trop à gauche et elle s'exécutera après "
                "la boucle au lieu d'être dedans : le total sera faux, sans aucun message "
                "d'erreur."
            ),
            "ar": (
                "كل ما يُزاح إلى الداخل تحت سطر for أو if ينتمي إليه. وإذا وضعت السطر الذي "
                "يضيف إلى المجموع مستوى واحدًا أبعد إلى اليسار، فسيُنفَّذ بعد الحلقة بدل أن "
                "يكون داخلها، فيخرج المجموع خاطئًا دون أي رسالة خطأ."
            ),
        },
        "config": {"kind": "exam_tip"},
    },
]
