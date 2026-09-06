"""Stage 8 — Advanced Computer Science.

The material that only makes sense once the foundations are in place:
what an operating system actually does with the hardware, how the hardware
executes anything at all, and what changes when one machine becomes many.
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

OPERATING_SYSTEMS = CourseSpec(
    slug="operating-systems",
    stage=8,
    track="advanced",
    icon="⚙️",
    difficulty=D.advanced,
    estimated_hours=12,
    prerequisite_slug="computer-systems",
    title=T("Operating Systems", "Systèmes d'Exploitation", "أنظمة التشغيل"),
    description=T(
        "The program that runs the others: processes and threads, scheduling, virtual memory, concurrency and the file system.",
        "Le programme qui exécute les autres : processus et threads, ordonnancement, mémoire virtuelle, concurrence et système de fichiers.",
        "البرنامج الذي يشغّل البقيّة: العمليات والخيوط، والجدولة، والذاكرة الافتراضية، والتزامن، ونظام الملفّات.",
    ),
    skills=T(
        "Processes, threads, scheduling, context switching, virtual memory, deadlock, race conditions, file systems",
        "Processus, threads, ordonnancement, changement de contexte, mémoire virtuelle, interblocage, conditions de course, systèmes de fichiers",
        "العمليات، الخيوط، الجدولة، تبديل السياق، الذاكرة الافتراضية، الجمود، حالات السباق، أنظمة الملفّات",
    ),
    modules=[
        Module(
            slug="processes-and-scheduling",
            title=T("Processes and Scheduling", "Processus et Ordonnancement", "العمليات والجدولة"),
            description=T(
                "How one processor appears to run twenty programs at once.",
                "Comment un seul processeur semble exécuter vingt programmes à la fois.",
                "كيف يبدو أنّ معالجًا واحدًا يشغّل عشرين برنامجًا في آن.",
            ),
            lessons=[
                Lesson(
                    slug="processes-and-threads",
                    minutes=35,
                    xp=65,
                    difficulty=D.advanced,
                    title=T("Processes and Threads", "Processus et Threads", "العمليات والخيوط"),
                    story=T(
                        "One crashed browser tab does not take the browser with it. That is an operating system decision, not luck.",
                        "Un onglet planté n'entraîne pas tout le navigateur. C'est une décision du système, pas de la chance.",
                        "تبويب متعطّل لا يُسقط المتصفّح كلّه. وهذا قرار من نظام التشغيل لا حظّ.",
                    ),
                    objective=T(
                        "Distinguish processes from threads and explain what isolation costs and buys.",
                        "Distinguer processus et threads et expliquer ce que coûte et rapporte l'isolation.",
                        "التمييز بين العمليات والخيوط، وشرح ما يكلّفه العزل وما يمنحه.",
                    ),
                    skills=T(
                        "Processes, threads, address space, isolation, context switching, IPC",
                        "Processus, threads, espace d'adressage, isolation, changement de contexte, IPC",
                        "العمليات، الخيوط، فضاء العناوين، العزل، تبديل السياق، الاتّصال بين العمليات",
                    ),
                    blocks=[
                        Text(
                            T(
                                "A **process** is a running program with its own private address space. Nothing it does can touch another process's memory — which is why one crash stays local. A **thread** is a line of execution *inside* a process, sharing that memory with its siblings: cheap to create and to switch between, and able to corrupt each other's data precisely because the memory is shared.",
                                "Un **processus** est un programme en cours avec son propre espace d'adressage privé. Rien de ce qu'il fait ne touche la mémoire d'un autre — d'où le confinement des plantages. Un **thread** est un fil d'exécution *dans* un processus, partageant cette mémoire avec ses frères : peu coûteux à créer et à commuter, et capable de corrompre leurs données précisément parce que la mémoire est partagée.",
                                "**العملية** برنامج قيد التشغيل له فضاء عناوين خاصّ به. ولا شيء ممّا تفعله يمسّ ذاكرة عملية أخرى — ولهذا يبقى الانهيار محلّيًا. أمّا **الخيط** فهو خطّ تنفيذ *داخل* عملية يتشارك تلك الذاكرة مع إخوته: رخيص الإنشاء والتبديل، وقادر على إفساد بيانات إخوته لأنّ الذاكرة مشتركة بالضبط.",
                            )
                        ),
                        Text(
                            T(
                                "Choosing between them is choosing what you fear more. Separate processes give safety and let a crash or a compromise stay contained; they pay for it in memory and in the cost of passing messages between them. Threads give speed and easy sharing; they pay for it with race conditions, locks and bugs that appear once a week and never in the debugger.",
                                "Choisir entre les deux, c'est choisir ce que l'on craint le plus. Des processus séparés apportent la sûreté et confinent plantages et compromissions ; ils le paient en mémoire et en coût de communication. Les threads apportent vitesse et partage facile ; ils le paient en conditions de course, verrous et bugs qui surviennent une fois par semaine et jamais dans le débogueur.",
                                "الاختيار بينهما هو اختيار ما تخشاه أكثر. فالعمليات المنفصلة تمنح الأمان وتحصر الانهيار أو الاختراق، وتدفع ثمن ذلك ذاكرةً وكلفةَ تبادل الرسائل. أمّا الخيوط فتمنح السرعة وسهولة المشاركة، وتدفع الثمن حالاتِ سباق وأقفالًا وأخطاءً تظهر مرّة في الأسبوع ولا تظهر في المصحّح أبدًا.",
                            )
                        ),
                        Code(
                            T(
                                "A **context switch** is the operating system saving one execution's state and restoring another's:",
                                "Un **changement de contexte** est la sauvegarde de l'état d'une exécution et la restauration d'une autre :",
                                "**تبديل السياق** هو حفظ النظام لحالة تنفيذ واستعادته لأخرى:",
                            ),
                            "# What the OS saves and restores on every switch:\n"
                            "#   - the program counter (which instruction is next)\n"
                            "#   - the CPU registers\n"
                            "#   - the stack pointer\n"
                            "#   - for a PROCESS switch, also the memory mappings, which\n"
                            "#     invalidates cached address translations -- this is why a\n"
                            "#     process switch costs noticeably more than a thread switch.\n\n"
                            "# Twenty programs on four cores are not running simultaneously.\n"
                            "# They are being switched between thousands of times a second,\n"
                            "# fast enough that a human cannot perceive the gaps.",
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "What is the main difference between two threads and two processes?",
                                "Quelle est la différence principale entre deux threads et deux processus ?",
                                "ما الفرق الرئيسي بين خيطين وعمليّتين؟",
                            ),
                            hint=T("Think about memory.", "Pensez à la mémoire.", "فكّر في الذاكرة."),
                            explanation=T(
                                "Threads share one address space; processes each have their own, which is what provides isolation.",
                                "Les threads partagent un espace d'adressage ; chaque processus a le sien, d'où l'isolation.",
                                "الخيوط تتشارك فضاء عناوين واحدًا، ولكلّ عملية فضاؤها الخاصّ، وهذا مصدر العزل.",
                            ),
                            options=[
                                Option(T("Threads are always faster to compute", "Les threads calculent toujours plus vite", "الخيوط أسرع حسابًا دائمًا")),
                                Option(
                                    T(
                                        "Threads share memory; processes have separate address spaces",
                                        "Les threads partagent la mémoire ; les processus ont des espaces séparés",
                                        "الخيوط تتشارك الذاكرة، وللعمليات فضاءات عناوين منفصلة",
                                    ),
                                    correct=True,
                                ),
                                Option(T("Processes cannot communicate at all", "Les processus ne peuvent pas communiquer", "لا تستطيع العمليات التواصل إطلاقًا")),
                                Option(T("Only processes can be scheduled", "Seuls les processus sont ordonnançables", "العمليات وحدها قابلة للجدولة")),
                            ],
                        ),
                        MCQ(
                            prompt=T(
                                "A browser renders each tab in its own process. What is the main reason?",
                                "Un navigateur exécute chaque onglet dans son propre processus. Pourquoi principalement ?",
                                "يشغّل المتصفّح كلّ تبويب في عملية خاصّة. ما السبب الرئيسي؟",
                            ),
                            hint=T("What does a separate address space prevent?", "Qu'empêche un espace d'adressage séparé ?", "ماذا يمنع فضاء العناوين المنفصل؟"),
                            explanation=T(
                                "Isolation: a crash or a compromised page cannot reach the memory of other tabs or of the browser itself.",
                                "L'isolation : un plantage ou une page compromise n'atteint pas la mémoire des autres onglets ni du navigateur.",
                                "العزل: فالانهيار أو الصفحة المخترقة لا يصل إلى ذاكرة التبويبات الأخرى ولا إلى المتصفّح نفسه.",
                            ),
                            options=[
                                Option(T("It uses less memory overall", "Cela consomme moins de mémoire", "يستهلك ذاكرة أقلّ إجمالًا")),
                                Option(
                                    T(
                                        "A crashed or compromised tab cannot affect the others",
                                        "Un onglet planté ou compromis n'affecte pas les autres",
                                        "التبويب المتعطّل أو المخترق لا يؤثّر في غيره",
                                    ),
                                    correct=True,
                                ),
                                Option(T("Processes start faster than threads", "Les processus démarrent plus vite que les threads", "العمليات تبدأ أسرع من الخيوط")),
                                Option(T("It avoids the need for scheduling", "Cela évite l'ordonnancement", "يلغي الحاجة إلى الجدولة")),
                            ],
                        ),
                    ],
                ),
                Lesson(
                    slug="concurrency-hazards",
                    minutes=40,
                    xp=70,
                    difficulty=D.advanced,
                    title=T("Race Conditions and Deadlock", "Conditions de Course et Interblocage", "حالات السباق والجمود"),
                    story=T(
                        "Two people withdraw from the same account at the same instant, and the balance ends up wrong. The code looked fine.",
                        "Deux personnes retirent du même compte au même instant, et le solde est faux. Le code semblait correct.",
                        "شخصان يسحبان من الحساب نفسه في اللحظة نفسها، فينتهي الرصيد خاطئًا. وقد بدا الكود سليمًا.",
                    ),
                    objective=T(
                        "Recognise a race condition, protect a critical section, and explain how deadlock is avoided.",
                        "Reconnaître une condition de course, protéger une section critique, et expliquer comment éviter l'interblocage.",
                        "التعرّف على حالة السباق، وحماية المقطع الحرج، وشرح كيفية تفادي الجمود.",
                    ),
                    skills=T(
                        "Race conditions, critical sections, mutexes, atomicity, deadlock, lock ordering",
                        "Conditions de course, sections critiques, mutex, atomicité, interblocage, ordre des verrous",
                        "حالات السباق، المقاطع الحرجة، الأقفال، الذرّية، الجمود، ترتيب الأقفال",
                    ),
                    blocks=[
                        Text(
                            T(
                                "A **race condition** is a bug whose outcome depends on timing. `balance = balance - 100` looks like one action but is three: read, subtract, write. If two threads interleave between the read and the write, one withdrawal disappears — and the bug shows up under load, never while you are watching.",
                                "Une **condition de course** est un bug dont le résultat dépend du timing. `solde = solde - 100` paraît être une action mais en fait trois : lire, soustraire, écrire. Si deux threads s'entrelacent entre la lecture et l'écriture, un retrait disparaît — et le bug apparaît en charge, jamais sous vos yeux.",
                                "**حالة السباق** خلل تتوقّف نتيجته على التوقيت. فـ`balance = balance - 100` تبدو فعلًا واحدًا لكنّها ثلاثة: قراءة وطرح وكتابة. وإذا تداخل خيطان بين القراءة والكتابة اختفى أحد السحبين — ويظهر الخلل تحت الحمل ولا يظهر أبدًا وأنت تراقب.",
                            )
                        ),
                        Code(
                            T(
                                "The fix is a **lock** around the **critical section** — the smallest region that must not be interrupted:",
                                "Le correctif est un **verrou** autour de la **section critique** — la plus petite région ininterruptible :",
                                "الحلّ **قفل** حول **المقطع الحرج** — أصغر منطقة يجب ألّا تُقاطَع:",
                            ),
                            "import threading\n\n"
                            "balance = 1000\n"
                            "lock = threading.Lock()\n\n"
                            "def withdraw(amount):\n"
                            "    global balance\n"
                            "    with lock:                 # only one thread inside at a time\n"
                            "        if balance >= amount:  # check and update are now one\n"
                            "            balance -= amount  # indivisible step\n\n"
                            "# Hold the lock for as short a time as possible: everything\n"
                            "# inside it is serialised, so a lock around slow work turns a\n"
                            "# concurrent program back into a sequential one.",
                        ),
                        Text(
                            T(
                                "**Deadlock** is the opposite failure: thread A holds lock 1 and waits for lock 2, thread B holds lock 2 and waits for lock 1, and neither ever moves again. The standard prevention is a **global lock order** — every thread acquires locks in the same agreed sequence, which makes the circular wait impossible by construction.",
                                "L'**interblocage** est la panne inverse : le thread A détient le verrou 1 et attend le 2, B détient le 2 et attend le 1, et plus rien ne bouge. La prévention standard est un **ordre global des verrous** — chaque thread les acquiert dans la même séquence convenue, rendant l'attente circulaire impossible par construction.",
                                "**الجمود** هو الفشل المعاكس: الخيط A يحمل القفل 1 وينتظر القفل 2، والخيط B يحمل 2 وينتظر 1، فلا يتحرّك أيّ منهما أبدًا. والوقاية المعيارية **ترتيب عامّ للأقفال** — إذ يحصل كلّ خيط على الأقفال بالتسلسل المتّفق عليه نفسه، فيصير الانتظار الدائري مستحيلًا بالبناء.",
                            )
                        ),
                        ExamTip(
                            T(
                                "\"It works on my machine\" is especially untrustworthy for concurrency bugs: your machine has different core counts, timings and load. A race condition that never triggers in development can be reliable in production.",
                                "« Ça marche chez moi » est particulièrement peu fiable pour les bugs de concurrence : votre machine a d'autres cœurs, timings et charges. Une condition de course jamais déclenchée en développement peut être fiable en production.",
                                "عبارة «يعمل على جهازي» غير جديرة بالثقة خصوصًا في أخطاء التزامن: فجهازك له عدد أنوية وتوقيتات وحمل مختلفة. وحالة سباق لا تُستثار أبدًا في التطوير قد تكون منتظمة في الإنتاج.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "Why is `balance = balance - 100` unsafe when two threads run it at once?",
                                "Pourquoi `solde = solde - 100` est-il dangereux si deux threads l'exécutent en même temps ?",
                                "لماذا تكون `balance = balance - 100` غير آمنة عند تنفيذ خيطين لها معًا؟",
                            ),
                            hint=T("How many machine-level steps is that one line?", "Combien d'étapes machine représente cette ligne ?", "كم خطوة على مستوى الآلة يمثّلها هذا السطر؟"),
                            explanation=T(
                                "It is read, modify, write. A second thread can read the old value between the first thread's read and write, so one update is lost.",
                                "C'est lire, modifier, écrire. Un second thread peut lire l'ancienne valeur entre la lecture et l'écriture du premier : une mise à jour est perdue.",
                                "إنّها قراءة ثمّ تعديل ثمّ كتابة. ويمكن لخيط ثانٍ قراءة القيمة القديمة بين قراءة الأوّل وكتابته، فيضيع أحد التحديثين.",
                            ),
                            options=[
                                Option(T("Subtraction is slow", "La soustraction est lente", "الطرح بطيء")),
                                Option(
                                    T(
                                        "It is three steps, and another thread can interleave between them",
                                        "Ce sont trois étapes, et un autre thread peut s'y intercaler",
                                        "إنّها ثلاث خطوات ويمكن لخيط آخر التداخل بينها",
                                    ),
                                    correct=True,
                                ),
                                Option(T("Threads cannot use global variables", "Les threads ne peuvent pas utiliser de variables globales", "لا تستطيع الخيوط استخدام المتغيّرات العامّة")),
                                Option(T("The value is stored on disk", "La valeur est stockée sur disque", "القيمة مخزّنة على القرص")),
                            ],
                        ),
                        MCQ(
                            prompt=T(
                                "What is the standard way to prevent deadlock between two locks?",
                                "Quel est le moyen standard d'éviter l'interblocage entre deux verrous ?",
                                "ما الطريقة المعيارية لمنع الجمود بين قفلين؟",
                            ),
                            hint=T("Deadlock needs a circular wait. Break the circle.", "L'interblocage exige une attente circulaire. Brisez le cercle.", "الجمود يحتاج انتظارًا دائريًا. اكسر الدائرة."),
                            explanation=T(
                                "If every thread acquires locks in the same global order, no circular wait can form, so deadlock becomes structurally impossible.",
                                "Si tous les threads acquièrent les verrous dans le même ordre global, aucune attente circulaire ne se forme : l'interblocage devient impossible.",
                                "إذا حصل كلّ خيط على الأقفال بالترتيب العامّ نفسه، فلا يتشكّل انتظار دائري، ويصير الجمود مستحيلًا بنيويًا.",
                            ),
                            options=[
                                Option(T("Use more threads", "Utiliser plus de threads", "استخدم خيوطًا أكثر")),
                                Option(T("Always acquire locks in the same global order", "Toujours acquérir les verrous dans le même ordre global", "احصل على الأقفال دائمًا بالترتيب العامّ نفسه"), correct=True),
                                Option(T("Remove all locks", "Supprimer tous les verrous", "احذف كلّ الأقفال")),
                                Option(T("Increase the process priority", "Augmenter la priorité du processus", "ارفع أولوية العملية")),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        Module(
            slug="memory-and-storage-management",
            title=T("Memory and Storage Management", "Gestion de la Mémoire et du Stockage", "إدارة الذاكرة والتخزين"),
            description=T(
                "Virtual memory, paging, and how files are actually kept.",
                "Mémoire virtuelle, pagination, et comment les fichiers sont réellement conservés.",
                "الذاكرة الافتراضية والترحيل وكيف تُحفَظ الملفّات فعلًا.",
            ),
            lessons=[
                Lesson(
                    slug="virtual-memory",
                    minutes=35,
                    xp=65,
                    difficulty=D.advanced,
                    title=T("Virtual Memory", "La Mémoire Virtuelle", "الذاكرة الافتراضية"),
                    story=T(
                        "Every program believes it owns the whole machine's memory, starting at address zero. All of them are wrong, and none of them can tell.",
                        "Chaque programme croit posséder toute la mémoire, à partir de l'adresse zéro. Tous se trompent, et aucun ne peut s'en apercevoir.",
                        "كلّ برنامج يظنّ أنّه يملك ذاكرة الجهاز كلّها بدءًا من العنوان صفر. وكلّها مخطئة، ولا يستطيع أيّ منها أن يعرف.",
                    ),
                    objective=T(
                        "Explain address translation, paging and why swapping causes sudden slowdowns.",
                        "Expliquer la traduction d'adresses, la pagination et pourquoi le swap provoque des ralentissements soudains.",
                        "شرح ترجمة العناوين والترحيل ولماذا يسبّب التبديل بطئًا مفاجئًا.",
                    ),
                    skills=T(
                        "Virtual addresses, page tables, MMU, page faults, swapping, memory protection",
                        "Adresses virtuelles, tables de pages, MMU, défauts de page, swap, protection mémoire",
                        "العناوين الافتراضية، جداول الصفحات، وحدة إدارة الذاكرة، أخطاء الصفحات، التبديل، حماية الذاكرة",
                    ),
                    blocks=[
                        Text(
                            T(
                                "Each process gets a **virtual address space** of its own. The hardware's memory management unit translates every virtual address to a physical one through **page tables** that the operating system controls. Two benefits follow immediately: a process physically cannot name another's memory, and physical memory can be handed out in fixed-size **pages** without fragmenting.",
                                "Chaque processus reçoit son propre **espace d'adressage virtuel**. L'unité de gestion mémoire traduit chaque adresse virtuelle en adresse physique via des **tables de pages** contrôlées par le système. Deux bénéfices immédiats : un processus ne peut physiquement pas nommer la mémoire d'un autre, et la mémoire physique s'attribue par **pages** de taille fixe sans fragmentation.",
                                "تحصل كلّ عملية على **فضاء عناوين افتراضي** خاصّ بها. وتترجم وحدة إدارة الذاكرة في العتاد كلّ عنوان افتراضي إلى فيزيائي عبر **جداول صفحات** يتحكّم بها نظام التشغيل. ويتبع ذلك مباشرةً فائدتان: لا تستطيع العملية فيزيائيًا تسمية ذاكرة عملية أخرى، ويمكن توزيع الذاكرة الفيزيائية في **صفحات** ثابتة الحجم دون تجزئة.",
                            )
                        ),
                        Text(
                            T(
                                "When a program touches a page that is not currently in RAM, the hardware raises a **page fault**, the OS fetches the page from disk and the instruction resumes. That is invisible when it happens occasionally. When memory is over-committed the system spends most of its time doing it — **thrashing** — and the machine appears to freeze despite the CPU being nearly idle.",
                                "Quand un programme touche une page absente de la RAM, le matériel lève un **défaut de page**, le système la charge depuis le disque et l'instruction reprend. C'est invisible si cela arrive occasionnellement. Quand la mémoire est surengagée, le système ne fait plus que cela — l'**écroulement** — et la machine semble figée alors que le processeur est presque inactif.",
                                "حين يمسّ برنامج صفحة غير موجودة في الذاكرة، يطلق العتاد **خطأ صفحة**، فيجلب النظام الصفحة من القرص وتستأنف التعليمة. وهذا غير محسوس إن حدث عرضًا. أمّا حين تُثقَل الذاكرة فوق طاقتها فيقضي النظام جلّ وقته في ذلك — وهو **الانهيار (thrashing)** — فيبدو الجهاز متجمّدًا رغم أنّ المعالج شبه خامل.",
                            )
                        ),
                        Code(
                            T(
                                "Why the same address prints differently in two runs — and why that is fine:",
                                "Pourquoi la même adresse s'affiche différemment à chaque exécution — et pourquoi c'est normal :",
                                "لماذا يُطبع العنوان نفسه مختلفًا في تشغيلين — ولماذا هذا سليم:",
                            ),
                            "value = 42\n"
                            "print(hex(id(value)))   # a VIRTUAL address, meaningful only\n"
                            "                        # inside this process\n\n"
                            "# Two processes can both hold 'address 0x7f2a1c00' and refer to\n"
                            "# completely different physical memory. Address-space layout\n"
                            "# randomisation deliberately changes the mapping on every run,\n"
                            "# which is a security measure: it makes an attacker's hardcoded\n"
                            "# address useless.",
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "A machine becomes unusably slow but CPU usage is low and disk activity is constant. What is happening?",
                                "Une machine devient très lente, avec peu de CPU et un disque constamment actif. Que se passe-t-il ?",
                                "يصبح الجهاز بطيئًا جدًا مع استخدام منخفض للمعالج ونشاط قرص متواصل. ماذا يحدث؟",
                            ),
                            hint=T("Where is the time going, if not to computation?", "Où passe le temps, si ce n'est en calcul ?", "أين يذهب الوقت إن لم يكن في الحساب؟"),
                            explanation=T(
                                "The system is thrashing: it is spending its time swapping pages between RAM and disk rather than executing instructions.",
                                "Le système s'écroule : il passe son temps à échanger des pages entre RAM et disque au lieu d'exécuter des instructions.",
                                "النظام في حالة انهيار: يقضي وقته في تبديل الصفحات بين الذاكرة والقرص بدل تنفيذ التعليمات.",
                            ),
                            options=[
                                Option(T("A deadlock between two threads", "Un interblocage entre deux threads", "جمود بين خيطين")),
                                Option(T("Thrashing: constant paging between RAM and disk", "Écroulement : pagination constante entre RAM et disque", "انهيار: ترحيل متواصل بين الذاكرة والقرص"), correct=True),
                                Option(T("A race condition", "Une condition de course", "حالة سباق")),
                                Option(T("Too many CPU cores", "Trop de cœurs CPU", "أنوية معالجة أكثر من اللازم")),
                            ],
                        ),
                        ShortAnswer(
                            prompt=T(
                                "Why can one process not read another process's memory? One sentence.",
                                "Pourquoi un processus ne peut-il pas lire la mémoire d'un autre ? Une phrase.",
                                "لماذا لا تستطيع عملية قراءة ذاكرة عملية أخرى؟ جملة واحدة.",
                            ),
                            hint=T(
                                "Think about what an address means inside a process.",
                                "Pensez à ce que signifie une adresse dans un processus.",
                                "فكّر في معنى العنوان داخل العملية.",
                            ),
                            explanation=T(
                                "Each process has its own virtual address space, and its page tables only map to physical memory the OS has assigned to it, so other memory is simply not addressable.",
                                "Chaque processus a son espace d'adressage virtuel, et ses tables de pages ne pointent que vers la mémoire physique que l'OS lui a attribuée : le reste n'est pas adressable.",
                                "لكلّ عملية فضاء عناوين افتراضي خاصّ، وجداول صفحاتها لا تُرسم إلّا على الذاكرة الفيزيائية التي خصّصها لها النظام، فما عداها غير قابل للعنونة أصلًا.",
                            ),
                            keywords=[
                                ["virtual", "address space", "page table", "virtuel", "espace d'adressage", "افتراضي", "فضاء العناوين", "جدول الصفحات"],
                            ],
                            reference_answer="Because each process has its own virtual address space and page tables that map only to the physical memory the operating system gave it, so another process's memory has no address it can name.",
                        ),
                    ],
                ),
            ],
        ),
    ],
)


COMPUTER_ARCHITECTURE = CourseSpec(
    slug="computer-architecture",
    stage=8,
    track="advanced",
    icon="🔬",
    difficulty=D.advanced,
    estimated_hours=12,
    prerequisite_slug="computer-systems",
    title=T("Computer Architecture", "Architecture des Ordinateurs", "معمارية الحاسوب"),
    description=T(
        "How the hardware executes anything: instruction sets, pipelines, the memory hierarchy, and why cache behaviour decides real performance.",
        "Comment le matériel exécute quoi que ce soit : jeux d'instructions, pipelines, hiérarchie mémoire, et pourquoi le cache décide des performances réelles.",
        "كيف ينفّذ العتاد أيّ شيء: مجموعات التعليمات، وخطوط الأنابيب، وتدرّج الذاكرة، ولماذا يقرّر سلوك المخبأ الأداء الحقيقي.",
    ),
    skills=T(
        "Instruction sets, pipelining, cache hierarchy, locality, branch prediction, parallelism",
        "Jeux d'instructions, pipeline, hiérarchie de cache, localité, prédiction de branchement, parallélisme",
        "مجموعات التعليمات، خطّ الأنابيب، تدرّج المخبأ، المحلّية، تنبّؤ التفرّع، التوازي",
    ),
    modules=[
        Module(
            slug="instructions-and-pipelines",
            title=T("Instructions and Pipelines", "Instructions et Pipelines", "التعليمات وخطوط الأنابيب"),
            description=T(
                "What the processor is actually given, and how it overlaps the work.",
                "Ce que le processeur reçoit réellement, et comment il chevauche le travail.",
                "ما الذي يُعطى للمعالج فعلًا، وكيف يداخل بين الأعمال.",
            ),
            lessons=[
                Lesson(
                    slug="instruction-sets-and-pipelining",
                    minutes=35,
                    xp=65,
                    difficulty=D.advanced,
                    title=T("Instruction Sets and Pipelining", "Jeux d'Instructions et Pipeline", "مجموعات التعليمات وخطّ الأنابيب"),
                    story=T(
                        "A processor is a factory line. Its speed comes less from working faster than from never letting a station stand idle.",
                        "Un processeur est une chaîne de montage. Sa vitesse vient moins d'un travail plus rapide que du fait qu'aucun poste ne reste inactif.",
                        "المعالج خطّ إنتاج. وسرعته تأتي من ألّا تبقى محطّة خاملة أكثر ممّا تأتي من العمل الأسرع.",
                    ),
                    objective=T(
                        "Explain the instruction cycle as a pipeline and why a mispredicted branch is expensive.",
                        "Expliquer le cycle d'instruction comme un pipeline et pourquoi un branchement mal prédit coûte cher.",
                        "شرح دورة التعليمة كخطّ أنابيب، ولماذا يكلّف التفرّع الخاطئ التنبّؤ كثيرًا.",
                    ),
                    skills=T(
                        "ISA, RISC vs CISC, pipeline stages, hazards, branch prediction, clock speed",
                        "ISA, RISC vs CISC, étages de pipeline, aléas, prédiction de branchement, fréquence",
                        "معمارية مجموعة التعليمات، RISC مقابل CISC، مراحل خطّ الأنابيب، المخاطر، تنبّؤ التفرّع، تردّد الساعة",
                    ),
                    blocks=[
                        Text(
                            T(
                                "The **instruction set architecture** is the contract between hardware and software: the operations the processor understands and what each one means. **RISC** designs (ARM, RISC-V) keep instructions few, simple and uniform; **CISC** designs (x86) offer many complex ones. Modern x86 chips actually decode those complex instructions into simpler internal operations, so the distinction is now more about the interface than the implementation.",
                                "L'**architecture du jeu d'instructions** est le contrat entre matériel et logiciel : les opérations comprises par le processeur et leur signification. Les conceptions **RISC** (ARM, RISC-V) gardent des instructions peu nombreuses, simples et uniformes ; les **CISC** (x86) en offrent beaucoup de complexes. Les puces x86 modernes décodent en fait ces instructions en opérations internes plus simples : la distinction porte désormais plus sur l'interface que sur l'implémentation.",
                                "**معمارية مجموعة التعليمات** هي العقد بين العتاد والبرمجيات: العمليات التي يفهمها المعالج ومعنى كلّ منها. وتصاميم **RISC** (مثل ARM وRISC-V) تُبقي التعليمات قليلة وبسيطة ومنتظمة، أمّا **CISC** (مثل x86) فتقدّم كثيرًا منها معقّدًا. والمعالجات x86 الحديثة تفكّ تلك التعليمات المعقّدة إلى عمليات داخلية أبسط، فصار الفرق يتعلّق بالواجهة أكثر منه بالتنفيذ.",
                            )
                        ),
                        Code(
                            T(
                                "**Pipelining** overlaps the stages so a new instruction starts every cycle:",
                                "Le **pipeline** chevauche les étages pour qu'une instruction démarre à chaque cycle :",
                                "**خطّ الأنابيب** يداخل المراحل فتبدأ تعليمة جديدة كلّ نبضة:",
                            ),
                            "# Without a pipeline - one instruction finishes before the next starts:\n"
                            "#   [Fetch][Decode][Execute][Write]\n"
                            "#                             [Fetch][Decode][Execute][Write]\n\n"
                            "# With a 4-stage pipeline - four instructions in flight at once:\n"
                            "#   [Fetch][Decode][Execute][Write]\n"
                            "#          [Fetch][Decode][Execute][Write]\n"
                            "#                 [Fetch][Decode][Execute][Write]\n"
                            "#                        [Fetch][Decode][Execute][Write]\n\n"
                            "# Each instruction still takes 4 cycles, but the THROUGHPUT is\n"
                            "# now one per cycle instead of one per four.",
                        ),
                        Text(
                            T(
                                "The pipeline only pays off while it stays full, and a **branch** — an `if` — threatens that: the processor does not yet know which way execution will go. So it guesses, using a **branch predictor**, and continues speculatively. A correct guess costs nothing; a wrong one means discarding the partially executed instructions and refilling the pipeline, which is why unpredictable branches inside a hot loop are measurably expensive.",
                                "Le pipeline ne rapporte que s'il reste plein, et un **branchement** — un `if` — menace cela : le processeur ignore encore la direction. Il devine donc, via un **prédicteur de branchement**, et continue spéculativement. Une bonne prédiction ne coûte rien ; une mauvaise oblige à jeter les instructions en cours et à recharger le pipeline, d'où le coût mesurable des branchements imprévisibles dans une boucle chaude.",
                                "لا يُثمر خطّ الأنابيب إلّا ما دام ممتلئًا، و**التفرّع** — أي `if` — يهدّد ذلك: فالمعالج لا يعرف بعدُ أيّ اتّجاه سيسلك التنفيذ. لذا يخمّن مستعينًا بـ**متنبّئ التفرّع** ويواصل تخمينيًا. والتخمين الصحيح لا يكلّف شيئًا، أمّا الخاطئ فيعني إلغاء التعليمات المنفَّذة جزئيًا وإعادة ملء الخطّ، ولهذا فالتفرّعات غير المتوقَّعة داخل حلقة ساخنة مكلفة بشكل ملموس.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "What does pipelining improve?",
                                "Qu'améliore le pipeline ?",
                                "ما الذي يحسّنه خطّ الأنابيب؟",
                            ),
                            hint=T("Does one instruction finish any sooner?", "Une instruction se termine-t-elle plus tôt ?", "هل تنتهي التعليمة الواحدة أسرع؟"),
                            explanation=T(
                                "Latency per instruction is unchanged; throughput improves because several instructions are in different stages at once.",
                                "La latence par instruction est inchangée ; le débit s'améliore car plusieurs instructions occupent des étages différents.",
                                "زمن التعليمة الواحدة لا يتغيّر؛ لكنّ الإنتاجية تتحسّن لأنّ عدّة تعليمات تشغل مراحل مختلفة في آن.",
                            ),
                            options=[
                                Option(T("The time a single instruction takes", "Le temps d'une seule instruction", "زمن تعليمة واحدة")),
                                Option(T("Throughput: how many instructions complete per cycle", "Le débit : instructions terminées par cycle", "الإنتاجية: كم تعليمة تكتمل في كلّ نبضة"), correct=True),
                                Option(T("The amount of RAM available", "La quantité de RAM disponible", "حجم الذاكرة المتاحة")),
                                Option(T("The size of the instruction set", "La taille du jeu d'instructions", "حجم مجموعة التعليمات")),
                            ],
                        ),
                        MCQ(
                            prompt=T(
                                "Why does a mispredicted branch cost performance?",
                                "Pourquoi un branchement mal prédit coûte-t-il en performance ?",
                                "لماذا يكلّف التفرّع الخاطئ التنبّؤ أداءً؟",
                            ),
                            hint=T("What was already in the pipeline when the guess turned out wrong?", "Qu'y avait-il déjà dans le pipeline quand la prédiction s'est révélée fausse ?", "ما الذي كان في خطّ الأنابيب حين تبيّن خطأ التخمين؟"),
                            explanation=T(
                                "Speculatively started instructions must be discarded and the pipeline refilled, wasting the cycles already spent on them.",
                                "Les instructions lancées spéculativement sont jetées et le pipeline rechargé : les cycles déjà dépensés sont perdus.",
                                "تُلغى التعليمات التي بدأت تخمينيًا ويُعاد ملء خطّ الأنابيب، فتضيع النبضات التي أُنفقت عليها.",
                            ),
                            options=[
                                Option(T("The processor slows its clock", "Le processeur réduit sa fréquence", "يخفّض المعالج تردّده")),
                                Option(
                                    T(
                                        "Speculatively executed instructions are discarded and the pipeline refills",
                                        "Les instructions spéculatives sont jetées et le pipeline se recharge",
                                        "تُلغى التعليمات التخمينية ويُعاد ملء خطّ الأنابيب",
                                    ),
                                    correct=True,
                                ),
                                Option(T("The cache is erased", "Le cache est effacé", "يُمسَح المخبأ")),
                                Option(T("The instruction set changes", "Le jeu d'instructions change", "تتغيّر مجموعة التعليمات")),
                            ],
                        ),
                    ],
                ),
                Lesson(
                    slug="memory-hierarchy-and-cache",
                    minutes=35,
                    xp=65,
                    difficulty=D.advanced,
                    title=T("The Memory Hierarchy and Cache", "La Hiérarchie Mémoire et le Cache", "تدرّج الذاكرة والمخبأ"),
                    story=T(
                        "Two loops do exactly the same arithmetic on the same data, and one is six times faster. Nothing about the algorithm explains it.",
                        "Deux boucles font exactement le même calcul sur les mêmes données, et l'une est six fois plus rapide. L'algorithme n'explique rien.",
                        "حلقتان تجريان الحساب نفسه على البيانات نفسها، وإحداهما أسرع ستّ مرّات. ولا شيء في الخوارزمية يفسّر ذلك.",
                    ),
                    objective=T(
                        "Explain the cache hierarchy and write loops that respect locality of reference.",
                        "Expliquer la hiérarchie de cache et écrire des boucles respectant la localité des références.",
                        "شرح تدرّج المخبأ وكتابة حلقات تحترم محلّية الوصول.",
                    ),
                    skills=T(
                        "L1/L2/L3 cache, cache lines, temporal and spatial locality, access patterns",
                        "Cache L1/L2/L3, lignes de cache, localité temporelle et spatiale, motifs d'accès",
                        "مخابئ L1/L2/L3، أسطر المخبأ، المحلّية الزمنية والمكانية، أنماط الوصول",
                    ),
                    blocks=[
                        Text(
                            T(
                                "Memory forms a hierarchy, each level bigger and far slower than the one above: registers, then L1 cache (about a nanosecond), L2, L3, then RAM (around a hundred nanoseconds), then SSD (tens of microseconds). The gap between L1 and RAM is roughly a factor of a hundred — which is why *where* your data sits routinely matters more than how many operations you perform on it.",
                                "La mémoire forme une hiérarchie, chaque niveau plus grand et bien plus lent que le précédent : registres, cache L1 (environ une nanoseconde), L2, L3, puis RAM (une centaine de nanosecondes), puis SSD (dizaines de microsecondes). L'écart entre L1 et RAM est d'environ un facteur cent — d'où l'importance de l'*emplacement* des données, souvent supérieure au nombre d'opérations.",
                                "تتشكّل الذاكرة في تدرّج، كلّ مستوى أكبر وأبطأ بكثير ممّا فوقه: المسجّلات، ثمّ مخبأ L1 (نحو نانوثانية)، ثمّ L2 وL3، ثمّ الذاكرة (نحو مئة نانوثانية)، ثمّ SSD (عشرات الميكروثواني). والفجوة بين L1 والذاكرة نحو مئة ضعف — ولهذا فإنّ *موضع* بياناتك يهمّ عادةً أكثر من عدد العمليات التي تجريها عليها.",
                            )
                        ),
                        Text(
                            T(
                                "Caches work because programs show **locality**. **Temporal**: what you used, you will probably use again soon. **Spatial**: what is next to what you used, you will probably use next — so memory is fetched in **cache lines** of about 64 bytes, never one byte at a time. Reading an array in order gets roughly sixteen 4-byte values per fetch; jumping around gets one.",
                                "Les caches fonctionnent grâce à la **localité**. **Temporelle** : ce qu'on a utilisé sera probablement réutilisé bientôt. **Spatiale** : ce qui est voisin sera probablement utilisé ensuite — la mémoire est donc lue par **lignes de cache** d'environ 64 octets, jamais octet par octet. Parcourir un tableau dans l'ordre donne environ seize valeurs de 4 octets par lecture ; sauter partout en donne une.",
                                "تعمل المخابئ بفضل **المحلّية**. **الزمنية**: ما استخدمته ستستخدمه غالبًا قريبًا. و**المكانية**: ما يجاور ما استخدمته ستستخدمه غالبًا تاليًا — لذا تُجلَب الذاكرة في **أسطر مخبأ** بنحو 64 بايتًا، لا بايتًا بايتًا. فقراءة مصفوفة بالترتيب تعطي نحو ستّ عشرة قيمة من 4 بايتات لكلّ جلب، أمّا القفز عشوائيًا فيعطي واحدة.",
                            )
                        ),
                        Code(
                            T(
                                "Same operations, same data, different access order:",
                                "Mêmes opérations, mêmes données, ordre d'accès différent :",
                                "العمليات نفسها والبيانات نفسها بترتيب وصول مختلف:",
                            ),
                            "N = 1000\n"
                            "grid = [[1] * N for _ in range(N)]\n\n"
                            "# Row-major: consecutive addresses, one cache line serves many\n"
                            "# reads. This is the fast one.\n"
                            "total = 0\n"
                            "for row in range(N):\n"
                            "    for col in range(N):\n"
                            "        total += grid[row][col]\n\n"
                            "# Column-major: every read jumps N elements ahead, so almost\n"
                            "# every access misses the cache. Identical arithmetic, several\n"
                            "# times slower on the same machine.\n"
                            "# for col in range(N):\n"
                            "#     for row in range(N):\n"
                            "#         total += grid[row][col]\n\n"
                            "print(total)",
                        ),
                        ExamTip(
                            T(
                                "When two implementations have the same Big-O but very different measured speed, the memory access pattern is the first thing to look at.",
                                "Quand deux implémentations ont le même Big-O mais des vitesses très différentes, le motif d'accès mémoire est la première chose à examiner.",
                                "حين يتساوى تنفيذان في Big-O ويختلفان كثيرًا في السرعة المقيسة، فأوّل ما تنظر إليه هو نمط الوصول إلى الذاكرة.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "Why is reading a 2D array row by row faster than column by column?",
                                "Pourquoi lire un tableau 2D ligne par ligne est-il plus rapide que colonne par colonne ?",
                                "لماذا قراءة مصفوفة ثنائية صفًّا صفًّا أسرع من قراءتها عمودًا عمودًا؟",
                            ),
                            hint=T("Think about what a single memory fetch brings back.", "Pensez à ce que ramène une seule lecture mémoire.", "فكّر فيما يجلبه استحضار واحد من الذاكرة."),
                            explanation=T(
                                "Row-major traversal follows consecutive addresses, so each 64-byte cache line serves many reads; column traversal misses on almost every access.",
                                "Le parcours par lignes suit des adresses consécutives : chaque ligne de cache de 64 octets sert plusieurs lectures ; par colonnes, presque chaque accès manque le cache.",
                                "المرور صفًّا صفًّا يتبع عناوين متتالية، فيخدم كلّ سطر مخبأ من 64 بايتًا قراءات كثيرة، أمّا المرور عموديًا فيُخفق في المخبأ عند كلّ وصول تقريبًا.",
                            ),
                            options=[
                                Option(T("Rows contain fewer elements", "Les lignes ont moins d'éléments", "الصفوف تحوي عناصر أقلّ")),
                                Option(
                                    T(
                                        "Row order matches how memory is laid out, so cache lines are used fully",
                                        "L'ordre par ligne correspond à la disposition mémoire : les lignes de cache sont pleinement utilisées",
                                        "ترتيب الصفوف يطابق تخطيط الذاكرة، فتُستغلّ أسطر المخبأ كاملة",
                                    ),
                                    correct=True,
                                ),
                                Option(T("The compiler removes the inner loop", "Le compilateur supprime la boucle interne", "المصرّف يحذف الحلقة الداخلية")),
                                Option(T("Column access uses more instructions", "L'accès par colonne utilise plus d'instructions", "الوصول العمودي يستخدم تعليمات أكثر")),
                            ],
                        ),
                        Ordering(
                            prompt=T(
                                "Order these from fastest to slowest access.",
                                "Classez du plus rapide au plus lent en accès.",
                                "رتّبها من الأسرع إلى الأبطأ وصولًا.",
                            ),
                            hint=T("Each level down is roughly an order of magnitude slower.", "Chaque niveau inférieur est environ dix fois plus lent.", "كلّ مستوى أدنى أبطأ بنحو عشرة أضعاف."),
                            explanation=T(
                                "Registers, then L1 cache, then main memory, then SSD — spanning about six orders of magnitude end to end.",
                                "Registres, cache L1, mémoire principale, puis SSD — soit environ six ordres de grandeur d'écart.",
                                "المسجّلات ثمّ مخبأ L1 ثمّ الذاكرة الرئيسية ثمّ قرص SSD — بفارق نحو ستّة رتب من حيث المقدار.",
                            ),
                            steps=[
                                T("CPU registers", "Registres du processeur", "مسجّلات المعالج"),
                                T("L1 cache", "Cache L1", "مخبأ L1"),
                                T("Main memory (RAM)", "Mémoire principale (RAM)", "الذاكرة الرئيسية (RAM)"),
                                T("SSD storage", "Stockage SSD", "تخزين SSD"),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)


ADVANCED_COMPUTING = CourseSpec(
    slug="advanced-computing",
    stage=8,
    track="advanced",
    icon="🚀",
    difficulty=D.advanced,
    estimated_hours=14,
    prerequisite_slug="algorithms-complexity",
    title=T("Advanced Computing", "Informatique Avancée", "الحوسبة المتقدّمة"),
    description=T(
        "What changes at scale: how compilers turn language into machine code, how parallel programs share work, and what becomes hard when one machine becomes many.",
        "Ce qui change à grande échelle : comment les compilateurs transforment un langage en code machine, comment les programmes parallèles partagent le travail, et ce qui devient difficile quand une machine devient plusieurs.",
        "ما الذي يتغيّر عند الحجم الكبير: كيف تحوّل المصرّفات اللغة إلى كود آلة، وكيف تتقاسم البرامج المتوازية العمل، وما الذي يصعب حين يصير الجهاز الواحد أجهزةً.",
    ),
    skills=T(
        "Compilers, lexing and parsing, ASTs, parallelism, Amdahl's law, distributed systems, CAP, cloud computing",
        "Compilateurs, analyse lexicale et syntaxique, AST, parallélisme, loi d'Amdahl, systèmes distribués, CAP, cloud",
        "المصرّفات، التحليل اللفظي والنحوي، الأشجار النحوية، التوازي، قانون أمدال، الأنظمة الموزّعة، CAP، الحوسبة السحابية",
    ),
    modules=[
        Module(
            slug="compilers",
            title=T("Compilers", "Les Compilateurs", "المصرّفات"),
            description=T(
                "From text to a syntax tree to machine code.",
                "Du texte à l'arbre syntaxique puis au code machine.",
                "من النصّ إلى الشجرة النحوية إلى كود الآلة.",
            ),
            lessons=[
                Lesson(
                    slug="how-compilers-work",
                    minutes=40,
                    xp=70,
                    difficulty=D.advanced,
                    title=T("How Compilers Work", "Comment Fonctionnent les Compilateurs", "كيف تعمل المصرّفات"),
                    story=T(
                        "Every syntax error you have ever seen came from one specific phase. Knowing which one makes the message readable.",
                        "Toute erreur de syntaxe que vous avez vue vient d'une phase précise. Savoir laquelle rend le message lisible.",
                        "كلّ خطأ صياغة رأيته جاء من مرحلة بعينها. ومعرفة أيّها تجعل الرسالة مقروءة.",
                    ),
                    objective=T(
                        "Name the phases of compilation and read an abstract syntax tree.",
                        "Nommer les phases de compilation et lire un arbre syntaxique abstrait.",
                        "تسمية مراحل التصريف وقراءة شجرة نحوية مجرّدة.",
                    ),
                    skills=T(
                        "Lexical analysis, parsing, AST, semantic analysis, optimisation, code generation",
                        "Analyse lexicale, analyse syntaxique, AST, analyse sémantique, optimisation, génération de code",
                        "التحليل اللفظي، التحليل النحوي، الشجرة النحوية، التحليل الدلالي، التحسين، توليد الكود",
                    ),
                    blocks=[
                        Text(
                            T(
                                "Compilation runs in phases. **Lexical analysis** turns characters into tokens (`total`, `=`, `price`, `*`, `2`). **Parsing** arranges those tokens into an **abstract syntax tree** according to the grammar — this is the phase that reports \"unexpected token\". **Semantic analysis** checks meaning: does this name exist, do these types agree? Then **optimisation** and **code generation** produce the output.",
                                "La compilation se déroule en phases. L'**analyse lexicale** transforme les caractères en tokens (`total`, `=`, `prix`, `*`, `2`). L'**analyse syntaxique** organise ces tokens en **arbre syntaxique abstrait** selon la grammaire — c'est elle qui signale « token inattendu ». L'**analyse sémantique** vérifie le sens : ce nom existe-t-il, ces types s'accordent-ils ? Puis l'**optimisation** et la **génération de code** produisent la sortie.",
                                "يجري التصريف على مراحل. **التحليل اللفظي** يحوّل المحارف إلى رموز (`total` و`=` و`price` و`*` و`2`). و**التحليل النحوي** يرتّب تلك الرموز في **شجرة نحوية مجرّدة** وفق القواعد — وهذه المرحلة هي التي تبلّغ عن «رمز غير متوقّع». و**التحليل الدلالي** يفحص المعنى: هل يوجد هذا الاسم؟ هل تتوافق الأنواع؟ ثمّ يأتي **التحسين** و**توليد الكود** لإنتاج المخرجات.",
                            )
                        ),
                        Code(
                            T(
                                "Python exposes its own parser, so you can see the tree directly:",
                                "Python expose son propre analyseur : on peut voir l'arbre directement :",
                                "يعرض بايثون محلّله النحوي، فيمكنك رؤية الشجرة مباشرة:",
                            ),
                            "import ast\n\n"
                            "tree = ast.parse('total = price * 2')\n"
                            "print(ast.dump(tree, indent=2))\n\n"
                            "# Assign(\n"
                            "#   targets=[Name(id='total')],\n"
                            "#   value=BinOp(left=Name(id='price'), op=Mult(), right=Constant(2)))\n"
                            "#\n"
                            "# The tree, not the text, is what every later phase works on --\n"
                            "# and it is exactly what AtlasCode's own sandbox validator walks\n"
                            "# to decide whether submitted code is safe to run.",
                        ),
                        Text(
                            T(
                                "Errors are reported by the phase that can detect them, which is why the messages differ so much in usefulness. A missing bracket is caught by the parser, which knows only shape. An undefined variable is caught by semantic analysis, which knows names. A wrong answer is caught by neither — the compiler has no idea what you meant.",
                                "Les erreurs sont signalées par la phase capable de les détecter, d'où des messages d'utilité très variable. Une parenthèse manquante est vue par l'analyseur syntaxique, qui ne connaît que la forme. Une variable non définie est vue par l'analyse sémantique, qui connaît les noms. Une réponse fausse n'est vue par aucune — le compilateur ignore votre intention.",
                                "تُبلَّغ الأخطاء من المرحلة القادرة على كشفها، ولهذا تتفاوت رسائلها كثيرًا في الفائدة. فالقوس الناقص يكشفه المحلّل النحوي الذي لا يعرف إلّا الشكل. والمتغيّر غير المعرَّف يكشفه التحليل الدلالي الذي يعرف الأسماء. أمّا الإجابة الخاطئة فلا يكشفها أيّ منهما — إذ لا فكرة لدى المصرّف عمّا قصدته.",
                            )
                        ),
                    ],
                    exercises=[
                        Ordering(
                            prompt=T(
                                "Put the compilation phases in order.",
                                "Remettez les phases de compilation dans l'ordre.",
                                "رتّب مراحل التصريف.",
                            ),
                            hint=T("You cannot build a tree before you have tokens.", "On ne construit pas d'arbre sans tokens.", "لا يمكنك بناء شجرة قبل أن تملك رموزًا."),
                            explanation=T(
                                "Lexical analysis, parsing, semantic analysis, optimisation, then code generation.",
                                "Analyse lexicale, analyse syntaxique, analyse sémantique, optimisation, puis génération de code.",
                                "التحليل اللفظي ثمّ النحوي ثمّ الدلالي ثمّ التحسين ثمّ توليد الكود.",
                            ),
                            steps=[
                                T("Lexical analysis: characters to tokens", "Analyse lexicale : caractères en tokens", "التحليل اللفظي: من محارف إلى رموز"),
                                T("Parsing: tokens to a syntax tree", "Analyse syntaxique : tokens en arbre", "التحليل النحوي: من رموز إلى شجرة"),
                                T("Semantic analysis: names and types", "Analyse sémantique : noms et types", "التحليل الدلالي: الأسماء والأنواع"),
                                T("Optimisation", "Optimisation", "التحسين"),
                                T("Code generation", "Génération de code", "توليد الكود"),
                            ],
                        ),
                        MCQ(
                            prompt=T(
                                "Which phase reports the use of a variable that was never defined?",
                                "Quelle phase signale l'usage d'une variable jamais définie ?",
                                "أيّ مرحلة تبلّغ عن استخدام متغيّر لم يُعرَّف قطّ؟",
                            ),
                            hint=T("Which phase knows about names, not just shapes?", "Quelle phase connaît les noms, pas seulement la forme ?", "أيّ مرحلة تعرف الأسماء لا الشكل فقط؟"),
                            explanation=T(
                                "The parser only checks structure. Knowing that a name was never bound is a meaning question, handled by semantic analysis.",
                                "L'analyseur syntaxique ne vérifie que la structure. Savoir qu'un nom n'a jamais été lié relève du sens : l'analyse sémantique.",
                                "المحلّل النحوي يفحص البنية فقط. أمّا معرفة أنّ اسمًا لم يُربَط قطّ فمسألة معنى تتولّاها المرحلة الدلالية.",
                            ),
                            options=[
                                Option(T("Lexical analysis", "L'analyse lexicale", "التحليل اللفظي")),
                                Option(T("Parsing", "L'analyse syntaxique", "التحليل النحوي")),
                                Option(T("Semantic analysis", "L'analyse sémantique", "التحليل الدلالي"), correct=True),
                                Option(T("Code generation", "La génération de code", "توليد الكود")),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        Module(
            slug="parallel-and-distributed",
            title=T("Parallel and Distributed Systems", "Systèmes Parallèles et Distribués", "الأنظمة المتوازية والموزّعة"),
            description=T(
                "Using many cores, then many machines — and what each one costs.",
                "Utiliser plusieurs cœurs, puis plusieurs machines — et ce que chacun coûte.",
                "استخدام أنوية كثيرة ثمّ أجهزة كثيرة — وكلفة كلّ منهما.",
            ),
            lessons=[
                Lesson(
                    slug="parallelism-and-amdahl",
                    minutes=35,
                    xp=65,
                    difficulty=D.advanced,
                    title=T("Parallelism and Amdahl's Law", "Parallélisme et Loi d'Amdahl", "التوازي وقانون أمدال"),
                    story=T(
                        "Nine women cannot deliver a baby in one month, and sixteen cores cannot make a sequential program sixteen times faster.",
                        "Neuf femmes ne font pas un bébé en un mois, et seize cœurs ne rendent pas un programme séquentiel seize fois plus rapide.",
                        "تسع نساء لا يلدن طفلًا في شهر، وستّة عشر نواة لا تجعل برنامجًا تسلسليًا أسرع ستّ عشرة مرّة.",
                    ),
                    objective=T(
                        "Distinguish parallelism from concurrency and use Amdahl's law to bound the possible speed-up.",
                        "Distinguer parallélisme et concurrence et utiliser la loi d'Amdahl pour borner l'accélération possible.",
                        "التمييز بين التوازي والتزامن، واستخدام قانون أمدال لتحديد سقف التسريع الممكن.",
                    ),
                    skills=T(
                        "Parallelism vs concurrency, Amdahl's law, speed-up, coordination overhead",
                        "Parallélisme vs concurrence, loi d'Amdahl, accélération, surcoût de coordination",
                        "التوازي مقابل التزامن، قانون أمدال، التسريع، كلفة التنسيق",
                    ),
                    blocks=[
                        Text(
                            T(
                                "**Concurrency** is structuring a program so several tasks are in progress at once; **parallelism** is actually executing them at the same instant on different cores. A single-core machine can be concurrent and never parallel. The distinction matters because concurrency is a design choice and parallelism is a hardware capability.",
                                "La **concurrence** structure un programme pour que plusieurs tâches progressent ensemble ; le **parallélisme** les exécute réellement au même instant sur des cœurs différents. Une machine monocœur peut être concurrente sans jamais être parallèle. La distinction compte : la concurrence est un choix de conception, le parallélisme une capacité matérielle.",
                                "**التزامن** هو بناء البرنامج بحيث تتقدّم عدّة مهامّ معًا؛ أمّا **التوازي** فهو تنفيذها فعليًا في اللحظة نفسها على أنوية مختلفة. فجهاز بنواة واحدة يمكن أن يكون متزامنًا ولا يكون متوازيًا أبدًا. والفرق مهمّ لأنّ التزامن خيار تصميمي والتوازي قدرة عتادية.",
                            )
                        ),
                        Text(
                            T(
                                "**Amdahl's law** bounds what parallelism can ever achieve: if a fraction *s* of the work must run sequentially, the maximum speed-up is 1/s no matter how many cores you add. Ten percent sequential caps you at ten times, on infinite hardware. This is why the honest first question is \"what fraction of this is genuinely parallelisable?\" rather than \"how many cores can we buy?\"",
                                "La **loi d'Amdahl** borne ce que le parallélisme peut atteindre : si une fraction *s* du travail est séquentielle, l'accélération maximale est 1/s, quel que soit le nombre de cœurs. Dix pour cent de séquentiel plafonne à dix fois, sur du matériel infini. D'où la vraie première question : « quelle fraction est réellement parallélisable ? » et non « combien de cœurs pouvons-nous acheter ? »",
                                "**قانون أمدال** يحدّ ما يستطيع التوازي بلوغه: فإذا كان جزء *s* من العمل يجب أن يجري تسلسليًا، فأقصى تسريع هو 1/s مهما أضفت من أنوية. فعشرة بالمئة تسلسلية تحدّك عند عشرة أضعاف حتى على عتاد لا نهائي. ولهذا فالسؤال الأوّل الأمين هو «أيّ نسبة من هذا قابلة فعلًا للتوازي؟» لا «كم نواة نستطيع شراءها؟»",
                            )
                        ),
                        Code(
                            T(
                                "The ceiling, computed:",
                                "Le plafond, calculé :",
                                "السقف محسوبًا:",
                            ),
                            "def speedup(sequential_fraction, cores):\n"
                            "    parallel = 1 - sequential_fraction\n"
                            "    return 1 / (sequential_fraction + parallel / cores)\n\n"
                            "for cores in (2, 4, 16, 1024):\n"
                            "    print(cores, round(speedup(0.10, cores), 2))\n\n"
                            "# 10% sequential: 1024 cores buys about 9.9x, not 1024x.\n"
                            "# And this ignores coordination cost, which grows with the\n"
                            "# number of workers -- so past some point, adding cores makes\n"
                            "# the program measurably slower.",
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "20% of a program must run sequentially. What is the maximum possible speed-up?",
                                "20 % d'un programme doit être séquentiel. Quelle est l'accélération maximale ?",
                                "‏20% من برنامج يجب أن يعمل تسلسليًا. ما أقصى تسريع ممكن؟",
                            ),
                            hint=T("Amdahl's limit is 1 divided by the sequential fraction.", "La limite d'Amdahl est 1 divisé par la fraction séquentielle.", "حدّ أمدال هو 1 مقسومًا على النسبة التسلسلية."),
                            explanation=T(
                                "1 / 0.20 = 5. Even with unlimited cores the program cannot go more than five times faster.",
                                "1 / 0,20 = 5. Même avec une infinité de cœurs, le programme ne peut aller plus de cinq fois plus vite.",
                                "‏1 / 0.20 = 5. فحتى بأنوية لا محدودة لا يستطيع البرنامج أن يكون أسرع من خمسة أضعاف.",
                            ),
                            options=[
                                Option(T("2x", "2x", "ضعفان")),
                                Option(T("5x", "5x", "خمسة أضعاف"), correct=True),
                                Option(T("20x", "20x", "عشرون ضعفًا")),
                                Option(T("Unlimited, with enough cores", "Illimitée, avec assez de cœurs", "غير محدود بأنوية كافية")),
                            ],
                        ),
                        Prediction(
                            prompt=T(
                                "What does this print?",
                                "Qu'affiche ce code ?",
                                "ما الذي يطبعه هذا الكود؟",
                            ),
                            hint=T("speedup(0.5, 2) = 1 / (0.5 + 0.25).", "speedup(0.5, 2) = 1 / (0,5 + 0,25).", "‏speedup(0.5, 2) = 1 / (0.5 + 0.25)."),
                            explanation=T(
                                "With half the work sequential, two cores give 1/0.75 ≈ 1.33 and four give 1/0.625 = 1.6.",
                                "Avec la moitié du travail séquentielle, deux cœurs donnent 1/0,75 ≈ 1,33 et quatre donnent 1/0,625 = 1,6.",
                                "بنصف العمل تسلسليًا تعطي نواتان 1/0.75 ≈ 1.33 وتعطي أربع 1/0.625 = 1.6.",
                            ),
                            code="def speedup(sequential_fraction, cores):\n    parallel = 1 - sequential_fraction\n    return 1 / (sequential_fraction + parallel / cores)\n\nprint(round(speedup(0.5, 2), 2))\nprint(round(speedup(0.5, 4), 2))",
                            expected_output="1.33\n1.6",
                        ),
                    ],
                ),
                Lesson(
                    slug="distributed-systems-and-cloud",
                    minutes=40,
                    xp=70,
                    difficulty=D.advanced,
                    title=T("Distributed Systems and the Cloud", "Systèmes Distribués et Cloud", "الأنظمة الموزّعة والسحابة"),
                    story=T(
                        "The moment there are two machines, the network can fail between them, and every guarantee you had becomes a choice.",
                        "Dès qu'il y a deux machines, le réseau peut tomber entre elles, et chaque garantie devient un choix.",
                        "ما إن يوجد جهازان حتى تصير الشبكة قابلة للانقطاع بينهما، ويتحوّل كلّ ضمان كان لديك إلى خيار.",
                    ),
                    objective=T(
                        "State the CAP theorem correctly and explain what cloud service models actually change.",
                        "Énoncer correctement le théorème CAP et expliquer ce que changent réellement les modèles de service cloud.",
                        "صياغة مبرهنة CAP بدقّة، وشرح ما تغيّره نماذج الخدمات السحابية فعلًا.",
                    ),
                    skills=T(
                        "Partial failure, CAP theorem, consistency models, replication, IaaS/PaaS/SaaS, elasticity",
                        "Défaillance partielle, théorème CAP, modèles de cohérence, réplication, IaaS/PaaS/SaaS, élasticité",
                        "الفشل الجزئي، مبرهنة CAP، نماذج الاتّساق، النسخ المتماثل، IaaS/PaaS/SaaS، المرونة",
                    ),
                    blocks=[
                        Text(
                            T(
                                "The defining property of a distributed system is **partial failure**: one node is down, or reachable by some peers and not others, and no one can tell the difference between a slow machine and a dead one. Single-machine intuitions about time, order and \"the current value\" stop holding.",
                                "La propriété caractéristique d'un système distribué est la **défaillance partielle** : un nœud est tombé, ou joignable par certains pairs seulement, et nul ne distingue une machine lente d'une machine morte. Les intuitions monomachine sur le temps, l'ordre et « la valeur actuelle » cessent de valoir.",
                                "الخاصّية المميّزة للنظام الموزّع هي **الفشل الجزئي**: عقدة معطّلة، أو يصل إليها بعض النظراء دون غيرهم، ولا أحد يميّز بين جهاز بطيء وجهاز ميّت. وتتوقّف عن الصمود بديهيّاتُ الجهاز الواحد عن الزمن والترتيب و«القيمة الحالية».",
                            )
                        ),
                        Text(
                            T(
                                "The **CAP theorem** says that when a network **partition** happens — and it will — a system must choose between **consistency** (every read sees the latest write, or an error) and **availability** (every request gets an answer, possibly stale). It is not \"pick two of three\": partitions are not optional, so the real choice is between C and A during a partition. A bank picks consistency; a social feed picks availability.",
                                "Le **théorème CAP** dit qu'en cas de **partition** réseau — et il y en aura — un système doit choisir entre la **cohérence** (toute lecture voit la dernière écriture, sinon une erreur) et la **disponibilité** (toute requête obtient une réponse, éventuellement périmée). Ce n'est pas « deux sur trois » : les partitions ne sont pas optionnelles, le vrai choix est entre C et A pendant une partition. Une banque choisit la cohérence ; un fil social, la disponibilité.",
                                "تقول **مبرهنة CAP** إنّه عند حدوث **انقسام** في الشبكة — وسيحدث — يجب أن يختار النظام بين **الاتّساق** (كلّ قراءة ترى آخر كتابة وإلّا فخطأ) و**التوافر** (كلّ طلب يحصل على إجابة ولو قديمة). وليست المسألة «اختر اثنين من ثلاثة»: فالانقسامات ليست اختيارية، والاختيار الحقيقي بين C وA أثناء الانقسام. المصرف يختار الاتّساق، وخلاصة التواصل الاجتماعي تختار التوافر.",
                            )
                        ),
                        Code(
                            T(
                                "The service models differ in one thing: where your responsibility ends.",
                                "Les modèles de service diffèrent sur un point : où s'arrête votre responsabilité.",
                                "تختلف نماذج الخدمة في أمر واحد: أين تنتهي مسؤوليّتك.",
                            ),
                            "# IaaS  - you rent machines. You run the OS, the runtime, the app,\n"
                            "#         the patches, the backups. Maximum control and work.\n"
                            "# PaaS  - you deploy code. The platform runs the OS and runtime.\n"
                            "#         (Render and Vercel, which host this very project.)\n"
                            "# SaaS  - you use finished software. You own only your data and\n"
                            "#         your configuration.\n\n"
                            "# The cloud's real product is ELASTICITY: capacity you can add in\n"
                            "# minutes and stop paying for in minutes. It is not automatically\n"
                            "# cheaper -- a steady, predictable workload is often cheaper on\n"
                            "# hardware you own. It is faster to change your mind.",
                        ),
                        ExamTip(
                            T(
                                "Do not write \"CAP means choose two of three\". Partitions are a fact of networks, not an option, so the theorem is about what you give up *while a partition is happening*.",
                                "N'écrivez pas « CAP signifie choisir deux sur trois ». Les partitions sont un fait des réseaux, pas une option : le théorème porte sur ce que l'on abandonne *pendant* une partition.",
                                "لا تكتب «CAP تعني اختر اثنين من ثلاثة». فالانقسامات واقع في الشبكات لا خيار، والمبرهنة تتعلّق بما تتنازل عنه *أثناء* حدوث الانقسام.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "During a network partition, a banking ledger refuses writes rather than risk divergence. What has it chosen?",
                                "Pendant une partition réseau, un registre bancaire refuse les écritures plutôt que risquer la divergence. Qu'a-t-il choisi ?",
                                "أثناء انقسام شبكي، يرفض سجلّ مصرفي الكتابات بدل المخاطرة بالتباعد. ماذا اختار؟",
                            ),
                            hint=T("It gave up answering in order to stay correct.", "Il renonce à répondre pour rester correct.", "تخلّى عن الإجابة كي يبقى صحيحًا."),
                            explanation=T(
                                "Refusing to serve rather than serve possibly-wrong data is choosing consistency over availability.",
                                "Refuser de répondre plutôt que servir des données peut-être fausses, c'est choisir la cohérence sur la disponibilité.",
                                "رفض الخدمة بدل تقديم بيانات قد تكون خاطئة هو اختيار الاتّساق على التوافر.",
                            ),
                            options=[
                                Option(T("Availability over consistency", "La disponibilité sur la cohérence", "التوافر على الاتّساق")),
                                Option(T("Consistency over availability", "La cohérence sur la disponibilité", "الاتّساق على التوافر"), correct=True),
                                Option(T("Partition tolerance over both", "La tolérance au partitionnement sur les deux", "تحمّل الانقسام على كليهما")),
                                Option(T("Nothing; CAP does not apply", "Rien ; CAP ne s'applique pas", "لا شيء؛ فـ CAP لا تنطبق")),
                            ],
                        ),
                        ShortAnswer(
                            prompt=T(
                                "Why is partition tolerance not really optional in a distributed system? One sentence.",
                                "Pourquoi la tolérance au partitionnement n'est-elle pas vraiment optionnelle ? Une phrase.",
                                "لماذا لا يكون تحمّل الانقسام اختياريًا فعلًا في نظام موزّع؟ جملة واحدة.",
                            ),
                            hint=T(
                                "What is guaranteed to happen to a network eventually?",
                                "Qu'est-il certain qu'il arrive à un réseau ?",
                                "ما الذي سيحدث للشبكة حتمًا في النهاية؟",
                            ),
                            explanation=T(
                                "Networks inevitably drop messages and links fail, so a partition will occur whether the design accounts for it or not — the only choice is how the system behaves when it does.",
                                "Les réseaux perdent des messages et des liens tombent : une partition surviendra, que la conception l'ait prévue ou non — le seul choix est le comportement du système à ce moment.",
                                "الشبكات تُسقِط الرسائل حتمًا وتتعطّل الوصلات، فسيقع الانقسام سواء راعاه التصميم أم لا — والخيار الوحيد هو كيف يتصرّف النظام حينها.",
                            ),
                            keywords=[
                                ["network", "réseau", "الشبكة", "شبكات"],
                                ["fail", "fails", "will happen", "inevitable", "tombe", "inévitable", "تفشل", "حتمًا", "يقع"],
                            ],
                            reference_answer="Because networks inevitably fail and drop messages, so a partition will happen regardless of the design; the only real choice is how the system behaves during one.",
                        ),
                    ],
                ),
            ],
        ),
    ],
)


async def seed_operating_systems(db, order: int) -> int:
    print("Seeding Operating Systems...")
    return await seed_course(db, OPERATING_SYSTEMS, order)


async def seed_computer_architecture(db, order: int) -> int:
    print("Seeding Computer Architecture...")
    return await seed_course(db, COMPUTER_ARCHITECTURE, order)


async def seed_advanced_computing(db, order: int) -> int:
    print("Seeding Advanced Computing...")
    return await seed_course(db, ADVANCED_COMPUTING, order)
