"""Stage 6 — Cybersecurity.

Three defensive courses. *Introduction to Cybersecurity* establishes the
principles, identity and the cryptography every later topic leans on.
*Fundamentals of Computer Networks Security* applies them to the network.
*Secure Software Development* applies them to the code a student writes.

Everything here is written from the defender's side: what the weakness is, why
it exists, and what removes it. No operational attack instructions.
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
    ShortAnswer,
    T,
    Text,
    seed_course,
)

CYBERSECURITY_FOUNDATIONS = CourseSpec(
    slug="cybersecurity-foundations",
    stage=6,
    track="security",
    icon="🛡️",
    difficulty=D.intermediate,
    estimated_hours=10,
    prerequisite_slug="networking",
    title=T("Introduction to Cybersecurity", "Introduction à la Cybersécurité", "مقدّمة في الأمن السيبراني"),
    description=T(
        "The principles security is built on: the CIA triad, identity and access, password storage, and the cryptography underneath it all.",
        "Les principes sur lesquels repose la sécurité : la triade DIC, identité et accès, stockage des mots de passe, et la cryptographie qui les sous-tend.",
        "المبادئ التي يُبنى عليها الأمن: ثلاثية السرّية والسلامة والتوافر، والهوية والصلاحيات، وتخزين كلمات المرور، والتعمية التي تسند ذلك كلّه.",
    ),
    skills=T(
        "CIA triad, threat modelling, authentication, authorisation, hashing, encryption, public-key cryptography",
        "Triade DIC, modélisation des menaces, authentification, autorisation, hachage, chiffrement, cryptographie asymétrique",
        "ثلاثية CIA، نمذجة التهديدات، التوثيق، التخويل، التجزئة، التشفير، تعمية المفتاح العامّ",
    ),
    modules=[
        Module(
            slug="security-principles",
            title=T("Security Principles", "Principes de Sécurité", "مبادئ الأمن"),
            description=T(
                "What we are protecting, from whom, and the rules that make protection work.",
                "Ce que l'on protège, contre qui, et les règles qui font que la protection fonctionne.",
                "ما الذي نحميه، وممّن، والقواعد التي تجعل الحماية ناجعة.",
            ),
            lessons=[
                Lesson(
                    slug="cia-triad",
                    minutes=30,
                    xp=55,
                    difficulty=D.intermediate,
                    title=T("The CIA Triad", "La Triade DIC", "ثلاثية CIA"),
                    story=T(
                        "Every security decision is a trade between three goals that pull against each other.",
                        "Toute décision de sécurité est un arbitrage entre trois objectifs qui se contredisent.",
                        "كلّ قرار أمني مقايضة بين ثلاثة أهداف يشدّ بعضها بعضًا.",
                    ),
                    objective=T(
                        "Classify a security requirement as confidentiality, integrity or availability, and explain the trade-offs.",
                        "Classer une exigence de sécurité en confidentialité, intégrité ou disponibilité, et expliquer les compromis.",
                        "تصنيف المتطلّب الأمني إلى سرّية أو سلامة أو توافر، وشرح المقايضات بينها.",
                    ),
                    skills=T(
                        "Confidentiality, integrity, availability, defence in depth, least privilege",
                        "Confidentialité, intégrité, disponibilité, défense en profondeur, moindre privilège",
                        "السرّية، السلامة، التوافر، الدفاع المتعمّق، أقلّ صلاحية",
                    ),
                    blocks=[
                        Text(
                            T(
                                "**Confidentiality**: only the right people can read it. **Integrity**: nobody can change it undetected. **Availability**: the people who need it can get it when they need it. Almost every security control serves one of the three, and strengthening one often costs another — an encrypted backup nobody can decrypt is perfectly confidential and completely useless.",
                                "**Confidentialité** : seules les bonnes personnes peuvent lire. **Intégrité** : personne ne peut modifier sans être détecté. **Disponibilité** : ceux qui en ont besoin y accèdent au moment voulu. Presque tout contrôle sert l'un des trois, et renforcer l'un coûte souvent un autre — une sauvegarde chiffrée que personne ne peut déchiffrer est parfaitement confidentielle et totalement inutile.",
                                "**السرّية**: لا يقرؤه إلّا أصحاب الحقّ. و**السلامة**: لا يستطيع أحد تغييره دون أن يُكتشَف. و**التوافر**: من يحتاجه يصل إليه حين يحتاجه. وكلّ ضابط أمني تقريبًا يخدم واحدًا من الثلاثة، وتقوية أحدها كثيرًا ما تكلّف آخر — فنسخة احتياطية مشفّرة لا يستطيع أحد فكّها سرّية تمامًا وعديمة الفائدة تمامًا.",
                            )
                        ),
                        Text(
                            T(
                                "Two principles run through everything that follows. **Least privilege**: every account, service and token gets the smallest set of permissions that lets it do its job, so a compromise stays small. **Defence in depth**: assume any single control will fail, and make sure something else is still standing when it does.",
                                "Deux principes traversent tout ce qui suit. **Moindre privilège** : chaque compte, service et jeton reçoit le plus petit ensemble de permissions nécessaires, pour qu'une compromission reste limitée. **Défense en profondeur** : supposez que tout contrôle unique échouera, et assurez-vous qu'autre chose tienne encore.",
                                "مبدآن يسريان في كلّ ما يلي. **أقلّ صلاحية**: يحصل كلّ حساب وخدمة ورمز على أصغر مجموعة صلاحيات تكفي لعمله، فيبقى أيّ اختراق محدودًا. و**الدفاع المتعمّق**: افترض أنّ أيّ ضابط منفرد سيفشل، واحرص على بقاء شيء آخر قائمًا عند فشله.",
                            )
                        ),
                        Code(
                            T(
                                "The same three goals, expressed as things a real system does:",
                                "Les mêmes trois objectifs, exprimés comme actions d'un vrai système :",
                                "الأهداف الثلاثة نفسها معبّرًا عنها بأفعال نظام حقيقي:",
                            ),
                            "# Confidentiality - TLS in transit, encryption at rest,\n"
                            "#                   access checks on every read.\n"
                            "# Integrity       - password hashes, signed tokens, audit logs,\n"
                            "#                   database constraints, checksums on backups.\n"
                            "# Availability    - backups that are restored and tested, rate\n"
                            "#                   limits, redundancy, monitoring and alerts.\n\n"
                            "# A ransomware incident attacks availability and integrity;\n"
                            "# a leaked database attacks confidentiality. Different\n"
                            "# defences, because they are different failures.",
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "An attacker silently edits exam marks in a database. Which property was broken?",
                                "Un attaquant modifie discrètement des notes en base. Quelle propriété est violée ?",
                                "غيّر مهاجم درجات امتحان في قاعدة البيانات بصمت. أيّ خاصّية انتُهكت؟",
                            ),
                            hint=T("Nothing was leaked and the service kept working.", "Rien n'a fuité et le service fonctionnait.", "لم يتسرّب شيء وظلّت الخدمة تعمل."),
                            explanation=T(
                                "The data was modified without authorisation and without detection: that is a failure of integrity.",
                                "Les données ont été modifiées sans autorisation ni détection : c'est une atteinte à l'intégrité.",
                                "عُدِّلت البيانات دون تخويل ودون كشف: وهذا إخلال بالسلامة.",
                            ),
                            options=[
                                Option(T("Confidentiality", "Confidentialité", "السرّية")),
                                Option(T("Integrity", "Intégrité", "السلامة"), correct=True),
                                Option(T("Availability", "Disponibilité", "التوافر")),
                                Option(T("None of them", "Aucune", "لا شيء منها")),
                            ],
                        ),
                        MCQ(
                            prompt=T(
                                "A reporting service only ever reads data. What does least privilege require?",
                                "Un service de reporting ne fait que lire des données. Qu'exige le moindre privilège ?",
                                "خدمة تقارير لا تفعل إلّا القراءة. ماذا يقتضي مبدأ أقلّ صلاحية؟",
                            ),
                            hint=T("What is the smallest permission set that still lets it work?", "Quel est le plus petit ensemble de permissions suffisant ?", "ما أصغر مجموعة صلاحيات تكفي لعملها؟"),
                            explanation=T(
                                "It should hold read-only credentials, so a compromise of that service cannot alter or delete anything.",
                                "Il doit utiliser des identifiants en lecture seule, pour qu'une compromission ne puisse rien modifier ni supprimer.",
                                "يجب أن تحمل بيانات اعتماد للقراءة فقط، فلا يستطيع اختراقها تغيير شيء أو حذفه.",
                            ),
                            options=[
                                Option(T("Full administrator access for convenience", "Un accès administrateur complet par commodité", "صلاحية مدير كاملة للتسهيل")),
                                Option(T("A read-only database account", "Un compte de base de données en lecture seule", "حساب قاعدة بيانات للقراءة فقط"), correct=True),
                                Option(T("The same account the web application uses", "Le même compte que l'application web", "الحساب نفسه الذي يستخدمه تطبيق الويب")),
                                Option(T("No credentials at all", "Aucun identifiant", "لا بيانات اعتماد إطلاقًا")),
                            ],
                        ),
                    ],
                ),
                Lesson(
                    slug="authentication-and-authorisation",
                    minutes=35,
                    xp=60,
                    difficulty=D.intermediate,
                    title=T("Authentication and Authorisation", "Authentification et Autorisation", "التوثيق والتخويل"),
                    story=T(
                        "Who are you, and what are you allowed to do? Two questions, and confusing them is a vulnerability.",
                        "Qui êtes-vous, et qu'avez-vous le droit de faire ? Deux questions, et les confondre est une vulnérabilité.",
                        "من أنت؟ وما المسموح لك بفعله؟ سؤالان، والخلط بينهما ثغرة.",
                    ),
                    objective=T(
                        "Distinguish authentication from authorisation and describe how sessions and tokens carry identity.",
                        "Distinguer authentification et autorisation et décrire comment sessions et jetons portent l'identité.",
                        "التمييز بين التوثيق والتخويل، ووصف كيف تحمل الجلسات والرموز الهويّة.",
                    ),
                    skills=T(
                        "Authentication factors, MFA, sessions, tokens, RBAC, access control checks",
                        "Facteurs d'authentification, MFA, sessions, jetons, RBAC, contrôles d'accès",
                        "عوامل التوثيق، المصادقة متعدّدة العوامل، الجلسات، الرموز، التحكّم بالأدوار، فحوص الصلاحية",
                    ),
                    blocks=[
                        Text(
                            T(
                                "**Authentication** proves identity, using something you know (a password), something you have (a phone, a security key) or something you are (a fingerprint). Combining two different kinds is **multi-factor authentication**, and it is the single most effective control against stolen passwords. **Authorisation** is the separate question of what that proven identity may do.",
                                "L'**authentification** prouve l'identité, par quelque chose que l'on sait (mot de passe), que l'on a (téléphone, clé de sécurité) ou que l'on est (empreinte). Combiner deux catégories différentes donne l'**authentification multifacteur**, le contrôle le plus efficace contre les mots de passe volés. L'**autorisation** est la question distincte de ce que cette identité prouvée peut faire.",
                                "**التوثيق** يثبت الهويّة عبر شيء تعرفه (كلمة مرور) أو شيء تملكه (هاتف أو مفتاح أمان) أو شيء أنتَه (بصمة). وجمع نوعين مختلفين هو **التوثيق متعدّد العوامل**، وهو أنجع ضابط منفرد ضدّ كلمات المرور المسروقة. أمّا **التخويل** فسؤال منفصل عمّا يُسمح لتلك الهويّة المثبَتة بفعله.",
                            )
                        ),
                        Text(
                            T(
                                "After a successful login the server issues a **session** or a **token** so the user does not re-authenticate on every request. A token is signed, so the server can verify it was issued by itself and has not been altered — but a signature only proves *who*, never *what they may do*. Authorisation has to be checked separately, on every request, on the server.",
                                "Après une connexion réussie, le serveur émet une **session** ou un **jeton** pour éviter de se ré-authentifier à chaque requête. Un jeton est signé : le serveur vérifie qu'il l'a bien émis et qu'il n'a pas été altéré — mais une signature ne prouve que *qui*, jamais *ce qui est permis*. L'autorisation doit être vérifiée séparément, à chaque requête, côté serveur.",
                                "بعد نجاح تسجيل الدخول يُصدر الخادم **جلسة** أو **رمزًا** كي لا يعيد المستخدم التوثيق مع كلّ طلب. والرمز موقَّع، فيتحقّق الخادم أنّه هو من أصدره وأنّه لم يُغيَّر — لكنّ التوقيع لا يثبت إلّا *من*، ولا يثبت أبدًا *ما المسموح له*. فالتخويل يجب فحصه منفصلًا، مع كلّ طلب، على الخادم.",
                            )
                        ),
                        Code(
                            T(
                                "The vulnerability class this prevents is called broken access control:",
                                "La classe de vulnérabilité ainsi évitée s'appelle contrôle d'accès défaillant :",
                                "فئة الثغرات التي يمنعها هذا تُسمّى «تحكّم وصول معطوب»:",
                            ),
                            "# Vulnerable: identity was checked, permission was not.\n"
                            "@router.get('/invoices/{invoice_id}')\n"
                            "async def read_invoice(invoice_id, user = Depends(current_user)):\n"
                            "    return await load_invoice(invoice_id)   # any logged-in user\n"
                            "                                            # can read any invoice\n\n"
                            "# Fixed: the object is checked against the caller, server-side.\n"
                            "@router.get('/invoices/{invoice_id}')\n"
                            "async def read_invoice(invoice_id, user = Depends(current_user)):\n"
                            "    invoice = await load_invoice(invoice_id)\n"
                            "    if invoice.owner_id != user.id:\n"
                            "        raise HTTPException(status_code=404)  # not 403: do not\n"
                            "    return invoice                            # confirm it exists",
                        ),
                        ExamTip(
                            T(
                                "Hiding a button in the interface is not authorisation. The browser is under the user's control, so every permission decision has to be repeated on the server.",
                                "Masquer un bouton dans l'interface n'est pas de l'autorisation. Le navigateur est sous le contrôle de l'utilisateur : chaque décision de permission doit être répétée côté serveur.",
                                "إخفاء زرّ في الواجهة ليس تخويلًا. فالمتصفّح تحت سيطرة المستخدم، ولذلك يجب تكرار كلّ قرار صلاحية على الخادم.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "A logged-in student changes the id in a URL and sees another student's marks. What failed?",
                                "Un élève connecté modifie l'identifiant dans une URL et voit les notes d'un autre. Qu'est-ce qui a échoué ?",
                                "طالب مسجّل الدخول غيّر المعرّف في الرابط فرأى درجات طالب آخر. ما الذي أخفق؟",
                            ),
                            hint=T("Identity was proven correctly. What was not checked?", "L'identité était prouvée. Que n'a-t-on pas vérifié ?", "أُثبتت الهويّة فعلًا. فما الذي لم يُفحَص؟"),
                            explanation=T(
                                "Authentication worked — the server knew who it was. Authorisation did not: nothing checked that this user owned that record.",
                                "L'authentification a marché — le serveur savait qui c'était. L'autorisation non : rien n'a vérifié que cet utilisateur possédait cet enregistrement.",
                                "نجح التوثيق — فقد عرف الخادم هويّته. أمّا التخويل فلم ينجح: لم يفحص شيء أنّ هذا المستخدم يملك ذلك السجلّ.",
                            ),
                            options=[
                                Option(T("Authentication", "L'authentification", "التوثيق")),
                                Option(T("Authorisation", "L'autorisation", "التخويل"), correct=True),
                                Option(T("Encryption in transit", "Le chiffrement en transit", "التشفير أثناء النقل")),
                                Option(T("Availability", "La disponibilité", "التوافر")),
                            ],
                        ),
                        MCQ(
                            prompt=T(
                                "Which pair is genuine multi-factor authentication?",
                                "Quelle paire constitue une vraie authentification multifacteur ?",
                                "أيّ زوج يمثّل توثيقًا متعدّد العوامل حقيقيًا؟",
                            ),
                            hint=T("The two factors must be different kinds of thing.", "Les deux facteurs doivent être de natures différentes.", "يجب أن يكون العاملان من نوعين مختلفين."),
                            explanation=T(
                                "A password (something you know) plus a hardware key (something you have) uses two different categories; two passwords are one category twice.",
                                "Un mot de passe (ce que l'on sait) et une clé matérielle (ce que l'on a) relèvent de deux catégories ; deux mots de passe, d'une seule.",
                                "كلمة مرور (شيء تعرفه) مع مفتاح عتادي (شيء تملكه) عاملان من فئتين مختلفتين، أمّا كلمتا مرور فمن فئة واحدة مكرّرة.",
                            ),
                            options=[
                                Option(T("A password and a second password", "Un mot de passe et un second mot de passe", "كلمة مرور وكلمة مرور ثانية")),
                                Option(T("A password and a hardware security key", "Un mot de passe et une clé de sécurité matérielle", "كلمة مرور ومفتاح أمان عتادي"), correct=True),
                                Option(T("A username and a password", "Un identifiant et un mot de passe", "اسم مستخدم وكلمة مرور")),
                                Option(T("A password and a security question", "Un mot de passe et une question secrète", "كلمة مرور وسؤال سرّي")),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        Module(
            slug="cryptography-fundamentals",
            title=T("Cryptography Fundamentals", "Fondamentaux de la Cryptographie", "أساسيات التعمية"),
            description=T(
                "Hashing, encryption and public keys — what each one is actually for.",
                "Hachage, chiffrement et clés publiques — à quoi sert réellement chacun.",
                "التجزئة والتشفير والمفاتيح العامّة — ما الغرض الحقيقي من كلّ منها.",
            ),
            lessons=[
                Lesson(
                    slug="hashing-and-passwords",
                    minutes=35,
                    xp=65,
                    difficulty=D.intermediate,
                    title=T("Hashing and Password Storage", "Hachage et Stockage des Mots de Passe", "التجزئة وتخزين كلمات المرور"),
                    story=T(
                        "Every leaked-password headline is the same story: the database was stolen, and it should not have mattered.",
                        "Chaque fuite de mots de passe raconte la même histoire : la base a été volée, et cela n'aurait pas dû importer.",
                        "كلّ خبر عن تسرّب كلمات مرور هو القصّة نفسها: سُرقت قاعدة البيانات، وما كان ينبغي أن يهمّ ذلك.",
                    ),
                    objective=T(
                        "Explain why passwords are hashed rather than encrypted, and what salting and slow hashing achieve.",
                        "Expliquer pourquoi les mots de passe sont hachés et non chiffrés, et ce qu'apportent le salage et le hachage lent.",
                        "شرح لماذا تُجزَّأ كلمات المرور بدل تشفيرها، وما الذي يحقّقه التمليح والتجزئة البطيئة.",
                    ),
                    skills=T(
                        "Hash functions, one-way, salt, work factor, bcrypt/PBKDF2/Argon2, integrity",
                        "Fonctions de hachage, sens unique, sel, facteur de travail, bcrypt/PBKDF2/Argon2, intégrité",
                        "دوالّ التجزئة، الاتّجاه الواحد، الملح، عامل الجهد، bcrypt/PBKDF2/Argon2، السلامة",
                    ),
                    blocks=[
                        Text(
                            T(
                                "A **hash** turns any input into a fixed-size fingerprint, and cannot be reversed — many inputs map to the same output space, so the information to invert it is simply not there. Encryption is *designed* to be reversed by whoever holds the key; a password should never be recoverable at all, which is why passwords are hashed and not encrypted.",
                                "Un **hachage** transforme toute entrée en une empreinte de taille fixe, non inversible — de nombreuses entrées se projettent sur le même espace de sortie : l'information nécessaire à l'inversion n'existe pas. Le chiffrement est *conçu* pour être inversé par le détenteur de la clé ; un mot de passe ne doit jamais être récupérable, d'où le hachage et non le chiffrement.",
                                "**التجزئة** تحوّل أيّ مدخل إلى بصمة ثابتة الطول ولا يمكن عكسها — إذ ترتسم مدخلات كثيرة على فضاء المخرجات نفسه، فالمعلومة اللازمة للعكس غير موجودة أصلًا. أمّا التشفير فمصمَّم ليُعكَس بيد من يملك المفتاح؛ وكلمة المرور يجب ألّا تكون قابلة للاسترجاع أبدًا، ولهذا تُجزَّأ ولا تُشفَّر.",
                            )
                        ),
                        Text(
                            T(
                                "Two additions turn a hash into safe password storage. A **salt** is a unique random value stored beside each hash, so two users with the same password get different hashes and a precomputed table is useless. A deliberately **slow** algorithm with a tunable **work factor** — bcrypt, PBKDF2, Argon2 — makes each guess expensive, which is exactly what a general-purpose fast hash like SHA-256 fails to do.",
                                "Deux ajouts transforment un hachage en stockage sûr. Un **sel** est une valeur aléatoire unique stockée à côté de chaque empreinte : deux utilisateurs au même mot de passe obtiennent des empreintes différentes, et une table précalculée devient inutile. Un algorithme délibérément **lent** à **facteur de travail** réglable — bcrypt, PBKDF2, Argon2 — rend chaque essai coûteux, ce qu'un hachage rapide comme SHA-256 ne fait pas.",
                                "إضافتان تحوّلان التجزئة إلى تخزين آمن. **الملح** قيمة عشوائية فريدة تُخزَّن بجانب كلّ بصمة، فيحصل مستخدمان لهما كلمة المرور نفسها على بصمتين مختلفتين ويصبح الجدول المحسوب مسبقًا عديم الفائدة. وخوارزمية **بطيئة** عمدًا بعامل جهد قابل للضبط — bcrypt أو PBKDF2 أو Argon2 — تجعل كلّ تخمين مكلفًا، وهو بالضبط ما تعجز عنه تجزئة سريعة عامّة الغرض مثل SHA-256.",
                            )
                        ),
                        Code(
                            T(
                                "This is exactly how AtlasCode itself stores passwords (see app/core/security.py):",
                                "C'est précisément ainsi qu'AtlasCode stocke les mots de passe (voir app/core/security.py) :",
                                "هكذا يخزّن AtlasCode كلمات المرور فعلًا (انظر app/core/security.py):",
                            ),
                            "from passlib.context import CryptContext\n\n"
                            "pwd_context = CryptContext(\n"
                            "    schemes=['pbkdf2_sha256'],\n"
                            "    pbkdf2_sha256__default_rounds=600_000,   # the work factor\n"
                            ")\n\n"
                            "stored = pwd_context.hash('correct horse battery staple')\n"
                            "# passlib generates a random salt and embeds it in the string,\n"
                            "# together with the algorithm and the round count:\n"
                            "#   $pbkdf2-sha256$600000$<salt>$<hash>\n\n"
                            "print(pwd_context.verify('correct horse battery staple', stored))\n"
                            "print(pwd_context.verify('wrong guess', stored))",
                        ),
                        ExamTip(
                            T(
                                "\"We encrypt your passwords\" in a breach notice means they could be decrypted, which is a design fault, not reassurance. The correct sentence is \"we store salted hashes with a high work factor\".",
                                "« Nous chiffrons vos mots de passe » dans un avis de fuite signifie qu'ils sont déchiffrables : c'est un défaut de conception, pas une garantie. La bonne phrase est « nous stockons des empreintes salées à facteur de travail élevé ».",
                                "عبارة «نشفّر كلمات مروركم» في إشعار اختراق تعني أنّها قابلة لفكّ التشفير، وهذا عيب تصميمي لا طمأنة. والصيغة الصحيحة: «نخزّن بصمات مملّحة بعامل جهد عالٍ».",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "Why is a unique salt stored with every password hash?",
                                "Pourquoi un sel unique est-il stocké avec chaque empreinte de mot de passe ?",
                                "لماذا يُخزَّن ملح فريد مع كلّ بصمة كلمة مرور؟",
                            ),
                            hint=T(
                                "Think about two users who happen to choose the same password.",
                                "Pensez à deux utilisateurs choisissant le même mot de passe.",
                                "فكّر في مستخدمين اختارا كلمة المرور نفسها.",
                            ),
                            explanation=T(
                                "The salt makes identical passwords hash differently, so one precomputed table cannot crack many accounts at once.",
                                "Le sel fait que des mots de passe identiques donnent des empreintes différentes : une table précalculée ne peut casser plusieurs comptes d'un coup.",
                                "الملح يجعل كلمات المرور المتطابقة تُنتج بصمات مختلفة، فلا يستطيع جدول محسوب مسبقًا كسر حسابات كثيرة دفعةً واحدة.",
                            ),
                            options=[
                                Option(T("To let the server recover the password later", "Pour permettre au serveur de récupérer le mot de passe", "ليتمكّن الخادم من استرجاع كلمة المرور لاحقًا")),
                                Option(
                                    T(
                                        "So identical passwords produce different hashes",
                                        "Pour que des mots de passe identiques donnent des empreintes différentes",
                                        "كي تُنتج كلمات المرور المتطابقة بصمات مختلفة",
                                    ),
                                    correct=True,
                                ),
                                Option(T("To make hashing faster", "Pour accélérer le hachage", "لتسريع التجزئة")),
                                Option(T("To compress the stored value", "Pour compresser la valeur stockée", "لضغط القيمة المخزّنة")),
                            ],
                        ),
                        ShortAnswer(
                            prompt=T(
                                "Why is a deliberately slow hash better than SHA-256 for passwords? One sentence.",
                                "Pourquoi un hachage volontairement lent vaut-il mieux que SHA-256 pour les mots de passe ? Une phrase.",
                                "لماذا التجزئة البطيئة عمدًا أفضل من SHA-256 لكلمات المرور؟ جملة واحدة.",
                            ),
                            hint=T(
                                "Think from the point of view of someone testing billions of guesses.",
                                "Placez-vous du côté de qui teste des milliards d'essais.",
                                "ضع نفسك مكان من يجرّب مليارات التخمينات.",
                            ),
                            explanation=T(
                                "A slow hash with a high work factor makes each guess expensive, so testing a stolen database becomes impractically slow.",
                                "Un hachage lent à facteur de travail élevé rend chaque essai coûteux : tester une base volée devient trop lent.",
                                "التجزئة البطيئة بعامل جهد عالٍ تجعل كلّ تخمين مكلفًا، فيصبح اختبار قاعدة مسروقة بطيئًا إلى حدّ العجز.",
                            ),
                            keywords=[
                                ["slow", "slower", "expensive", "cost", "lent", "coûteux", "بطيء", "مكلف"],
                                ["guess", "guesses", "attempt", "essai", "تخمين", "محاولة"],
                            ],
                            reference_answer="Because a slow hash makes every guess expensive, so an attacker with a stolen database cannot test billions of candidate passwords quickly.",
                        ),
                    ],
                ),
                Lesson(
                    slug="encryption-and-public-keys",
                    minutes=35,
                    xp=65,
                    difficulty=D.advanced,
                    title=T("Encryption and Public-Key Cryptography", "Chiffrement et Cryptographie à Clé Publique", "التشفير وتعمية المفتاح العامّ"),
                    story=T(
                        "How do two strangers agree on a secret while everyone is listening? The answer is why the web works.",
                        "Comment deux inconnus se mettent-ils d'accord sur un secret alors que tout le monde écoute ? La réponse explique le web.",
                        "كيف يتّفق غريبان على سرّ والجميع يستمع؟ الجواب هو سبب عمل الويب.",
                    ),
                    objective=T(
                        "Distinguish symmetric from asymmetric encryption and explain how HTTPS combines them.",
                        "Distinguer chiffrement symétrique et asymétrique et expliquer comment HTTPS les combine.",
                        "التمييز بين التشفير المتناظر وغير المتناظر، وشرح كيف يجمع HTTPS بينهما.",
                    ),
                    skills=T(
                        "Symmetric/asymmetric encryption, key exchange, digital signatures, certificates, TLS",
                        "Chiffrement symétrique/asymétrique, échange de clés, signatures numériques, certificats, TLS",
                        "التشفير المتناظر وغير المتناظر، تبادل المفاتيح، التواقيع الرقمية، الشهادات، TLS",
                    ),
                    blocks=[
                        Text(
                            T(
                                "**Symmetric** encryption (AES) uses one key for both locking and unlocking. It is fast, and it has one problem: both sides must already share the key. **Asymmetric** encryption gives everyone a pair — a public key anyone may hold and a private key that never leaves its owner. What one locks, only the other opens.",
                                "Le chiffrement **symétrique** (AES) utilise une seule clé pour fermer et ouvrir. Il est rapide, avec un seul problème : les deux parties doivent déjà partager la clé. Le chiffrement **asymétrique** donne à chacun une paire — une clé publique que tout le monde peut détenir, une clé privée qui ne quitte jamais son propriétaire. Ce que l'une ferme, seule l'autre l'ouvre.",
                                "التشفير **المتناظر** (AES) يستخدم مفتاحًا واحدًا للإقفال والفتح. وهو سريع، وله مشكلة واحدة: على الطرفين أن يتشاركا المفتاح مسبقًا. أمّا التشفير **غير المتناظر** فيعطي كلّ طرف زوجًا — مفتاحًا عامًّا يمكن لأيّ أحد حمله، ومفتاحًا خاصًّا لا يغادر صاحبه أبدًا. وما يقفله أحدهما لا يفتحه إلّا الآخر.",
                            )
                        ),
                        Text(
                            T(
                                "That asymmetry gives two different powers. Encrypt with someone's **public** key and only they can read it — confidentiality. Encrypt a fingerprint with your **private** key and anyone can verify it was you and that nothing changed — a **digital signature**, which is integrity plus authenticity.",
                                "Cette asymétrie donne deux pouvoirs. Chiffrer avec la clé **publique** de quelqu'un : lui seul peut lire — confidentialité. Chiffrer une empreinte avec sa clé **privée** : chacun peut vérifier que c'était bien vous et que rien n'a changé — une **signature numérique**, soit intégrité et authenticité.",
                                "هذا اللاتناظر يمنح قدرتين مختلفتين. فالتشفير بمفتاح شخص **العامّ** يجعله وحده قادرًا على القراءة — وهذه سرّية. وتشفير بصمة بمفتاحك **الخاصّ** يتيح للجميع التحقّق أنّك أنت وأنّ شيئًا لم يتغيّر — وهذا **توقيع رقمي**، أي سلامة مع أصالة.",
                            )
                        ),
                        Code(
                            T(
                                "HTTPS uses both, because each solves the other's problem:",
                                "HTTPS utilise les deux, car chacun résout le problème de l'autre :",
                                "يستخدم HTTPS الاثنين، لأنّ كلًّا منهما يحلّ مشكلة الآخر:",
                            ),
                            "# 1. The server presents a CERTIFICATE: its public key, signed by\n"
                            "#    a certificate authority the browser already trusts.\n"
                            "# 2. The browser verifies that signature -> it is really this site.\n"
                            "# 3. Both sides use asymmetric maths to agree on a fresh\n"
                            "#    SYMMETRIC session key that no listener can derive.\n"
                            "# 4. The rest of the conversation uses that fast symmetric key.\n\n"
                            "# Asymmetric solves 'how do we agree on a key at all'.\n"
                            "# Symmetric solves 'how do we encrypt megabytes quickly'.\n"
                            "# The padlock in the address bar means step 2 succeeded --\n"
                            "# it says the connection is private, NOT that the site is honest.",
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "You want to send a file only Amina can read. Which key do you encrypt with?",
                                "Vous voulez envoyer un fichier que seule Amina peut lire. Avec quelle clé chiffrez-vous ?",
                                "تريد إرسال ملفّ لا تقرؤه إلّا أمينة. بأيّ مفتاح تشفّر؟",
                            ),
                            hint=T("Only her private key can undo it, so what must lock it?", "Seule sa clé privée peut l'ouvrir : que faut-il utiliser pour fermer ?", "مفتاحها الخاصّ وحده يفتحه، فبمَ تُقفله؟"),
                            explanation=T(
                                "Encrypting with Amina's public key means only the matching private key — which only she has — can decrypt it.",
                                "Chiffrer avec la clé publique d'Amina signifie que seule la clé privée correspondante, qu'elle seule détient, peut déchiffrer.",
                                "التشفير بمفتاح أمينة العامّ يعني أنّ المفتاح الخاصّ المقابل — وهي وحدها تملكه — هو ما يفكّه.",
                            ),
                            options=[
                                Option(T("Amina's public key", "La clé publique d'Amina", "مفتاح أمينة العامّ"), correct=True),
                                Option(T("Amina's private key", "La clé privée d'Amina", "مفتاح أمينة الخاصّ")),
                                Option(T("Your own private key", "Votre propre clé privée", "مفتاحك الخاصّ")),
                                Option(T("A shared password", "Un mot de passe partagé", "كلمة مرور مشتركة")),
                            ],
                        ),
                        MCQ(
                            prompt=T(
                                "What does the padlock in a browser's address bar actually guarantee?",
                                "Que garantit réellement le cadenas dans la barre d'adresse ?",
                                "ماذا يضمن القفل في شريط العنوان فعلًا؟",
                            ),
                            hint=T("It is a statement about the connection, not about the company.", "C'est une affirmation sur la connexion, pas sur l'entreprise.", "إنّه قول عن الاتّصال لا عن الجهة."),
                            explanation=T(
                                "It means traffic is encrypted and the certificate matches the domain. It says nothing about whether the site is trustworthy — phishing sites use HTTPS too.",
                                "Cela signifie que le trafic est chiffré et que le certificat correspond au domaine. Rien sur l'honnêteté du site — les sites d'hameçonnage utilisent aussi HTTPS.",
                                "يعني أنّ حركة البيانات مشفّرة وأنّ الشهادة تطابق النطاق. ولا يقول شيئًا عن نزاهة الموقع — فمواقع التصيّد تستخدم HTTPS أيضًا.",
                            ),
                            options=[
                                Option(T("The site is owned by a legitimate company", "Le site appartient à une entreprise légitime", "الموقع يملكه كيان شرعي")),
                                Option(
                                    T(
                                        "Traffic is encrypted and the certificate matches the domain",
                                        "Le trafic est chiffré et le certificat correspond au domaine",
                                        "حركة البيانات مشفّرة والشهادة تطابق النطاق",
                                    ),
                                    correct=True,
                                ),
                                Option(T("The site cannot contain malware", "Le site ne peut pas contenir de logiciel malveillant", "لا يمكن أن يحوي الموقع برمجيات خبيثة")),
                                Option(T("Your password is stored safely there", "Votre mot de passe y est stocké en sécurité", "كلمة مرورك مخزّنة هناك بأمان")),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)


NETWORK_SECURITY = CourseSpec(
    slug="network-security-fundamentals",
    stage=6,
    track="security",
    icon="🔐",
    difficulty=D.intermediate,
    estimated_hours=10,
    prerequisite_slug="cybersecurity-foundations",
    title=T(
        "Fundamentals of Computer Networks Security",
        "Fondamentaux de la Sécurité des Réseaux Informatiques",
        "أساسيات أمن شبكات الحاسوب",
    ),
    description=T(
        "Securing the network itself: where traffic is exposed, how segmentation and firewalls contain damage, how TLS protects a conversation, and how attacks are detected and answered.",
        "Sécuriser le réseau lui-même : où le trafic est exposé, comment segmentation et pare-feux limitent les dégâts, comment TLS protège une conversation, et comment détecter et répondre aux attaques.",
        "تأمين الشبكة نفسها: أين تنكشف حركة البيانات، وكيف تحدّ التجزئة والجدران النارية من الضرر، وكيف يحمي TLS المحادثة، وكيف تُكتشَف الهجمات ويُستجاب لها.",
    ),
    skills=T(
        "Network threat model, firewalls, segmentation, VPN, TLS, monitoring, incident response",
        "Modèle de menace réseau, pare-feux, segmentation, VPN, TLS, supervision, réponse à incident",
        "نموذج تهديد الشبكة، الجدران النارية، التجزئة، الشبكة الخاصّة الافتراضية، TLS، المراقبة، الاستجابة للحوادث",
    ),
    modules=[
        Module(
            slug="network-threat-model",
            title=T("The Network Threat Model", "Le Modèle de Menace Réseau", "نموذج تهديد الشبكة"),
            description=T(
                "What an unprotected network exposes, and why.",
                "Ce qu'expose un réseau non protégé, et pourquoi.",
                "ما الذي تكشفه شبكة غير محميّة، ولماذا.",
            ),
            lessons=[
                Lesson(
                    slug="why-networks-are-exposed",
                    minutes=35,
                    xp=60,
                    difficulty=D.intermediate,
                    title=T("Why Networks Are Exposed", "Pourquoi les Réseaux Sont Exposés", "لماذا تنكشف الشبكات"),
                    story=T(
                        "The internet was designed to deliver packets, not to protect them. Security was added later, on purpose, in layers.",
                        "Internet a été conçu pour acheminer des paquets, pas pour les protéger. La sécurité a été ajoutée ensuite, volontairement, par couches.",
                        "صُمِّمت الإنترنت لتوصيل الرزم لا لحمايتها. وأُضيف الأمن لاحقًا عن قصد، على طبقات.",
                    ),
                    objective=T(
                        "Describe what an on-path observer can see, and which protections remove which exposure.",
                        "Décrire ce qu'un observateur sur le chemin peut voir, et quelles protections suppriment quelle exposition.",
                        "وصف ما يراه مراقب على المسار، وأيّ الحمايات تزيل أيّ انكشاف.",
                    ),
                    skills=T(
                        "Packets in transit, on-path observers, metadata, encryption boundaries, public Wi-Fi",
                        "Paquets en transit, observateurs sur le chemin, métadonnées, frontières de chiffrement, Wi-Fi public",
                        "الرزم أثناء النقل، المراقبون على المسار، البيانات الوصفية، حدود التشفير، الواي فاي العامّ",
                    ),
                    blocks=[
                        Text(
                            T(
                                "A packet crossing the internet passes through routers nobody in the conversation controls. Anything sent without encryption is readable by every one of them — which is why plain HTTP, FTP and Telnet are considered unsafe on any network you do not own, and why the modern web is HTTPS by default.",
                                "Un paquet traversant Internet passe par des routeurs que personne dans la conversation ne contrôle. Tout ce qui est envoyé en clair y est lisible — d'où le caractère non sûr de HTTP, FTP et Telnet sur un réseau qui n'est pas le vôtre, et le HTTPS par défaut du web moderne.",
                                "الرزمة العابرة للإنترنت تمرّ بموجّهات لا يتحكّم بها أحد من طرفَي المحادثة. وكلّ ما يُرسَل بلا تشفير يمكن لكلّ واحد منها قراءته — ولهذا يُعدّ HTTP وFTP وTelnet غير آمنة على أيّ شبكة لا تملكها، ولهذا صار الويب الحديث HTTPS افتراضيًا.",
                            )
                        ),
                        Text(
                            T(
                                "Encryption hides the **content**, not the **metadata**. An observer still sees which addresses talked, when, how often and roughly how much. That is why the destination domain leaks even under TLS unless Encrypted Client Hello is in use, and why traffic analysis is a real discipline.",
                                "Le chiffrement masque le **contenu**, pas les **métadonnées**. Un observateur voit toujours quelles adresses ont communiqué, quand, à quelle fréquence et à peu près combien. C'est pourquoi le domaine de destination fuit même sous TLS sans Encrypted Client Hello, et pourquoi l'analyse de trafic est une vraie discipline.",
                                "التشفير يخفي **المحتوى** لا **البيانات الوصفية**. فالمراقب يظلّ يرى أيّ العناوين تحادثت ومتى وكم مرّة وبأيّ حجم تقريبًا. ولهذا يتسرّب نطاق الوجهة حتى تحت TLS ما لم يُستخدم Encrypted Client Hello، ولهذا فتحليل حركة البيانات تخصّص قائم بذاته.",
                            )
                        ),
                        Code(
                            T(
                                "The same request, before and after transport security:",
                                "La même requête, avant et après la sécurisation du transport :",
                                "الطلب نفسه قبل تأمين النقل وبعده:",
                            ),
                            "# Over plain HTTP, every router on the path sees this in full:\n"
                            "#   POST /login HTTP/1.1\n"
                            "#   Host: school.example\n"
                            "#   email=amina@example.com&password=hunter2\n\n"
                            "# Over HTTPS it sees only:\n"
                            "#   - the two IP addresses\n"
                            "#   - the timing and size of the encrypted records\n"
                            "#   - (usually) the destination hostname during the handshake\n"
                            "# The path, headers, body and cookies are unreadable.",
                        ),
                        ExamTip(
                            T(
                                "\"The Wi-Fi has a password\" is not the same as \"my traffic is private\". Everyone else with that same password is on the network too. End-to-end encryption is what protects you; the Wi-Fi key only controls who may join.",
                                "« Le Wi-Fi a un mot de passe » n'équivaut pas à « mon trafic est privé ». Tous ceux qui ont ce mot de passe sont sur le même réseau. C'est le chiffrement de bout en bout qui protège ; la clé Wi-Fi ne contrôle que qui peut se connecter.",
                                "عبارة «الواي فاي له كلمة مرور» ليست عبارة «حركتي خاصّة». فكلّ من يملك كلمة المرور نفسها موجود على الشبكة. والتشفير من الطرف إلى الطرف هو ما يحميك، أمّا مفتاح الواي فاي فيتحكّم فقط بمن يُسمح له بالانضمام.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "You use HTTPS on a café network. What can the network operator still learn?",
                                "Vous utilisez HTTPS sur le réseau d'un café. Que peut encore apprendre l'opérateur du réseau ?",
                                "تستخدم HTTPS على شبكة مقهى. ماذا يظلّ مشغّل الشبكة قادرًا على معرفته؟",
                            ),
                            hint=T("Encryption protects content. What is outside the content?", "Le chiffrement protège le contenu. Qu'y a-t-il en dehors ?", "التشفير يحمي المحتوى. فما الذي يقع خارجه؟"),
                            explanation=T(
                                "Metadata remains visible: which servers you connected to, when, and how much data moved. The page contents and credentials do not.",
                                "Les métadonnées restent visibles : quels serveurs, quand, quel volume. Le contenu des pages et les identifiants, non.",
                                "تبقى البيانات الوصفية ظاهرة: بأيّ خوادم اتّصلت ومتى وكم من البيانات انتقل. أمّا محتوى الصفحات وبيانات الاعتماد فلا.",
                            ),
                            options=[
                                Option(T("Your password", "Votre mot de passe", "كلمة مرورك")),
                                Option(T("The contents of the pages you read", "Le contenu des pages lues", "محتوى الصفحات التي تقرأها")),
                                Option(
                                    T(
                                        "Which servers you contacted and when",
                                        "Quels serveurs vous avez contactés et quand",
                                        "بأيّ خوادم اتّصلت ومتى",
                                    ),
                                    correct=True,
                                ),
                                Option(T("Nothing at all", "Rien du tout", "لا شيء إطلاقًا")),
                            ],
                        ),
                        MCQ(
                            prompt=T(
                                "Which of these protocols sends credentials in the clear and should be replaced?",
                                "Lequel de ces protocoles envoie les identifiants en clair et doit être remplacé ?",
                                "أيّ من هذه البروتوكولات يرسل بيانات الاعتماد بلا تشفير وينبغي استبداله؟",
                            ),
                            hint=T("One of these predates transport encryption entirely.", "L'un d'eux est antérieur au chiffrement du transport.", "أحدها أقدم من تشفير النقل أصلًا."),
                            explanation=T(
                                "Telnet transmits everything, including passwords, unencrypted; SSH replaced it precisely for that reason.",
                                "Telnet transmet tout en clair, mots de passe compris ; SSH l'a remplacé exactement pour cela.",
                                "‏Telnet ينقل كلّ شيء بلا تشفير بما فيه كلمات المرور؛ وقد حلّ SSH محلّه لهذا السبب بالذات.",
                            ),
                            options=[
                                Option(T("SSH", "SSH", "SSH")),
                                Option(T("Telnet", "Telnet", "Telnet"), correct=True),
                                Option(T("HTTPS", "HTTPS", "HTTPS")),
                                Option(T("SFTP", "SFTP", "SFTP")),
                            ],
                        ),
                    ],
                ),
                Lesson(
                    slug="firewalls-and-segmentation",
                    minutes=35,
                    xp=60,
                    difficulty=D.intermediate,
                    title=T("Firewalls and Network Segmentation", "Pare-feux et Segmentation Réseau", "الجدران النارية وتجزئة الشبكة"),
                    story=T(
                        "A ship does not sink because it took on water. It sinks because there were no bulkheads.",
                        "Un navire ne coule pas parce qu'il a pris l'eau. Il coule parce qu'il n'y avait pas de cloisons.",
                        "لا تغرق السفينة لأنّ الماء دخلها، بل لأنّه لم تكن فيها حواجز.",
                    ),
                    objective=T(
                        "Write default-deny firewall policy and design segments that limit lateral movement.",
                        "Écrire une politique de pare-feu par refus par défaut et concevoir des segments limitant les déplacements latéraux.",
                        "كتابة سياسة جدار ناري بالمنع الافتراضي، وتصميم أجزاء تحدّ من التنقّل الجانبي.",
                    ),
                    skills=T(
                        "Default deny, ingress/egress rules, DMZ, VLANs, lateral movement, zero trust",
                        "Refus par défaut, règles entrantes/sortantes, DMZ, VLAN, mouvement latéral, zero trust",
                        "المنع الافتراضي، قواعد الدخول والخروج، المنطقة منزوعة السلاح، VLAN، التنقّل الجانبي، انعدام الثقة",
                    ),
                    blocks=[
                        Text(
                            T(
                                "A **firewall** decides which traffic may pass, based on address, port and direction. The only defensible starting policy is **default deny**: block everything, then allow exactly what is needed. A default-allow list is a list of the attacks you have already thought of, which is not the same as the attacks that exist.",
                                "Un **pare-feu** décide du trafic autorisé selon l'adresse, le port et le sens. La seule politique de départ défendable est le **refus par défaut** : tout bloquer, puis autoriser exactement le nécessaire. Une liste en autorisation par défaut n'est que la liste des attaques auxquelles on a déjà pensé, ce qui n'est pas la liste de celles qui existent.",
                                "**الجدار الناري** يقرّر أيّ حركة يُسمح بمرورها بناءً على العنوان والمنفذ والاتّجاه. والسياسة الابتدائية الوحيدة القابلة للدفاع هي **المنع الافتراضي**: امنع كلّ شيء ثمّ اسمح بما يلزم بالضبط. أمّا قائمة السماح الافتراضي فليست إلّا قائمة الهجمات التي فكّرت فيها، وهي غير قائمة الهجمات الموجودة.",
                            )
                        ),
                        Text(
                            T(
                                "**Segmentation** splits one flat network into zones that cannot freely reach each other: public web servers in a DMZ, databases on an internal segment reachable only from the application, staff devices elsewhere. It does not stop the first compromise — it stops that compromise from becoming every machine, which is called **lateral movement**.",
                                "La **segmentation** divise un réseau plat en zones qui ne se joignent pas librement : serveurs web publics en DMZ, bases de données sur un segment interne joignable seulement depuis l'application, postes du personnel ailleurs. Elle n'empêche pas la première compromission — elle l'empêche de devenir celle de toutes les machines, ce qu'on appelle le **mouvement latéral**.",
                                "**التجزئة** تقسّم الشبكة المسطّحة إلى مناطق لا يصل بعضها إلى بعض بحرّية: خوادم الويب العامّة في منطقة منزوعة السلاح، وقواعد البيانات في جزء داخلي لا يُوصَل إليه إلّا من التطبيق، وأجهزة الموظّفين في مكان آخر. وهي لا تمنع الاختراق الأوّل — بل تمنعه من أن يصير اختراق كلّ جهاز، وهو ما يُسمّى **التنقّل الجانبي**.",
                            )
                        ),
                        Code(
                            T(
                                "A default-deny policy for a small web application:",
                                "Une politique de refus par défaut pour une petite application web :",
                                "سياسة منع افتراضي لتطبيق ويب صغير:",
                            ),
                            "# Policy, in plain terms:\n"
                            "#   DENY   all inbound traffic                       <- the default\n"
                            "#   ALLOW  tcp/443 from anywhere        -> web tier   (public site)\n"
                            "#   ALLOW  tcp/5432 from web tier only  -> db tier    (nothing else)\n"
                            "#   ALLOW  tcp/22   from admin VPN only -> all tiers  (never public)\n"
                            "#   DENY   outbound from db tier to the internet      <- stops a\n"
                            "#                                                        breached\n"
                            "#                                                        database\n"
                            "#                                                        phoning out\n\n"
                            "# Note the last rule: egress filtering is what turns a break-in\n"
                            "# into a contained incident instead of a data exfiltration.",
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "Why is \"deny everything, then allow what is needed\" better than the reverse?",
                                "Pourquoi « tout refuser, puis autoriser le nécessaire » vaut-il mieux que l'inverse ?",
                                "لماذا «امنع كلّ شيء ثمّ اسمح بما يلزم» أفضل من العكس؟",
                            ),
                            hint=T("Which policy fails safely when you forget something?", "Quelle politique échoue en sécurité si l'on oublie quelque chose ?", "أيّ سياسة تفشل بأمان إذا نسيت شيئًا؟"),
                            explanation=T(
                                "With default deny, anything you forget stays blocked. With default allow, anything you forget stays open — and you only learn which after an incident.",
                                "En refus par défaut, tout oubli reste bloqué. En autorisation par défaut, tout oubli reste ouvert — et on l'apprend après l'incident.",
                                "مع المنع الافتراضي يبقى كلّ ما نسيته ممنوعًا. ومع السماح الافتراضي يبقى كلّ ما نسيته مفتوحًا — ولا تعرف أيّها إلّا بعد الحادثة.",
                            ),
                            options=[
                                Option(T("It is faster to process", "C'est plus rapide à traiter", "معالجته أسرع")),
                                Option(
                                    T(
                                        "Anything you forget to consider stays blocked rather than open",
                                        "Tout oubli reste bloqué au lieu d'être ouvert",
                                        "كلّ ما تنسى النظر فيه يبقى ممنوعًا بدل أن يبقى مفتوحًا",
                                    ),
                                    correct=True,
                                ),
                                Option(T("It removes the need for encryption", "Cela supprime le besoin de chiffrement", "يلغي الحاجة إلى التشفير")),
                                Option(T("It requires fewer rules in total", "Cela demande moins de règles au total", "يتطلّب قواعد أقلّ إجمالًا")),
                            ],
                        ),
                        ShortAnswer(
                            prompt=T(
                                "A web server is compromised. Explain in one sentence how segmentation limits the damage.",
                                "Un serveur web est compromis. Expliquez en une phrase comment la segmentation limite les dégâts.",
                                "اختُرق خادم ويب. اشرح بجملة كيف تحدّ التجزئة من الضرر.",
                            ),
                            hint=T(
                                "Think about what the attacker can reach next.",
                                "Pensez à ce que l'attaquant peut atteindre ensuite.",
                                "فكّر فيما يستطيع المهاجم الوصول إليه بعد ذلك.",
                            ),
                            explanation=T(
                                "Segmentation confines the attacker to that zone: the compromised server can only reach the few services its segment permits, so lateral movement to databases and internal systems is blocked.",
                                "La segmentation confine l'attaquant à cette zone : le serveur compromis n'atteint que les services permis par son segment, ce qui bloque le mouvement latéral vers les bases et les systèmes internes.",
                                "التجزئة تحبس المهاجم في تلك المنطقة: فالخادم المخترق لا يصل إلّا إلى الخدمات القليلة التي يسمح بها جزؤه، فيُمنع التنقّل الجانبي إلى قواعد البيانات والأنظمة الداخلية.",
                            ),
                            keywords=[
                                ["reach", "access", "atteindre", "accès", "الوصول", "يصل"],
                                ["segment", "zone", "network", "segment", "réseau", "جزء", "منطقة", "الشبكة"],
                            ],
                            reference_answer="Because the compromised server can only reach the few services its own segment allows, so the attacker cannot move laterally to the database or internal systems.",
                        ),
                    ],
                ),
            ],
        ),
        Module(
            slug="securing-traffic",
            title=T("Securing Traffic", "Sécuriser le Trafic", "تأمين حركة البيانات"),
            description=T(
                "TLS, VPNs and the protocols that make an untrusted network usable.",
                "TLS, VPN et les protocoles qui rendent utilisable un réseau non fiable.",
                "‏TLS والشبكات الخاصّة الافتراضية والبروتوكولات التي تجعل شبكة غير موثوقة صالحة للاستعمال.",
            ),
            lessons=[
                Lesson(
                    slug="tls-in-practice",
                    minutes=35,
                    xp=65,
                    difficulty=D.intermediate,
                    title=T("TLS in Practice", "TLS en Pratique", "‏TLS عمليًا"),
                    story=T(
                        "TLS is not a checkbox. It is a chain of trust, and every link has failed somewhere in the real world.",
                        "TLS n'est pas une case à cocher. C'est une chaîne de confiance, et chaque maillon a déjà rompu dans le monde réel.",
                        "‏TLS ليس خانة تُعلَّم. إنّه سلسلة ثقة، وكلّ حلقة فيها انكسرت مرّة في الواقع.",
                    ),
                    objective=T(
                        "Explain what a certificate proves, why validation must not be disabled, and what HSTS adds.",
                        "Expliquer ce que prouve un certificat, pourquoi la validation ne doit pas être désactivée, et ce qu'apporte HSTS.",
                        "شرح ما تثبته الشهادة، ولماذا يجب عدم تعطيل التحقّق، وما الذي يضيفه HSTS.",
                    ),
                    skills=T(
                        "Certificates, certificate authorities, chain of trust, validation, HSTS, downgrade",
                        "Certificats, autorités de certification, chaîne de confiance, validation, HSTS, rétrogradation",
                        "الشهادات، سلطات إصدار الشهادات، سلسلة الثقة، التحقّق، HSTS، الخفض القسري",
                    ),
                    blocks=[
                        Text(
                            T(
                                "A **certificate** binds a domain name to a public key, signed by a **certificate authority** the client already trusts. Validation checks three things: the signature chains to a trusted root, the name matches the site you asked for, and the certificate has not expired or been revoked. All three matter — a valid certificate for the wrong domain proves nothing.",
                                "Un **certificat** lie un nom de domaine à une clé publique, signé par une **autorité de certification** déjà approuvée par le client. La validation vérifie trois choses : la signature remonte à une racine de confiance, le nom correspond au site demandé, et le certificat n'est ni expiré ni révoqué. Les trois comptent — un certificat valide pour un autre domaine ne prouve rien.",
                                "**الشهادة** تربط اسم نطاق بمفتاح عامّ، وتوقّعها **سلطة إصدار** يثق بها العميل مسبقًا. ويتحقّق التحقّق من ثلاثة أمور: أنّ التوقيع يصل إلى جذر موثوق، وأنّ الاسم يطابق الموقع المطلوب، وأنّ الشهادة لم تنتهِ ولم تُلغَ. والثلاثة مهمّة — فشهادة صالحة لنطاق آخر لا تثبت شيئًا.",
                            )
                        ),
                        Code(
                            T(
                                "The single most damaging line in security-related code:",
                                "La ligne la plus destructrice du code lié à la sécurité :",
                                "أكثر سطر ضررًا في الكود المتعلّق بالأمن:",
                            ),
                            "# Do not do this. Ever. In any language.\n"
                            "response = requests.get(url, verify=False)\n\n"
                            "# It disables certificate validation, so ANY server that can\n"
                            "# intercept the connection is accepted. The traffic is still\n"
                            "# encrypted -- to the attacker. You have kept the padlock icon\n"
                            "# and thrown away everything it was protecting.\n\n"
                            "# If a certificate fails to validate, the fix is to install the\n"
                            "# correct CA bundle or renew the certificate -- never to stop\n"
                            "# checking.",
                        ),
                        Text(
                            T(
                                "Two hardening steps close the remaining gaps. **HSTS** tells the browser to use HTTPS for this domain for months to come, so the first plain-HTTP request — the one an attacker would redirect — never happens again. And **redirect HTTP to HTTPS** on the server, so a mistyped link cannot silently downgrade.",
                                "Deux renforcements comblent les derniers écarts. **HSTS** indique au navigateur d'utiliser HTTPS pour ce domaine pendant des mois, de sorte que la première requête en clair — celle qu'un attaquant redirigerait — ne se reproduise plus. Et **redirigez HTTP vers HTTPS** côté serveur, pour qu'un lien mal saisi ne rétrograde pas silencieusement.",
                                "خطوتان تسدّان ما تبقّى من ثغرات. **HSTS** يخبر المتصفّح باستخدام HTTPS لهذا النطاق لأشهر مقبلة، فلا يتكرّر أوّل طلب بلا تشفير — وهو الطلب الذي قد يوجّهه مهاجم. و**أعِد توجيه HTTP إلى HTTPS** على الخادم، كي لا يؤدّي رابط مكتوب خطأً إلى خفض صامت.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "A developer adds `verify=False` to make a TLS error go away. What is the consequence?",
                                "Un développeur ajoute `verify=False` pour faire disparaître une erreur TLS. Quelle en est la conséquence ?",
                                "أضاف مطوّر `verify=False` ليختفي خطأ TLS. ما النتيجة؟",
                            ),
                            hint=T("What was the certificate check actually for?", "À quoi servait la vérification du certificat ?", "ما الغرض الحقيقي من فحص الشهادة؟"),
                            explanation=T(
                                "The connection is still encrypted, but any intercepting server is now accepted as the real one, so encryption protects the attacker's channel instead of yours.",
                                "La connexion reste chiffrée, mais tout serveur interceptant est désormais accepté comme légitime : le chiffrement protège le canal de l'attaquant.",
                                "يبقى الاتّصال مشفّرًا، لكنّ أيّ خادم معترض صار مقبولًا على أنّه الحقيقي، فيحمي التشفير قناة المهاجم بدل قناتك.",
                            ),
                            options=[
                                Option(T("Nothing; the traffic is still encrypted and safe", "Rien ; le trafic reste chiffré et sûr", "لا شيء؛ فالحركة تبقى مشفّرة وآمنة")),
                                Option(
                                    T(
                                        "Any intercepting server is trusted, so interception becomes undetectable",
                                        "Tout serveur interceptant est approuvé : l'interception devient indétectable",
                                        "يصبح أيّ خادم معترض موثوقًا، فلا يمكن كشف الاعتراض",
                                    ),
                                    correct=True,
                                ),
                                Option(T("The traffic is sent in plain text", "Le trafic est envoyé en clair", "تُرسَل الحركة بلا تشفير")),
                                Option(T("Only the server is affected, not the client", "Seul le serveur est affecté", "يتأثّر الخادم وحده دون العميل")),
                            ],
                        ),
                        Ordering(
                            prompt=T(
                                "Put the TLS handshake steps in order.",
                                "Remettez les étapes de la poignée de main TLS dans l'ordre.",
                                "رتّب خطوات مصافحة TLS.",
                            ),
                            hint=T("The certificate must be checked before any secret is agreed.", "Le certificat doit être vérifié avant tout accord sur un secret.", "يجب فحص الشهادة قبل الاتّفاق على أيّ سرّ."),
                            explanation=T(
                                "The client greets, the server presents its certificate, the client validates it, both derive a session key, and only then does encrypted data flow.",
                                "Le client salue, le serveur présente son certificat, le client le valide, les deux dérivent une clé de session, et seulement ensuite les données chiffrées circulent.",
                                "يبدأ العميل بالتحيّة، ثمّ يقدّم الخادم شهادته، ثمّ يتحقّق منها العميل، ثمّ يشتقّ الطرفان مفتاح جلسة، وعندها فقط تنتقل البيانات المشفّرة.",
                            ),
                            steps=[
                                T("The client opens the connection and offers its supported ciphers", "Le client ouvre la connexion et propose ses algorithmes", "يفتح العميل الاتّصال ويعرض الخوارزميات المدعومة"),
                                T("The server presents its certificate", "Le serveur présente son certificat", "يقدّم الخادم شهادته"),
                                T("The client validates the certificate chain and hostname", "Le client valide la chaîne et le nom d'hôte", "يتحقّق العميل من سلسلة الشهادة واسم المضيف"),
                                T("Both sides derive a shared session key", "Les deux dérivent une clé de session partagée", "يشتقّ الطرفان مفتاح جلسة مشتركًا"),
                                T("Application data flows encrypted", "Les données applicatives circulent chiffrées", "تنتقل بيانات التطبيق مشفّرة"),
                            ],
                        ),
                    ],
                ),
                Lesson(
                    slug="monitoring-and-incident-response",
                    minutes=35,
                    xp=65,
                    difficulty=D.advanced,
                    title=T("Monitoring and Incident Response", "Supervision et Réponse à Incident", "المراقبة والاستجابة للحوادث"),
                    story=T(
                        "The question is not whether you will be breached. It is how long it takes you to notice.",
                        "La question n'est pas de savoir si vous serez compromis, mais en combien de temps vous le remarquerez.",
                        "السؤال ليس هل ستُخترق، بل كم تستغرق حتى تلاحظ.",
                    ),
                    objective=T(
                        "Say what must be logged, what makes an alert actionable, and follow the phases of incident response.",
                        "Dire ce qui doit être journalisé, ce qui rend une alerte actionnable, et suivre les phases de la réponse à incident.",
                        "تحديد ما يجب تسجيله، وما الذي يجعل التنبيه قابلًا للتصرّف، واتّباع مراحل الاستجابة للحوادث.",
                    ),
                    skills=T(
                        "Logging, IDS, alert fatigue, detection, containment, eradication, recovery, post-mortem",
                        "Journalisation, IDS, fatigue d'alerte, détection, confinement, éradication, récupération, post-mortem",
                        "التسجيل، أنظمة كشف التسلّل، إرهاق التنبيهات، الكشف، الاحتواء، الاستئصال، التعافي، المراجعة اللاحقة",
                    ),
                    blocks=[
                        Text(
                            T(
                                "Log the events that answer \"who did what, when, from where\": authentication attempts and their outcome, permission failures, administrative actions, configuration changes. And log them **without secrets** — passwords, tokens and full card numbers must never reach a log file, because logs are copied, shipped and read far more widely than the database ever is.",
                                "Journalisez ce qui répond à « qui a fait quoi, quand, depuis où » : tentatives d'authentification et leur issue, refus de permission, actions d'administration, changements de configuration. Et journalisez **sans secrets** — mots de passe, jetons et numéros de carte ne doivent jamais atteindre un fichier de log, car les logs sont copiés, transférés et lus bien plus largement que la base.",
                                "سجّل الأحداث التي تجيب عن «من فعل ماذا ومتى ومن أين»: محاولات التوثيق ونتائجها، وحالات رفض الصلاحية، والإجراءات الإدارية، وتغييرات الإعداد. وسجّلها **بلا أسرار** — فكلمات المرور والرموز وأرقام البطاقات الكاملة يجب ألّا تصل إلى ملفّ سجلّ أبدًا، لأنّ السجلّات تُنسَخ وتُنقَل وتُقرأ على نطاق أوسع بكثير من قاعدة البيانات.",
                            )
                        ),
                        Text(
                            T(
                                "An alert nobody acts on is worse than no alert, because it trains the team to ignore the console — **alert fatigue** is a documented cause of missed breaches. Tune for a small number of high-signal alerts: impossible-travel logins, a spike in permission denials, an outbound connection from a database server.",
                                "Une alerte que personne ne traite est pire que pas d'alerte : elle apprend à ignorer la console — la **fatigue d'alerte** est une cause documentée de compromissions manquées. Réglez sur un petit nombre d'alertes à fort signal : connexions géographiquement impossibles, pic de refus de permission, connexion sortante depuis un serveur de base de données.",
                                "التنبيه الذي لا يتصرّف أحد بناءً عليه أسوأ من غيابه، لأنّه يدرّب الفريق على تجاهل الشاشة — و**إرهاق التنبيهات** سبب موثَّق لاختراقات فائتة. اضبط عددًا صغيرًا من التنبيهات عالية الدلالة: تسجيل دخول من موقعين متعذّرين زمنيًا، وارتفاع مفاجئ في حالات رفض الصلاحية، واتّصال صادر من خادم قاعدة بيانات.",
                            )
                        ),
                        Code(
                            T(
                                "The phases, in the order they are actually performed:",
                                "Les phases, dans l'ordre où elles sont réellement exécutées :",
                                "المراحل بالترتيب الذي تُنفَّذ به فعلًا:",
                            ),
                            "# 1. PREPARE     runbooks, contacts, tested backups, log retention\n"
                            "# 2. DETECT      an alert or a report says something is wrong\n"
                            "# 3. CONTAIN     isolate the host, revoke the tokens, block the\n"
                            "#                account -- stop the bleeding before investigating\n"
                            "# 4. ERADICATE   remove the foothold, close the vulnerability\n"
                            "# 5. RECOVER     restore from known-good backups, watch closely\n"
                            "# 6. LEARN       blameless post-mortem: what let this happen, and\n"
                            "#                what change makes the whole class impossible\n\n"
                            "# Containment comes BEFORE eradication: an attacker who is still\n"
                            "# connected while you clean up simply re-enters behind you.",
                        ),
                    ],
                    exercises=[
                        Ordering(
                            prompt=T(
                                "Put the incident response phases in order.",
                                "Remettez les phases de réponse à incident dans l'ordre.",
                                "رتّب مراحل الاستجابة للحوادث.",
                            ),
                            hint=T("Stop the bleeding before cleaning the wound.", "Arrêtez l'hémorragie avant de nettoyer la plaie.", "أوقف النزيف قبل تنظيف الجرح."),
                            explanation=T(
                                "Prepare, detect, contain, eradicate, recover, then learn — containment precedes eradication so the attacker cannot return mid-cleanup.",
                                "Préparer, détecter, confiner, éradiquer, récupérer, apprendre — le confinement précède l'éradication pour que l'attaquant ne revienne pas en plein nettoyage.",
                                "التحضير ثمّ الكشف ثمّ الاحتواء ثمّ الاستئصال ثمّ التعافي ثمّ التعلّم — والاحتواء قبل الاستئصال كي لا يعود المهاجم أثناء التنظيف.",
                            ),
                            steps=[
                                T("Prepare: runbooks, contacts and tested backups", "Préparer : runbooks, contacts et sauvegardes testées", "التحضير: أدلّة إجراءات وجهات اتّصال ونسخ احتياطية مختبَرة"),
                                T("Detect the incident", "Détecter l'incident", "كشف الحادثة"),
                                T("Contain it: isolate hosts and revoke access", "Confiner : isoler les hôtes et révoquer les accès", "الاحتواء: عزل الأجهزة وسحب الصلاحيات"),
                                T("Eradicate the cause", "Éradiquer la cause", "استئصال السبب"),
                                T("Recover from known-good backups", "Récupérer depuis des sauvegardes saines", "التعافي من نسخ احتياطية سليمة"),
                                T("Run a blameless post-mortem", "Faire un post-mortem sans reproche", "إجراء مراجعة لاحقة بلا لوم"),
                            ],
                        ),
                        MCQ(
                            prompt=T(
                                "Which of these must never appear in an application log?",
                                "Lequel ne doit jamais apparaître dans un log applicatif ?",
                                "أيّ ممّا يلي يجب ألّا يظهر في سجلّ التطبيق أبدًا؟",
                            ),
                            hint=T("Logs are copied and read far more widely than the database.", "Les logs sont copiés et lus bien plus largement que la base.", "السجلّات تُنسَخ وتُقرأ على نطاق أوسع بكثير من قاعدة البيانات."),
                            explanation=T(
                                "Session tokens are credentials: anyone who reads the log could impersonate the user, so they are redacted before logging.",
                                "Les jetons de session sont des identifiants : quiconque lit le log pourrait usurper l'utilisateur ; ils sont donc masqués.",
                                "رموز الجلسة بيانات اعتماد: فمن يقرأ السجلّ يستطيع انتحال المستخدم، لذا تُحجَب قبل التسجيل.",
                            ),
                            options=[
                                Option(T("The time of the request", "L'heure de la requête", "وقت الطلب")),
                                Option(T("The user's session token", "Le jeton de session de l'utilisateur", "رمز جلسة المستخدم"), correct=True),
                                Option(T("The HTTP status code returned", "Le code de statut HTTP renvoyé", "رمز حالة HTTP المُرجَع")),
                                Option(T("The source IP address", "L'adresse IP source", "عنوان IP المصدر")),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)


SECURE_DEVELOPMENT = CourseSpec(
    slug="secure-software-development",
    stage=6,
    track="security",
    icon="🧰",
    difficulty=D.advanced,
    estimated_hours=10,
    prerequisite_slug="cybersecurity-foundations",
    title=T("Secure Software Development", "Développement Logiciel Sécurisé", "تطوير البرمجيات الآمن"),
    description=T(
        "Writing code that does not become the vulnerability: input handling, injection, the browser's security model, secrets and dependencies.",
        "Écrire du code qui ne devient pas la vulnérabilité : traitement des entrées, injections, modèle de sécurité du navigateur, secrets et dépendances.",
        "كتابة كود لا يصير هو الثغرة: معالجة المدخلات، والحقن، ونموذج أمان المتصفّح، والأسرار، والتبعيّات.",
    ),
    skills=T(
        "Input validation, SQL injection, XSS, CSRF, secrets management, dependency security",
        "Validation des entrées, injection SQL, XSS, CSRF, gestion des secrets, sécurité des dépendances",
        "التحقّق من المدخلات، حقن SQL، XSS، CSRF، إدارة الأسرار، أمن التبعيّات",
    ),
    modules=[
        Module(
            slug="input-and-injection",
            title=T("Input and Injection", "Entrées et Injections", "المدخلات والحقن"),
            description=T(
                "Why mixing data with instructions is the root of a whole family of vulnerabilities.",
                "Pourquoi mélanger données et instructions est à la racine de toute une famille de vulnérabilités.",
                "لماذا خلط البيانات بالتعليمات أصل عائلة كاملة من الثغرات.",
            ),
            lessons=[
                Lesson(
                    slug="validating-input",
                    minutes=35,
                    xp=60,
                    difficulty=D.intermediate,
                    title=T("Trust Boundaries and Input Validation", "Frontières de Confiance et Validation des Entrées", "حدود الثقة والتحقّق من المدخلات"),
                    story=T(
                        "Every field a user can type into is a place someone else can type into too.",
                        "Chaque champ où un utilisateur peut écrire est un endroit où quelqu'un d'autre peut écrire aussi.",
                        "كلّ حقل يستطيع مستخدم الكتابة فيه هو مكان يستطيع غيره الكتابة فيه أيضًا.",
                    ),
                    objective=T(
                        "Identify trust boundaries and validate input by allowlist on the server.",
                        "Identifier les frontières de confiance et valider les entrées par liste blanche côté serveur.",
                        "تحديد حدود الثقة والتحقّق من المدخلات بقائمة سماح على الخادم.",
                    ),
                    skills=T(
                        "Trust boundaries, allowlist validation, canonicalisation, server-side checks",
                        "Frontières de confiance, validation par liste blanche, canonicalisation, contrôles côté serveur",
                        "حدود الثقة، التحقّق بقائمة السماح، التوحيد القياسي، الفحوص على الخادم",
                    ),
                    blocks=[
                        Text(
                            T(
                                "A **trust boundary** is any point where data arrives from somewhere you do not control: a form, a URL, an upload, a header, another service's response. Everything crossing one must be validated **on the server**, because everything before that point runs on a machine the user owns.",
                                "Une **frontière de confiance** est tout point où des données arrivent d'un endroit que vous ne contrôlez pas : formulaire, URL, téléversement, en-tête, réponse d'un autre service. Tout ce qui la franchit doit être validé **côté serveur**, car tout ce qui précède s'exécute sur une machine appartenant à l'utilisateur.",
                                "**حدّ الثقة** أيّ نقطة تصل عندها بيانات من مكان لا تتحكّم به: نموذج أو رابط أو ملفّ مرفوع أو ترويسة أو استجابة خدمة أخرى. وكلّ ما يعبر هذا الحدّ يجب التحقّق منه **على الخادم**، لأنّ كلّ ما قبله يعمل على جهاز يملكه المستخدم.",
                            )
                        ),
                        Text(
                            T(
                                "Validate by **allowlist**, not blocklist: state what is acceptable and reject everything else. A blocklist is a list of the bad inputs you thought of, and attackers specialise in the ones you did not. Check type, length, range, format and set membership — and do it before the value is used for anything.",
                                "Validez par **liste blanche**, pas par liste noire : énoncez ce qui est acceptable et rejetez le reste. Une liste noire est la liste des mauvaises entrées auxquelles vous avez pensé, et les attaquants se spécialisent dans les autres. Vérifiez type, longueur, plage, format et appartenance — avant toute utilisation de la valeur.",
                                "تحقّق بـ**قائمة سماح** لا بقائمة منع: حدّد المقبول وارفض ما عداه. فقائمة المنع هي قائمة المدخلات السيّئة التي فكّرت فيها، والمهاجمون يتخصّصون في التي لم تفكّر فيها. افحص النوع والطول والمدى والصيغة والانتماء — وافعل ذلك قبل استخدام القيمة في أيّ شيء.",
                            )
                        ),
                        Code(
                            T(
                                "AtlasCode's own request models are allowlist validation — the schema is the rule:",
                                "Les modèles de requête d'AtlasCode sont une validation par liste blanche — le schéma est la règle :",
                                "نماذج الطلبات في AtlasCode نفسها تحقّق بقائمة سماح — فالمخطّط هو القاعدة:",
                            ),
                            "from pydantic import BaseModel, EmailStr, Field\n\n"
                            "class UserCreate(BaseModel):\n"
                            "    email: EmailStr                                  # format\n"
                            "    username: str = Field(min_length=3, max_length=100)  # length\n"
                            "    password: str = Field(min_length=8, max_length=100)\n"
                            "    preferred_language: LanguageEnum                 # membership\n\n"
                            "# Anything not matching is rejected with 422 before a single line\n"
                            "# of business logic runs. Note the maximum lengths: without them,\n"
                            "# a 10 MB username is a denial-of-service vector, not a typo.",
                        ),
                        ExamTip(
                            T(
                                "Client-side validation is a courtesy to honest users — it makes forms pleasant. It is not a security control, because anyone can send a request without ever loading your page.",
                                "La validation côté client est une courtoisie envers les utilisateurs honnêtes — elle rend les formulaires agréables. Ce n'est pas un contrôle de sécurité : n'importe qui peut envoyer une requête sans charger votre page.",
                                "التحقّق في المتصفّح مجاملة للمستخدمين النزهاء تجعل النماذج مريحة، لكنّه ليس ضابطًا أمنيًا، لأنّ بإمكان أيّ أحد إرسال طلب دون تحميل صفحتك أصلًا.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "Why is allowlist validation preferred over blocklist validation?",
                                "Pourquoi préférer la validation par liste blanche à la liste noire ?",
                                "لماذا يُفضَّل التحقّق بقائمة السماح على قائمة المنع؟",
                            ),
                            hint=T("Which list can be complete?", "Quelle liste peut être complète ?", "أيّ قائمة يمكن أن تكون كاملة؟"),
                            explanation=T(
                                "You can enumerate what is valid; you cannot enumerate everything invalid, so a blocklist is always incomplete.",
                                "On peut énumérer ce qui est valide ; on ne peut pas énumérer tout ce qui ne l'est pas : une liste noire est toujours incomplète.",
                                "يمكنك تعداد ما هو صالح، ولا يمكنك تعداد كلّ ما هو غير صالح، فتبقى قائمة المنع ناقصة دائمًا.",
                            ),
                            options=[
                                Option(T("Allowlists are shorter to write", "Les listes blanches sont plus courtes", "قوائم السماح أقصر كتابةً")),
                                Option(
                                    T(
                                        "Valid input can be enumerated; invalid input cannot",
                                        "L'entrée valide est énumérable ; l'invalide non",
                                        "المدخلات الصالحة قابلة للتعداد، وغير الصالحة لا",
                                    ),
                                    correct=True,
                                ),
                                Option(T("Blocklists are slower to evaluate", "Les listes noires sont plus lentes", "قوائم المنع أبطأ تقييمًا")),
                                Option(T("Allowlists remove the need for encryption", "Les listes blanches suppriment le besoin de chiffrement", "قوائم السماح تلغي الحاجة إلى التشفير")),
                            ],
                        ),
                        MCQ(
                            prompt=T(
                                "Your React form already checks the email format. What must the server do?",
                                "Votre formulaire React vérifie déjà le format de l'e-mail. Que doit faire le serveur ?",
                                "نموذج React لديك يفحص صيغة البريد أصلًا. فماذا يجب أن يفعل الخادم؟",
                            ),
                            hint=T("Can a request reach the server without the form?", "Une requête peut-elle atteindre le serveur sans le formulaire ?", "هل يمكن أن يصل طلب إلى الخادم دون المرور بالنموذج؟"),
                            explanation=T(
                                "Requests can be sent directly with any tool, so the server must repeat every check regardless of what the client did.",
                                "Les requêtes peuvent être envoyées directement avec n'importe quel outil : le serveur doit refaire chaque contrôle.",
                                "يمكن إرسال الطلبات مباشرة بأيّ أداة، لذا على الخادم إعادة كلّ فحص مهما فعل العميل.",
                            ),
                            options=[
                                Option(T("Trust the client and skip the check", "Faire confiance au client et sauter le contrôle", "يثق بالعميل ويتخطّى الفحص")),
                                Option(T("Validate the email again, server-side", "Valider l'e-mail à nouveau, côté serveur", "يتحقّق من البريد مجدّدًا على الخادم"), correct=True),
                                Option(T("Only validate if the request has no session", "Valider seulement sans session", "يتحقّق فقط إن لم تكن هناك جلسة")),
                                Option(T("Validate in the database only", "Valider uniquement en base de données", "يتحقّق في قاعدة البيانات فقط")),
                            ],
                        ),
                    ],
                ),
                Lesson(
                    slug="injection-and-web-vulnerabilities",
                    minutes=40,
                    xp=70,
                    difficulty=D.advanced,
                    title=T("Injection and Common Web Vulnerabilities", "Injections et Vulnérabilités Web Courantes", "الحقن والثغرات الشائعة في الويب"),
                    story=T(
                        "SQL injection, XSS and command injection are one mistake wearing three costumes: data got treated as instructions.",
                        "Injection SQL, XSS et injection de commandes sont une seule erreur en trois costumes : des données traitées comme des instructions.",
                        "حقن SQL وXSS وحقن الأوامر خطأ واحد بثلاثة أثواب: بيانات عومِلت كتعليمات.",
                    ),
                    objective=T(
                        "Explain the shared cause of injection flaws and apply the standard defence for each.",
                        "Expliquer la cause commune des failles d'injection et appliquer la défense standard pour chacune.",
                        "شرح السبب المشترك لثغرات الحقن وتطبيق الدفاع المعياري لكلّ منها.",
                    ),
                    skills=T(
                        "SQL injection, parameterised queries, XSS, output encoding, CSRF tokens, ORM safety",
                        "Injection SQL, requêtes paramétrées, XSS, encodage de sortie, jetons CSRF, sécurité ORM",
                        "حقن SQL، الاستعلامات ذات المعاملات، XSS، ترميز المخرجات، رموز CSRF، أمان ORM",
                    ),
                    blocks=[
                        Text(
                            T(
                                "Every injection flaw has the same shape: a value from the user is pasted into something that gets **interpreted** — a SQL statement, an HTML page, a shell command — and the interpreter cannot tell the difference between the data you meant and the instructions the attacker sent.",
                                "Toute faille d'injection a la même forme : une valeur de l'utilisateur est collée dans quelque chose qui sera **interprété** — requête SQL, page HTML, commande shell — et l'interpréteur ne distingue pas les données voulues des instructions envoyées par l'attaquant.",
                                "لكلّ ثغرة حقن الشكل نفسه: قيمة من المستخدم تُلصَق داخل شيء سيُفسَّر — عبارة SQL أو صفحة HTML أو أمر صدفة — ولا يستطيع المفسّر التمييز بين البيانات التي قصدتها والتعليمات التي أرسلها المهاجم.",
                            )
                        ),
                        Code(
                            T(
                                "The fix is always the same idea: keep data and code in separate channels.",
                                "Le correctif est toujours la même idée : séparer les canaux des données et du code.",
                                "الحلّ هو الفكرة نفسها دائمًا: افصل قناة البيانات عن قناة الكود.",
                            ),
                            "# VULNERABLE - the value becomes part of the statement\n"
                            "query = f\"SELECT * FROM users WHERE email = '{email}'\"\n\n"
                            "# SAFE - the value travels beside the statement, never inside it.\n"
                            "# The database parses the query first, then binds the parameter,\n"
                            "# so the value can never change what the query means.\n"
                            "await db.execute(\n"
                            "    text('SELECT * FROM users WHERE email = :email'),\n"
                            "    {'email': email},\n"
                            ")\n\n"
                            "# Safer still: an ORM parameterises for you.\n"
                            "await db.execute(select(User).where(User.email == email))",
                        ),
                        Text(
                            T(
                                "**XSS** is the same bug in HTML: user text is rendered as markup and the browser runs it as script. The defence is **contextual output encoding** — React does this by default, which is why `{userText}` is safe and `dangerouslySetInnerHTML` is named the way it is. **CSRF** is different: the browser helpfully attaches the victim's cookies to a request another site triggered, so the defence is an unguessable token the other site cannot read, plus `SameSite` cookies.",
                                "**XSS** est le même bug en HTML : du texte utilisateur est rendu comme balisage et le navigateur l'exécute. La défense est l'**encodage de sortie contextuel** — React le fait par défaut, d'où la sûreté de `{userText}` et le nom de `dangerouslySetInnerHTML`. **CSRF** est différent : le navigateur attache obligeamment les cookies de la victime à une requête déclenchée par un autre site ; la défense est un jeton imprévisible que l'autre site ne peut pas lire, plus des cookies `SameSite`.",
                                "**XSS** هو الخلل نفسه في HTML: نصّ المستخدم يُعرَض كوسوم فينفّذه المتصفّح كسكربت. والدفاع هو **ترميز المخرجات حسب السياق** — وReact يفعل ذلك افتراضيًا، ولهذا فإنّ `{userText}` آمن وسُمّي `dangerouslySetInnerHTML` بهذا الاسم. أمّا **CSRF** فمختلف: إذ يُرفق المتصفّح متعاونًا كعكات الضحيّة بطلب أطلقه موقع آخر، فيكون الدفاع رمزًا غير قابل للتخمين لا يستطيع الموقع الآخر قراءته، مع كعكات `SameSite`.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "What actually prevents SQL injection?",
                                "Qu'est-ce qui empêche réellement l'injection SQL ?",
                                "ما الذي يمنع حقن SQL فعلًا؟",
                            ),
                            hint=T("Think about when the database decides what the query means.", "Pensez au moment où la base décide du sens de la requête.", "فكّر في اللحظة التي تقرّر فيها قاعدة البيانات معنى الاستعلام."),
                            explanation=T(
                                "Parameterised queries let the database parse the statement before the value is bound, so the value cannot alter the statement's structure.",
                                "Les requêtes paramétrées font analyser l'instruction avant la liaison de la valeur : celle-ci ne peut plus modifier la structure.",
                                "الاستعلامات ذات المعاملات تجعل قاعدة البيانات تحلّل العبارة قبل ربط القيمة، فلا تستطيع القيمة تغيير بنية العبارة.",
                            ),
                            options=[
                                Option(T("Removing apostrophes from the input", "Supprimer les apostrophes de l'entrée", "حذف علامات الاقتباس من المدخل")),
                                Option(T("Using parameterised queries", "Utiliser des requêtes paramétrées", "استخدام استعلامات ذات معاملات"), correct=True),
                                Option(T("Hiding SQL errors from the user", "Masquer les erreurs SQL à l'utilisateur", "إخفاء أخطاء SQL عن المستخدم")),
                                Option(T("Renaming the database tables", "Renommer les tables", "تغيير أسماء جداول قاعدة البيانات")),
                            ],
                        ),
                        MCQ(
                            prompt=T(
                                "A comment field renders whatever users type directly as HTML. Which vulnerability is that?",
                                "Un champ de commentaire affiche tel quel le texte des utilisateurs en HTML. Quelle vulnérabilité est-ce ?",
                                "حقل تعليقات يعرض ما يكتبه المستخدمون مباشرةً كـ HTML. أيّ ثغرة هذه؟",
                            ),
                            hint=T("The browser will execute what it is given.", "Le navigateur exécutera ce qu'on lui donne.", "المتصفّح سينفّذ ما يُعطى له."),
                            explanation=T(
                                "That is cross-site scripting: user content is interpreted as markup and script rather than displayed as text.",
                                "C'est du cross-site scripting : le contenu utilisateur est interprété comme balisage et script au lieu d'être affiché comme texte.",
                                "هذه ثغرة البرمجة عبر المواقع (XSS): إذ يُفسَّر محتوى المستخدم كوسوم وسكربت بدل عرضه كنصّ.",
                            ),
                            options=[
                                Option(T("SQL injection", "Injection SQL", "حقن SQL")),
                                Option(T("Cross-site scripting (XSS)", "Cross-site scripting (XSS)", "البرمجة عبر المواقع (XSS)"), correct=True),
                                Option(T("CSRF", "CSRF", "CSRF")),
                                Option(T("A denial-of-service flaw", "Une faille de déni de service", "ثغرة حجب خدمة")),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        Module(
            slug="secrets-and-dependencies",
            title=T("Secrets and Dependencies", "Secrets et Dépendances", "الأسرار والتبعيّات"),
            description=T(
                "The two places most real breaches actually start.",
                "Les deux endroits où commencent la plupart des vraies compromissions.",
                "الموضعان اللذان تبدأ منهما معظم الاختراقات الحقيقية.",
            ),
            lessons=[
                Lesson(
                    slug="managing-secrets",
                    minutes=30,
                    xp=60,
                    difficulty=D.intermediate,
                    title=T("Managing Secrets", "Gérer les Secrets", "إدارة الأسرار"),
                    story=T(
                        "A key committed to Git is public the moment it is pushed, and deleting the file does not take it back.",
                        "Une clé committée dans Git est publique dès le push, et supprimer le fichier ne la reprend pas.",
                        "المفتاح المُثبَّت في Git يصير عامًّا لحظة دفعه، وحذف الملفّ لا يستعيده.",
                    ),
                    objective=T(
                        "Keep credentials out of source control and rotate them correctly when exposed.",
                        "Garder les identifiants hors du contrôle de version et les faire tourner correctement en cas d'exposition.",
                        "إبقاء بيانات الاعتماد خارج نظام إدارة الإصدارات وتدويرها بشكل صحيح عند انكشافها.",
                    ),
                    skills=T(
                        "Environment variables, secret managers, .gitignore, key rotation, least privilege",
                        "Variables d'environnement, gestionnaires de secrets, .gitignore, rotation des clés, moindre privilège",
                        "متغيّرات البيئة، مديرو الأسرار، ‎.gitignore‎، تدوير المفاتيح، أقلّ صلاحية",
                    ),
                    blocks=[
                        Text(
                            T(
                                "Configuration that differs between environments — database URLs, API keys, signing secrets — belongs in **environment variables** or a secret manager, never in the repository. The code reads the name; the value is supplied by the platform. AtlasCode's `Settings` class does exactly this, and refuses to start in production with the default signing key still in place.",
                                "La configuration qui varie selon l'environnement — URLs de base, clés d'API, secrets de signature — appartient aux **variables d'environnement** ou à un gestionnaire de secrets, jamais au dépôt. Le code lit le nom ; la valeur vient de la plateforme. La classe `Settings` d'AtlasCode fait exactement cela et refuse de démarrer en production avec la clé de signature par défaut.",
                                "الإعدادات التي تختلف بين البيئات — روابط قواعد البيانات ومفاتيح الواجهات وأسرار التوقيع — مكانها **متغيّرات البيئة** أو مدير أسرار، لا المستودع أبدًا. الكود يقرأ الاسم، والمنصّة تزوّده بالقيمة. وصنف `Settings` في AtlasCode يفعل ذلك بالضبط ويرفض الإقلاع في الإنتاج إن بقي مفتاح التوقيع الافتراضي.",
                            )
                        ),
                        Code(
                            T(
                                "Reading configuration by name, with a guard that fails loudly:",
                                "Lire la configuration par nom, avec un garde qui échoue bruyamment :",
                                "قراءة الإعدادات بالاسم مع حارس يفشل بصوت عالٍ:",
                            ),
                            "class Settings(BaseSettings):\n"
                            "    database_url: str = 'sqlite+aiosqlite:///./atlascode.db'\n"
                            "    secret_key: str = INSECURE_DEFAULT_SECRET_KEY\n\n"
                            "    class Config:\n"
                            "        env_file = '.env'      # local only; .env is git-ignored\n\n"
                            "def get_settings() -> Settings:\n"
                            "    settings = Settings()\n"
                            "    if not settings.debug and settings.is_using_insecure_default_secret:\n"
                            "        raise RuntimeError('Set a real SECRET_KEY before running with DEBUG=false')\n"
                            "    return settings",
                        ),
                        Text(
                            T(
                                "If a secret does reach a repository, **rotate it**. Rewriting history does not help: the value was cloned, cached, mirrored and possibly scraped within seconds. Issue a new credential, revoke the old one, then clean the history for tidiness — in that order.",
                                "Si un secret atteint un dépôt, **faites-le tourner**. Réécrire l'historique ne suffit pas : la valeur a été clonée, mise en cache, mirroir et sans doute moissonnée en quelques secondes. Émettez un nouvel identifiant, révoquez l'ancien, puis nettoyez l'historique par propreté — dans cet ordre.",
                                "إذا وصل سرّ إلى مستودع فـ**دوّره**. إعادة كتابة التاريخ لا تنفع: فالقيمة استُنسخت وخُزّنت ونُسخت وربّما حُصدت خلال ثوانٍ. أصدِر بيانات اعتماد جديدة، ثمّ ألغِ القديمة، ثمّ نظّف التاريخ للترتيب — بهذا الترتيب.",
                            )
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "An API key was pushed to a public repository an hour ago. What is the first thing to do?",
                                "Une clé d'API a été poussée sur un dépôt public il y a une heure. Que faire en premier ?",
                                "دُفع مفتاح واجهة برمجية إلى مستودع عامّ قبل ساعة. ما أوّل ما تفعله؟",
                            ),
                            hint=T("Can you take back something that was already downloaded?", "Peut-on reprendre ce qui a déjà été téléchargé ?", "هل يمكنك استرجاع شيء جرى تنزيله بالفعل؟"),
                            explanation=T(
                                "Assume it is compromised and rotate: issue a new key and revoke the old one. Cleaning history afterwards is housekeeping, not remediation.",
                                "Considérez-la compromise et faites-la tourner : nouvelle clé, révocation de l'ancienne. Nettoyer l'historique ensuite relève du rangement, pas de la remédiation.",
                                "اعتبره مكشوفًا ودوّره: أصدِر مفتاحًا جديدًا وألغِ القديم. أمّا تنظيف التاريخ لاحقًا فترتيب لا معالجة.",
                            ),
                            options=[
                                Option(T("Delete the file in a new commit", "Supprimer le fichier dans un nouveau commit", "احذف الملفّ في تثبيت جديد")),
                                Option(T("Revoke the key and issue a new one", "Révoquer la clé et en émettre une nouvelle", "ألغِ المفتاح وأصدِر آخر"), correct=True),
                                Option(T("Make the repository private", "Rendre le dépôt privé", "اجعل المستودع خاصًّا")),
                                Option(T("Add the file to .gitignore", "Ajouter le fichier à .gitignore", "أضف الملفّ إلى ‎.gitignore‎")),
                            ],
                        ),
                        ShortAnswer(
                            prompt=T(
                                "Why is rewriting Git history not enough after leaking a secret? One sentence.",
                                "Pourquoi réécrire l'historique Git ne suffit-il pas après une fuite de secret ? Une phrase.",
                                "لماذا لا تكفي إعادة كتابة تاريخ Git بعد تسريب سرّ؟ جملة واحدة.",
                            ),
                            hint=T(
                                "Think about who already has a copy.",
                                "Pensez à qui en a déjà une copie.",
                                "فكّر فيمن يملك نسخة بالفعل.",
                            ),
                            explanation=T(
                                "Anyone who cloned, forked, mirrored or scraped the repository already holds the value, so only revoking and reissuing the credential removes the access.",
                                "Quiconque a cloné, forké, mis en miroir ou moissonné le dépôt détient déjà la valeur : seule la révocation et la réémission suppriment l'accès.",
                                "كلّ من استنسخ المستودع أو نسخه أو حصده يملك القيمة أصلًا، فلا يزيل الوصولَ إلّا إلغاء بيانات الاعتماد وإعادة إصدارها.",
                            ),
                            keywords=[
                                ["copy", "copies", "cloned", "clone", "mirror", "copie", "cloné", "نسخة", "استنسخ"],
                                ["revoke", "rotate", "new key", "révoquer", "rotation", "إلغاء", "تدوير"],
                            ],
                            reference_answer="Because anyone who cloned or scraped the repository already has a copy of the value, so the only real fix is to revoke the credential and issue a new one.",
                        ),
                    ],
                ),
                Lesson(
                    slug="dependency-security",
                    minutes=30,
                    xp=60,
                    difficulty=D.intermediate,
                    title=T("Dependency Security", "Sécurité des Dépendances", "أمن التبعيّات"),
                    story=T(
                        "Your application is mostly other people's code. Their bugs are your vulnerabilities.",
                        "Votre application est surtout le code des autres. Leurs bugs sont vos vulnérabilités.",
                        "تطبيقك في معظمه كود آخرين. وأخطاؤهم هي ثغراتك.",
                    ),
                    objective=T(
                        "Pin, audit and update dependencies, and judge whether a new package is worth adding.",
                        "Épingler, auditer et mettre à jour les dépendances, et juger si un nouveau paquet mérite d'être ajouté.",
                        "تثبيت التبعيّات وتدقيقها وتحديثها، والحكم إن كانت حزمة جديدة تستحقّ الإضافة.",
                    ),
                    skills=T(
                        "Version pinning, lockfiles, CVE advisories, transitive dependencies, supply chain",
                        "Épinglage de versions, lockfiles, avis CVE, dépendances transitives, chaîne d'approvisionnement",
                        "تثبيت الإصدارات، ملفّات القفل، نشرات الثغرات، التبعيّات غير المباشرة، سلسلة التوريد",
                    ),
                    blocks=[
                        Text(
                            T(
                                "**Pin your versions** and commit the lockfile: an unpinned build installs whatever was published this morning, so the code you tested is not the code you deployed. Pinning also means an upgrade is a deliberate, reviewable change rather than something that happens to you.",
                                "**Épinglez vos versions** et committez le lockfile : une build non épinglée installe ce qui a été publié ce matin, donc le code testé n'est pas celui déployé. L'épinglage fait aussi de la montée de version un changement délibéré et relisible, au lieu d'un événement subi.",
                                "**ثبّت إصداراتك** وثبّت ملفّ القفل في المستودع: فالبناء غير المثبَّت يركّب ما نُشر هذا الصباح، فيكون الكود الذي اختبرته غير الذي نشرته. والتثبيت يجعل الترقية أيضًا تغييرًا مقصودًا قابلًا للمراجعة بدل أن تكون شيئًا يحدث لك.",
                            )
                        ),
                        Text(
                            T(
                                "Then **watch the advisories** and update deliberately. Most of your dependency tree is **transitive** — packages you never chose, pulled in by the ones you did — which is why an audit tool that walks the whole tree finds things reading your own requirements file never will.",
                                "Ensuite, **suivez les avis de sécurité** et mettez à jour délibérément. L'essentiel de votre arbre de dépendances est **transitif** — des paquets jamais choisis, amenés par ceux que vous avez choisis — d'où l'utilité d'un outil d'audit parcourant tout l'arbre, que la lecture de votre fichier de dépendances ne remplacera jamais.",
                                "ثمّ **تابع نشرات الثغرات** وحدّث عن قصد. فمعظم شجرة تبعيّاتك **غير مباشر** — حزم لم تخترها جلبتها الحزم التي اخترتها — ولهذا تجد أداة تدقيق تمشي على الشجرة كلّها ما لن تجده أبدًا بقراءة ملفّ متطلّباتك.",
                            )
                        ),
                        Code(
                            T(
                                "Pinned, auditable, and reviewed like any other change:",
                                "Épinglé, auditable, et relu comme tout autre changement :",
                                "مثبَّت وقابل للتدقيق ويُراجَع كأيّ تغيير آخر:",
                            ),
                            "# requirements.txt - exact versions, so every install is identical\n"
                            "fastapi==0.109.0\n"
                            "sqlalchemy==2.0.23\n"
                            "passlib[bcrypt]==1.7.4\n\n"
                            "# Check the whole tree, not just what you wrote down:\n"
                            "#   pip-audit          (Python)\n"
                            "#   npm audit          (JavaScript)\n\n"
                            "# Before adding a dependency, ask:\n"
                            "#   - is it maintained, and by how many people?\n"
                            "#   - how many transitive packages does it bring?\n"
                            "#   - could a dozen lines of my own code replace it?",
                        ),
                    ],
                    exercises=[
                        MCQ(
                            prompt=T(
                                "Why should a project commit its lockfile?",
                                "Pourquoi un projet doit-il committer son lockfile ?",
                                "لماذا يجب أن يثبّت المشروع ملفّ القفل في المستودع؟",
                            ),
                            hint=T("What guarantees the build you tested is the build you ship?", "Qu'est-ce qui garantit que la build testée est celle livrée ?", "ما الذي يضمن أنّ ما اختبرته هو ما نشرته؟"),
                            explanation=T(
                                "A lockfile records the exact resolved versions, so every install — CI, a teammate's machine, production — gets identical code.",
                                "Un lockfile enregistre les versions résolues exactes : chaque installation — CI, poste d'un collègue, production — obtient un code identique.",
                                "ملفّ القفل يسجّل الإصدارات المحلولة بدقّة، فيحصل كلّ تركيب — في CI أو على جهاز زميل أو في الإنتاج — على الكود نفسه.",
                            ),
                            options=[
                                Option(T("It makes installation faster", "Cela accélère l'installation", "يجعل التركيب أسرع")),
                                Option(
                                    T(
                                        "Every environment installs the exact same versions",
                                        "Tout environnement installe exactement les mêmes versions",
                                        "تركّب كلّ بيئة الإصدارات نفسها بالضبط",
                                    ),
                                    correct=True,
                                ),
                                Option(T("It encrypts the dependencies", "Cela chiffre les dépendances", "يشفّر التبعيّات")),
                                Option(T("It removes transitive dependencies", "Cela supprime les dépendances transitives", "يزيل التبعيّات غير المباشرة")),
                            ],
                        ),
                        MCQ(
                            prompt=T(
                                "You need to pad a string to a fixed width. A package does it in one call. What is the security-aware choice?",
                                "Vous devez compléter une chaîne à une largeur fixe. Un paquet le fait en un appel. Quel est le choix conscient de la sécurité ?",
                                "تحتاج إلى حشو سلسلة إلى عرض ثابت. توجد حزمة تفعل ذلك باستدعاء واحد. ما الخيار الواعي أمنيًا؟",
                            ),
                            hint=T("Every dependency is code you now have to trust and track.", "Chaque dépendance est du code à surveiller et à faire confiance.", "كلّ تبعيّة كود صرت تثق به وتتابعه."),
                            explanation=T(
                                "A one-line standard-library call adds no supply-chain surface. Dependencies are worth their risk for hard problems, not for trivia.",
                                "Un appel d'une ligne de la bibliothèque standard n'ajoute aucune surface d'attaque. Les dépendances valent leur risque pour les problèmes difficiles, pas pour des broutilles.",
                                "استدعاء من سطر واحد من المكتبة القياسية لا يضيف أيّ سطح هجوم. والتبعيّات تستحقّ مخاطرها في المسائل الصعبة لا في التوافه.",
                            ),
                            options=[
                                Option(T("Add the package; it saves typing", "Ajouter le paquet ; cela économise de la frappe", "أضف الحزمة؛ فهي توفّر الكتابة")),
                                Option(
                                    T(
                                        "Use the standard library's built-in padding instead",
                                        "Utiliser le remplissage intégré de la bibliothèque standard",
                                        "استخدم الحشو المدمج في المكتبة القياسية",
                                    ),
                                    correct=True,
                                ),
                                Option(T("Copy the package's source into your repository", "Copier le source du paquet dans votre dépôt", "انسخ مصدر الحزمة إلى مستودعك")),
                                Option(T("Add it, but pin it to the latest version always", "L'ajouter, épinglé toujours à la dernière version", "أضفها لكن ثبّتها دائمًا على أحدث إصدار")),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)


async def seed_cybersecurity_foundations(db, order: int) -> int:
    print("Seeding Introduction to Cybersecurity...")
    return await seed_course(db, CYBERSECURITY_FOUNDATIONS, order)


async def seed_network_security(db, order: int) -> int:
    print("Seeding Fundamentals of Computer Networks Security...")
    return await seed_course(db, NETWORK_SECURITY, order)


async def seed_secure_development(db, order: int) -> int:
    print("Seeding Secure Software Development...")
    return await seed_course(db, SECURE_DEVELOPMENT, order)
