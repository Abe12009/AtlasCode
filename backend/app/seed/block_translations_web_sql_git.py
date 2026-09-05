# -*- coding: utf-8 -*-
"""FR/AR lesson-block translations for Web Fundamentals, SQL & Databases and
Git & GitHub (courses 2, 3 and 4).

Same contract as block_translations_python: keyed by lesson_block.id, ``en``
repeats the source so the backfill can verify before writing, and code examples
are copied verbatim from the base block.

Technical identifiers (HTML tags, CSS properties, SQL keywords, Git commands)
are deliberately left untranslated in both languages, since those are the exact
tokens the student must type.
"""

WEB_SQL_GIT_BLOCKS = {
    # --- Course 2: Web Fundamentals ---
    52: {
        "en": "The web works on a client-server model. Your browser (client) requests a page from a server via HTTP. The server responds with HTML, which the browser renders.",
        "fr": "Le web repose sur un modèle client-serveur. Votre navigateur (le client) demande une page à un serveur via HTTP. Le serveur répond avec du HTML, que le navigateur affiche.",
        "ar": "يقوم الويب على نموذج العميل والخادم. يطلب متصفّحك (العميل) صفحةً من الخادم عبر بروتوكول HTTP، فيردّ الخادم بشيفرة HTML يعرضها المتصفّح.",
    },
    53: {
        "en": "Basic HTML structure:",
        "fr": "Structure HTML de base :",
        "ar": "البنية الأساسية لصفحة HTML:",
    },
    54: {
        "en": "HTML documents have a DOCTYPE, html root, head (metadata), and body (visible content). Tags like h1, p, div structure the content.",
        "fr": "Un document HTML comporte un DOCTYPE, une racine html, un head (métadonnées) et un body (contenu visible). Des balises comme h1, p ou div structurent le contenu.",
        "ar": "يتكوّن مستند HTML من DOCTYPE وجذر html وقسم head للبيانات الوصفية وقسم body للمحتوى المرئي. وتُنظّم وسوم مثل h1 وp وdiv هذا المحتوى.",
    },
    55: {
        "en": "Semantic HTML uses tags that describe their content: header, nav, main, article, section, aside, footer. This improves accessibility and SEO.",
        "fr": "Le HTML sémantique utilise des balises qui décrivent leur contenu : header, nav, main, article, section, aside, footer. Cela améliore l'accessibilité et le référencement.",
        "ar": "تستخدم لغة HTML الدلالية وسومًا تصف محتواها، مثل header وnav وmain وarticle وsection وaside وfooter، وهو ما يحسّن إمكانية الوصول وتحسين محركات البحث.",
    },
    56: {
        "en": "Semantic layout:",
        "fr": "Mise en page sémantique :",
        "ar": "تخطيط دلالي للصفحة:",
    },
    57: {
        "en": "Div and span are generic containers. Prefer semantic tags when they match your content's meaning.",
        "fr": "div et span sont des conteneurs génériques. Préférez les balises sémantiques lorsqu'elles correspondent au sens de votre contenu.",
        "ar": "الوسمان div وspan حاويتان عامّتان. فضّل الوسوم الدلالية كلما كانت مطابقة لمعنى محتواك.",
    },
    58: {
        "en": 'Text: h1-h6 for headings, p for paragraphs, strong/em for emphasis. Links use <a href="url">text</a>. Images use <img src="url" alt="description">.',
        "fr": 'Texte : h1 à h6 pour les titres, p pour les paragraphes, strong et em pour la mise en valeur. Les liens s\'écrivent <a href="url">texte</a>. Les images s\'écrivent <img src="url" alt="description">.',
        "ar": 'النصوص: من h1 إلى h6 للعناوين، وp للفقرات، وstrong وem للتأكيد. وتُكتب الروابط بالصيغة <a href="url">نص</a>، والصور بالصيغة <img src="url" alt="وصف">.',
    },
    59: {
        "en": "Content elements:",
        "fr": "Éléments de contenu :",
        "ar": "عناصر المحتوى:",
    },
    60: {
        "en": "Always include alt text for images (accessibility). Use relative URLs for internal links, absolute for external.",
        "fr": "Renseignez toujours le texte alternatif des images (accessibilité). Utilisez des URL relatives pour les liens internes et absolues pour les liens externes.",
        "ar": "احرص دائمًا على كتابة النص البديل للصور من أجل إمكانية الوصول. واستخدم روابط نسبية للصفحات الداخلية وروابط مطلقة للمواقع الخارجية.",
    },
    61: {
        "en": "Lists: ul (unordered), ol (ordered), li (items). Tables: table, tr (row), th (header), td (cell). Forms: form, input (text, email, password), button, label.",
        "fr": "Listes : ul (non ordonnée), ol (ordonnée), li (éléments). Tableaux : table, tr (ligne), th (en-tête), td (cellule). Formulaires : form, input (text, email, password), button, label.",
        "ar": "القوائم: ul غير المرتّبة، وol المرتّبة، وli للعناصر. الجداول: table وtr للصف وth لخلية العنوان وtd للخلية. النماذج: form وinput بأنواعه text وemail وpassword، إضافةً إلى button وlabel.",
    },
    62: {
        "en": "Lists, tables, forms:",
        "fr": "Listes, tableaux et formulaires :",
        "ar": "القوائم والجداول والنماذج:",
    },
    63: {
        "en": "Forms send data to a server. Each input needs a name attribute. Labels improve accessibility by associating text with inputs.",
        "fr": "Les formulaires envoient des données à un serveur. Chaque champ a besoin d'un attribut name. Les balises label améliorent l'accessibilité en associant un texte à chaque champ.",
        "ar": "ترسل النماذج البيانات إلى الخادم، ويحتاج كل حقل إلى الخاصية name. وتُحسّن وسوم label إمكانية الوصول بربط النص بالحقل المقابل له.",
    },
    64: {
        "en": "CSS (Cascading Style Sheets) styles HTML. A rule has a selector (which element) and declarations (property: value). Can be inline, internal, or external.",
        "fr": "CSS (Cascading Style Sheets) met en forme le HTML. Une règle comporte un sélecteur (quel élément) et des déclarations (propriété : valeur). Le CSS peut être en ligne, interne ou externe.",
        "ar": "تُنسّق لغة CSS مظهر صفحات HTML. وتتكوّن القاعدة من مُحدِّد يبيّن العنصر المستهدف ومن تصريحات على شكل خاصية وقيمة. ويمكن كتابة CSS داخل الوسم أو داخل الصفحة أو في ملف خارجي.",
    },
    65: {
        "en": "CSS syntax:",
        "fr": "Syntaxe CSS :",
        "ar": "صياغة CSS:",
    },
    66: {
        "en": "Selectors: element (h1), class (.classname), id (#idname). Properties: color, background-color, font-size, margin, padding, border. Values: keywords, hex, rgb, pixels, rem, %.",
        "fr": "Sélecteurs : élément (h1), classe (.classname), identifiant (#idname). Propriétés : color, background-color, font-size, margin, padding, border. Valeurs : mots-clés, hexadécimal, rgb, pixels, rem, %.",
        "ar": "المُحدِّدات: بالعنصر مثل h1، أو بالصنف مثل classname.، أو بالمعرّف مثل idname#. الخصائص: color وbackground-color وfont-size وmargin وpadding وborder. القيم: كلمات مفتاحية أو ألوان بالنظام السداسي أو rgb أو وحدات pixels وrem والنسبة المئوية.",
    },
    67: {
        "en": 'Descendant selector (space): div p targets p inside div. Pseudo-classes: :hover, :focus, :first-child. Attribute: input[type="text"]. Box model: margin, border, padding, content.',
        "fr": 'Sélecteur descendant (espace) : div p cible les p situés dans un div. Pseudo-classes : :hover, :focus, :first-child. Attribut : input[type="text"]. Modèle de boîte : margin, border, padding, content.',
        "ar": 'المُحدِّد المتفرّع بمسافة: تستهدف div p كل عنصر p داخل div. الأصناف الزائفة: hover: وfocus: وfirst-child:. والتحديد بالخاصية: ["input[type="text. ونموذج الصندوق يتكوّن من margin وborder وpadding والمحتوى.',
    },
    68: {
        "en": "Advanced selectors and box model:",
        "fr": "Sélecteurs avancés et modèle de boîte :",
        "ar": "المُحدِّدات المتقدّمة ونموذج الصندوق:",
    },
    69: {
        "en": "Total width = width + padding + border + margin. box-sizing: border-box includes padding/border in width.",
        "fr": "Largeur totale = width + padding + border + margin. Avec box-sizing: border-box, le padding et la bordure sont inclus dans la largeur.",
        "ar": "العرض الكلي = width + padding + border + margin. ومع box-sizing: border-box يُحتسب الحشو والحدود ضمن العرض نفسه.",
    },
    70: {
        "en": "Flexbox makes layout easy. Set display: flex on a container. Children become flex items. Control direction, alignment, distribution with properties.",
        "fr": "Flexbox simplifie la mise en page. Appliquez display: flex à un conteneur : ses enfants deviennent des éléments flex. Des propriétés contrôlent la direction, l'alignement et la répartition.",
        "ar": "يُبسّط Flexbox تصميم التخطيط. طبّق display: flex على الحاوية فتتحوّل عناصرها الأبناء إلى عناصر مرنة، وتتحكّم الخصائص في الاتجاه والمحاذاة والتوزيع.",
    },
    71: {
        "en": "Flexbox layout:",
        "fr": "Mise en page avec Flexbox :",
        "ar": "التخطيط باستخدام Flexbox:",
    },
    72: {
        "en": "flex-direction: row (default), column, row-reverse, column-reverse. justify-content: center, space-between, space-around. align-items: center, stretch, flex-start. gap adds spacing between items.",
        "fr": "flex-direction : row (par défaut), column, row-reverse, column-reverse. justify-content : center, space-between, space-around. align-items : center, stretch, flex-start. gap ajoute de l'espace entre les éléments.",
        "ar": "الخاصية flex-direction تقبل row وهي الافتراضية، وcolumn وrow-reverse وcolumn-reverse. والخاصية justify-content تقبل center وspace-between وspace-around. والخاصية align-items تقبل center وstretch وflex-start. أما gap فتضيف مسافة بين العناصر.",
    },
    73: {
        "en": "Responsive design adapts to screen sizes. Viewport meta tag enables mobile scaling. Media queries apply CSS at breakpoints. Mobile-first: base styles for mobile, enhance for larger screens.",
        "fr": "Le design responsive s'adapte à la taille de l'écran. La balise meta viewport active la mise à l'échelle mobile. Les media queries appliquent du CSS à certains points de rupture. Approche mobile-first : styles de base pour mobile, puis enrichissement pour les grands écrans.",
        "ar": "يتكيّف التصميم المتجاوب مع أحجام الشاشات. ويُفعّل وسم meta viewport ضبط المقياس على الهواتف، بينما تُطبّق استعلامات الوسائط قواعد CSS عند نقاط توقّف محدّدة. وفي نهج الهاتف أولًا تُكتب الأنماط الأساسية للهاتف ثم تُحسَّن للشاشات الأكبر.",
    },
    74: {
        "en": "Responsive basics:",
        "fr": "Bases du responsive :",
        "ar": "أساسيات التصميم المتجاوب:",
    },
    75: {
        "en": "Common breakpoints: 480px (mobile), 768px (tablet), 1024px (desktop), 1200px (large). Use relative units (%, rem, em) for fluid layouts.",
        "fr": "Points de rupture courants : 480px (mobile), 768px (tablette), 1024px (ordinateur), 1200px (grand écran). Utilisez des unités relatives (%, rem, em) pour des mises en page fluides.",
        "ar": "نقاط التوقّف الشائعة: 480px للهاتف، و768px للّوحي، و1024px للحاسوب المكتبي، و1200px للشاشات الكبيرة. واستخدم وحدات نسبية مثل % وrem وem للحصول على تخطيط مرن.",
    },

    # --- Course 3: SQL & Databases ---
    76: {
        "en": "A database stores data in tables. Tables have rows (records) and columns (fields). Each table should have a primary key - a unique identifier for each row. Foreign keys link tables together.",
        "fr": "Une base de données stocke les données dans des tables. Une table possède des lignes (enregistrements) et des colonnes (champs). Chaque table doit avoir une clé primaire, identifiant unique de chaque ligne. Les clés étrangères relient les tables entre elles.",
        "ar": "تُخزّن قاعدة البيانات بياناتها في جداول، ويتكوّن الجدول من صفوف تمثّل السجلات ومن أعمدة تمثّل الحقول. وينبغي أن يكون لكل جدول مفتاح أساسي يميّز كل صف تمييزًا فريدًا، بينما تربط المفاتيح الأجنبية الجداول ببعضها.",
    },
    77: {
        "en": "Conceptual table structure:",
        "fr": "Structure conceptuelle d'une table :",
        "ar": "البنية المفاهيمية للجدول:",
    },
    78: {
        "en": "PK = Primary Key (unique, not null). FK = Foreign Key (references another table's PK). Relationships: one-to-many, many-to-many.",
        "fr": "PK = clé primaire (unique, non nulle). FK = clé étrangère (référence la clé primaire d'une autre table). Relations : un-à-plusieurs, plusieurs-à-plusieurs.",
        "ar": "يرمز PK إلى المفتاح الأساسي وهو فريد ولا يقبل القيمة الفارغة، ويرمز FK إلى المفتاح الأجنبي الذي يشير إلى المفتاح الأساسي في جدول آخر. والعلاقات نوعان: واحد إلى متعدّد، ومتعدّد إلى متعدّد.",
    },
    79: {
        "en": "SELECT retrieves data. SELECT column FROM table. Use * for all columns. WHERE filters rows. AND/OR combine conditions. IN checks multiple values. LIKE uses % (any chars) and _ (single char) wildcards.",
        "fr": "SELECT récupère des données : SELECT colonne FROM table. Utilisez * pour toutes les colonnes. WHERE filtre les lignes. AND/OR combinent des conditions. IN teste plusieurs valeurs. LIKE utilise les jokers % (n'importe quels caractères) et _ (un seul caractère).",
        "ar": "تسترجع SELECT البيانات بالصيغة SELECT colonne FROM table، ويُستخدم * لجلب كل الأعمدة. وتُصفّي WHERE الصفوف، ويجمع AND وOR بين الشروط، ويتحقّق IN من عدة قيم، ويستعمل LIKE الرمزين % لأي عدد من المحارف و_ لمحرف واحد.",
    },
    80: {
        "en": "SELECT examples:",
        "fr": "Exemples de SELECT :",
        "ar": "أمثلة على SELECT:",
    },
    81: {
        "en": "String comparisons are case-sensitive in some databases. Use ILIKE for case-insensitive (PostgreSQL). Always quote string values.",
        "fr": "Dans certaines bases, la comparaison de chaînes distingue les majuscules des minuscules. Utilisez ILIKE pour ignorer la casse (PostgreSQL). Mettez toujours les chaînes entre guillemets simples.",
        "ar": "تُفرّق بعض قواعد البيانات بين الحروف الكبيرة والصغيرة عند مقارنة النصوص. استخدم ILIKE لتجاهل حالة الأحرف في PostgreSQL، واحرص دائمًا على وضع القيم النصية بين علامتَي اقتباس.",
    },
    82: {
        "en": "INSERT adds rows: INSERT INTO table (col1, col2) VALUES (val1, val2). UPDATE changes existing: UPDATE table SET col = val WHERE condition. DELETE removes: DELETE FROM table WHERE condition. Always use WHERE with UPDATE/DELETE!",
        "fr": "INSERT ajoute des lignes : INSERT INTO table (col1, col2) VALUES (val1, val2). UPDATE modifie l'existant : UPDATE table SET col = val WHERE condition. DELETE supprime : DELETE FROM table WHERE condition. Utilisez toujours WHERE avec UPDATE et DELETE !",
        "ar": "تضيف INSERT صفوفًا بالصيغة INSERT INTO table (col1, col2) VALUES (val1, val2)، وتُعدّل UPDATE القائم بالصيغة UPDATE table SET col = val WHERE condition، وتحذف DELETE بالصيغة DELETE FROM table WHERE condition. واستخدم دائمًا WHERE مع UPDATE وDELETE!",
    },
    83: {
        "en": "Data modification:",
        "fr": "Modification des données :",
        "ar": "تعديل البيانات:",
    },
    84: {
        "en": "Without WHERE, UPDATE/DELETE affects ALL rows. Use transactions (BEGIN, COMMIT, ROLLBACK) for multiple related changes.",
        "fr": "Sans WHERE, UPDATE et DELETE touchent TOUTES les lignes. Utilisez des transactions (BEGIN, COMMIT, ROLLBACK) pour un ensemble de modifications liées.",
        "ar": "من دون WHERE تؤثّر UPDATE وDELETE في جميع الصفوف. واستخدم المعاملات عبر BEGIN وCOMMIT وROLLBACK عند إجراء عدة تعديلات مترابطة.",
    },
    85: {
        "en": "ORDER BY sorts results: ASC (default) or DESC. GROUP BY aggregates rows with same values. COUNT(), SUM(), AVG(), MIN(), MAX() compute summaries. HAVING filters groups (like WHERE for groups).",
        "fr": "ORDER BY trie les résultats : ASC (par défaut) ou DESC. GROUP BY regroupe les lignes de même valeur. COUNT(), SUM(), AVG(), MIN() et MAX() calculent des synthèses. HAVING filtre les groupes (comme WHERE, mais pour les groupes).",
        "ar": "ترتّب ORDER BY النتائج تصاعديًا بـ ASC وهو الافتراضي أو تنازليًا بـ DESC. وتجمّع GROUP BY الصفوف المتشابهة في القيمة، وتحسب الدوال ()COUNT و()SUM و()AVG و()MIN و()MAX ملخّصات، بينما تُصفّي HAVING المجموعات كما تُصفّي WHERE الصفوف.",
    },
    86: {
        "en": "Aggregation:",
        "fr": "Agrégation :",
        "ar": "التجميع والدوال التجميعية:",
    },
    87: {
        "en": "Columns in SELECT with GROUP BY must be either grouped or aggregated. HAVING runs after GROUP BY, WHERE runs before.",
        "fr": "Avec GROUP BY, les colonnes du SELECT doivent être soit regroupées, soit agrégées. HAVING s'applique après GROUP BY, tandis que WHERE s'applique avant.",
        "ar": "عند استخدام GROUP BY يجب أن يكون كل عمود في SELECT إمّا ضمن التجميع وإمّا داخل دالة تجميعية. وتُنفَّذ HAVING بعد GROUP BY، بينما تُنفَّذ WHERE قبلها.",
    },
    88: {
        "en": "JOINs combine rows from two tables based on a related column. INNER JOIN returns matches only. LEFT JOIN returns all from left table, matches from right. RIGHT JOIN opposite. FULL JOIN returns all from both.",
        "fr": "Les JOIN combinent les lignes de deux tables à partir d'une colonne commune. INNER JOIN ne renvoie que les correspondances. LEFT JOIN renvoie toutes les lignes de la table de gauche et les correspondances de droite. RIGHT JOIN fait l'inverse. FULL JOIN renvoie tout des deux côtés.",
        "ar": "تجمع عمليات JOIN صفوفًا من جدولين اعتمادًا على عمود مشترك. تُرجع INNER JOIN الصفوف المتطابقة فقط، وتُرجع LEFT JOIN كل صفوف الجدول الأيسر مع ما يطابقها من الأيمن، وتفعل RIGHT JOIN العكس، بينما تُرجع FULL JOIN كل الصفوف من الجدولين.",
    },
    89: {
        "en": "JOIN examples:",
        "fr": "Exemples de JOIN :",
        "ar": "أمثلة على JOIN:",
    },
    90: {
        "en": "Use aliases (s, e, c) for shorter queries. JOIN condition goes in ON clause. Think: what data do I need from both tables?",
        "fr": "Utilisez des alias (s, e, c) pour raccourcir vos requêtes. La condition de jointure se place dans la clause ON. Demandez-vous : de quelles données ai-je besoin dans chacune des deux tables ?",
        "ar": "استخدم أسماءً مختصرة مثل s وe وc لتقصير الاستعلامات. ويُكتب شرط الربط داخل عبارة ON. واسأل نفسك دائمًا: ما البيانات التي أحتاجها من كل من الجدولين؟",
    },

    # --- Course 4: Git & GitHub ---
    91: {
        "en": "Version control tracks changes to files over time. Git is a distributed version control system. Every developer has a full copy of the repository. Key concepts: repository, commit, staging area, working directory.",
        "fr": "La gestion de versions suit l'évolution des fichiers dans le temps. Git est un système de gestion de versions distribué : chaque développeur possède une copie complète du dépôt. Notions clés : dépôt, commit, zone de préparation (staging), répertoire de travail.",
        "ar": "يتتبّع نظام إدارة الإصدارات التغييرات التي تطرأ على الملفات عبر الزمن. وGit نظام موزّع لإدارة الإصدارات، إذ يملك كل مطوّر نسخة كاملة من المستودع. ومفاهيمه الأساسية هي: المستودع، والالتزام (commit)، ومنطقة التجهيز، ومجلّد العمل.",
    },
    92: {
        "en": "Basic Git workflow:",
        "fr": "Flux de travail Git de base :",
        "ar": "سير العمل الأساسي في Git:",
    },
    93: {
        "en": "git init creates a new repo. git add stages changes. git commit saves a snapshot. Commits should be atomic (one logical change) with clear messages.",
        "fr": "git init crée un nouveau dépôt. git add prépare les modifications. git commit enregistre un instantané. Un commit doit être atomique (une seule modification logique) et accompagné d'un message clair.",
        "ar": "ينشئ git init مستودعًا جديدًا، ويُجهّز git add التغييرات، ويحفظ git commit لقطةً منها. وينبغي أن يكون كل التزام ذرّيًا يمثّل تغييرًا منطقيًا واحدًا مع رسالة واضحة.",
    },
    94: {
        "en": 'git log shows commit history. git diff shows changes between commits or working directory. Good commit messages: short summary (50 chars), blank line, detailed explanation if needed. Use imperative mood: "Add feature" not "Added feature".',
        "fr": 'git log affiche l\'historique des commits. git diff montre les différences entre commits ou avec le répertoire de travail. Un bon message de commit : résumé court (50 caractères), ligne vide, puis explication détaillée si nécessaire. Employez l\'impératif : "Add feature" plutôt que "Added feature".',
        "ar": 'يعرض git log سجلّ الالتزامات، ويُظهر git diff الفروق بين الالتزامات أو مقارنةً بمجلّد العمل. ورسالة الالتزام الجيدة تبدأ بملخّص قصير في حدود 50 محرفًا، يليه سطر فارغ ثم شرح مفصّل عند الحاجة. واستخدم صيغة الأمر: "Add feature" لا "Added feature".',
    },
    95: {
        "en": "History commands:",
        "fr": "Commandes d'historique :",
        "ar": "أوامر استعراض السجلّ:",
    },
    96: {
        "en": "HEAD is the current commit. HEAD~1 is parent. Use git log --oneline --graph for visual history. Write meaningful messages for your future self.",
        "fr": "HEAD désigne le commit courant, HEAD~1 son parent. Utilisez git log --oneline --graph pour visualiser l'historique. Rédigez des messages utiles pour vous-même dans six mois.",
        "ar": "يشير HEAD إلى الالتزام الحالي، بينما يشير HEAD~1 إلى الالتزام الأب. واستخدم git log --oneline --graph لعرض السجلّ بصريًا. واكتب رسائل ذات معنى تنفعك أنت مستقبلًا.",
    },
    97: {
        "en": "Branches let you work on features without affecting main. git branch creates, git checkout (or git switch) switches. Merge combines branches. Conflicts happen when same lines changed differently - resolve manually.",
        "fr": "Les branches permettent de développer des fonctionnalités sans toucher à main. git branch en crée une, git checkout (ou git switch) en change. La fusion combine les branches. Un conflit survient quand les mêmes lignes ont été modifiées différemment : il faut le résoudre à la main.",
        "ar": "تتيح لك الفروع العمل على ميزات جديدة من دون المساس بالفرع main. ينشئ git branch فرعًا، وينتقل git checkout أو git switch بينها، ويدمج الأمر merge الفروع. ويقع التعارض عندما تُعدَّل الأسطر نفسها بطرق مختلفة، فيلزم حلّه يدويًا.",
    },
    98: {
        "en": "Branch workflow:",
        "fr": "Flux de travail avec les branches :",
        "ar": "سير العمل باستخدام الفروع:",
    },
    99: {
        "en": "Fast-forward merge when no new commits on main. Merge commit when both branches have new commits. Resolve conflicts by editing files, then git add and git commit.",
        "fr": "Fusion en avance rapide (fast-forward) quand main n'a pas de nouveaux commits ; commit de fusion quand les deux branches en ont. Résolvez les conflits en éditant les fichiers, puis git add et git commit.",
        "ar": "يحدث الدمج السريع (fast-forward) عندما لا يحتوي main على التزامات جديدة، أما إذا كان في الفرعين التزامات جديدة فيُنشأ التزام دمج. وتُحلّ التعارضات بتحرير الملفات ثم تنفيذ git add و git commit.",
    },
    100: {
        "en": "Remote repositories (like GitHub) enable collaboration. git remote add origin <url> links local to remote. git push sends commits. git pull fetches and merges. git clone copies a remote repo locally.",
        "fr": "Les dépôts distants (comme GitHub) rendent la collaboration possible. git remote add origin <url> relie le dépôt local au distant. git push envoie les commits, git pull les récupère et les fusionne, git clone copie un dépôt distant en local.",
        "ar": "تتيح المستودعات البعيدة مثل GitHub العمل التعاوني. يربط الأمر git remote add origin <url> المستودع المحلي بالبعيد، ويرسل git push الالتزامات، ويجلب git pull التغييرات ويدمجها، بينما ينسخ git clone مستودعًا بعيدًا إلى جهازك.",
    },
    101: {
        "en": "Remote workflow:",
        "fr": "Flux de travail avec un dépôt distant :",
        "ar": "سير العمل مع المستودع البعيد:",
    },
    102: {
        "en": "origin is the default remote name. -u sets upstream tracking. SSH or HTTPS for authentication. GitHub provides web interface for issues, PRs, actions.",
        "fr": "origin est le nom par défaut du dépôt distant. L'option -u définit le suivi de branche amont. L'authentification se fait en SSH ou HTTPS. GitHub fournit une interface web pour les issues, les pull requests et les actions.",
        "ar": "الاسم origin هو الاسم الافتراضي للمستودع البعيد، ويحدّد الخيار u- تتبّع الفرع البعيد. وتتم المصادقة عبر SSH أو HTTPS. ويوفّر GitHub واجهة ويب للمسائل وطلبات الدمج والإجراءات الآلية.",
    },
    103: {
        "en": "Pull Requests (PRs) propose changes for review. Fork -> clone -> branch -> commit -> push -> PR. Reviewers comment, approve, request changes. Merge on GitHub (merge, squash, rebase). Issues track bugs/features.",
        "fr": "Les pull requests (PR) proposent des modifications à relire. Fork -> clone -> branche -> commit -> push -> PR. Les relecteurs commentent, approuvent ou demandent des changements. La fusion se fait sur GitHub (merge, squash, rebase). Les issues assurent le suivi des bugs et des fonctionnalités.",
        "ar": "تقترح طلبات الدمج (PR) تغييرات لمراجعتها، ومسارها: fork ثم clone ثم إنشاء فرع ثم commit ثم push ثم فتح الطلب. ويعلّق المراجعون أو يوافقون أو يطلبون تعديلات، ثم يتم الدمج على GitHub بأسلوب merge أو squash أو rebase. أما المسائل (issues) فتتابع الأخطاء والميزات.",
    },
    104: {
        "en": "PR workflow:",
        "fr": "Flux de travail d'une pull request :",
        "ar": "سير العمل في طلب الدمج:",
    },
    105: {
        "en": "Keep PRs small and focused. Write clear descriptions. Respond to reviews promptly. Delete branch after merge. GitHub Actions can run tests automatically on PRs.",
        "fr": "Gardez des pull requests courtes et ciblées. Rédigez des descriptions claires. Répondez rapidement aux relectures. Supprimez la branche après la fusion. GitHub Actions peut lancer les tests automatiquement sur chaque PR.",
        "ar": "اجعل طلبات الدمج صغيرة ومركّزة، واكتب وصفًا واضحًا لها، وردّ سريعًا على ملاحظات المراجعين، واحذف الفرع بعد الدمج. ويمكن لـ GitHub Actions تشغيل الاختبارات تلقائيًا على كل طلب دمج.",
    },
}
