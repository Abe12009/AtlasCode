"""Database Design & Normalization — the course between basic SQL and
advanced querying.

A student who has finished SQL & Databases can already write SELECT/INSERT/
JOIN, but has no way yet to decide what tables should exist in the first
place, or why a schema they're handed is shaped the way it is. This course
closes that gap: modeling a real problem into entities, choosing keys and
constraints, and normalizing (and knowing when not to).
"""

from app.models import DifficultyEnum as D

from .authoring import (
    Code,
    CourseSpec,
    Lesson,
    MCQ,
    Module,
    Option,
    Ordering,
    Prediction,
    SQLWriting,
    T,
    Text,
)

DATABASE_DESIGN_MODULES = [
    Module(
        slug="modeling-data",
        title=T("Modeling Data", "Modéliser les Données", "نمذجة البيانات"),
        description=T(
            "Turn a real-world problem into entities, attributes, and relationships — before a single CREATE TABLE.",
            "Transformez un problème réel en entités, attributs et relations — avant le moindre CREATE TABLE.",
            "حوّل مشكلة واقعية إلى كيانات وسمات وعلاقات — قبل أي CREATE TABLE.",
        ),
        lessons=[
            Lesson(
                slug="from-problem-to-entities",
                minutes=30,
                xp=50,
                difficulty=D.beginner,
                title=T("From Problem to Entities", "Du Problème aux Entités", "من المشكلة إلى الكيانات"),
                story=T(
                    "A friend asks you to design the database for their online bookstore. Before writing any SQL, "
                    "you need to figure out *what things* the database has to remember, and *what it needs to know* about each one.",
                    "Un ami vous demande de concevoir la base de données de sa librairie en ligne. Avant d'écrire le moindre SQL, "
                    "il faut déterminer *quelles choses* la base doit mémoriser, et *ce qu'elle doit savoir* sur chacune.",
                    "يطلب منك صديق تصميم قاعدة بيانات لمكتبته الإلكترونية. قبل كتابة أي SQL، عليك تحديد *ما الأشياء* التي يجب أن تتذكرها قاعدة البيانات، و*ما الذي يجب أن تعرفه* عن كل واحد منها.",
                ),
                objective=T(
                    "Identify entities, attributes, and relationships from a plain-language problem description.",
                    "Identifier entités, attributs et relations à partir d'une description en langage naturel.",
                    "تحديد الكيانات والسمات والعلاقات انطلاقًا من وصف بلغة طبيعية للمشكلة.",
                ),
                skills=T(
                    "Data modeling, entities, attributes, relationships",
                    "Modélisation de données, entités, attributs, relations",
                    "نمذجة البيانات، الكيانات، السمات، العلاقات",
                ),
                blocks=[
                    Text(T(
                        "Data modeling is the step *before* SQL: deciding what tables should exist and what belongs in "
                        "each one. Get it wrong and every query afterward fights the schema. Get it right and most queries "
                        "become obvious. The building blocks are entities, attributes, and relationships.",
                        "La modélisation de données précède le SQL : décider quelles tables doivent exister et ce qui va "
                        "dans chacune. Se tromper ici fait que chaque requête se bat contre le schéma. Bien faire rend la "
                        "plupart des requêtes évidentes. Les briques de base sont les entités, les attributs et les relations.",
                        "نمذجة البيانات هي الخطوة *قبل* SQL: تحديد الجداول التي يجب أن توجد وما ينتمي إلى كل منها. الخطأ هنا "
                        "يجعل كل استعلام لاحق يصارع المخطط. الإتقان يجعل معظم الاستعلامات واضحة. اللبنات الأساسية هي الكيانات والسمات والعلاقات.",
                    )),
                    Text(T(
                        "An **entity** is a distinct thing worth tracking on its own — a Book, an Author, a Customer, an "
                        "Order. A good test: if you'd say \"which one?\" about it (which book, which customer), it's "
                        "probably an entity, not just a detail of another one. An **attribute** is a fact *about* one "
                        "entity — a Book's title, ISBN, and price are attributes of Book, not entities themselves.",
                        "Une **entité** est une chose distincte qui mérite d'être suivie pour elle-même — un Livre, un "
                        "Auteur, un Client, une Commande. Un bon test : si on dirait \"lequel ?\" à son sujet (quel livre, "
                        "quel client), c'est probablement une entité, pas un simple détail d'une autre. Un **attribut** "
                        "est un fait *à propos* d'une entité — le titre, l'ISBN et le prix d'un Livre sont des attributs "
                        "du Livre, pas des entités elles-mêmes.",
                        "**الكيان** هو شيء متمايز يستحق التتبع بذاته — كتاب، مؤلف، زبون، طلب. اختبار جيد: إذا كنت ستقول "
                        "\"أيّهم؟\" عنه (أي كتاب، أي زبون)، فهو على الأرجح كيان، وليس مجرد تفصيل عن كيان آخر. **السمة** هي "
                        "حقيقة *عن* كيان واحد — عنوان الكتاب ورقمه المعياري وسعره سمات للكتاب، وليست كيانات بحد ذاتها.",
                    )),
                    Text(T(
                        "A **relationship** connects two entities: a Customer *places* an Order; an Author *writes* a "
                        "Book. Naming the relationship with a verb (\"places\", \"writes\") usually clarifies whether "
                        "you actually have two entities or just one entity with a confusingly-named attribute.",
                        "Une **relation** relie deux entités : un Client *passe* une Commande ; un Auteur *écrit* un "
                        "Livre. Nommer la relation avec un verbe (\"passe\", \"écrit\") clarifie généralement si vous "
                        "avez vraiment deux entités ou une seule entité avec un attribut mal nommé.",
                        "**العلاقة** تربط بين كيانين: الزبون *يضع* طلبًا؛ المؤلف *يكتب* كتابًا. تسمية العلاقة بفعل "
                        "(\"يضع\"، \"يكتب\") يوضح عادة ما إذا كان لديك فعلاً كيانان أم كيان واحد فقط بسمة سيئة التسمية.",
                    )),
                    Code(
                        T("A first pass at the bookstore, in plain notes before any SQL exists:",
                          "Un premier passage sur la librairie, en notes simples avant tout SQL :",
                          "محاولة أولى للمكتبة، في ملاحظات بسيطة قبل وجود أي SQL:"),
                        "Entities found in \"customers browse books, and place orders for one or more books\":\n"
                        "  Book        -- attributes: title, isbn, price\n"
                        "  Customer    -- attributes: name, email\n"
                        "  Order       -- attributes: order_date, status\n\n"
                        "Relationships:\n"
                        "  Customer --places--> Order\n"
                        "  Order    --contains--> Book   (an order can contain several books)",
                    ),
                ],
                exercises=[
                    MCQ(
                        T("A bookstore tracks books, authors, and customers. Which of these is an attribute, not an entity?",
                          "Une librairie suit les livres, auteurs et clients. Lequel de ces éléments est un attribut, pas une entité ?",
                          "تتبع مكتبة الكتب والمؤلفين والزبائن. أي من هذه سمة وليس كيانًا؟"),
                        T("Ask: would you ever say \"which one\" about it on its own?",
                          "Demandez-vous : diriez-vous jamais \"lequel\" à son sujet, seul ?",
                          "اسأل: هل ستقول يومًا \"أيّهم\" عنه بمفرده؟"),
                        T("A book's price is a fact about a specific book — it doesn't exist independently, so it's an attribute of Book, not its own entity.",
                          "Le prix d'un livre est un fait à propos d'un livre précis — il n'existe pas indépendamment, c'est donc un attribut de Livre, pas une entité à part.",
                          "سعر الكتاب حقيقة عن كتاب محدد — لا يوجد بشكل مستقل، فهو سمة للكتاب وليس كيانًا قائمًا بذاته."),
                        [
                            Option(T("Book", "Livre", "كتاب")),
                            Option(T("Customer", "Client", "زبون")),
                            Option(T("A book's price", "Le prix d'un livre", "سعر الكتاب"), correct=True),
                            Option(T("Author", "Auteur", "مؤلف")),
                        ],
                    ),
                    Ordering(
                        T("Put these data-modeling steps in the order you'd actually do them.",
                          "Mettez ces étapes de modélisation de données dans l'ordre où vous les feriez réellement.",
                          "رتّب خطوات نمذجة البيانات هذه بالترتيب الذي تنفذها فعليًا."),
                        T("You can't name attributes of a thing you haven't identified as an entity yet.",
                          "On ne peut pas nommer les attributs d'une chose qu'on n'a pas encore identifiée comme entité.",
                          "لا يمكنك تسمية سمات شيء لم تحدده بعد ككيان."),
                        T("Requirements come first — you can't model what you don't understand. Entities before their attributes. Relationships last, since they connect entities that must already exist.",
                          "Les besoins d'abord — on ne peut pas modéliser ce qu'on ne comprend pas. Les entités avant leurs attributs. Les relations en dernier, car elles relient des entités qui doivent déjà exister.",
                          "المتطلبات أولاً — لا يمكنك نمذجة ما لا تفهمه. الكيانات قبل سماتها. العلاقات أخيرًا لأنها تربط كيانات يجب أن تكون موجودة مسبقًا."),
                        [
                            T("Gather requirements: what does the system need to remember?", "Recueillir les besoins : que doit mémoriser le système ?", "جمع المتطلبات: ما الذي يجب أن يتذكره النظام؟"),
                            T("Identify entities: the distinct things worth tracking.", "Identifier les entités : les choses distinctes à suivre.", "تحديد الكيانات: الأشياء المتمايزة الجديرة بالتتبع."),
                            T("Identify attributes: the facts about each entity.", "Identifier les attributs : les faits sur chaque entité.", "تحديد السمات: الحقائق عن كل كيان."),
                            T("Identify relationships: how entities connect to each other.", "Identifier les relations : comment les entités se connectent.", "تحديد العلاقات: كيف ترتبط الكيانات ببعضها."),
                        ],
                        xp=15,
                    ),
                ],
            ),
            Lesson(
                slug="er-diagrams-and-cardinality",
                minutes=35,
                xp=55,
                difficulty=D.beginner,
                title=T("ER Diagrams and Cardinality", "Diagrammes ER et Cardinalité", "مخططات الكيان-العلاقة والتعددية"),
                story=T(
                    "Your entities and relationships from the last lesson need a precise shape before they become "
                    "tables: exactly *how many* of one thing can relate to *how many* of another.",
                    "Vos entités et relations de la dernière leçon ont besoin d'une forme précise avant de devenir des "
                    "tables : exactement *combien* d'une chose peuvent se relier à *combien* d'une autre.",
                    "تحتاج الكيانات والعلاقات من الدرس السابق إلى شكل دقيق قبل أن تصبح جداول: بالضبط *كم* من شيء يمكن أن يرتبط بـ *كم* من شيء آخر.",
                ),
                objective=T(
                    "Read and draw simple ER diagrams, and classify a relationship as one-to-one, one-to-many, or many-to-many.",
                    "Lire et dessiner des diagrammes ER simples, et classer une relation en un-à-un, un-à-plusieurs ou plusieurs-à-plusieurs.",
                    "قراءة ورسم مخططات كيان-علاقة بسيطة، وتصنيف العلاقة كواحد لواحد، أو واحد لكثير، أو كثير لكثير.",
                ),
                skills=T(
                    "ER diagrams, cardinality, one-to-many, many-to-many, junction tables",
                    "Diagrammes ER, cardinalité, un-à-plusieurs, plusieurs-à-plusieurs, tables de jonction",
                    "مخططات الكيان-العلاقة، التعددية، واحد لكثير، كثير لكثير، جداول الوصل",
                ),
                blocks=[
                    Text(T(
                        "An Entity-Relationship (ER) diagram draws entities as boxes and relationships as lines between "
                        "them, labeled with a verb. The detail that turns a diagram into something you can actually "
                        "build from is **cardinality**: how many instances on each side can participate.",
                        "Un diagramme Entité-Relation (ER) dessine les entités en boîtes et les relations en lignes "
                        "entre elles, étiquetées par un verbe. Le détail qui transforme un diagramme en quelque chose "
                        "de constructible est la **cardinalité** : combien d'instances de chaque côté peuvent participer.",
                        "يرسم مخطط الكيان-العلاقة (ER) الكيانات كمربعات والعلاقات كخطوط بينها، مُسمّاة بفعل. التفصيل الذي "
                        "يحوّل المخطط إلى شيء يمكن بناؤه فعليًا هو **التعددية**: كم عدد النسخ من كل جانب يمكن أن تشارك.",
                    )),
                    Text(T(
                        "**One-to-one** (1:1): one row on each side, at most — a Person and their Passport. "
                        "**One-to-many** (1:N): one row on one side relates to many on the other — one Author writes "
                        "many Books, but each Book (in a simple model) has one Author. **Many-to-many** (M:N): rows on "
                        "both sides can relate to many on the other — a Book has many Authors *and* an Author writes many Books.",
                        "**Un-à-un** (1:1) : une ligne de chaque côté, au plus — une Personne et son Passeport. "
                        "**Un-à-plusieurs** (1:N) : une ligne d'un côté se relie à plusieurs de l'autre — un Auteur "
                        "écrit plusieurs Livres, mais chaque Livre (dans un modèle simple) a un seul Auteur. "
                        "**Plusieurs-à-plusieurs** (M:N) : les lignes des deux côtés peuvent se relier à plusieurs de "
                        "l'autre — un Livre a plusieurs Auteurs *et* un Auteur écrit plusieurs Livres.",
                        "**واحد لواحد** (1:1): صف واحد من كل جانب على الأكثر — شخص وجواز سفره. **واحد لكثير** (1:N): صف "
                        "واحد من جانب يرتبط بعدة صفوف من الجانب الآخر — مؤلف واحد يكتب عدة كتب، لكن كل كتاب (في نموذج "
                        "بسيط) له مؤلف واحد. **كثير لكثير** (M:N): صفوف من الجانبين يمكن أن ترتبط بعدة صفوف من الجانب "
                        "الآخر — للكتاب عدة مؤلفين *و*للمؤلف عدة كتب.",
                    )),
                    Text(T(
                        "A relational database has no way to store many-to-many directly — a row can't hold a variable "
                        "number of foreign keys. The fix is a **junction table** (also called a join or bridge table): "
                        "a new table whose rows are just pairs of foreign keys, one pair per (Book, Author) combination.",
                        "Une base relationnelle ne peut pas stocker directement du plusieurs-à-plusieurs — une ligne ne "
                        "peut pas contenir un nombre variable de clés étrangères. La solution est une **table de "
                        "jonction** (aussi appelée table de liaison) : une nouvelle table dont les lignes sont juste "
                        "des paires de clés étrangères, une paire par combinaison (Livre, Auteur).",
                        "لا تستطيع قاعدة البيانات العلائقية تخزين علاقة كثير لكثير مباشرة — لا يمكن لصف أن يحمل عددًا "
                        "متغيرًا من المفاتيح الخارجية. الحل هو **جدول وصل** (يسمى أيضًا جدول ربط): جدول جديد صفوفه مجرد "
                        "أزواج من المفاتيح الخارجية، زوج واحد لكل توليفة (كتاب، مؤلف).",
                    )),
                    Code(
                        T("Modeling Book-Author as many-to-many with a junction table:",
                          "Modéliser Livre-Auteur en plusieurs-à-plusieurs avec une table de jonction :",
                          "نمذجة كتاب-مؤلف كعلاقة كثير لكثير بجدول وصل:"),
                        "books            -- id (PK), title, isbn, price\n"
                        "authors          -- id (PK), name\n"
                        "book_authors     -- book_id (FK -> books.id), author_id (FK -> authors.id)\n"
                        "                    -- one row per (book, author) pair; the pair together is the PK",
                    ),
                ],
                exercises=[
                    MCQ(
                        T("A Customer places many Orders, but each Order belongs to exactly one Customer. What is the cardinality of Customer-to-Order?",
                          "Un Client passe plusieurs Commandes, mais chaque Commande appartient à un seul Client. Quelle est la cardinalité Client-Commande ?",
                          "الزبون يضع عدة طلبات، لكن كل طلب ينتمي لزبون واحد فقط. ما تعددية الزبون-الطلب؟"),
                        T("Which side can have \"many\", and which side is stuck at one?",
                          "Quel côté peut avoir \"plusieurs\", et quel côté est limité à un ?",
                          "أي جانب يمكن أن يكون \"كثيرًا\"، وأي جانب محصور بواحد؟"),
                        T("One Customer relates to many Orders, but each Order has only one Customer — that's one-to-many from Customer to Order.",
                          "Un Client se relie à plusieurs Commandes, mais chaque Commande n'a qu'un Client — c'est un-à-plusieurs de Client vers Commande.",
                          "زبون واحد يرتبط بعدة طلبات، لكن كل طلب له زبون واحد فقط — هذا واحد لكثير من الزبون إلى الطلب."),
                        [
                            Option(T("One-to-one", "Un-à-un", "واحد لواحد")),
                            Option(T("One-to-many", "Un-à-plusieurs", "واحد لكثير"), correct=True),
                            Option(T("Many-to-many", "Plusieurs-à-plusieurs", "كثير لكثير")),
                            Option(T("No relationship exists", "Aucune relation n'existe", "لا توجد علاقة")),
                        ],
                    ),
                    SQLWriting(
                        T("A Student can enroll in many Courses, and a Course can have many Students. Write the CREATE TABLE for the junction table `enrollments`, with foreign keys to `students` and `courses`.",
                          "Un Étudiant peut s'inscrire à plusieurs Cours, et un Cours peut avoir plusieurs Étudiants. Écrivez le CREATE TABLE de la table de jonction `enrollments`, avec des clés étrangères vers `students` et `courses`.",
                          "يمكن لطالب التسجيل في عدة مقررات، ويمكن لمقرر أن يضم عدة طلاب. اكتب CREATE TABLE لجدول الوصل `enrollments`، بمفاتيح خارجية إلى `students` و `courses`."),
                        T("Two FOREIGN KEY columns, one referencing each side.",
                          "Deux colonnes FOREIGN KEY, chacune référençant un côté.",
                          "عمودان FOREIGN KEY، كل واحد يشير إلى جانب."),
                        T("A many-to-many relationship becomes a table whose columns are foreign keys to both sides — student_id references students, course_id references courses.",
                          "Une relation plusieurs-à-plusieurs devient une table dont les colonnes sont des clés étrangères vers les deux côtés — student_id référence students, course_id référence courses.",
                          "علاقة كثير لكثير تصبح جدولًا أعمدته مفاتيح خارجية إلى الجانبين — student_id يشير إلى students، وcourse_id يشير إلى courses."),
                        "CREATE TABLE enrollments (\n  ____\n);",
                        "CREATE TABLE enrollments (\n"
                        "  student_id INTEGER REFERENCES students(id),\n"
                        "  course_id INTEGER REFERENCES courses(id),\n"
                        "  PRIMARY KEY (student_id, course_id)\n"
                        ");",
                        ["student_id", "course_id", ["REFERENCES students", "FOREIGN KEY"], ["REFERENCES courses", "FOREIGN KEY"]],
                        xp=20,
                    ),
                ],
            ),
        ],
    ),
    Module(
        slug="keys-and-constraints",
        title=T("Keys & Constraints", "Clés et Contraintes", "المفاتيح والقيود"),
        description=T(
            "Give the database rules it enforces for you: what must be unique, what can never be empty, what must stay consistent.",
            "Donnez à la base des règles qu'elle applique pour vous : ce qui doit être unique, ce qui ne peut jamais être vide, ce qui doit rester cohérent.",
            "امنح قاعدة البيانات قواعد تفرضها بدلاً عنك: ما يجب أن يكون فريدًا، وما لا يمكن أن يكون فارغًا أبدًا، وما يجب أن يبقى متسقًا.",
        ),
        lessons=[
            Lesson(
                slug="primary-foreign-composite-keys",
                minutes=35,
                xp=55,
                difficulty=D.beginner,
                title=T("Primary, Foreign, and Composite Keys", "Clés Primaires, Étrangères et Composites", "المفاتيح الأساسية والخارجية والمركّبة"),
                story=T(
                    "The junction table from the last lesson raised a question: what's the primary key of a table "
                    "that's *only* foreign keys?",
                    "La table de jonction de la dernière leçon a soulevé une question : quelle est la clé primaire "
                    "d'une table qui n'est *que* des clés étrangères ?",
                    "أثار جدول الوصل من الدرس السابق سؤالًا: ما هو المفتاح الأساسي لجدول لا يحتوي *إلا* على مفاتيح خارجية؟",
                ),
                objective=T(
                    "Distinguish candidate, primary, foreign, and composite keys, and choose a composite primary key correctly.",
                    "Distinguer clés candidates, primaires, étrangères et composites, et choisir correctement une clé primaire composite.",
                    "التمييز بين المفاتيح المرشحة والأساسية والخارجية والمركّبة، واختيار مفتاح أساسي مركّب بشكل صحيح.",
                ),
                skills=T(
                    "Candidate keys, primary keys, foreign keys, composite keys",
                    "Clés candidates, clés primaires, clés étrangères, clés composites",
                    "المفاتيح المرشحة، المفاتيح الأساسية، المفاتيح الخارجية، المفاتيح المركّبة",
                ),
                blocks=[
                    Text(T(
                        "A **candidate key** is any column (or set of columns) that could uniquely identify a row — a "
                        "`students` table might have both `id` and `email` as candidate keys, since both are unique. "
                        "The **primary key** is whichever candidate key you actually pick to be *the* identifier used "
                        "everywhere else (foreign keys point at it). The others remain candidate keys, usually enforced with a UNIQUE constraint instead.",
                        "Une **clé candidate** est toute colonne (ou ensemble de colonnes) qui pourrait identifier une "
                        "ligne de façon unique — une table `students` pourrait avoir `id` et `email` comme clés "
                        "candidates, les deux étant uniques. La **clé primaire** est la clé candidate que vous choisissez "
                        "réellement comme identifiant utilisé partout ailleurs (les clés étrangères pointent vers elle). "
                        "Les autres restent des clés candidates, généralement imposées par une contrainte UNIQUE.",
                        "**المفتاح المرشح** هو أي عمود (أو مجموعة أعمدة) يمكن أن يحدد صفًا بشكل فريد — قد يحتوي جدول "
                        "`students` على `id` و`email` كمفتاحين مرشحين، فكلاهما فريد. **المفتاح الأساسي** هو المفتاح "
                        "المرشح الذي تختاره فعليًا ليكون *المُعرّف* المستخدم في كل مكان آخر (تشير إليه المفاتيح "
                        "الخارجية). البقية تبقى مفاتيح مرشحة، تُفرض عادة بقيد UNIQUE.",
                    )),
                    Text(T(
                        "Most tables use a single auto-incrementing `id` as the primary key even when a \"natural\" "
                        "candidate exists (like `email`), because natural keys can change (a user updates their email) "
                        "and surrogate keys (a meaningless generated number) never need to.",
                        "La plupart des tables utilisent un `id` auto-incrémenté comme clé primaire même si une clé "
                        "\"naturelle\" existe (comme `email`), car les clés naturelles peuvent changer (un utilisateur "
                        "met à jour son email) alors qu'une clé de substitution (un nombre généré sans signification) n'a jamais besoin de changer.",
                        "تستخدم معظم الجداول `id` تلقائي التزايد كمفتاح أساسي حتى عند وجود مرشح \"طبيعي\" (مثل "
                        "`email`)، لأن المفاتيح الطبيعية يمكن أن تتغير (يحدّث المستخدم بريده الإلكتروني) بينما المفاتيح "
                        "البديلة (رقم مُولّد بلا معنى) لا تحتاج للتغيير أبدًا.",
                    )),
                    Text(T(
                        "A **composite key** is a primary key made of more than one column together — used exactly "
                        "when no single column is unique on its own, like the junction table from the last lesson: "
                        "neither `student_id` nor `course_id` alone is unique (a student has many enrollments), but "
                        "the *pair* is — a student can't enroll in the same course twice.",
                        "Une **clé composite** est une clé primaire formée de plusieurs colonnes ensemble — utilisée "
                        "exactement quand aucune colonne seule n'est unique, comme la table de jonction de la dernière "
                        "leçon : ni `student_id` ni `course_id` seuls ne sont uniques (un étudiant a plusieurs "
                        "inscriptions), mais la *paire* l'est — un étudiant ne peut pas s'inscrire deux fois au même cours.",
                        "**المفتاح المركّب** هو مفتاح أساسي مكوّن من أكثر من عمود معًا — يُستخدم بالضبط عندما لا يكون أي "
                        "عمود منفرد فريدًا، كجدول الوصل من الدرس السابق: لا `student_id` ولا `course_id` فريد بمفرده "
                        "(للطالب عدة تسجيلات)، لكن *الزوج* فريد — لا يمكن للطالب التسجيل في نفس المقرر مرتين.",
                    )),
                    Code(
                        T("Candidate vs. primary vs. composite, side by side:",
                          "Candidate vs primaire vs composite, côte à côte :",
                          "المرشح مقابل الأساسي مقابل المركّب، جنبًا إلى جنب:"),
                        "CREATE TABLE students (\n"
                        "  id INTEGER PRIMARY KEY,     -- chosen primary key (surrogate)\n"
                        "  email TEXT UNIQUE NOT NULL  -- candidate key, enforced but not primary\n"
                        ");\n\n"
                        "CREATE TABLE enrollments (\n"
                        "  student_id INTEGER REFERENCES students(id),\n"
                        "  course_id INTEGER REFERENCES courses(id),\n"
                        "  PRIMARY KEY (student_id, course_id)   -- composite: neither column alone is unique\n"
                        ");",
                    ),
                ],
                exercises=[
                    MCQ(
                        T("A `students` table has both `id` (auto-incrementing) and `student_number` (a unique school-issued number) columns. If `id` is chosen as the primary key, what is `student_number`?",
                          "Une table `students` a les colonnes `id` (auto-incrémentée) et `student_number` (numéro scolaire unique). Si `id` est choisi comme clé primaire, qu'est ce que `student_number` ?",
                          "لجدول `students` عمودان `id` (تلقائي التزايد) و`student_number` (رقم مدرسي فريد). إذا اختير `id` كمفتاح أساسي، فماذا يكون `student_number`؟"),
                        T("It's still unique, just not the one chosen as THE identifier.",
                          "Il est toujours unique, simplement pas celui choisi comme LE identifiant.",
                          "لا يزال فريدًا، لكنه ليس المُعرّف المختار."),
                        T("Both id and student_number could uniquely identify a row, making them both candidate keys. Only one becomes the primary key; the other stays a candidate key, usually enforced with UNIQUE.",
                          "id et student_number pourraient tous deux identifier une ligne de façon unique, ce sont donc des clés candidates. Une seule devient la clé primaire ; l'autre reste une clé candidate, généralement imposée avec UNIQUE.",
                          "كلاهما id وstudent_number يمكن أن يحدد صفًا بشكل فريد، فكلاهما مفتاح مرشح. واحد فقط يصبح المفتاح الأساسي؛ والآخر يبقى مفتاحًا مرشحًا، يُفرض عادة بـ UNIQUE."),
                        [
                            Option(T("A foreign key", "Une clé étrangère", "مفتاح خارجي")),
                            Option(T("A composite key", "Une clé composite", "مفتاح مركّب")),
                            Option(T("A candidate key that was not chosen as primary", "Une clé candidate non choisie comme primaire", "مفتاح مرشح لم يُختر كأساسي"), correct=True),
                            Option(T("Not a key of any kind", "Pas une clé du tout", "ليس مفتاحًا من أي نوع")),
                        ],
                    ),
                    SQLWriting(
                        T("Write CREATE TABLE for `order_items`: it needs a composite primary key of `order_id` and `product_id` (an order can't list the same product twice), plus a `quantity` column.",
                          "Écrivez le CREATE TABLE de `order_items` : il lui faut une clé primaire composite de `order_id` et `product_id` (une commande ne peut pas lister deux fois le même produit), plus une colonne `quantity`.",
                          "اكتب CREATE TABLE لـ `order_items`: يحتاج مفتاحًا أساسيًا مركّبًا من `order_id` و`product_id` (لا يمكن للطلب أن يذكر نفس المنتج مرتين)، بالإضافة إلى عمود `quantity`."),
                        T("PRIMARY KEY (col1, col2) with both columns listed inside the parentheses.",
                          "PRIMARY KEY (col1, col2) avec les deux colonnes listées entre parenthèses.",
                          "PRIMARY KEY (col1, col2) مع ذكر العمودين داخل القوسين."),
                        T("A composite primary key lists both columns together in one PRIMARY KEY(...) clause — that's what makes the pair unique, not either column alone.",
                          "Une clé primaire composite liste les deux colonnes ensemble dans une seule clause PRIMARY KEY(...) — c'est ce qui rend la paire unique, pas chaque colonne seule.",
                          "المفتاح الأساسي المركّب يذكر العمودين معًا في عبارة PRIMARY KEY(...) واحدة — وهذا ما يجعل الزوج فريدًا، وليس أي عمود بمفرده."),
                        "CREATE TABLE order_items (\n  ____\n);",
                        "CREATE TABLE order_items (\n"
                        "  order_id INTEGER REFERENCES orders(id),\n"
                        "  product_id INTEGER REFERENCES products(id),\n"
                        "  quantity INTEGER,\n"
                        "  PRIMARY KEY (order_id, product_id)\n"
                        ");",
                        [["PRIMARY KEY (order_id, product_id)", "PRIMARY KEY(order_id, product_id)"], "quantity"],
                        xp=20,
                    ),
                ],
            ),
            Lesson(
                slug="constraints-and-referential-integrity",
                minutes=35,
                xp=55,
                difficulty=D.beginner,
                title=T("Constraints & Referential Integrity", "Contraintes et Intégrité Référentielle", "القيود والتكامل المرجعي"),
                story=T(
                    "Keys tell the database what identifies a row. Constraints tell it what makes a row *valid* in the "
                    "first place — and what should happen to related rows when one gets deleted.",
                    "Les clés indiquent à la base ce qui identifie une ligne. Les contraintes indiquent ce qui rend une "
                    "ligne *valide* — et ce qui doit arriver aux lignes liées quand l'une est supprimée.",
                    "تخبر المفاتيح قاعدة البيانات بما يحدد الصف. تخبرها القيود بما يجعل الصف *صالحًا* أصلًا — وما الذي "
                    "يجب أن يحدث للصفوف المرتبطة عند حذف صف.",
                ),
                objective=T(
                    "Use NOT NULL, UNIQUE, CHECK, and DEFAULT constraints, and predict the effect of ON DELETE CASCADE/SET NULL/RESTRICT.",
                    "Utiliser les contraintes NOT NULL, UNIQUE, CHECK et DEFAULT, et prédire l'effet de ON DELETE CASCADE/SET NULL/RESTRICT.",
                    "استخدام قيود NOT NULL وUNIQUE وCHECK وDEFAULT، وتوقّع أثر ON DELETE CASCADE/SET NULL/RESTRICT.",
                ),
                skills=T(
                    "NOT NULL, UNIQUE, CHECK, DEFAULT, referential integrity, ON DELETE",
                    "NOT NULL, UNIQUE, CHECK, DEFAULT, intégrité référentielle, ON DELETE",
                    "NOT NULL، UNIQUE، CHECK، DEFAULT، التكامل المرجعي، ON DELETE",
                ),
                blocks=[
                    Text(T(
                        "Column constraints reject bad data before it's ever stored. `NOT NULL` requires a value. "
                        "`UNIQUE` forbids duplicates (and allows enforcing a candidate key that isn't the primary key). "
                        "`CHECK` runs an arbitrary boolean expression — `CHECK (price >= 0)` rejects negative prices. "
                        "`DEFAULT` fills a value in when none is given.",
                        "Les contraintes de colonne rejettent les mauvaises données avant qu'elles ne soient stockées. "
                        "`NOT NULL` exige une valeur. `UNIQUE` interdit les doublons (et permet d'imposer une clé "
                        "candidate qui n'est pas la primaire). `CHECK` exécute une expression booléenne arbitraire — "
                        "`CHECK (price >= 0)` rejette les prix négatifs. `DEFAULT` remplit une valeur si aucune n'est donnée.",
                        "قيود الأعمدة ترفض البيانات السيئة قبل تخزينها. `NOT NULL` يتطلب قيمة. `UNIQUE` يمنع التكرار "
                        "(ويسمح بفرض مفتاح مرشح ليس أساسيًا). `CHECK` ينفّذ تعبيرًا منطقيًا اختياريًا — `CHECK (price >= 0)` "
                        "يرفض الأسعار السالبة. `DEFAULT` يملأ قيمة عند عدم إعطاء أي قيمة.",
                    )),
                    Text(T(
                        "**Referential integrity** means a foreign key value must always point at a row that actually "
                        "exists — an `order_items.product_id` can never reference a product that was deleted, unless "
                        "you say what should happen instead. `ON DELETE` decides: `RESTRICT` (the default-ish behavior) "
                        "blocks the delete while references exist; `CASCADE` deletes the dependent rows too; `SET NULL` "
                        "clears the foreign key instead of deleting anything.",
                        "L'**intégrité référentielle** signifie qu'une valeur de clé étrangère doit toujours pointer "
                        "vers une ligne qui existe réellement — `order_items.product_id` ne peut jamais référencer un "
                        "produit supprimé, sauf si vous précisez ce qui doit se passer à la place. `ON DELETE` décide : "
                        "`RESTRICT` bloque la suppression tant que des références existent ; `CASCADE` supprime aussi "
                        "les lignes dépendantes ; `SET NULL` vide la clé étrangère au lieu de supprimer quoi que ce soit.",
                        "**التكامل المرجعي** يعني أن قيمة المفتاح الخارجي يجب أن تشير دائمًا إلى صف موجود فعلًا — لا "
                        "يمكن لـ `order_items.product_id` أن يشير أبدًا إلى منتج محذوف، ما لم تحدد ما يجب أن يحدث بدلًا "
                        "من ذلك. يقرر `ON DELETE`: يمنع `RESTRICT` الحذف طالما توجد إشارات إليه؛ يحذف `CASCADE` الصفوف "
                        "التابعة أيضًا؛ يمسح `SET NULL` المفتاح الخارجي بدل حذف أي شيء.",
                    )),
                    Code(
                        T("Constraints and ON DELETE behavior together:",
                          "Contraintes et comportement ON DELETE ensemble :",
                          "القيود وسلوك ON DELETE معًا:"),
                        "CREATE TABLE products (\n"
                        "  id INTEGER PRIMARY KEY,\n"
                        "  name TEXT NOT NULL,\n"
                        "  sku TEXT UNIQUE NOT NULL,\n"
                        "  price NUMERIC CHECK (price >= 0),\n"
                        "  in_stock INTEGER DEFAULT 0\n"
                        ");\n\n"
                        "CREATE TABLE order_items (\n"
                        "  order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,   -- deleting an order deletes its items\n"
                        "  product_id INTEGER REFERENCES products(id) ON DELETE RESTRICT, -- can't delete a product still on an order\n"
                        "  PRIMARY KEY (order_id, product_id)\n"
                        ");",
                    ),
                ],
                exercises=[
                    MCQ(
                        T("`order_items.order_id` is set to `ON DELETE CASCADE`. What happens if you delete a row from `orders`?",
                          "`order_items.order_id` est réglé sur `ON DELETE CASCADE`. Que se passe-t-il si vous supprimez une ligne de `orders` ?",
                          "تم ضبط `order_items.order_id` على `ON DELETE CASCADE`. ماذا يحدث إذا حذفت صفًا من `orders`؟"),
                        T("CASCADE means the deletion \"flows down\" to the dependent rows.",
                          "CASCADE signifie que la suppression \"se propage\" aux lignes dépendantes.",
                          "CASCADE يعني أن الحذف \"ينساب\" إلى الصفوف التابعة."),
                        T("ON DELETE CASCADE automatically deletes every row in order_items that referenced the deleted order — the deletion cascades to dependents instead of being blocked or leaving orphans.",
                          "ON DELETE CASCADE supprime automatiquement chaque ligne de order_items qui référençait la commande supprimée — la suppression se propage aux dépendants au lieu d'être bloquée ou de laisser des orphelins.",
                          "يحذف ON DELETE CASCADE تلقائيًا كل صف في order_items كان يشير إلى الطلب المحذوف — ينساب الحذف إلى التابعين بدل أن يُمنع أو يترك صفوفًا يتيمة."),
                        [
                            Option(T("The delete is blocked while order_items rows reference it", "La suppression est bloquée tant que des lignes order_items la référencent", "يُمنع الحذف طالما توجد صفوف order_items تشير إليه")),
                            Option(T("The matching order_items rows are deleted too", "Les lignes order_items correspondantes sont aussi supprimées", "تُحذف صفوف order_items المطابقة أيضًا"), correct=True),
                            Option(T("The matching order_items rows have order_id set to NULL", "Les lignes order_items correspondantes ont order_id mis à NULL", "تُصبح قيمة order_id في صفوف order_items المطابقة NULL")),
                            Option(T("Nothing — CASCADE only affects INSERT", "Rien — CASCADE n'affecte que INSERT", "لا شيء — CASCADE يؤثر فقط على INSERT")),
                        ],
                    ),
                    Prediction(
                        T("`products.price` has `CHECK (price >= 0)`. What happens when this INSERT runs?",
                          "`products.price` a `CHECK (price >= 0)`. Que se passe-t-il quand cet INSERT s'exécute ?",
                          "لدى `products.price` قيد `CHECK (price >= 0)`. ماذا يحدث عند تنفيذ هذا الإدراج؟"),
                        T("Does -5 satisfy price >= 0?",
                          "Est-ce que -5 satisfait price >= 0 ?",
                          "هل يحقق -5 الشرط price >= 0؟"),
                        T("CHECK (price >= 0) rejects any row where the expression evaluates to false — -5 >= 0 is false, so the database refuses the INSERT with a constraint violation error.",
                          "CHECK (price >= 0) rejette toute ligne où l'expression est fausse — -5 >= 0 est faux, donc la base refuse l'INSERT avec une erreur de violation de contrainte.",
                          "يرفض CHECK (price >= 0) أي صف يكون فيه التعبير خاطئًا — -5 >= 0 خطأ، فترفض قاعدة البيانات عملية الإدراج بخطأ انتهاك قيد."),
                        "INSERT INTO products (name, sku, price) VALUES ('Broken Mug', 'MUG-1', -5);",
                        "The INSERT is rejected: a CHECK constraint violation (price -5 does not satisfy price >= 0).",
                        xp=15,
                    ),
                ],
            ),
        ],
    ),
    Module(
        slug="normalization",
        title=T("Normalization", "Normalisation", "التسوية"),
        description=T(
            "The rules that keep a schema free of redundancy and the anomalies it causes — and when to deliberately break them.",
            "Les règles qui gardent un schéma libre de redondance et des anomalies qu'elle cause — et quand les enfreindre volontairement.",
            "القواعد التي تُبقي المخطط خاليًا من التكرار والمشاكل التي يسببها — ومتى تُخرق هذه القواعد عمدًا.",
        ),
        lessons=[
            Lesson(
                slug="first-and-second-normal-form",
                minutes=40,
                xp=60,
                difficulty=D.intermediate,
                title=T("First and Second Normal Form", "Première et Deuxième Forme Normale", "الصورة الطبيعية الأولى والثانية"),
                story=T(
                    "A junior teammate designed a table that \"works\" — every query so far has run fine — but every "
                    "time a student changes their email, five rows need updating instead of one. Something is wrong "
                    "with the shape of the data, not the queries against it.",
                    "Un coéquipier junior a conçu une table qui \"fonctionne\" — toutes les requêtes jusqu'ici tournent "
                    "bien — mais chaque fois qu'un étudiant change son email, cinq lignes doivent être mises à jour au "
                    "lieu d'une. Quelque chose ne va pas dans la forme des données, pas dans les requêtes.",
                    "صمم زميل مبتدئ جدولاً \"يعمل\" — كل الاستعلامات حتى الآن تنفّذ بلا مشاكل — لكن في كل مرة يغيّر فيها "
                    "طالب بريده الإلكتروني، يجب تحديث خمسة صفوف بدل صف واحد. هناك خطأ في شكل البيانات، وليس في الاستعلامات.",
                ),
                objective=T(
                    "Recognize violations of 1NF (non-atomic values, repeating groups) and 2NF (partial dependency on a composite key), and fix them.",
                    "Reconnaître les violations de 1NF (valeurs non atomiques, groupes répétitifs) et de 2NF (dépendance partielle sur une clé composite), et les corriger.",
                    "التعرف على انتهاكات الصورة الأولى (قيم غير ذرية، مجموعات متكررة) والصورة الثانية (اعتماد جزئي على مفتاح مركّب)، وتصحيحها.",
                ),
                skills=T(
                    "Normalization, 1NF, 2NF, atomic values, partial dependency, redundancy",
                    "Normalisation, 1NF, 2NF, valeurs atomiques, dépendance partielle, redondance",
                    "التسوية، الصورة الأولى، الصورة الثانية، القيم الذرية، الاعتماد الجزئي، التكرار",
                ),
                blocks=[
                    Text(T(
                        "Normalization is a series of rules (\"normal forms\") that remove redundancy from a schema so "
                        "each fact is stored in exactly one place. Redundancy isn't just wasted space — it's what "
                        "causes **update anomalies** (changing one fact means finding and updating every copy), "
                        "**insert anomalies** (you can't record a fact without also inventing an unrelated one), and "
                        "**delete anomalies** (deleting one fact accidentally deletes another).",
                        "La normalisation est une série de règles (\"formes normales\") qui éliminent la redondance "
                        "d'un schéma afin que chaque fait soit stocké à un seul endroit. La redondance n'est pas "
                        "seulement un gaspillage d'espace — elle cause des **anomalies de mise à jour** (changer un "
                        "fait signifie trouver et mettre à jour chaque copie), des **anomalies d'insertion** (on ne "
                        "peut pas enregistrer un fait sans en inventer un autre sans rapport), et des **anomalies de "
                        "suppression** (supprimer un fait en supprime accidentellement un autre).",
                        "التسوية سلسلة من القواعد (\"الصور الطبيعية\") تزيل التكرار من المخطط بحيث تُخزَّن كل حقيقة في "
                        "مكان واحد فقط. التكرار ليس مجرد هدر للمساحة — إنه سبب **شذوذ التحديث** (تغيير حقيقة واحدة "
                        "يعني إيجاد وتحديث كل نسخة منها)، و**شذوذ الإدراج** (لا يمكنك تسجيل حقيقة دون اختراع حقيقة أخرى "
                        "غير ذات صلة)، و**شذوذ الحذف** (حذف حقيقة يحذف عن طريق الخطأ حقيقة أخرى).",
                    )),
                    Text(T(
                        "**First Normal Form (1NF)**: every column holds a single, atomic value — no comma-separated "
                        "lists stuffed into one field, no repeating groups of columns like `phone1`, `phone2`, "
                        "`phone3`. If a cell answers \"how many?\" as well as \"what?\", split it into its own table.",
                        "**Première Forme Normale (1NF)** : chaque colonne contient une seule valeur atomique — pas de "
                        "listes séparées par des virgules entassées dans un champ, pas de groupes répétitifs de "
                        "colonnes comme `phone1`, `phone2`, `phone3`. Si une cellule répond à \"combien ?\" en plus de "
                        "\"quoi ?\", séparez-la dans sa propre table.",
                        "**الصورة الطبيعية الأولى (1NF)**: كل عمود يحمل قيمة واحدة ذرية — لا قوائم مفصولة بفواصل "
                        "محشورة في حقل واحد، ولا مجموعات أعمدة متكررة مثل `phone1` و`phone2` و`phone3`. إذا كانت خلية "
                        "تجيب على \"كم؟\" بالإضافة إلى \"ماذا؟\"، افصلها في جدول خاص بها.",
                    )),
                    Text(T(
                        "**Second Normal Form (2NF)** only matters for tables with a *composite* primary key: every "
                        "non-key column must depend on the *whole* key, not just part of it. In an `enrollments` "
                        "table keyed on `(student_id, course_id)`, a `student_name` column would depend only on "
                        "`student_id` — that's a **partial dependency**, and it's the same redundancy problem as 1NF, "
                        "just triggered by a composite key instead of a repeating group.",
                        "La **Deuxième Forme Normale (2NF)** ne concerne que les tables avec une clé primaire "
                        "*composite* : chaque colonne non-clé doit dépendre de la clé *entière*, pas seulement d'une "
                        "partie. Dans une table `enrollments` avec pour clé `(student_id, course_id)`, une colonne "
                        "`student_name` ne dépendrait que de `student_id` — c'est une **dépendance partielle**, le "
                        "même problème de redondance que 1NF, déclenché cette fois par une clé composite.",
                        "**الصورة الطبيعية الثانية (2NF)** تخص فقط الجداول ذات المفتاح الأساسي *المركّب*: يجب أن يعتمد "
                        "كل عمود غير مفتاحي على المفتاح *بالكامل*، وليس على جزء منه فقط. في جدول `enrollments` مفتاحه "
                        "`(student_id, course_id)`، عمود `student_name` سيعتمد فقط على `student_id` — هذا **اعتماد "
                        "جزئي**، ونفس مشكلة التكرار التي في 1NF، لكنها هنا بسبب مفتاح مركّب بدل مجموعة متكررة.",
                    )),
                    Code(
                        T("A 1NF violation (repeating columns) and its fix:",
                          "Une violation 1NF (colonnes répétitives) et sa correction :",
                          "انتهاك للصورة الأولى (أعمدة متكررة) وتصحيحه:"),
                        "-- Violates 1NF: a variable number of phones crammed into fixed columns\n"
                        "students(id, name, phone1, phone2, phone3)\n\n"
                        "-- 1NF: one row per fact, no limit on how many phones a student has\n"
                        "students(id, name)\n"
                        "student_phones(student_id, phone)",
                    ),
                ],
                exercises=[
                    MCQ(
                        T("A `students` table has a column `courses_taken` storing values like `\"SQL101, WEB201, MATH110\"`. Which rule does this violate?",
                          "Une table `students` a une colonne `courses_taken` avec des valeurs comme `\"SQL101, WEB201, MATH110\"`. Quelle règle est violée ?",
                          "لجدول `students` عمود `courses_taken` يحمل قيمًا مثل `\"SQL101, WEB201, MATH110\"`. أي قاعدة يُخالف هذا؟"),
                        T("Is a comma-separated list one atomic value?",
                          "Une liste séparée par des virgules est-elle une valeur atomique ?",
                          "هل القائمة المفصولة بفواصل قيمة ذرية واحدة؟"),
                        T("1NF requires atomic values — a comma-separated list is really several values crammed into one cell, which makes filtering, counting, or joining on individual courses painful or impossible with plain SQL.",
                          "1NF exige des valeurs atomiques — une liste séparée par des virgules est en réalité plusieurs valeurs entassées dans une cellule, ce qui rend le filtrage, le comptage ou la jointure sur des cours individuels pénible voire impossible en SQL standard.",
                          "تتطلب 1NF قيمًا ذرية — القائمة المفصولة بفواصل هي في الحقيقة عدة قيم محشورة في خلية واحدة، مما يجعل التصفية أو العد أو الربط على مقرر بمفرده صعبًا أو مستحيلًا بـ SQL العادي."),
                        [
                            Option(T("First Normal Form (1NF)", "Première Forme Normale (1NF)", "الصورة الطبيعية الأولى (1NF)"), correct=True),
                            Option(T("Second Normal Form (2NF)", "Deuxième Forme Normale (2NF)", "الصورة الطبيعية الثانية (2NF)")),
                            Option(T("Referential integrity", "Intégrité référentielle", "التكامل المرجعي")),
                            Option(T("Nothing — this is a valid design", "Rien — ce design est valide", "لا شيء — هذا تصميم صالح")),
                        ],
                    ),
                    MCQ(
                        T("`enrollments(student_id, course_id, student_email, grade)` uses (student_id, course_id) as its composite primary key. Which column causes a 2NF violation?",
                          "`enrollments(student_id, course_id, student_email, grade)` utilise (student_id, course_id) comme clé primaire composite. Quelle colonne cause une violation 2NF ?",
                          "يستخدم `enrollments(student_id, course_id, student_email, grade)` (student_id, course_id) كمفتاح أساسي مركّب. أي عمود يسبب انتهاك الصورة الثانية؟"),
                        T("Which column's value only depends on ONE half of the composite key?",
                          "La valeur de quelle colonne ne dépend que d'UNE moitié de la clé composite ?",
                          "قيمة أي عمود تعتمد فقط على نصف واحد من المفتاح المركّب؟"),
                        T("student_email depends only on student_id (a student's email doesn't change per course), not on the full (student_id, course_id) pair — a classic partial dependency. grade genuinely depends on both: it's specific to that student in that course.",
                          "student_email ne dépend que de student_id (l'email d'un étudiant ne change pas par cours), pas de la paire complète (student_id, course_id) — une dépendance partielle classique. grade dépend réellement des deux : il est spécifique à cet étudiant dans ce cours.",
                          "يعتمد student_email فقط على student_id (بريد الطالب لا يتغير حسب المقرر)، وليس على الزوج الكامل (student_id, course_id) — اعتماد جزئي كلاسيكي. أما grade فيعتمد فعلاً على كليهما: فهو خاص بذلك الطالب في ذلك المقرر."),
                        [
                            Option(T("grade", "grade", "grade")),
                            Option(T("student_email", "student_email", "student_email"), correct=True),
                            Option(T("student_id", "student_id", "student_id")),
                            Option(T("course_id", "course_id", "course_id")),
                        ],
                    ),
                ],
            ),
            Lesson(
                slug="third-normal-form-and-denormalizing",
                minutes=40,
                xp=60,
                difficulty=D.intermediate,
                title=T("Third Normal Form & When to Denormalize", "Troisième Forme Normale et Dénormaliser", "الصورة الطبيعية الثالثة ومتى نُخالفها"),
                story=T(
                    "The schema is now free of 1NF and 2NF problems, but changing a customer's city still means "
                    "updating a `city_population` value stored on every one of their orders. One more rule to go.",
                    "Le schéma est maintenant libre des problèmes 1NF et 2NF, mais changer la ville d'un client "
                    "signifie toujours mettre à jour une valeur `city_population` stockée sur chacune de ses "
                    "commandes. Encore une règle à appliquer.",
                    "أصبح المخطط الآن خاليًا من مشاكل 1NF و2NF، لكن تغيير مدينة زبون لا يزال يعني تحديث قيمة "
                    "`city_population` مخزّنة في كل طلب من طلباته. قاعدة واحدة أخرى متبقية.",
                ),
                objective=T(
                    "Recognize a transitive dependency (3NF violation) and fix it, and decide when denormalizing on purpose is the right tradeoff.",
                    "Reconnaître une dépendance transitive (violation 3NF) et la corriger, et décider quand dénormaliser volontairement est le bon compromis.",
                    "التعرف على الاعتماد الانتقالي (انتهاك الصورة الثالثة) وتصحيحه، وتحديد متى يكون كسر التسوية عمدًا هو الخيار الصحيح.",
                ),
                skills=T(
                    "Third Normal Form, transitive dependency, denormalization tradeoffs",
                    "Troisième Forme Normale, dépendance transitive, compromis de dénormalisation",
                    "الصورة الطبيعية الثالثة، الاعتماد الانتقالي، مقايضات كسر التسوية",
                ),
                blocks=[
                    Text(T(
                        "**Third Normal Form (3NF)**: no non-key column may depend on *another non-key column* — only "
                        "on the primary key directly. If `orders(id, customer_id, customer_city, city_population)` "
                        "exists, `city_population` depends on `customer_city`, which itself depends on `customer_id` — "
                        "a chain, or **transitive dependency**, rather than a direct one to the primary key.",
                        "**Troisième Forme Normale (3NF)** : aucune colonne non-clé ne peut dépendre d'une *autre "
                        "colonne non-clé* — seulement directement de la clé primaire. Si `orders(id, customer_id, "
                        "customer_city, city_population)` existe, `city_population` dépend de `customer_city`, qui "
                        "dépend lui-même de `customer_id` — une chaîne, ou **dépendance transitive**, plutôt qu'une "
                        "dépendance directe à la clé primaire.",
                        "**الصورة الطبيعية الثالثة (3NF)**: لا يجوز لأي عمود غير مفتاحي أن يعتمد على *عمود آخر غير "
                        "مفتاحي* — بل على المفتاح الأساسي مباشرة فقط. إذا وُجد `orders(id, customer_id, customer_city, "
                        "city_population)`، فإن `city_population` يعتمد على `customer_city`، الذي يعتمد بدوره على "
                        "`customer_id` — سلسلة، أو **اعتماد انتقالي**، بدل اعتماد مباشر على المفتاح الأساسي.",
                    )),
                    Text(T(
                        "The fix is the same move every time: pull the transitively-dependent facts into their own "
                        "table, keyed on whatever they actually depend on. `city_population` moves to a `cities` "
                        "table keyed on `city`; `orders` keeps only `customer_id`, and the city (and its population) "
                        "is reached by joining through `customers`.",
                        "La correction est toujours le même geste : extraire les faits transitivement dépendants dans "
                        "leur propre table, avec pour clé ce dont ils dépendent réellement. `city_population` part "
                        "dans une table `cities` avec pour clé `city` ; `orders` ne garde que `customer_id`, et la "
                        "ville (et sa population) s'obtient par jointure via `customers`.",
                        "التصحيح نفس الخطوة دائمًا: انقل الحقائق المعتمدة انتقاليًا إلى جدولها الخاص، بمفتاح هو ما "
                        "تعتمد عليه فعلًا. ينتقل `city_population` إلى جدول `cities` بمفتاح `city`؛ يحتفظ `orders` فقط "
                        "بـ `customer_id`، وتُستَرجَع المدينة (وعدد سكانها) عبر ربط بـ `customers`.",
                    )),
                    Text(T(
                        "Fully normalized schemas minimize redundancy but maximize the number of JOINs a query needs. "
                        "**Denormalization** — deliberately re-adding some redundancy — trades write-time complexity "
                        "for read-time speed, and is a reasonable choice for reporting tables, caches, or columns that "
                        "almost never change (storing a `product_name_snapshot` on an order line so historical "
                        "invoices don't change if the product is later renamed is denormalization done on purpose, not "
                        "a mistake).",
                        "Les schémas totalement normalisés minimisent la redondance mais maximisent le nombre de "
                        "JOINs nécessaires. La **dénormalisation** — réintroduire volontairement de la redondance — "
                        "échange de la complexité à l'écriture contre de la vitesse à la lecture, et c'est un choix "
                        "raisonnable pour des tables de reporting, des caches, ou des colonnes qui changent presque "
                        "jamais (stocker un `product_name_snapshot` sur une ligne de commande pour que les factures "
                        "historiques ne changent pas si le produit est renommé plus tard est une dénormalisation "
                        "volontaire, pas une erreur).",
                        "المخططات المسوّاة بالكامل تقلل التكرار لكنها تزيد عدد عمليات JOIN التي يحتاجها الاستعلام. "
                        "**كسر التسوية** — إعادة إدخال بعض التكرار عمدًا — يبادل تعقيدًا وقت الكتابة بسرعة وقت القراءة، "
                        "وهو خيار معقول لجداول التقارير أو التخزين المؤقت أو الأعمدة التي نادرًا ما تتغير (تخزين "
                        "`product_name_snapshot` في سطر الطلب حتى لا تتغير الفواتير التاريخية إذا أُعيدت تسمية المنتج "
                        "لاحقًا هو كسر تسوية مقصود، وليس خطأً).",
                    )),
                    Code(
                        T("Fixing the transitive dependency:",
                          "Correction de la dépendance transitive :",
                          "تصحيح الاعتماد الانتقالي:"),
                        "-- Violates 3NF: city_population depends on customer_city, not on orders.id directly\n"
                        "orders(id, customer_id, customer_city, city_population, order_date)\n\n"
                        "-- 3NF: city facts live where they belong, reached by joining\n"
                        "orders(id, customer_id, order_date)\n"
                        "customers(id, name, city)\n"
                        "cities(city, population)",
                    ),
                ],
                exercises=[
                    MCQ(
                        T("`employees(id, name, department_id, department_name, department_budget)` stores department_name and department_budget directly on every employee row. What's the problem?",
                          "`employees(id, name, department_id, department_name, department_budget)` stocke department_name et department_budget directement sur chaque ligne employé. Quel est le problème ?",
                          "يخزّن `employees(id, name, department_id, department_name, department_budget)` department_name وdepartment_budget مباشرة في كل صف موظف. ما المشكلة؟"),
                        T("Do department_name and department_budget depend on the employee, or on the department?",
                          "department_name et department_budget dépendent-ils de l'employé, ou du département ?",
                          "هل يعتمد department_name وdepartment_budget على الموظف، أم على القسم؟"),
                        T("department_name and department_budget depend on department_id, a non-key column — a transitive dependency. Every employee in the same department repeats the same department facts, and changing a department's budget means updating every one of its employees' rows.",
                          "department_name et department_budget dépendent de department_id, une colonne non-clé — une dépendance transitive. Chaque employé du même département répète les mêmes faits, et changer le budget d'un département signifie mettre à jour toutes les lignes de ses employés.",
                          "يعتمد department_name وdepartment_budget على department_id، وهو عمود غير مفتاحي — اعتماد انتقالي. كل موظف في نفس القسم يكرر نفس حقائق القسم، وتغيير ميزانية قسم يعني تحديث كل صفوف موظفيه."),
                        [
                            Option(T("Nothing, this is already 3NF", "Rien, c'est déjà 3NF", "لا شيء، هذا بالفعل 3NF")),
                            Option(T("A transitive dependency: department facts depend on department_id, not on the employee directly", "Une dépendance transitive : les faits du département dépendent de department_id, pas directement de l'employé", "اعتماد انتقالي: حقائق القسم تعتمد على department_id، وليس على الموظف مباشرة"), correct=True),
                            Option(T("A missing primary key", "Une clé primaire manquante", "مفتاح أساسي مفقود")),
                            Option(T("A many-to-many relationship", "Une relation plusieurs-à-plusieurs", "علاقة كثير لكثير")),
                        ],
                    ),
                    SQLWriting(
                        T("Fix the employees table above by splitting it into two properly-normalized tables: `employees` and `departments`. Write both CREATE TABLE statements.",
                          "Corrigez la table employees ci-dessus en la divisant en deux tables normalisées : `employees` et `departments`. Écrivez les deux CREATE TABLE.",
                          "صحّح جدول employees أعلاه بتقسيمه إلى جدولين مسوّيين بشكل صحيح: `employees` و`departments`. اكتب عبارتي CREATE TABLE."),
                        T("departments gets its own table keyed on id, holding name and budget. employees keeps only a department_id foreign key.",
                          "departments obtient sa propre table avec pour clé id, contenant name et budget. employees ne garde qu'une clé étrangère department_id.",
                          "يحصل departments على جدوله الخاص بمفتاح id، يحمل name وbudget. يحتفظ employees فقط بمفتاح خارجي department_id."),
                        T("Pulling department_name and department_budget into their own departments table (keyed on id) removes the transitive dependency — employees now only stores a department_id foreign key, and department facts live in exactly one row each.",
                          "Extraire department_name et department_budget dans leur propre table departments (avec pour clé id) supprime la dépendance transitive — employees ne stocke plus qu'une clé étrangère department_id, et les faits du département vivent en une seule ligne chacun.",
                          "سحب department_name وdepartment_budget إلى جدول departments الخاص بها (بمفتاح id) يزيل الاعتماد الانتقالي — يخزّن employees الآن فقط مفتاحًا خارجيًا department_id، وتعيش حقائق القسم في صف واحد لكل قسم."),
                        "CREATE TABLE departments (\n  ____\n);\n\nCREATE TABLE employees (\n  ____\n);",
                        "CREATE TABLE departments (\n"
                        "  id INTEGER PRIMARY KEY,\n"
                        "  name TEXT NOT NULL,\n"
                        "  budget NUMERIC\n"
                        ");\n\n"
                        "CREATE TABLE employees (\n"
                        "  id INTEGER PRIMARY KEY,\n"
                        "  name TEXT NOT NULL,\n"
                        "  department_id INTEGER REFERENCES departments(id)\n"
                        ");",
                        ["CREATE TABLE departments", "CREATE TABLE employees", ["department_id", "department_id INTEGER"]],
                        xp=20,
                    ),
                ],
            ),
        ],
    ),
]
