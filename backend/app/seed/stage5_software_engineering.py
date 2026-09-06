"""Stage 5 — Software Engineering.

Programming is making a computer do something. Software engineering is making
it keep doing it, in a team, for years. Version control workflow, code review,
testing strategy, architecture, APIs, and the pipeline that ships it.
"""

from app.models import DifficultyEnum as D

from .authoring import (
    Code,
    CourseSpec,
    ExamTip,
    FillBlank,
    Lesson,
    MCQ,
    Module,
    Option,
    Ordering,
    ShortAnswer,
    T,
    Text,
    seed_course,
)

SOFTWARE_ENGINEERING = CourseSpec(
    slug="software-engineering",
    stage=5,
    track="engineering",
    icon="🏗️",
    difficulty=D.intermediate,
    estimated_hours=12,
    prerequisite_slug="git-github",
    title=T("Software Engineering", "Génie Logiciel", "هندسة البرمجيات"),
    description=T(
        "How working code becomes maintainable software: branching workflows, code review, testing strategy, architecture, APIs and CI/CD.",
        "Comment du code qui marche devient un logiciel maintenable : workflows de branches, revue de code, stratégie de test, architecture, APIs et CI/CD.",
        "كيف يتحوّل الكود الذي يعمل إلى برمجيات قابلة للصيانة: سير عمل الفروع، ومراجعة الكود، واستراتيجية الاختبار، والمعمارية، وواجهات البرمجة، وCI/CD.",
    ),
    skills=T(
        "Branching, pull requests, code review, testing pyramid, architecture, REST, CI/CD",
        "Branches, pull requests, revue de code, pyramide des tests, architecture, REST, CI/CD",
        "الفروع، طلبات الدمج، مراجعة الكود، هرم الاختبار، المعمارية، REST، CI/CD",
    ),
    modules=[
        Module(
            slug="working-in-a-team",
            title=T("Working in a Team", "Travailler en Équipe", "العمل ضمن فريق"),
            description=T(
                "Branching workflows and the code review that makes them safe.",
                "Workflows de branches et la revue de code qui les sécurise.",
                "سير عمل الفروع والمراجعة التي تجعله آمنًا.",
            ),
            lessons=[
                Lesson(
                    slug="branching-workflows",
                    minutes=35,
                    xp=60,
                    difficulty=D.intermediate,
                    title=T("Branching Workflows", "Workflows de Branches", "سير عمل الفروع"),
                    story=T(
                        "Five people, one codebase, no one blocked and nothing lost. That is what a workflow buys you.",
                        "Cinq personnes, une base de code, personne bloqué et rien de perdu. Voilà ce qu'achète un workflow.",
                        "خمسة أشخاص وقاعدة كود واحدة، لا أحد معطّل ولا شيء يضيع. هذا ما يشتريه لك سير العمل.",
                    ),
                    objective=T(
                        "Use short-lived feature branches, keep them current, and merge without losing work.",
                        "Utiliser des branches de fonctionnalité courtes, les garder à jour, et fusionner sans perdre de travail.",
                        "استخدام فروع ميزات قصيرة العمر، وإبقاؤها محدّثة، والدمج دون فقدان عمل.",
                    ),
                    skills=T(
                        "Feature branches, trunk-based development, merge vs rebase, conflicts",
                        "Branches de fonctionnalité, développement sur trunk, merge vs rebase, conflits",
                        "فروع الميزات، التطوير على الجذع، الدمج مقابل إعادة الأساس، التعارضات",
                    ),
                    blocks=[
                        Text(
                            T(
                                "A **feature branch** is a private copy of the code where one change is developed. The rule that matters is not which workflow you pick but how long branches live: a branch open for three days merges cleanly, a branch open for three weeks becomes a conflict-resolution project of its own.",
                                "Une **branche de fonctionnalité** est une copie privée du code où l'on développe un changement. La règle qui compte n'est pas le workflow choisi mais la durée de vie des branches : une branche de trois jours fusionne proprement, une branche de trois semaines devient un projet de résolution de conflits.",
                                "**فرع الميزة** نسخة خاصّة من الكود يُطوَّر فيها تغيير واحد. والقاعدة المهمّة ليست أيّ سير عمل تختار بل كم يعيش الفرع: فرعٌ عمره ثلاثة أيّام يندمج بسلاسة، وفرعٌ عمره ثلاثة أسابيع يصبح مشروع حلّ تعارضات بحدّ ذاته.",
                            )
                        ),
                        Code(
                            T(
                                "The loop every change goes through:",
                                "La boucle que suit chaque changement :",
                                "الحلقة التي يمرّ بها كلّ تغيير:",
                            ),
                            "git switch -c feature/login-rate-limit   # branch off main\n"
                            "# ... make the change, commit in small steps ...\n"
                            "git add -p\n"
                            "git commit -m 'Rate-limit failed login attempts'\n\n"
                            "git fetch origin                        # bring main up to date\n"
                            "git rebase origin/main                  # replay my work on top of it\n\n"
                            "git push -u origin feature/login-rate-limit\n"
                            "# open a pull request, get it reviewed, merge, delete the branch",
                        ),
                        Text(
                            T(
                                "**Merge** keeps the true history, including the fact that two lines of work happened at once. **Rebase** rewrites your commits on top of the latest main, producing a straight line that is easier to read. The safe rule: rebase your own unpushed branch; never rebase a branch other people have already pulled.",
                                "**Merge** conserve l'histoire réelle, y compris le fait que deux travaux ont eu lieu en parallèle. **Rebase** réécrit vos commits au-dessus du main récent, produisant une ligne droite plus lisible. La règle sûre : rebasez votre branche non poussée ; ne rebasez jamais une branche déjà récupérée par d'autres.",
                                "**الدمج (merge)** يحفظ التاريخ الحقيقي بما فيه أنّ خطّي عمل جريا معًا. و**إعادة الأساس (rebase)** تعيد كتابة تعديلاتك فوق آخر main فتنتج خطًّا مستقيمًا أسهل قراءة. والقاعدة الآمنة: أعِد أساس فرعك غير المدفوع، ولا تعِد أساس فرع سحبه آخرون.",
                            )
                        ),
                        ExamTip(
                            T(
                                "A merge conflict is not an error. It is Git saying two people changed the same lines and it will not guess which one is right. Read both sides, keep what is correct, and run the tests before committing the resolution.",
                                "Un conflit de fusion n'est pas une erreur. C'est Git qui dit que deux personnes ont modifié les mêmes lignes et qu'il ne devinera pas laquelle a raison. Lisez les deux versions, gardez ce qui est correct, et exécutez les tests avant de valider la résolution.",
                                "تعارض الدمج ليس خطأً. إنّه Git يقول إنّ شخصين غيّرا الأسطر نفسها ولن يخمّن أيّهما على صواب. اقرأ الجانبين، وأبقِ الصحيح، وشغّل الاختبارات قبل تثبيت الحلّ.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "Why are short-lived branches preferred?",
                                "Pourquoi préfère-t-on les branches de courte durée ?",
                                "لماذا تُفضَّل الفروع قصيرة العمر؟",
                            ),
                            hint=T("Think about what accumulates while a branch is open.", "Pensez à ce qui s'accumule pendant qu'une branche reste ouverte.", "فكّر فيما يتراكم بينما يبقى الفرع مفتوحًا."),
                            explanation=T(
                                "The longer a branch lives, the more main moves underneath it, so conflicts and integration risk grow with time.",
                                "Plus une branche vit, plus main évolue en dessous : conflits et risque d'intégration croissent avec le temps.",
                                "كلّما طال عمر الفرع تحرّك main تحته أكثر، فتزداد التعارضات ومخاطر الدمج مع الوقت.",
                            ),
                            options=[
                                Option(T("They use less disk space", "Elles occupent moins d'espace disque", "تستهلك مساحة قرص أقلّ")),
                                Option(
                                    T(
                                        "Less divergence from main, so fewer and smaller conflicts",
                                        "Moins de divergence avec main, donc moins de conflits et plus petits",
                                        "انحراف أقلّ عن main، فتعارضات أقلّ وأصغر",
                                    ),
                                    correct=True,
                                ),
                                Option(T("Git refuses branches older than a week", "Git refuse les branches de plus d'une semaine", "‏Git يرفض الفروع الأقدم من أسبوع")),
                                Option(T("They do not need review", "Elles n'ont pas besoin de revue", "لا تحتاج مراجعة")),
                            ],
                        ),
                        Ordering(
                            prompt=T(
                                "Put the steps of contributing a change in order.",
                                "Remettez dans l'ordre les étapes d'une contribution.",
                                "رتّب خطوات المساهمة بتغيير.",
                            ),
                            hint=T("The branch has to exist before you can push it.", "La branche doit exister avant d'être poussée.", "يجب أن يوجد الفرع قبل دفعه."),
                            explanation=T(
                                "Branch, commit, sync with main, push, open a pull request, then merge after review.",
                                "Créer la branche, committer, synchroniser avec main, pousser, ouvrir une pull request, puis fusionner après revue.",
                                "أنشئ الفرع، ثمّ ثبّت التغييرات، ثمّ زامن مع main، ثمّ ادفع، ثمّ افتح طلب دمج، ثمّ ادمج بعد المراجعة.",
                            ),
                            steps=[
                                T("Create a branch from main", "Créer une branche depuis main", "أنشئ فرعًا من main"),
                                T("Commit the change in small steps", "Committer le changement par petites étapes", "ثبّت التغيير على خطوات صغيرة"),
                                T("Bring the branch up to date with main", "Mettre la branche à jour avec main", "حدّث الفرع بآخر main"),
                                T("Push and open a pull request", "Pousser et ouvrir une pull request", "ادفع وافتح طلب دمج"),
                                T("Merge after review approves it", "Fusionner après approbation de la revue", "ادمج بعد موافقة المراجعة"),
                            ],
                        ),
                    ],
                ),
                Lesson(
                    slug="code-review",
                    minutes=30,
                    xp=55,
                    difficulty=D.intermediate,
                    title=T("Code Review", "La Revue de Code", "مراجعة الكود"),
                    story=T(
                        "The cheapest bug to fix is one that never got merged.",
                        "Le bug le moins cher à corriger est celui qui n'a jamais été fusionné.",
                        "أرخص خلل إصلاحًا هو الذي لم يُدمج قطّ.",
                    ),
                    objective=T(
                        "Review code usefully and respond to review without defensiveness.",
                        "Réviser du code utilement et répondre à une revue sans se braquer.",
                        "مراجعة الكود مراجعة مفيدة، والردّ على المراجعة دون تحفّز.",
                    ),
                    skills=T(
                        "Pull requests, review priorities, feedback, small diffs",
                        "Pull requests, priorités de revue, retours, petits diffs",
                        "طلبات الدمج، أولويات المراجعة، الملاحظات، الفروق الصغيرة",
                    ),
                    blocks=[
                        Text(
                            T(
                                "Review in priority order: **correctness** first (does it do the right thing, including at the edges?), then **security and data safety**, then **clarity for the next reader**, then style — which a formatter should be handling anyway. A review that opens with a naming nitpick and never checks the logic has failed at its job.",
                                "Révisez par ordre de priorité : d'abord la **correction** (fait-il la bonne chose, y compris aux limites ?), puis la **sécurité et l'intégrité des données**, puis la **clarté pour le prochain lecteur**, puis le style — qu'un formateur devrait de toute façon gérer. Une revue qui commence par un détail de nommage sans vérifier la logique a échoué.",
                                "راجع حسب الأولوية: أوّلًا **الصحّة** (هل يفعل الصواب بما في ذلك عند الحدود؟)، ثمّ **الأمن وسلامة البيانات**، ثمّ **الوضوح للقارئ التالي**، ثمّ الأسلوب — الذي ينبغي أن يتولّاه المنسّق الآلي أصلًا. والمراجعة التي تبدأ بملاحظة تسمية ولا تفحص المنطق قد أخفقت في مهمّتها.",
                            )
                        ),
                        Text(
                            T(
                                "Two habits make review work. As an author, **keep the diff small** — a 200-line change gets real scrutiny, a 2000-line change gets a rubber stamp. As a reviewer, **say why**: \"this crashes when the list is empty\" teaches something; \"I don't like this\" does not.",
                                "Deux habitudes font fonctionner la revue. En tant qu'auteur, **gardez le diff petit** — un changement de 200 lignes est vraiment examiné, un de 2000 est approuvé machinalement. En tant que relecteur, **dites pourquoi** : « ça plante si la liste est vide » enseigne quelque chose ; « je n'aime pas » non.",
                                "عادتان تجعلان المراجعة ناجحة. كمؤلّف: **أبقِ الفرق صغيرًا** — تغيير من 200 سطر يُفحَص فعلًا، وتغيير من 2000 سطر يُختَم آليًا. وكمراجِع: **اذكر السبب** — فقولك «ينهار حين تكون القائمة فارغة» يعلّم شيئًا، أمّا «لا يعجبني» فلا.",
                            )
                        ),
                        Code(
                            T(
                                "A review comment that teaches, on a real defect:",
                                "Un commentaire de revue qui enseigne, sur un vrai défaut :",
                                "تعليق مراجعة يعلّم، على خلل حقيقي:",
                            ),
                            "# Under review:\n"
                            "def average(marks):\n"
                            "    return sum(marks) / len(marks)\n\n"
                            "# Reviewer:\n"
                            "#   This raises ZeroDivisionError for an empty list, and the\n"
                            "#   import screen calls it before any marks exist. Return None\n"
                            "#   for the empty case and add a test for it?\n\n"
                            "def average(marks):\n"
                            "    if not marks:\n"
                            "        return None\n"
                            "    return sum(marks) / len(marks)",
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "What should a reviewer check first?",
                                "Que doit vérifier un relecteur en premier ?",
                                "ما الذي يجب أن يفحصه المراجِع أوّلًا؟",
                            ),
                            hint=T("Which problem is most expensive once merged?", "Quel problème coûte le plus cher une fois fusionné ?", "أيّ مشكلة أغلى ثمنًا بعد الدمج؟"),
                            explanation=T(
                                "Correctness comes first; formatting is a tool's job and naming can be fixed later, but a wrong result ships to users.",
                                "La correction d'abord ; le formatage est l'affaire d'un outil et le nommage se corrige plus tard, mais un résultat faux part en production.",
                                "الصحّة أوّلًا؛ فالتنسيق مهمّة أداة والتسمية تُصلَح لاحقًا، أمّا النتيجة الخاطئة فتصل إلى المستخدمين.",
                            ),
                            options=[
                                Option(T("Indentation and formatting", "L'indentation et le formatage", "المسافات البادئة والتنسيق")),
                                Option(T("Whether the code is correct, including edge cases", "Si le code est correct, cas limites compris", "هل الكود صحيح بما في ذلك الحالات الحدّية"), correct=True),
                                Option(T("Whether the author used their favourite library", "Si l'auteur a utilisé sa bibliothèque préférée", "هل استخدم المؤلّف مكتبته المفضّلة")),
                                Option(T("The number of commits", "Le nombre de commits", "عدد التثبيتات")),
                            ],
                        ),
                        ShortAnswer(
                            prompt=T(
                                "Why is a 2000-line pull request harder to review well than four 500-line ones?",
                                "Pourquoi une pull request de 2000 lignes est-elle plus difficile à bien réviser que quatre de 500 ?",
                                "لماذا يصعب مراجعة طلب دمج من 2000 سطر أكثر من أربعة من 500 سطر؟",
                            ),
                            hint=T(
                                "Think about attention, and about how one change relates to another.",
                                "Pensez à l'attention, et à la façon dont les changements se rapportent entre eux.",
                                "فكّر في الانتباه، وفي كيفية ارتباط التغييرات ببعضها.",
                            ),
                            explanation=T(
                                "Attention does not scale with size: reviewers skim large diffs, unrelated changes hide each other, and a defect in the middle is far easier to miss.",
                                "L'attention ne suit pas la taille : on survole les gros diffs, les changements sans rapport se masquent, et un défaut au milieu passe bien plus facilement inaperçu.",
                                "الانتباه لا ينمو مع الحجم: يمرّ المراجعون سريعًا على الفروق الكبيرة، وتخفي التغييرات غير المترابطة بعضها، ويسهل جدًا تفويت خلل في وسطها.",
                            ),
                            keywords=[
                                ["attention", "focus", "skim", "attention", "survole", "انتباه", "تركيز"],
                                ["miss", "missed", "hidden", "hide", "manquer", "masqué", "تفويت", "يخفي"],
                            ],
                            reference_answer="Because attention does not scale with size: reviewers skim a huge diff, unrelated changes hide each other, and defects are easily missed.",
                        ),
                    ],
                ),
            ],
        ),
        Module(
            slug="testing-strategy",
            title=T("Testing Strategy", "Stratégie de Test", "استراتيجية الاختبار"),
            description=T(
                "What to test, at which level, and what a test suite is really for.",
                "Quoi tester, à quel niveau, et à quoi sert vraiment une suite de tests.",
                "ماذا تختبر، وعلى أيّ مستوى، وما الغرض الحقيقي من مجموعة الاختبارات.",
            ),
            lessons=[
                Lesson(
                    slug="testing-pyramid",
                    minutes=35,
                    xp=60,
                    difficulty=D.intermediate,
                    title=T("Unit, Integration and End-to-End Tests", "Tests Unitaires, d'Intégration et de Bout en Bout", "اختبارات الوحدة والتكامل والطرف إلى الطرف"),
                    story=T(
                        "A suite that takes forty minutes and fails at random is worse than no suite at all — nobody will run it.",
                        "Une suite qui prend quarante minutes et échoue au hasard est pire que rien : personne ne l'exécutera.",
                        "مجموعة اختبارات تستغرق أربعين دقيقة وتفشل عشوائيًا أسوأ من لا شيء — إذ لن يشغّلها أحد.",
                    ),
                    objective=T(
                        "Choose the right test level for a given risk and keep the suite fast and trustworthy.",
                        "Choisir le bon niveau de test pour un risque donné et garder la suite rapide et fiable.",
                        "اختيار مستوى الاختبار المناسب لكلّ خطر، وإبقاء المجموعة سريعة وجديرة بالثقة.",
                    ),
                    skills=T(
                        "Unit tests, integration tests, end-to-end tests, flaky tests, coverage",
                        "Tests unitaires, d'intégration, de bout en bout, tests instables, couverture",
                        "اختبارات الوحدة، اختبارات التكامل، اختبارات الطرف إلى الطرف، الاختبارات المتقلّبة، التغطية",
                    ),
                    blocks=[
                        Text(
                            T(
                                "**Unit tests** check one function with everything else stubbed out: milliseconds each, so you can have thousands. **Integration tests** check that two real parts agree — your code and the real database, say. **End-to-end tests** drive the whole product like a user. Each level up is slower, flakier and more valuable per test, so you want many of the first and few of the last.",
                                "Les **tests unitaires** vérifient une fonction, tout le reste étant simulé : quelques millisecondes chacun, on peut en avoir des milliers. Les **tests d'intégration** vérifient que deux vraies parties s'accordent — votre code et la vraie base de données. Les **tests de bout en bout** pilotent tout le produit comme un utilisateur. Chaque niveau est plus lent, plus instable et plus précieux par test : beaucoup des premiers, peu des derniers.",
                                "**اختبارات الوحدة** تفحص دالّة واحدة مع تعطيل كلّ ما عداها: أجزاء من الثانية لكلّ اختبار، فيمكن أن تملك آلافًا منها. و**اختبارات التكامل** تفحص توافق جزأين حقيقيّين — كودك وقاعدة البيانات الحقيقية مثلًا. و**اختبارات الطرف إلى الطرف** تقود المنتج كلّه كما يفعل المستخدم. وكلّ مستوى أعلى أبطأ وأكثر تقلّبًا وأثمن لكلّ اختبار، فالمطلوب كثير من الأوّل وقليل من الأخير.",
                            )
                        ),
                        Text(
                            T(
                                "A **flaky** test — one that passes and fails on the same code — is worse than a missing test, because it trains the team to ignore red. Fix it or delete it the day you find it. And treat **coverage** as a hint, not a target: 100% coverage of code that asserts nothing meaningful proves only that the lines executed.",
                                "Un test **instable** — qui passe et échoue sur le même code — est pire qu'un test absent : il apprend à l'équipe à ignorer le rouge. Corrigez-le ou supprimez-le le jour où vous le trouvez. Et traitez la **couverture** comme un indice, pas un objectif : 100 % de couverture sans assertion utile prouve seulement que les lignes ont été exécutées.",
                                "الاختبار **المتقلّب** — الذي ينجح ويفشل على الكود نفسه — أسوأ من غياب الاختبار، لأنّه يدرّب الفريق على تجاهل اللون الأحمر. أصلحه أو احذفه يوم اكتشافه. وعامل **التغطية** كمؤشّر لا كهدف: فتغطية 100% لكود لا يؤكّد شيئًا ذا معنى لا تثبت إلّا أنّ الأسطر نُفّذت.",
                            )
                        ),
                        Code(
                            T(
                                "The same behaviour, checked at two levels:",
                                "Le même comportement, vérifié à deux niveaux :",
                                "السلوك نفسه مفحوصًا على مستويين:",
                            ),
                            "# Unit: the rule, in isolation - runs in microseconds\n"
                            "def test_password_too_short_is_rejected():\n"
                            "    assert is_valid_password('abc') is False\n\n"
                            "# Integration: the rule as the API really applies it\n"
                            "async def test_register_rejects_short_password(client):\n"
                            "    response = await client.post('/auth/register', json={\n"
                            "        'email': 'a@example.com', 'username': 'amina', 'password': 'abc',\n"
                            "    })\n"
                            "    assert response.status_code == 422",
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "Why should a test suite have many unit tests and few end-to-end tests?",
                                "Pourquoi une suite doit-elle avoir beaucoup de tests unitaires et peu de tests de bout en bout ?",
                                "لماذا يجب أن تحوي مجموعة الاختبارات كثيرًا من اختبارات الوحدة وقليلًا من اختبارات الطرف إلى الطرف؟",
                            ),
                            hint=T("Consider speed and reliability.", "Pensez vitesse et fiabilité.", "فكّر في السرعة والموثوقية."),
                            explanation=T(
                                "Unit tests are fast and pinpoint the failure; end-to-end tests are slow and flaky, so a few well-chosen ones give confidence without ruining the feedback loop.",
                                "Les tests unitaires sont rapides et localisent l'échec ; ceux de bout en bout sont lents et instables : quelques-uns bien choisis donnent confiance sans détruire la boucle de retour.",
                                "اختبارات الوحدة سريعة وتحدّد موضع الفشل، أمّا اختبارات الطرف إلى الطرف فبطيئة ومتقلّبة، فيكفي عدد قليل مختار بعناية لمنح الثقة دون تدمير حلقة التغذية الراجعة.",
                            ),
                            options=[
                                Option(T("End-to-end tests cannot find real bugs", "Les tests de bout en bout ne trouvent pas de vrais bugs", "اختبارات الطرف إلى الطرف لا تجد أخطاء حقيقية")),
                                Option(
                                    T(
                                        "Unit tests are fast and pinpoint failures; E2E tests are slow and flaky",
                                        "Les tests unitaires sont rapides et localisent l'échec ; les E2E sont lents et instables",
                                        "اختبارات الوحدة سريعة وتحدّد الفشل، واختبارات E2E بطيئة ومتقلّبة",
                                    ),
                                    correct=True,
                                ),
                                Option(T("Unit tests give 100% coverage automatically", "Les tests unitaires donnent 100 % de couverture", "اختبارات الوحدة تعطي تغطية 100% تلقائيًا")),
                                Option(T("End-to-end tests do not need maintenance", "Les tests E2E ne demandent pas de maintenance", "اختبارات E2E لا تحتاج صيانة")),
                            ],
                        ),
                        MCQ(
                            prompt=T(
                                "A test fails once in every ten runs with no code change. What should you do?",
                                "Un test échoue une fois sur dix sans changement de code. Que faire ?",
                                "اختبار يفشل مرّة من كلّ عشر مرّات دون تغيير في الكود. ماذا تفعل؟",
                            ),
                            hint=T("What does an unreliable red signal train the team to do?", "Qu'apprend un rouge peu fiable à l'équipe ?", "ما الذي يعلّمه الإشارة الحمراء غير الموثوقة للفريق؟"),
                            explanation=T(
                                "A flaky test teaches everyone to ignore failures, so it must be fixed or removed rather than re-run until green.",
                                "Un test instable apprend à tous à ignorer les échecs : il faut le corriger ou le supprimer, pas le relancer jusqu'au vert.",
                                "الاختبار المتقلّب يعلّم الجميع تجاهل الإخفاقات، فيجب إصلاحه أو حذفه لا إعادة تشغيله حتى يصير أخضر.",
                            ),
                            options=[
                                Option(T("Re-run it until it passes", "Le relancer jusqu'à ce qu'il passe", "أعِد تشغيله حتى ينجح")),
                                Option(T("Investigate and fix it, or delete it", "L'analyser et le corriger, ou le supprimer", "حقّق فيه وأصلحه، أو احذفه"), correct=True),
                                Option(T("Increase the test timeout and move on", "Augmenter le délai et passer à autre chose", "زد المهلة وامضِ قدمًا")),
                                Option(T("Add ten more tests to compensate", "Ajouter dix tests de plus pour compenser", "أضف عشرة اختبارات أخرى للتعويض")),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        Module(
            slug="architecture-and-delivery",
            title=T("Architecture and Delivery", "Architecture et Livraison", "المعمارية والتسليم"),
            description=T(
                "Layering an application, designing an API, and shipping it repeatedly.",
                "Structurer une application en couches, concevoir une API, et la livrer régulièrement.",
                "بناء التطبيق بطبقات، وتصميم واجهة برمجة، وتسليمه بانتظام.",
            ),
            lessons=[
                Lesson(
                    slug="layered-architecture",
                    minutes=35,
                    xp=60,
                    difficulty=D.intermediate,
                    title=T("Layered Architecture", "Architecture en Couches", "المعمارية الطبقية"),
                    story=T(
                        "When business rules live inside the HTTP handler, you cannot test them, reuse them, or find them.",
                        "Quand les règles métier vivent dans le gestionnaire HTTP, on ne peut ni les tester, ni les réutiliser, ni les trouver.",
                        "حين تعيش قواعد العمل داخل معالج HTTP، لا يمكنك اختبارها ولا إعادة استخدامها ولا حتى إيجادها.",
                    ),
                    objective=T(
                        "Separate presentation, business logic and data access, and justify why the dependencies point inwards.",
                        "Séparer présentation, logique métier et accès aux données, et justifier pourquoi les dépendances pointent vers l'intérieur.",
                        "الفصل بين العرض ومنطق العمل والوصول إلى البيانات، وتبرير اتّجاه التبعيّات نحو الداخل.",
                    ),
                    skills=T(
                        "Layers, separation of concerns, dependency direction, services",
                        "Couches, séparation des responsabilités, direction des dépendances, services",
                        "الطبقات، فصل الاهتمامات، اتّجاه التبعيّات، الخدمات",
                    ),
                    blocks=[
                        Text(
                            T(
                                "Three layers cover most applications. **Presentation** (an HTTP route, a screen) turns requests into calls and results into responses. **Domain / services** holds the rules — what is allowed, what a total is, when a lesson counts as complete. **Data access** persists and loads. AtlasCode's own backend is laid out this way: `api/` calls `services/`, which uses `models/`.",
                                "Trois couches couvrent la plupart des applications. La **présentation** (route HTTP, écran) transforme les requêtes en appels et les résultats en réponses. Le **domaine / services** contient les règles — ce qui est permis, comment se calcule un total, quand une leçon est terminée. L'**accès aux données** persiste et charge. Le backend d'AtlasCode est organisé ainsi : `api/` appelle `services/`, qui utilise `models/`.",
                                "ثلاث طبقات تغطّي معظم التطبيقات. **العرض** (مسار HTTP أو شاشة) يحوّل الطلبات إلى استدعاءات والنتائج إلى استجابات. و**المجال/الخدمات** يحمل القواعد — ما المسموح، وكيف يُحسب المجموع، ومتى يُعدّ الدرس مكتملًا. و**الوصول إلى البيانات** يحفظ ويحمّل. وخادم AtlasCode نفسه مبنيّ هكذا: `api/` تستدعي `services/` التي تستخدم `models/`.",
                            )
                        ),
                        Code(
                            T(
                                "The same feature, before and after the rules move out of the route:",
                                "La même fonctionnalité, avant et après la sortie des règles hors de la route :",
                                "الميزة نفسها قبل نقل القواعد خارج المسار وبعده:",
                            ),
                            "# Before: the rule is trapped inside an HTTP handler\n"
                            "@router.post('/exercises/{id}/submit')\n"
                            "async def submit(id, body, db):\n"
                            "    if body.answer == correct_answer:      # business rule, unreachable\n"
                            "        profile.xp += 10                    # from anywhere else\n"
                            "    ...\n\n"
                            "# After: the route is thin, the rule is a callable, testable unit\n"
                            "# services/grading.py\n"
                            "def grade(exercise, answer) -> GradingResult:\n"
                            "    ...\n\n"
                            "@router.post('/exercises/{id}/submit')\n"
                            "async def submit(id, body, db):\n"
                            "    result = grade(exercise, body)\n"
                            "    return result",
                        ),
                        Text(
                            T(
                                "The rule that keeps layers from collapsing: **dependencies point inwards**. The domain must not import the web framework or the database driver. Then the rules can be tested with no server and no database, and swapping either one does not touch a single line of business logic.",
                                "La règle qui empêche les couches de s'effondrer : **les dépendances pointent vers l'intérieur**. Le domaine ne doit importer ni le framework web ni le pilote de base de données. Les règles se testent alors sans serveur ni base, et changer l'un ou l'autre ne touche aucune ligne de logique métier.",
                                "القاعدة التي تمنع انهيار الطبقات: **تتّجه التبعيّات نحو الداخل**. فلا يجوز أن يستورد المجال إطار الويب ولا مشغّل قاعدة البيانات. عندئذٍ تُختبَر القواعد بلا خادم ولا قاعدة بيانات، ولا يمسّ تبديل أيّ منهما سطرًا واحدًا من منطق العمل.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "Which layer should contain the rule \"a lesson is complete when all its exercises are solved\"?",
                                "Quelle couche doit contenir la règle « une leçon est terminée quand tous ses exercices sont résolus » ?",
                                "أيّ طبقة يجب أن تحوي قاعدة «يكتمل الدرس عند حلّ كلّ تمارينه»؟",
                            ),
                            hint=T("Would that rule still be true in a mobile app with no HTTP?", "Cette règle serait-elle vraie dans une app mobile sans HTTP ?", "هل تبقى هذه القاعدة صحيحة في تطبيق جوّال بلا HTTP؟"),
                            explanation=T(
                                "It is a business rule, true regardless of transport or storage, so it belongs in the domain/service layer.",
                                "C'est une règle métier, vraie indépendamment du transport ou du stockage : elle appartient à la couche domaine/service.",
                                "إنّها قاعدة عمل صحيحة بغضّ النظر عن وسيلة النقل أو التخزين، فمكانها طبقة المجال/الخدمات.",
                            ),
                            options=[
                                Option(T("The HTTP route handler", "Le gestionnaire de route HTTP", "معالج مسار HTTP")),
                                Option(T("The domain/service layer", "La couche domaine/service", "طبقة المجال/الخدمات"), correct=True),
                                Option(T("The database schema", "Le schéma de base de données", "مخطّط قاعدة البيانات")),
                                Option(T("The frontend component", "Le composant frontend", "مكوّن الواجهة الأمامية")),
                            ],
                        ),
                        ShortAnswer(
                            prompt=T(
                                "Why must the domain layer not import the web framework? One sentence.",
                                "Pourquoi la couche domaine ne doit-elle pas importer le framework web ? Une phrase.",
                                "لماذا يجب ألّا تستورد طبقة المجال إطار الويب؟ جملة واحدة.",
                            ),
                            hint=T(
                                "Think about testing the rules, and about replacing the framework.",
                                "Pensez au test des règles, et au remplacement du framework.",
                                "فكّر في اختبار القواعد وفي استبدال الإطار.",
                            ),
                            explanation=T(
                                "Keeping the domain framework-free means the rules can be tested without a server and the framework can be replaced without touching business logic.",
                                "Un domaine sans framework permet de tester les règles sans serveur et de remplacer le framework sans toucher à la logique métier.",
                                "إبقاء المجال خاليًا من الإطار يتيح اختبار القواعد بلا خادم واستبدال الإطار دون المساس بمنطق العمل.",
                            ),
                            keywords=[
                                ["test", "tested", "testable", "tester", "اختبار", "اختبارها"],
                                ["replace", "swap", "change", "remplacer", "استبدال", "تغيير"],
                            ],
                            reference_answer="So the rules can be tested without a running server and the framework can be replaced later without changing any business logic.",
                        ),
                    ],
                ),
                Lesson(
                    slug="apis-and-ci-cd",
                    minutes=35,
                    xp=65,
                    difficulty=D.intermediate,
                    title=T("REST APIs and CI/CD", "APIs REST et CI/CD", "واجهات REST وCI/CD"),
                    story=T(
                        "An API is a promise to strangers. A pipeline is what stops you from breaking it.",
                        "Une API est une promesse faite à des inconnus. Un pipeline est ce qui vous empêche de la rompre.",
                        "الواجهة البرمجية وعدٌ لغرباء. وخطّ الإنتاج هو ما يمنعك من نقضه.",
                    ),
                    objective=T(
                        "Design REST endpoints with correct verbs and status codes, and describe what a CI pipeline must check.",
                        "Concevoir des endpoints REST avec les bons verbes et codes de statut, et décrire ce qu'un pipeline CI doit vérifier.",
                        "تصميم نقاط REST بأفعال ورموز حالة صحيحة، ووصف ما يجب أن يفحصه خطّ التكامل المستمرّ.",
                    ),
                    skills=T(
                        "REST resources, HTTP verbs, status codes, idempotency, CI, CD",
                        "Ressources REST, verbes HTTP, codes de statut, idempotence, CI, CD",
                        "موارد REST، أفعال HTTP، رموز الحالة، الخاصّية التكرارية، CI، CD",
                    ),
                    blocks=[
                        Text(
                            T(
                                "REST models the system as **resources** with **nouns** for paths and **verbs** for actions. `GET /courses/12` reads, `POST /courses` creates, `PATCH /courses/12` updates part, `DELETE /courses/12` removes. `GET /getCourse?id=12` is not wrong so much as it throws away everything the verb already told you.",
                                "REST modélise le système en **ressources**, avec des **noms** pour les chemins et des **verbes** pour les actions. `GET /courses/12` lit, `POST /courses` crée, `PATCH /courses/12` met à jour partiellement, `DELETE /courses/12` supprime. `GET /getCourse?id=12` n'est pas tant faux qu'il jette ce que le verbe disait déjà.",
                                "يُنمذج REST النظام على شكل **موارد**، فالمسارات **أسماء** والأفعال **أفعال HTTP**. فـ`GET /courses/12` يقرأ، و`POST /courses` ينشئ، و`PATCH /courses/12` يحدّث جزئيًا، و`DELETE /courses/12` يحذف. أمّا `GET /getCourse?id=12` فليس خطأً بقدر ما هو إهدار لما قاله الفعل أصلًا.",
                            )
                        ),
                        Text(
                            T(
                                "Status codes are part of the contract: **200** fine, **201** created, **204** done with nothing to return, **400** the request is malformed, **401** not authenticated, **403** authenticated but not allowed, **404** no such resource, **409** conflicts with current state, **500** we broke. Returning 200 with `{\"error\": ...}` inside forces every client to parse the body to find out whether it worked.",
                                "Les codes de statut font partie du contrat : **200** ok, **201** créé, **204** fait sans contenu, **400** requête malformée, **401** non authentifié, **403** authentifié mais non autorisé, **404** ressource inexistante, **409** conflit avec l'état actuel, **500** panne côté serveur. Renvoyer 200 avec `{\"error\": ...}` oblige chaque client à lire le corps pour savoir si ça a marché.",
                                "رموز الحالة جزء من العقد: **200** تمام، و**201** أُنشئ، و**204** تمّ دون محتوى، و**400** الطلب مشوّه، و**401** غير موثَّق، و**403** موثَّق لكن غير مسموح، و**404** لا مورد كهذا، و**409** تعارض مع الحالة الراهنة، و**500** عطل لدينا. وإرجاع 200 مع `{\"error\": ...}` يُجبر كلّ عميل على قراءة الجسم ليعرف هل نجح الطلب.",
                            )
                        ),
                        Code(
                            T(
                                "A pipeline is just the checks you would run by hand, run automatically on every push:",
                                "Un pipeline n'est que les vérifications qu'on ferait à la main, exécutées automatiquement à chaque push :",
                                "خطّ الإنتاج ليس إلّا الفحوص التي كنت ستجريها يدويًا، تُنفَّذ آليًا عند كلّ دفع:",
                            ),
                            "# .github/workflows/ci.yml  (the shape, not the whole file)\n"
                            "on: [push, pull_request]\n"
                            "jobs:\n"
                            "  check:\n"
                            "    steps:\n"
                            "      - run: pip install -r requirements.txt\n"
                            "      - run: ruff check .          # lint\n"
                            "      - run: mypy app             # types\n"
                            "      - run: pytest               # tests\n"
                            "      - run: npm run build        # the frontend must compile\n\n"
                            "# CI  = every push is verified.\n"
                            "# CD  = a verified main is deployed automatically.",
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "A client requests a course id that does not exist. Which status code?",
                                "Un client demande un identifiant de cours inexistant. Quel code de statut ?",
                                "يطلب عميل معرّف مقرّر غير موجود. أيّ رمز حالة؟",
                            ),
                            hint=T("The request was fine; the resource is not there.", "La requête était correcte ; la ressource n'existe pas.", "الطلب سليم، لكنّ المورد غير موجود."),
                            explanation=T(
                                "404 means the resource does not exist. 400 would say the request itself was malformed, which it was not.",
                                "404 signifie que la ressource n'existe pas. 400 dirait que la requête elle-même est malformée, ce qui n'est pas le cas.",
                                "‏404 تعني أنّ المورد غير موجود، أمّا 400 فتعني أنّ الطلب نفسه مشوّه وهو ليس كذلك.",
                            ),
                            options=[
                                Option(T("200", "200", "200")),
                                Option(T("400", "400", "400")),
                                Option(T("404", "404", "404"), correct=True),
                                Option(T("500", "500", "500")),
                            ],
                        ),
                        FillBlank(
                            prompt=T(
                                "Complete the REST call that updates part of course 12.",
                                "Complétez l'appel REST qui met à jour partiellement le cours 12.",
                                "أكمل نداء REST الذي يحدّث جزءًا من المقرّر 12.",
                            ),
                            hint=T("Partial update uses PATCH; the path is a noun.", "Une mise à jour partielle utilise PATCH ; le chemin est un nom.", "التحديث الجزئي يستخدم PATCH، والمسار اسم."),
                            explanation=T(
                                "`PATCH /courses/12` names the resource and lets the verb say what is being done to it.",
                                "`PATCH /courses/12` nomme la ressource et laisse le verbe dire ce qu'on lui fait.",
                                "‏`PATCH /courses/12` تسمّي المورد وتترك للفعل التعبير عمّا يُفعل به.",
                            ),
                            snippet="____ /____/12",
                            answers=["PATCH", "courses"],
                        ),
                    ],
                ),
            ],
        ),
    ],
)


async def seed_software_engineering(db, order: int) -> int:
    print("Seeding Software Engineering...")
    return await seed_course(db, SOFTWARE_ENGINEERING, order)
