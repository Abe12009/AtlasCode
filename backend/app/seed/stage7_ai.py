"""Stage 7 — Artificial Intelligence.

Three courses. *Introduction to Artificial Intelligence* explains what the
field is and how the pieces relate. *Machine Learning Fundamentals* covers the
actual method — data, training, evaluation, and the ways evaluation lies.
*AI Literacy* is about working with these systems honestly: verifying output,
recognising hallucination, and using AI to learn faster without learning less.
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

AI_FOUNDATIONS = CourseSpec(
    slug="ai-foundations",
    stage=7,
    track="ai",
    icon="🤖",
    difficulty=D.intermediate,
    estimated_hours=8,
    prerequisite_slug="math-for-cs",
    title=T("Introduction to Artificial Intelligence", "Introduction à l'Intelligence Artificielle", "مقدّمة في الذكاء الاصطناعي"),
    description=T(
        "What AI actually is, how it got here, how machine learning and neural networks fit inside it, and what generative models really do.",
        "Ce qu'est réellement l'IA, comment elle en est arrivée là, comment l'apprentissage automatique et les réseaux de neurones s'y inscrivent, et ce que font vraiment les modèles génératifs.",
        "ما هو الذكاء الاصطناعي فعلًا، وكيف وصل إلى هنا، وأين يقع تعلّم الآلة والشبكات العصبية منه، وما الذي تفعله النماذج التوليدية حقًّا.",
    ),
    skills=T(
        "AI history, search and rules, machine learning, neural networks, generative models, limitations",
        "Histoire de l'IA, recherche et règles, apprentissage automatique, réseaux de neurones, modèles génératifs, limites",
        "تاريخ الذكاء الاصطناعي، البحث والقواعد، تعلّم الآلة، الشبكات العصبية، النماذج التوليدية، الحدود",
    ),
    modules=[
        Module(
            slug="what-ai-is",
            title=T("What AI Is", "Ce Qu'est l'IA", "ما هو الذكاء الاصطناعي"),
            description=T(
                "The field, its two eras, and where the current systems come from.",
                "Le domaine, ses deux époques, et d'où viennent les systèmes actuels.",
                "المجال وعصراه ومن أين أتت الأنظمة الحالية.",
            ),
            lessons=[
                Lesson(
                    slug="ai-ml-and-deep-learning",
                    minutes=35,
                    xp=60,
                    difficulty=D.intermediate,
                    title=T("AI, Machine Learning and Deep Learning", "IA, Apprentissage Automatique et Apprentissage Profond", "الذكاء الاصطناعي وتعلّم الآلة والتعلّم العميق"),
                    story=T(
                        "Three words used interchangeably in headlines. They are three nested circles, and knowing which is which is half the subject.",
                        "Trois mots employés indifféremment dans les titres. Ce sont trois cercles emboîtés, et savoir lequel est lequel, c'est la moitié du sujet.",
                        "ثلاث كلمات تُستخدم بالتبادل في العناوين. وهي ثلاث دوائر متداخلة، ومعرفة أيّها أيّ هي نصف الموضوع.",
                    ),
                    objective=T(
                        "Place AI, machine learning and deep learning correctly, and tell a rule-based system from a learned one.",
                        "Situer correctement IA, apprentissage automatique et apprentissage profond, et distinguer un système à règles d'un système appris.",
                        "وضع الذكاء الاصطناعي وتعلّم الآلة والتعلّم العميق في مواضعها، والتمييز بين نظام قواعد ونظام متعلّم.",
                    ),
                    skills=T(
                        "AI vs ML vs deep learning, symbolic AI, learned models, narrow AI",
                        "IA vs AA vs apprentissage profond, IA symbolique, modèles appris, IA étroite",
                        "الذكاء الاصطناعي مقابل تعلّم الآلة والتعلّم العميق، الذكاء الرمزي، النماذج المتعلّمة، الذكاء الضيّق",
                    ),
                    blocks=[
                        Text(
                            T(
                                "**Artificial intelligence** is the whole field: making machines do things that seem to require intelligence. **Machine learning** is one approach within it — instead of writing the rules, you show the system examples and it derives the rules. **Deep learning** is one family of machine learning, using neural networks with many layers. Each is contained in the one before it.",
                                "L'**intelligence artificielle** est le domaine entier : faire faire aux machines ce qui semble exiger de l'intelligence. L'**apprentissage automatique** en est une approche — au lieu d'écrire les règles, on montre des exemples et le système les dérive. L'**apprentissage profond** est une famille de l'apprentissage automatique, à base de réseaux de neurones à nombreuses couches. Chacun est contenu dans le précédent.",
                                "**الذكاء الاصطناعي** هو المجال كلّه: جعل الآلات تفعل ما يبدو أنّه يتطلّب ذكاءً. و**تعلّم الآلة** أحد مناهجه — فبدل كتابة القواعد تعرض على النظام أمثلة فيستنبطها. و**التعلّم العميق** عائلة من تعلّم الآلة تستخدم شبكات عصبية متعدّدة الطبقات. وكلّ واحد منها داخل الذي قبله.",
                            )
                        ),
                        Code(
                            T(
                                "The same task, solved the two different ways:",
                                "La même tâche, résolue de deux façons différentes :",
                                "المهمّة نفسها محلولة بطريقتين مختلفتين:",
                            ),
                            "# Rule-based: a human writes the logic. Transparent, and it only\n"
                            "# knows exactly what it was told.\n"
                            "def is_spam_rules(subject):\n"
                            "    triggers = ['free money', 'you have won', 'click here now']\n"
                            "    return any(t in subject.lower() for t in triggers)\n\n"
                            "# Learned: a human supplies labelled examples; the model derives\n"
                            "# the pattern, including ones nobody thought to write down --\n"
                            "# and including ones nobody intended it to learn.\n"
                            "examples = [\n"
                            "    ('you have won a free prize', 'spam'),\n"
                            "    ('lesson 4 feedback', 'not spam'),\n"
                            "]\n\n"
                            "print(is_spam_rules('FREE MONEY waiting'))",
                        ),
                        Text(
                            T(
                                "Rules are predictable and auditable but cannot cover a world they were not told about. Learned models generalise to cases nobody wrote down — and, for the same reason, can be confidently wrong in ways nobody predicted. Every system in production today is **narrow**: extremely capable inside one task, with no understanding outside it.",
                                "Les règles sont prévisibles et auditables mais ne couvrent pas un monde qu'on ne leur a pas décrit. Les modèles appris généralisent à des cas jamais écrits — et, pour la même raison, se trompent avec assurance de façons imprévues. Tout système en production aujourd'hui est **étroit** : très capable dans une tâche, sans compréhension au-delà.",
                                "القواعد متوقَّعة وقابلة للتدقيق لكنّها لا تغطّي عالمًا لم يُخبَر عنه. أمّا النماذج المتعلّمة فتعمّم على حالات لم يكتبها أحد — وللسبب نفسه قد تخطئ بثقة بطرق لم يتوقّعها أحد. وكلّ نظام يعمل اليوم **ضيّق**: بالغ القدرة داخل مهمّة واحدة، بلا فهم خارجها.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "Which statement is correct?",
                                "Quel énoncé est correct ?",
                                "أيّ عبارة صحيحة؟",
                            ),
                            hint=T("Think of three nested circles.", "Pensez à trois cercles emboîtés.", "فكّر في ثلاث دوائر متداخلة."),
                            explanation=T(
                                "Deep learning is a subset of machine learning, which is a subset of AI.",
                                "L'apprentissage profond est un sous-ensemble de l'apprentissage automatique, lui-même sous-ensemble de l'IA.",
                                "التعلّم العميق جزء من تعلّم الآلة، وتعلّم الآلة جزء من الذكاء الاصطناعي.",
                            ),
                            options=[
                                Option(T("AI is a kind of machine learning", "L'IA est une sorte d'apprentissage automatique", "الذكاء الاصطناعي نوع من تعلّم الآلة")),
                                Option(
                                    T(
                                        "Deep learning ⊂ machine learning ⊂ artificial intelligence",
                                        "Apprentissage profond ⊂ apprentissage automatique ⊂ IA",
                                        "التعلّم العميق ⊂ تعلّم الآلة ⊂ الذكاء الاصطناعي",
                                    ),
                                    correct=True,
                                ),
                                Option(T("They are three names for the same thing", "Ce sont trois noms pour la même chose", "ثلاثة أسماء للشيء نفسه")),
                                Option(T("Machine learning ⊂ deep learning", "Apprentissage automatique ⊂ apprentissage profond", "تعلّم الآلة ⊂ التعلّم العميق")),
                            ],
                        ),
                        MCQ(
                            prompt=T(
                                "A hospital needs to explain to a regulator exactly why each decision was made. Which approach fits better?",
                                "Un hôpital doit expliquer à un régulateur exactement pourquoi chaque décision a été prise. Quelle approche convient mieux ?",
                                "مستشفى عليه أن يشرح لجهة تنظيمية سبب كلّ قرار بالضبط. أيّ منهج أنسب؟",
                            ),
                            hint=T("Which one can you read line by line?", "Lequel peut-on lire ligne par ligne ?", "أيّهما يمكنك قراءته سطرًا سطرًا؟"),
                            explanation=T(
                                "Explicit rules are auditable: each decision traces to a written condition. A large learned model gives an answer without a readable justification.",
                                "Des règles explicites sont auditables : chaque décision remonte à une condition écrite. Un grand modèle appris fournit une réponse sans justification lisible.",
                                "القواعد الصريحة قابلة للتدقيق: فكلّ قرار يعود إلى شرط مكتوب. أمّا النموذج المتعلّم الكبير فيعطي إجابة بلا تبرير مقروء.",
                            ),
                            options=[
                                Option(T("A rule-based system", "Un système à base de règles", "نظام قائم على القواعد"), correct=True),
                                Option(T("A deep neural network", "Un réseau de neurones profond", "شبكة عصبية عميقة")),
                                Option(T("A generative language model", "Un modèle de langage génératif", "نموذج لغوي توليدي")),
                                Option(T("Any of them, they are equivalent", "N'importe lequel, ils sont équivalents", "أيّها كان، فهي متكافئة")),
                            ],
                        ),
                    ],
                ),
                Lesson(
                    slug="neural-networks-and-generative-ai",
                    minutes=40,
                    xp=65,
                    difficulty=D.advanced,
                    title=T("Neural Networks and Generative AI", "Réseaux de Neurones et IA Générative", "الشبكات العصبية والذكاء التوليدي"),
                    story=T(
                        "A language model is not looking anything up. Understanding what it is doing instead explains almost all of its behaviour.",
                        "Un modèle de langage ne consulte rien. Comprendre ce qu'il fait à la place explique presque tout son comportement.",
                        "النموذج اللغوي لا يبحث عن شيء. وفهم ما يفعله بدل ذلك يفسّر جلّ سلوكه.",
                    ),
                    objective=T(
                        "Describe how a network learns from error, and explain why a generative model can be fluent and wrong.",
                        "Décrire comment un réseau apprend de l'erreur, et expliquer pourquoi un modèle génératif peut être fluide et faux.",
                        "وصف كيف تتعلّم الشبكة من الخطأ، وشرح لماذا قد يكون النموذج التوليدي فصيحًا وخاطئًا.",
                    ),
                    skills=T(
                        "Neurons, weights, layers, loss, training, tokens, next-token prediction, hallucination",
                        "Neurones, poids, couches, perte, entraînement, tokens, prédiction du token suivant, hallucination",
                        "العصبونات، الأوزان، الطبقات، الخسارة، التدريب، الرموز، تنبّؤ الرمز التالي، الهلوسة",
                    ),
                    blocks=[
                        Text(
                            T(
                                "A neural network is layers of very simple units. Each unit multiplies its inputs by **weights**, adds them up, and passes the result through a non-linear function. Training compares the output to the right answer, measures the gap with a **loss function**, and nudges every weight slightly in the direction that reduces it. Repeat a few million times.",
                                "Un réseau de neurones est un empilement d'unités très simples. Chaque unité multiplie ses entrées par des **poids**, les additionne et passe le résultat dans une fonction non linéaire. L'entraînement compare la sortie à la bonne réponse, mesure l'écart par une **fonction de perte**, et ajuste légèrement chaque poids dans le sens qui la réduit. Répétez quelques millions de fois.",
                                "الشبكة العصبية طبقات من وحدات بالغة البساطة. تضرب كلّ وحدة مدخلاتها بـ**أوزان** ثمّ تجمعها ثمّ تمرّر الناتج عبر دالّة غير خطّية. والتدريب يقارن المخرج بالإجابة الصحيحة ويقيس الفجوة بـ**دالّة خسارة** ويحرّك كلّ وزن قليلًا في اتّجاه تقليلها. ثمّ يكرّر ذلك ملايين المرّات.",
                            )
                        ),
                        Text(
                            T(
                                "A **large language model** is trained on one task: given some text, predict the next **token**. Everything else — answering, translating, writing code — is that one ability applied at scale. It has no database of facts to consult; it produces the continuation that its training makes most likely.",
                                "Un **grand modèle de langage** est entraîné à une seule tâche : prédire le **token** suivant. Tout le reste — répondre, traduire, écrire du code — est cette capacité appliquée à grande échelle. Il n'a aucune base de faits à consulter ; il produit la suite que son entraînement rend la plus probable.",
                                "**النموذج اللغوي الكبير** مدرَّب على مهمّة واحدة: بالنظر إلى نصّ، تنبّأ بـ**الرمز** التالي. وكلّ ما عدا ذلك — الإجابة والترجمة وكتابة الكود — هو تلك القدرة نفسها مطبَّقة على نطاق واسع. وليس لديه قاعدة حقائق يرجع إليها؛ بل ينتج التتمّة التي يجعلها تدريبه الأرجح.",
                            )
                        ),
                        Code(
                            T(
                                "Which is exactly why a wrong answer looks like a right one:",
                                "C'est précisément pourquoi une mauvaise réponse ressemble à une bonne :",
                                "ولهذا بالضبط تبدو الإجابة الخاطئة كالصحيحة:",
                            ),
                            "# Ask a model for a citation and it may produce:\n"
                            "#   'Benali, A. (2019). Adaptive Curriculum Sequencing.\n"
                            "#    Journal of Educational Computing, 41(3), 210-228.'\n"
                            "#\n"
                            "# Plausible author, plausible journal, plausible page range --\n"
                            "# and possibly no such paper. The model was never checking\n"
                            "# whether it exists; it was producing text shaped like a\n"
                            "# citation, because that is the task it was trained on.\n"
                            "#\n"
                            "# This failure is called HALLUCINATION. It is not a bug that\n"
                            "# will be patched out; it follows from how the system works,\n"
                            "# which is why anything checkable must be checked.",
                        ),
                        ExamTip(
                            T(
                                "Fluency is not evidence. A confident, well-formatted answer and a correct answer are produced by exactly the same process, so confidence carries no information about correctness.",
                                "La fluidité n'est pas une preuve. Une réponse assurée et bien mise en forme et une réponse correcte sortent du même processus : l'assurance ne dit rien de l'exactitude.",
                                "الفصاحة ليست دليلًا. فالإجابة الواثقة حسنة التنسيق والإجابة الصحيحة تخرجان من العملية نفسها، فلا تحمل الثقة أيّ معلومة عن الصحّة.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "What is a large language model directly trained to do?",
                                "Qu'un grand modèle de langage est-il directement entraîné à faire ?",
                                "ما الذي دُرِّب عليه النموذج اللغوي الكبير مباشرةً؟",
                            ),
                            hint=T("It is a single, surprisingly simple objective.", "C'est un objectif unique et étonnamment simple.", "إنّه هدف واحد بسيط على نحو مفاجئ."),
                            explanation=T(
                                "The training objective is next-token prediction. Every apparent capability is that objective generalised.",
                                "L'objectif d'entraînement est la prédiction du token suivant. Toute capacité apparente en découle.",
                                "هدف التدريب هو تنبّؤ الرمز التالي. وكلّ قدرة ظاهرة هي تعميم لذلك الهدف.",
                            ),
                            options=[
                                Option(T("Look answers up in a database of facts", "Chercher les réponses dans une base de faits", "البحث عن الإجابات في قاعدة حقائق")),
                                Option(T("Predict the next token of text", "Prédire le token suivant du texte", "التنبّؤ بالرمز التالي من النصّ"), correct=True),
                                Option(T("Verify statements against the internet", "Vérifier les affirmations sur Internet", "التحقّق من العبارات عبر الإنترنت")),
                                Option(T("Run the code it writes to check it", "Exécuter le code qu'il écrit pour le vérifier", "تنفيذ الكود الذي يكتبه للتحقّق منه")),
                            ],
                        ),
                        ShortAnswer(
                            prompt=T(
                                "Explain in one sentence why a language model can produce a convincing but non-existent citation.",
                                "Expliquez en une phrase pourquoi un modèle de langage peut produire une citation convaincante mais inexistante.",
                                "اشرح بجملة لماذا قد ينتج نموذج لغوي استشهادًا مقنعًا لكنّه غير موجود.",
                            ),
                            hint=T(
                                "What is it optimising for — plausibility, or truth?",
                                "Qu'optimise-t-il — la plausibilité ou la vérité ?",
                                "ما الذي يُحسّنه — المعقولية أم الحقيقة؟",
                            ),
                            explanation=T(
                                "It generates the most likely continuation given its training, which optimises for text that looks like a citation rather than for a citation that exists.",
                                "Il génère la suite la plus probable selon son entraînement, ce qui optimise un texte ressemblant à une citation, non une citation existante.",
                                "إنّه يولّد أرجح تتمّة وفق تدريبه، فيُحسّن نصًّا يشبه الاستشهاد لا استشهادًا موجودًا.",
                            ),
                            keywords=[
                                ["predict", "likely", "probable", "plausible", "prédit", "probable", "يتنبّأ", "أرجح", "محتمل"],
                                ["not check", "does not verify", "without verifying", "no database", "ne vérifie", "pas de base", "لا يتحقّق", "لا قاعدة"],
                            ],
                            reference_answer="Because it predicts the most likely next tokens rather than checking any source, so it produces text shaped like a real citation without verifying that the paper exists.",
                        ),
                    ],
                ),
            ],
        ),
    ],
)


MACHINE_LEARNING = CourseSpec(
    slug="machine-learning-fundamentals",
    stage=7,
    track="ai",
    icon="📊",
    difficulty=D.advanced,
    estimated_hours=12,
    prerequisite_slug="ai-foundations",
    title=T("Machine Learning Fundamentals", "Fondamentaux de l'Apprentissage Automatique", "أساسيات تعلّم الآلة"),
    description=T(
        "The actual method: datasets, features and labels, the train/validation/test split, overfitting, and evaluating a model honestly.",
        "La méthode réelle : jeux de données, caractéristiques et étiquettes, découpage entraînement/validation/test, surapprentissage, et évaluation honnête d'un modèle.",
        "المنهج الفعلي: مجموعات البيانات، والسمات والتسميات، وتقسيم التدريب والتحقّق والاختبار، والإفراط في التوفيق، وتقييم النموذج بأمانة.",
    ),
    skills=T(
        "Datasets, features, labels, supervised learning, train/test split, overfitting, precision and recall, bias",
        "Jeux de données, caractéristiques, étiquettes, apprentissage supervisé, découpage, surapprentissage, précision et rappel, biais",
        "مجموعات البيانات، السمات، التسميات، التعلّم المُشرَف، التقسيم، الإفراط في التوفيق، الدقّة والاستدعاء، التحيّز",
    ),
    modules=[
        Module(
            slug="data-and-training",
            title=T("Data and Training", "Données et Entraînement", "البيانات والتدريب"),
            description=T(
                "What a model learns from, and how the learning is organised.",
                "Ce dont un modèle apprend, et comment l'apprentissage est organisé.",
                "ممّ يتعلّم النموذج، وكيف يُنظَّم التعلّم.",
            ),
            lessons=[
                Lesson(
                    slug="features-labels-and-splits",
                    minutes=35,
                    xp=65,
                    difficulty=D.intermediate,
                    title=T("Features, Labels and Data Splits", "Caractéristiques, Étiquettes et Découpage des Données", "السمات والتسميات وتقسيم البيانات"),
                    story=T(
                        "A model that scores 100% on the data it was trained on has told you nothing at all.",
                        "Un modèle à 100 % sur ses données d'entraînement ne vous a rien appris.",
                        "نموذج يحرز 100% على البيانات التي تدرّب عليها لم يخبرك بشيء إطلاقًا.",
                    ),
                    objective=T(
                        "Split data into training, validation and test sets, and say what each one is for.",
                        "Découper les données en entraînement, validation et test, et dire à quoi sert chacun.",
                        "تقسيم البيانات إلى تدريب وتحقّق واختبار، وتحديد الغرض من كلّ منها.",
                    ),
                    skills=T(
                        "Features, labels, supervised learning, train/validation/test, leakage",
                        "Caractéristiques, étiquettes, apprentissage supervisé, entraînement/validation/test, fuite de données",
                        "السمات، التسميات، التعلّم المُشرَف، التدريب/التحقّق/الاختبار، تسرّب البيانات",
                    ),
                    blocks=[
                        Text(
                            T(
                                "In **supervised learning**, each example has **features** (the inputs you measure: hours studied, previous marks, attendance) and a **label** (the answer you want predicted: passed or failed). The model's job is to find the relationship between them that generalises to examples it has never seen.",
                                "En **apprentissage supervisé**, chaque exemple a des **caractéristiques** (les entrées mesurées : heures d'étude, notes antérieures, assiduité) et une **étiquette** (la réponse à prédire : réussi ou échoué). Le rôle du modèle est de trouver la relation qui se généralise à des exemples jamais vus.",
                                "في **التعلّم المُشرَف** لكلّ مثال **سمات** (المدخلات التي تقيسها: ساعات المذاكرة، الدرجات السابقة، الحضور) و**تسمية** (الإجابة المطلوب التنبّؤ بها: نجح أم رسب). ومهمّة النموذج إيجاد العلاقة بينها التي تعمّم على أمثلة لم يرها قطّ.",
                            )
                        ),
                        Text(
                            T(
                                "The data is split three ways. **Training** is what the model learns from. **Validation** is what you use to choose between models and settings. **Test** is touched exactly once, at the end, to estimate real performance — because the moment you tune anything against it, it stops being an honest estimate and becomes part of the training.",
                                "Les données sont découpées en trois. L'**entraînement** est ce dont le modèle apprend. La **validation** sert à choisir entre modèles et réglages. Le **test** n'est touché qu'une fois, à la fin, pour estimer la performance réelle — car dès qu'on l'utilise pour régler quoi que ce soit, il cesse d'être une estimation honnête.",
                                "تُقسَّم البيانات ثلاثة أقسام. **التدريب** هو ما يتعلّم منه النموذج. و**التحقّق** ما تستخدمه للاختيار بين النماذج والإعدادات. و**الاختبار** لا يُمسّ إلّا مرّة واحدة في النهاية لتقدير الأداء الحقيقي — لأنّك ما إن تضبط شيئًا عليه حتى يكفّ عن كونه تقديرًا أمينًا ويصير جزءًا من التدريب.",
                            )
                        ),
                        Code(
                            T(
                                "The split, and the mistake that quietly invalidates it:",
                                "Le découpage, et l'erreur qui l'invalide silencieusement :",
                                "التقسيم، والخطأ الذي يُبطله بصمت:",
                            ),
                            "rows = [\n"
                            "    # (hours_studied, previous_mark, attended_pct) -> passed\n"
                            "    ((12, 11, 90), 1),\n"
                            "    ((3,  7,  40), 0),\n"
                            "    ((8, 13,  85), 1),\n"
                            "]\n\n"
                            "split = int(len(rows) * 0.7)\n"
                            "train, test = rows[:split], rows[split:]\n\n"
                            "# DATA LEAKAGE: a feature that would not exist at prediction time.\n"
                            "# 'final_exam_mark' predicts 'passed' perfectly in the dataset and\n"
                            "# is unavailable when you actually need the prediction, so the\n"
                            "# model looks brilliant in testing and is useless in production.",
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "Why must the test set never be used while tuning a model?",
                                "Pourquoi le jeu de test ne doit-il jamais servir pendant le réglage ?",
                                "لماذا يجب ألّا تُستخدم مجموعة الاختبار أثناء ضبط النموذج؟",
                            ),
                            hint=T("What is it supposed to estimate?", "Qu'est-il censé estimer ?", "ما الذي يُفترض أن تقدّره؟"),
                            explanation=T(
                                "It exists to estimate performance on unseen data; tuning against it means the model has effectively seen it, so the estimate is optimistic.",
                                "Il sert à estimer la performance sur des données inédites ; régler dessus revient à ce que le modèle les ait vues, l'estimation devient optimiste.",
                                "وُجدت لتقدير الأداء على بيانات غير مرئية؛ والضبط عليها يعني أنّ النموذج رآها فعليًا، فيصبح التقدير متفائلًا.",
                            ),
                            options=[
                                Option(T("It is usually too small", "Il est généralement trop petit", "عادةً ما تكون صغيرة جدًا")),
                                Option(
                                    T(
                                        "Tuning against it makes it no longer an unseen-data estimate",
                                        "Le régler dessus fait qu'il n'estime plus des données inédites",
                                        "الضبط عليها يجعلها لم تعد تقديرًا لبيانات غير مرئية",
                                    ),
                                    correct=True,
                                ),
                                Option(T("It has no labels", "Il n'a pas d'étiquettes", "لا تحوي تسميات")),
                                Option(T("It slows down training", "Il ralentit l'entraînement", "تبطّئ التدريب")),
                            ],
                        ),
                        MCQ(
                            prompt=T(
                                "You are predicting whether a student will pass, before the year starts. Which feature is leakage?",
                                "Vous prédisez la réussite d'un élève avant le début de l'année. Quelle caractéristique est une fuite ?",
                                "تتنبّأ بنجاح طالب قبل بدء السنة. أيّ سمة تُعدّ تسرّبًا؟",
                            ),
                            hint=T("Which value does not exist yet at prediction time?", "Quelle valeur n'existe pas encore au moment de la prédiction ?", "أيّ قيمة لا توجد بعدُ لحظة التنبّؤ؟"),
                            explanation=T(
                                "The final exam mark is only known after the outcome, so a model using it cannot be used for its stated purpose.",
                                "La note de l'examen final n'est connue qu'après le résultat : un modèle l'utilisant ne peut servir à sa finalité annoncée.",
                                "درجة الامتحان النهائي لا تُعرَف إلّا بعد النتيجة، فالنموذج الذي يستخدمها لا يصلح للغرض المعلَن.",
                            ),
                            options=[
                                Option(T("Previous year's average mark", "Moyenne de l'année précédente", "معدّل السنة الماضية")),
                                Option(T("The final exam mark", "La note de l'examen final", "درجة الامتحان النهائي"), correct=True),
                                Option(T("Attendance in previous years", "Assiduité des années précédentes", "الحضور في السنوات السابقة")),
                                Option(T("Chosen subject options", "Options choisies", "المواد المختارة")),
                            ],
                        ),
                    ],
                ),
                Lesson(
                    slug="overfitting-and-evaluation",
                    minutes=40,
                    xp=70,
                    difficulty=D.advanced,
                    title=T("Overfitting and Honest Evaluation", "Surapprentissage et Évaluation Honnête", "الإفراط في التوفيق والتقييم الأمين"),
                    story=T(
                        "A model with 99% accuracy that predicts a rare disease can be worse than useless. Accuracy is the most misleading number in the field.",
                        "Un modèle à 99 % de justesse sur une maladie rare peut être pire qu'inutile. La justesse est le chiffre le plus trompeur du domaine.",
                        "نموذج بدقّة 99% للتنبّؤ بمرض نادر قد يكون أسوأ من عديم الفائدة. والدقّة أكثر الأرقام تضليلًا في هذا المجال.",
                    ),
                    objective=T(
                        "Recognise overfitting and choose between accuracy, precision and recall for a given cost of error.",
                        "Reconnaître le surapprentissage et choisir entre justesse, précision et rappel selon le coût de l'erreur.",
                        "التعرّف على الإفراط في التوفيق، والاختيار بين الدقّة الكلّية والدقّة والاستدعاء بحسب كلفة الخطأ.",
                    ),
                    skills=T(
                        "Overfitting, underfitting, regularisation, accuracy, precision, recall, class imbalance, bias",
                        "Surapprentissage, sous-apprentissage, régularisation, justesse, précision, rappel, déséquilibre des classes, biais",
                        "الإفراط في التوفيق، القصور، التنظيم، الدقّة الكلّية، الدقّة، الاستدعاء، اختلال التوازن، التحيّز",
                    ),
                    blocks=[
                        Text(
                            T(
                                "**Overfitting** is memorising the training data, including its noise, instead of learning the pattern. You see it as a large gap: excellent on training data, poor on validation data. **Underfitting** is the opposite — the model is too simple to capture the pattern and is mediocre on both.",
                                "Le **surapprentissage**, c'est mémoriser les données d'entraînement, bruit compris, au lieu d'apprendre le motif. Il se voit à un grand écart : excellent en entraînement, faible en validation. Le **sous-apprentissage** est l'inverse — le modèle est trop simple et médiocre sur les deux.",
                                "**الإفراط في التوفيق** هو حفظ بيانات التدريب بضجيجها بدل تعلّم النمط. وتراه فجوةً كبيرة: ممتاز على بيانات التدريب وضعيف على بيانات التحقّق. أمّا **القصور** فعكسه — النموذج أبسط من أن يلتقط النمط فيكون متوسّطًا في الاثنين.",
                            )
                        ),
                        Text(
                            T(
                                "**Accuracy** is the fraction of predictions that were right, and it collapses when classes are imbalanced: if 1 in 1000 patients has the disease, always answering \"no\" scores 99.9% and finds nobody. **Precision** asks: of the cases I flagged, how many were real? **Recall** asks: of the real cases, how many did I find? Which one matters depends entirely on which mistake costs more.",
                                "La **justesse** est la fraction de prédictions correctes, et elle s'effondre en cas de déséquilibre : si 1 patient sur 1000 est malade, répondre toujours « non » donne 99,9 % et ne trouve personne. La **précision** demande : parmi les cas signalés, combien étaient réels ? Le **rappel** demande : parmi les cas réels, combien ai-je trouvés ? Le choix dépend entièrement du coût de chaque erreur.",
                                "**الدقّة الكلّية** هي نسبة التنبّؤات الصحيحة، وتنهار عند اختلال توازن الفئات: فإذا كان مريض واحد من كلّ ألف مصابًا، فإنّ الإجابة بـ«لا» دائمًا تحرز 99.9% ولا تجد أحدًا. و**الدقّة** تسأل: من الحالات التي أشّرت عليها، كم كانت حقيقية؟ و**الاستدعاء** يسأل: من الحالات الحقيقية، كم وجدتُ؟ وأيّهما يهمّ يتوقّف كلّيًا على أيّ الخطأين أغلى.",
                            )
                        ),
                        Code(
                            T(
                                "The same predictions, judged three ways:",
                                "Les mêmes prédictions, jugées de trois façons :",
                                "التنبّؤات نفسها محكومًا عليها بثلاث طرق:",
                            ),
                            "actual    = [1, 0, 0, 1, 1, 0, 0, 0, 0, 0]   # 1 = has the disease\n"
                            "predicted = [1, 0, 0, 0, 1, 0, 1, 0, 0, 0]\n\n"
                            "tp = sum(a == 1 and p == 1 for a, p in zip(actual, predicted))\n"
                            "fp = sum(a == 0 and p == 1 for a, p in zip(actual, predicted))\n"
                            "fn = sum(a == 1 and p == 0 for a, p in zip(actual, predicted))\n"
                            "correct = sum(a == p for a, p in zip(actual, predicted))\n\n"
                            "print('accuracy ', correct / len(actual))\n"
                            "print('precision', tp / (tp + fp))   # of those flagged, how many real\n"
                            "print('recall   ', tp / (tp + fn))   # of the real ones, how many found\n\n"
                            "# Screening for a serious illness: a missed case is far worse than\n"
                            "# a false alarm, so you optimise RECALL and accept lower precision.\n"
                            "# Blocking accounts for fraud: a false accusation is expensive, so\n"
                            "# you optimise PRECISION.",
                        ),
                        ExamTip(
                            T(
                                "A model reflects its training data, including its history. If past hiring favoured one group, a model trained on those decisions will reproduce the pattern and call it objectivity. Auditing outcomes by group is part of evaluation, not an optional extra.",
                                "Un modèle reflète ses données d'entraînement, histoire comprise. Si les recrutements passés ont favorisé un groupe, un modèle entraîné dessus reproduira le schéma en l'appelant objectivité. Auditer les résultats par groupe fait partie de l'évaluation, pas d'un supplément optionnel.",
                                "النموذج يعكس بيانات تدريبه بما فيها تاريخها. فإن كان التوظيف السابق يحابي فئة، فالنموذج المدرَّب على تلك القرارات سيعيد إنتاج النمط ويسمّيه موضوعية. وتدقيق النتائج حسب الفئات جزء من التقييم لا إضافة اختيارية.",
                            )
                        ),
                    ],
                    exercises=[
                        Prediction(
                            prompt=T(
                                "What does this evaluation print?",
                                "Qu'affiche cette évaluation ?",
                                "ماذا يطبع هذا التقييم؟",
                            ),
                            hint=T(
                                "Count true positives, false positives and false negatives from the two lists.",
                                "Comptez vrais positifs, faux positifs et faux négatifs à partir des deux listes.",
                                "عُدّ الإيجابيات الصحيحة والكاذبة والسلبيات الكاذبة من القائمتين.",
                            ),
                            explanation=T(
                                "There are 2 true positives, 1 false positive and 1 false negative, so precision is 2/3 and recall is 2/3.",
                                "Il y a 2 vrais positifs, 1 faux positif et 1 faux négatif : précision 2/3 et rappel 2/3.",
                                "هناك إيجابيّتان صحيحتان وإيجابية كاذبة وسلبية كاذبة، فالدقّة 2/3 والاستدعاء 2/3.",
                            ),
                            code="actual    = [1, 0, 0, 1, 1, 0, 0, 0, 0, 0]\npredicted = [1, 0, 0, 0, 1, 0, 1, 0, 0, 0]\n\ntp = sum(a == 1 and p == 1 for a, p in zip(actual, predicted))\nfp = sum(a == 0 and p == 1 for a, p in zip(actual, predicted))\nfn = sum(a == 1 and p == 0 for a, p in zip(actual, predicted))\nprint(tp, fp, fn)",
                            expected_output="2 1 1",
                        ),
                        MCQ(
                            prompt=T(
                                "You are screening for a serious illness where missing a case is far worse than a false alarm. Which do you optimise?",
                                "Vous dépistez une maladie grave où manquer un cas est bien pire qu'une fausse alerte. Qu'optimisez-vous ?",
                                "تجري فحصًا لمرض خطير، وتفويت حالة أسوأ بكثير من إنذار كاذب. ما الذي تُحسّنه؟",
                            ),
                            hint=T("Which metric counts the cases you missed?", "Quelle métrique compte les cas manqués ?", "أيّ مقياس يعدّ الحالات التي فوّتّها؟"),
                            explanation=T(
                                "Recall measures how many real cases were found, so maximising it minimises missed diagnoses, at the price of more false alarms.",
                                "Le rappel mesure combien de cas réels ont été trouvés : le maximiser minimise les diagnostics manqués, au prix de plus de fausses alertes.",
                                "الاستدعاء يقيس كم حالة حقيقية وُجدت، فتعظيمه يقلّل التشخيصات الفائتة بثمن مزيد من الإنذارات الكاذبة.",
                            ),
                            options=[
                                Option(T("Accuracy", "La justesse", "الدقّة الكلّية")),
                                Option(T("Precision", "La précision", "الدقّة")),
                                Option(T("Recall", "Le rappel", "الاستدعاء"), correct=True),
                                Option(T("Training speed", "La vitesse d'entraînement", "سرعة التدريب")),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)


AI_LITERACY = CourseSpec(
    slug="ai-literacy",
    stage=7,
    track="ai",
    icon="🧠",
    difficulty=D.beginner,
    estimated_hours=6,
    prerequisite_slug="ai-foundations",
    title=T("AI Literacy and Responsible Use", "Culture de l'IA et Usage Responsable", "الوعي بالذكاء الاصطناعي والاستخدام المسؤول"),
    description=T(
        "How to work with AI tools well: asking useful questions, verifying what comes back, and using them to learn faster without learning less.",
        "Bien travailler avec les outils d'IA : poser des questions utiles, vérifier les réponses, et apprendre plus vite sans apprendre moins.",
        "كيف تعمل مع أدوات الذكاء الاصطناعي جيّدًا: طرح أسئلة مفيدة، والتحقّق ممّا يعود، واستخدامها لتتعلّم أسرع لا أقلّ.",
    ),
    skills=T(
        "Prompting, verification, hallucination, limitations, responsible use, AI-assisted programming, academic integrity",
        "Formulation de requêtes, vérification, hallucination, limites, usage responsable, programmation assistée, intégrité académique",
        "صياغة الطلبات، التحقّق، الهلوسة، الحدود، الاستخدام المسؤول، البرمجة بمساعدة الذكاء الاصطناعي، النزاهة الأكاديمية",
    ),
    modules=[
        Module(
            slug="working-with-ai",
            title=T("Working with AI Tools", "Travailler avec les Outils d'IA", "العمل مع أدوات الذكاء الاصطناعي"),
            description=T(
                "Asking well, and checking what you get back.",
                "Bien demander, et vérifier ce qu'on reçoit.",
                "أن تسأل جيّدًا وأن تتحقّق ممّا يعود إليك.",
            ),
            lessons=[
                Lesson(
                    slug="asking-and-verifying",
                    minutes=30,
                    xp=55,
                    difficulty=D.beginner,
                    title=T("Asking Well and Verifying Always", "Bien Demander et Toujours Vérifier", "أحسِن السؤال وتحقّق دائمًا"),
                    story=T(
                        "The difference between a useless answer and a useful one is usually in the question.",
                        "La différence entre une réponse inutile et une réponse utile tient généralement à la question.",
                        "الفرق بين إجابة عديمة الفائدة وأخرى مفيدة يكمن عادةً في السؤال.",
                    ),
                    objective=T(
                        "Write prompts that carry context and constraints, and verify every checkable claim.",
                        "Rédiger des requêtes portant contexte et contraintes, et vérifier chaque affirmation vérifiable.",
                        "كتابة طلبات تحمل السياق والقيود، والتحقّق من كلّ ادّعاء قابل للتحقّق.",
                    ),
                    skills=T(
                        "Context, constraints, iteration, verification, source checking",
                        "Contexte, contraintes, itération, vérification, contrôle des sources",
                        "السياق، القيود، التكرار، التحقّق، فحص المصادر",
                    ),
                    blocks=[
                        Text(
                            T(
                                "A good prompt carries four things: the **context** (what you are building and in what), the **task** (what you want, specifically), the **constraints** (what it must and must not do), and the **shape of the answer** you need. \"Fix my code\" gets a guess; the same request with the error message, the versions and the expected behaviour gets an answer.",
                                "Une bonne requête porte quatre choses : le **contexte** (ce que vous construisez et avec quoi), la **tâche** (ce que vous voulez, précisément), les **contraintes** (ce qui doit et ne doit pas être fait), et la **forme de réponse** attendue. « Corrige mon code » donne une supposition ; la même demande avec le message d'erreur, les versions et le comportement attendu donne une réponse.",
                                "الطلب الجيّد يحمل أربعة أشياء: **السياق** (ما الذي تبنيه وبأيّ أدوات)، و**المهمّة** (ما تريده تحديدًا)، و**القيود** (ما يجب وما لا يجب)، و**شكل الإجابة** المطلوب. فـ«أصلح كودي» يعطيك تخمينًا، أمّا الطلب نفسه مع رسالة الخطأ والإصدارات والسلوك المتوقّع فيعطيك إجابة.",
                            )
                        ),
                        Code(
                            T(
                                "The same question, asked twice:",
                                "La même question, posée deux fois :",
                                "السؤال نفسه مطروحًا مرّتين:",
                            ),
                            "# Weak:\n"
                            "#   'my login is broken, fix it'\n\n"
                            "# Strong:\n"
                            "#   'FastAPI 0.109 with SQLAlchemy async. POST /auth/login returns\n"
                            "#    500 with: MissingGreenlet: greenlet_spawn has not been called.\n"
                            "#    It happens only when the user has a related profile row.\n"
                            "#    Here is the endpoint and the model. What causes this, and\n"
                            "#    what is the smallest fix? Explain the cause before the code.'\n\n"
                            "# The second gets a real diagnosis because it contains the\n"
                            "# information a diagnosis requires. The first cannot.",
                        ),
                        Text(
                            T(
                                "Then verify. **Code**: run it, including the edge cases. **Facts**: check a primary source. **APIs and library functions**: confirm in the official documentation that they exist and take those arguments — invented function names are among the most common hallucinations. If a claim cannot be checked, treat it as a hypothesis, not an answer.",
                                "Puis vérifiez. **Code** : exécutez-le, cas limites compris. **Faits** : consultez une source primaire. **APIs et fonctions** : confirmez dans la documentation officielle qu'elles existent et acceptent ces arguments — les noms de fonctions inventés sont parmi les hallucinations les plus fréquentes. Si une affirmation est invérifiable, traitez-la comme une hypothèse.",
                                "ثمّ تحقّق. **الكود**: شغّله بما في ذلك الحالات الحدّية. و**الحقائق**: راجع مصدرًا أوّليًا. و**الواجهات ودوالّ المكتبات**: تأكّد من التوثيق الرسمي أنّها موجودة وتقبل تلك الوسائط — فأسماء الدوالّ المخترعة من أكثر الهلوسات شيوعًا. وإن تعذّر التحقّق من ادّعاء فعامله كفرضية لا كإجابة.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "An AI assistant suggests a library function you have never seen. What do you do first?",
                                "Un assistant IA propose une fonction de bibliothèque inconnue. Que faites-vous d'abord ?",
                                "يقترح مساعد ذكاء اصطناعي دالّة مكتبة لم ترها قطّ. ما أوّل ما تفعله؟",
                            ),
                            hint=T("Function names are among the easiest things to invent.", "Les noms de fonctions sont faciles à inventer.", "أسماء الدوالّ من أسهل ما يُخترَع."),
                            explanation=T(
                                "Check the official documentation: the function may not exist, or may not take those arguments in your version.",
                                "Consultez la documentation officielle : la fonction peut ne pas exister ou ne pas accepter ces arguments dans votre version.",
                                "راجع التوثيق الرسمي: فقد لا تكون الدالّة موجودة أو قد لا تقبل تلك الوسائط في نسختك.",
                            ),
                            options=[
                                Option(T("Use it; the assistant is usually right", "L'utiliser ; l'assistant a souvent raison", "استخدمها؛ فالمساعد غالبًا محقّ")),
                                Option(
                                    T(
                                        "Check the official documentation that it exists",
                                        "Vérifier dans la documentation officielle qu'elle existe",
                                        "تحقّق من التوثيق الرسمي أنّها موجودة",
                                    ),
                                    correct=True,
                                ),
                                Option(T("Ask the assistant whether it is sure", "Demander à l'assistant s'il est sûr", "اسأل المساعد إن كان متأكّدًا")),
                                Option(T("Search for a different assistant", "Chercher un autre assistant", "ابحث عن مساعد آخر")),
                            ],
                        ),
                        MCQ(
                            prompt=T(
                                "Which of these makes a prompt more likely to get a useful answer?",
                                "Lequel augmente les chances d'obtenir une réponse utile ?",
                                "أيّ ممّا يلي يزيد احتمال الحصول على إجابة مفيدة؟",
                            ),
                            hint=T("What would a human colleague need in order to help?", "De quoi un collègue aurait-il besoin pour aider ?", "ما الذي يحتاجه زميل بشري كي يساعدك؟"),
                            explanation=T(
                                "Concrete context — versions, the exact error, expected behaviour — is what makes a specific answer possible instead of a generic one.",
                                "Un contexte concret — versions, erreur exacte, comportement attendu — rend possible une réponse spécifique plutôt que générique.",
                                "السياق الملموس — الإصدارات والخطأ الدقيق والسلوك المتوقّع — هو ما يتيح إجابة محدّدة بدل إجابة عامّة.",
                            ),
                            options=[
                                Option(T("Asking politely", "Demander poliment", "أن تسأل بأدب")),
                                Option(
                                    T(
                                        "Including versions, the exact error and the expected behaviour",
                                        "Inclure les versions, l'erreur exacte et le comportement attendu",
                                        "تضمين الإصدارات والخطأ الدقيق والسلوك المتوقّع",
                                    ),
                                    correct=True,
                                ),
                                Option(T("Asking the same question repeatedly", "Reposer la même question", "تكرار السؤال نفسه")),
                                Option(T("Writing the prompt in capitals", "Écrire la requête en majuscules", "كتابة الطلب بحروف كبيرة")),
                            ],
                        ),
                    ],
                ),
                Lesson(
                    slug="ai-for-programmers",
                    minutes=35,
                    xp=60,
                    difficulty=D.beginner,
                    title=T("AI for Programmers, Without Losing the Skill", "L'IA pour les Programmeurs, Sans Perdre la Compétence", "الذكاء الاصطناعي للمبرمجين دون فقدان المهارة"),
                    story=T(
                        "The tool can write the code. It cannot be the person who understands it in six months when it breaks.",
                        "L'outil peut écrire le code. Il ne peut pas être celui qui le comprend dans six mois quand il casse.",
                        "الأداة تستطيع كتابة الكود. لكنّها لا تستطيع أن تكون من يفهمه بعد ستّة أشهر حين يتعطّل.",
                    ),
                    objective=T(
                        "Use AI where it genuinely helps, keep ownership of the code, and respect academic integrity.",
                        "Utiliser l'IA là où elle aide vraiment, garder la maîtrise du code, et respecter l'intégrité académique.",
                        "استخدام الذكاء الاصطناعي حيث ينفع فعلًا، والاحتفاظ بملكية الكود، واحترام النزاهة الأكاديمية.",
                    ),
                    skills=T(
                        "AI-assisted debugging, code explanation, review, dependency on tools, integrity, privacy",
                        "Débogage assisté, explication de code, revue, dépendance aux outils, intégrité, confidentialité",
                        "التصحيح بمساعدة الذكاء الاصطناعي، شرح الكود، المراجعة، الاعتماد على الأدوات، النزاهة، الخصوصية",
                    ),
                    blocks=[
                        Text(
                            T(
                                "AI is strongest where you can immediately check the result: **explaining** unfamiliar code, **suggesting** what a confusing error means, **drafting** tests you then read, **rephrasing** an idea you already understand. It is weakest where checking is expensive: architectural decisions, security-critical logic, and anything depending on facts about your specific system.",
                                "L'IA est la plus forte là où le résultat se vérifie immédiatement : **expliquer** du code inconnu, **suggérer** le sens d'une erreur obscure, **rédiger** des tests que vous relisez, **reformuler** une idée déjà comprise. Elle est la plus faible là où la vérification coûte cher : décisions d'architecture, logique critique pour la sécurité, et tout ce qui dépend de faits propres à votre système.",
                                "الذكاء الاصطناعي أقوى ما يكون حيث يمكنك التحقّق فورًا من النتيجة: **شرح** كود غير مألوف، و**اقتراح** معنى خطأ محيّر، و**صياغة** اختبارات تقرؤها بنفسك، و**إعادة صياغة** فكرة تفهمها أصلًا. وهو أضعف ما يكون حيث يكون التحقّق مكلفًا: قرارات المعمارية، والمنطق الحسّاس أمنيًا، وكلّ ما يتوقّف على وقائع خاصّة بنظامك.",
                            )
                        ),
                        Text(
                            T(
                                "The test for whether you are learning or outsourcing is simple: **could you have written this, and can you explain every line?** If not, you have added code you cannot maintain and skipped the practice that would have let you. Ask for an explanation before the code, and try the problem yourself first — the struggle is where the learning actually happens.",
                                "Le test pour savoir si vous apprenez ou sous-traitez est simple : **auriez-vous pu écrire ceci, et pouvez-vous expliquer chaque ligne ?** Sinon, vous avez ajouté du code non maintenable et sauté l'entraînement qui vous l'aurait permis. Demandez l'explication avant le code, et essayez d'abord seul — c'est dans l'effort que l'apprentissage se produit.",
                                "الاختبار الذي يحدّد هل تتعلّم أم تُسنِد بسيط: **هل كنت تستطيع كتابة هذا، وهل تستطيع شرح كلّ سطر؟** إن لم يكن، فقد أضفت كودًا لا تستطيع صيانته وتخطّيت التمرين الذي كان سيمكّنك منه. اطلب الشرح قبل الكود، وجرّب المسألة بنفسك أوّلًا — ففي المكابدة يحدث التعلّم فعلًا.",
                            )
                        ),
                        Code(
                            T(
                                "Two rules that are not optional:",
                                "Deux règles non négociables :",
                                "قاعدتان غير اختياريّتين:",
                            ),
                            "# 1. ACADEMIC INTEGRITY\n"
                            "#    Submitting generated work as your own is plagiarism in most\n"
                            "#    institutions, whatever the tool. Follow your course policy,\n"
                            "#    and when assistance is permitted, disclose what you used and\n"
                            "#    how. 'I did not know the rule' is not a defence anywhere.\n\n"
                            "# 2. PRIVACY AND SECRETS\n"
                            "#    Whatever you paste into a hosted tool leaves your machine.\n"
                            "#    Never paste API keys, passwords, personal data about other\n"
                            "#    people, or code your employer or school has not permitted\n"
                            "#    you to share. Reproduce the bug with fake data instead.",
                        ),
                        ExamTip(
                            T(
                                "In an interview, a viva or an exam you will be asked why the code works. Practise explaining your solutions out loud — a solution you cannot explain is one you do not yet have.",
                                "En entretien, en soutenance ou en examen, on vous demandera pourquoi le code fonctionne. Entraînez-vous à expliquer vos solutions à voix haute — une solution que vous ne pouvez pas expliquer n'est pas encore la vôtre.",
                                "في المقابلة أو المناقشة أو الامتحان سيُسأل عن سبب عمل الكود. تدرّب على شرح حلولك بصوت مسموع — فالحلّ الذي لا تستطيع شرحه ليس حلّك بعد.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "An AI tool gives you a working function you do not fully understand. What is the responsible next step?",
                                "Un outil d'IA vous donne une fonction qui marche mais que vous ne comprenez pas entièrement. Quelle est l'étape responsable ?",
                                "أعطتك أداة ذكاء اصطناعي دالّة تعمل لكنّك لا تفهمها تمامًا. ما الخطوة المسؤولة؟",
                            ),
                            hint=T("Who maintains this code in six months?", "Qui maintiendra ce code dans six mois ?", "من سيصون هذا الكود بعد ستّة أشهر؟"),
                            explanation=T(
                                "Understanding it before merging is what keeps the code maintainable and keeps you able to fix it later.",
                                "La comprendre avant de fusionner est ce qui garde le code maintenable et vous laisse capable de le corriger.",
                                "فهمها قبل الدمج هو ما يُبقي الكود قابلًا للصيانة ويُبقيك قادرًا على إصلاحه لاحقًا.",
                            ),
                            options=[
                                Option(T("Merge it; the tests pass", "La fusionner ; les tests passent", "ادمجها؛ فالاختبارات ناجحة")),
                                Option(
                                    T(
                                        "Work through it until you can explain every line, then decide",
                                        "L'étudier jusqu'à pouvoir expliquer chaque ligne, puis décider",
                                        "ادرسها حتى تستطيع شرح كلّ سطر ثمّ قرّر",
                                    ),
                                    correct=True,
                                ),
                                Option(T("Rename the variables so it looks like yours", "Renommer les variables pour qu'elle semble vôtre", "غيّر أسماء المتغيّرات لتبدو من عندك")),
                                Option(T("Delete the tests to save time", "Supprimer les tests pour gagner du temps", "احذف الاختبارات لتوفير الوقت")),
                            ],
                        ),
                        MCQ(
                            prompt=T(
                                "Which of these must never be pasted into a hosted AI tool?",
                                "Lequel ne doit jamais être collé dans un outil d'IA hébergé ?",
                                "أيّ ممّا يلي يجب ألّا يُلصَق أبدًا في أداة ذكاء اصطناعي مستضافة؟",
                            ),
                            hint=T("What leaves your machine, and what is it worth to someone else?", "Qu'est-ce qui quitte votre machine, et vaut quoi pour autrui ?", "ما الذي يغادر جهازك، وكم يساوي لغيرك؟"),
                            explanation=T(
                                "Production credentials and personal data about other people leave your control the moment they are sent, and neither is yours to disclose.",
                                "Identifiants de production et données personnelles d'autrui échappent à votre contrôle dès l'envoi, et ne vous appartiennent pas.",
                                "بيانات اعتماد الإنتاج والبيانات الشخصية عن آخرين تخرج عن سيطرتك لحظة إرسالها، وليست ملكك لتفشيها.",
                            ),
                            options=[
                                Option(T("A public error message", "Un message d'erreur public", "رسالة خطأ عامّة")),
                                Option(T("Production API keys and other people's personal data", "Clés d'API de production et données personnelles d'autrui", "مفاتيح واجهات الإنتاج وبيانات الآخرين الشخصية"), correct=True),
                                Option(T("A snippet from open-source documentation", "Un extrait de documentation open source", "مقتطف من توثيق مفتوح المصدر")),
                                Option(T("A question about Big-O notation", "Une question sur la notation Big-O", "سؤال عن تدوين Big-O")),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)


async def seed_ai_foundations(db, order: int) -> int:
    print("Seeding Introduction to Artificial Intelligence...")
    return await seed_course(db, AI_FOUNDATIONS, order)


async def seed_machine_learning(db, order: int) -> int:
    print("Seeding Machine Learning Fundamentals...")
    return await seed_course(db, MACHINE_LEARNING, order)


async def seed_ai_literacy(db, order: int) -> int:
    print("Seeding AI Literacy...")
    return await seed_course(db, AI_LITERACY, order)
