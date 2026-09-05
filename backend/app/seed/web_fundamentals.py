from .base import (
    get_or_create_course, get_or_create_module, get_or_create_lesson,
    LanguageEnum, DifficultyEnum, ExerciseTypeEnum
)
from .microquest_content import seed_blocks


async def seed_web_fundamentals(db):
    print("Seeding Web Fundamentals...")
    
    course_id = await get_or_create_course(db, "web-basics", 2, [
        {"language": LanguageEnum.en, "title": "Web Fundamentals", "description": "Build websites with HTML and CSS", "skills": "HTML, CSS, Responsive Design"},
        {"language": LanguageEnum.fr, "title": "Bases du Web", "description": "Construisez des sites web avec HTML et CSS", "skills": "HTML, CSS, Design Responsive"},
        {"language": LanguageEnum.ar, "title": "أساسيات الويب", "description": "ابنِ مواقع ويب مع HTML و CSS", "skills": "HTML، CSS، التصميم المتجاوب"},
    ])
    
    # Module 1: HTML Basics
    module1_id = await get_or_create_module(db, course_id, "html-basics", 1, [
        {"language": LanguageEnum.en, "title": "HTML Basics", "description": "Learn the structure and semantics of web pages"},
        {"language": LanguageEnum.fr, "title": "Bases HTML", "description": "Apprenez la structure et la sémantique des pages web"},
        {"language": LanguageEnum.ar, "title": "أساسيات HTML", "description": "تعلم هيكل ودلالات صفحات الويب"},
    ])
    
    # Lesson 17: How the Web Works
    await get_or_create_lesson(db, module1_id, "how-web-works", 1,
        DifficultyEnum.beginner, 30, 50,
        [
            {"language": LanguageEnum.en, "title": "How the Web Works", "story": "Understand what happens when you visit a website", "objective": "Explain clients, servers, HTTP, and HTML", "skills": "Web architecture, HTTP, clients, servers"},
            {"language": LanguageEnum.fr, "title": "Comment Fonctionne le Web", "story": "Comprenez ce qui se passe quand vous visitez un site web", "objective": "Expliquer clients, serveurs, HTTP et HTML", "skills": "Architecture web, HTTP, clients, serveurs"},
            {"language": LanguageEnum.ar, "title": "كيف يعمل الويب", "story": "افهم ما يحدث عند زيارة موقع ويب", "objective": "شرح العملاء، الخوادم، HTTP، و HTML", "skills": "هندسة الويب، HTTP، العملاء، الخوادم"},
        ],
        [
            {"type": "text", "order": 1, "content": "The web works on a client-server model. Your browser (client) requests a page from a server via HTTP. The server responds with HTML, which the browser renders."},
            {"type": "code", "order": 2, "content": "Basic HTML structure:", "code_example": '<!DOCTYPE html>\n<html>\n<head>\n    <title>My Page</title>\n</head>\n<body>\n    <h1>Hello, MoroccoCode!</h1>\n    <p>Welcome to the web.</p>\n</body>\n</html>'},
            {"type": "text", "order": 3, "content": "HTML documents have a DOCTYPE, html root, head (metadata), and body (visible content). Tags like h1, p, div structure the content."},
            # Micro-Quest blocks (hook 0, blueprint 4, exam_tip 5). The blueprint
            # is the order_steps interaction. Lessons without these render as before.
            *seed_blocks("how-web-works"),
        ],
        [
            {
                "type": ExerciseTypeEnum.multiple_choice,
                "order": 1,
                "xp_reward": 10,
                "starter_code": "",
                "solution_code": "",
                "validation_config": "",
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "What does a browser (client) do in the web model?", "hint": "It requests and displays pages", "explanation": "The browser requests pages from servers via HTTP and renders the HTML response for the user."},
                    {"language": LanguageEnum.fr, "prompt": "Que fait un navigateur (client) dans le modèle web ?", "hint": "Il demande et affiche les pages", "explanation": "Le navigateur demande les pages aux serveurs via HTTP et rend la réponse HTML pour l'utilisateur."},
                    {"language": LanguageEnum.ar, "prompt": "ماذا يفعل المتصفح (العميل) في نموذج الويب؟", "hint": "يطلب ويعرض الصفحات", "explanation": "المتصفح يطلب الصفحات من الخوادم عبر HTTP ويعرض استجابة HTML للمستخدم."},
                ],
                "options": [
                    {"order": 1, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "Stores all website data"}, {"language": LanguageEnum.fr, "text": "Stocke toutes les données du site"}, {"language": LanguageEnum.ar, "text": "يخزن جميع بيانات الموقع"}]},
                    {"order": 2, "is_correct": True, "translations": [{"language": LanguageEnum.en, "text": "Requests and displays web pages"}, {"language": LanguageEnum.fr, "text": "Demande et affiche les pages web"}, {"language": LanguageEnum.ar, "text": "يطلب ويعرض صفحات الويب"}]},
                    {"order": 3, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "Writes the HTML code"}, {"language": LanguageEnum.fr, "text": "Écrit le code HTML"}, {"language": LanguageEnum.ar, "text": "يكتب كود HTML"}]},
                    {"order": 4, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "Manages the database"}, {"language": LanguageEnum.fr, "text": "Gère la base de données"}, {"language": LanguageEnum.ar, "text": "يدير قاعدة البيانات"}]},
                ]
            }
        ]
    )
    
    # Lesson 18: HTML Structure
    await get_or_create_lesson(db, module1_id, "html-structure", 2,
        DifficultyEnum.beginner, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "HTML Structure", "story": "Master the building blocks of HTML documents", "objective": "Use semantic HTML tags correctly", "skills": "HTML tags, semantic elements, document structure"},
            {"language": LanguageEnum.fr, "title": "Structure HTML", "story": "Maîtrisez les blocs de construction des documents HTML", "objective": "Utiliser les balises HTML sémantiques correctement", "skills": "Balises HTML, éléments sémantiques, structure du document"},
            {"language": LanguageEnum.ar, "title": "هيكل HTML", "story": "أتقن اللبنات الأساسية لمستندات HTML", "objective": "استخدام علامات HTML الدلالية بشكل صحيح", "skills": "علامات HTML، عناصر دلالية، هيكل المستند"},
        ],
        [
            {"type": "text", "order": 1, "content": "Semantic HTML uses tags that describe their content: header, nav, main, article, section, aside, footer. This improves accessibility and SEO."},
            {"type": "code", "order": 2, "content": "Semantic layout:", "code_example": '<body>\n    <header>\n        <h1>Site Title</h1>\n        <nav>Navigation links</nav>\n    </header>\n    <main>\n        <article>Main content</article>\n        <aside>Sidebar</aside>\n    </main>\n    <footer>Footer info</footer>\n</body>'},
            {"type": "text", "order": 3, "content": "Div and span are generic containers. Prefer semantic tags when they match your content's meaning."},
        ],
        [
            {
                "type": ExerciseTypeEnum.code_writing,
                "order": 1,
                "xp_reward": 10,
                "starter_code": '<!DOCTYPE html>\n<html>\n<head>\n    <title>My Page</title>\n</head>\n<body>\n    <____>\n        <h1>MoroccoCode</h1>\n    </____>\n    <____>\n        <p>Main content goes here</p>\n    </____>\n    <____>\n        <p>&copy; 2025</p>\n    </____>\n</body>\n</html>',
                "solution_code": '<!DOCTYPE html>\n<html>\n<head>\n    <title>My Page</title>\n</head>\n<body>\n    <header>\n        <h1>MoroccoCode</h1>\n    </header>\n    <main>\n        <p>Main content goes here</p>\n    </main>\n    <footer>\n        <p>&copy; 2025</p>\n    </footer>\n</body>\n</html>',
                # Graded by keywords, not the Python sandbox: this answer is not Python.
                "validation_config": '{"expected_keywords": ["<header>", "<main>", "<footer>"]}',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Complete the HTML using semantic tags: header, main, footer.", "hint": "Header for top, main for content, footer for bottom", "explanation": "Semantic tags give meaning to document structure: header, main, footer."},
                    {"language": LanguageEnum.fr, "prompt": "Complétez le HTML avec des balises sémantiques : header, main, footer.", "hint": "Header pour le haut, main pour le contenu, footer pour le bas", "explanation": "Les balises sémantiques donnent du sens à la structure : header, main, footer."},
                    {"language": LanguageEnum.ar, "prompt": "أكمل HTML باستخدام علامات دلالية: header، main، footer.", "hint": "Header للأعلى، main للمحتوى، footer للأسفل", "explanation": "العلامات الدلالية تعطي معنى لهيكل المستند: header، main، footer."},
                ]
            }
        ]
    )
    
    # Lesson 19: Text, Links and Images
    await get_or_create_lesson(db, module1_id, "text-links-images", 3,
        DifficultyEnum.beginner, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "Text, Links and Images", "story": "Add content and navigation to your web pages", "objective": "Use text formatting, links, and images correctly", "skills": "Text tags, anchor tags, image tags, attributes"},
            {"language": LanguageEnum.fr, "title": "Texte, Liens et Images", "story": "Ajoutez du contenu et de la navigation à vos pages web", "objective": "Utiliser le formatage de texte, liens et images correctement", "skills": "Balises texte, ancres, images, attributs"},
            {"language": LanguageEnum.ar, "title": "النصوص والروابط والصور", "story": "أضف محتوى وتنقل لصفحات الويب الخاصة بك", "objective": "استخدام تنسيق النصوص والروابط والصور بشكل صحيح", "skills": "علامات النص، الروابط، الصور، السمات"},
        ],
        [
            {"type": "text", "order": 1, "content": "Text: h1-h6 for headings, p for paragraphs, strong/em for emphasis. Links use <a href=\"url\">text</a>. Images use <img src=\"url\" alt=\"description\">."},
            {"type": "code", "order": 2, "content": "Content elements:", "code_example": '<h1>Main Heading</h1>\n<p>This is a <strong>bold</strong> and <em>italic</em> paragraph.</p>\n<a href="https://moroccocode.com">Visit MoroccoCode</a>\n<img src="logo.png" alt="MoroccoCode Logo">'},
            {"type": "text", "order": 3, "content": "Always include alt text for images (accessibility). Use relative URLs for internal links, absolute for external."},
        ],
        [
            {
                "type": ExerciseTypeEnum.fill_blank,
                "order": 1,
                "xp_reward": 10,
                "starter_code": '<h1>Welcome</h1>\n<p>Learn <____>web development</____> with MoroccoCode.</p>\n<a ____="https://moroccocode.com">Visit</a>\n<img ____="logo.png" ____="Logo">',
                "solution_code": '<h1>Welcome</h1>\n<p>Learn <strong>web development</strong> with MoroccoCode.</p>\n<a href="https://moroccocode.com">Visit</a>\n<img src="logo.png" alt="Logo">',
                "validation_config": '{"blanks": [{"answer": "strong"}, {"answer": "strong"}, {"answer": "href"}, {"answer": "src"}, {"answer": "alt"}]}',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Fill in the tags and attributes: strong for bold, href for links, src/alt for images.", "hint": "strong=bold, href=link URL, src=image source, alt=description", "explanation": "HTML attributes provide additional information: href for links, src/alt for images."},
                    {"language": LanguageEnum.fr, "prompt": "Remplissez les balises et attributs : strong pour gras, href pour liens, src/alt pour images.", "hint": "strong=gras, href=URL lien, src=source image, alt=description", "explanation": "Les attributs HTML donnent des infos supplémentaires : href pour liens, src/alt pour images."},
                    {"language": LanguageEnum.ar, "prompt": "املأ العلامات والسمات: strong للعريض، href للروابط، src/alt للصور.", "hint": "strong=عريض، href=رابط، src=مصدر الصورة، alt=وصف", "explanation": "سمات HTML توفر معلومات إضافية: href للروابط، src/alt للصور."},
                ]
            }
        ]
    )
    
    # Lesson 20: Lists, Tables and Forms
    await get_or_create_lesson(db, module1_id, "lists-tables-forms", 4,
        DifficultyEnum.beginner, 40, 50,
        [
            {"language": LanguageEnum.en, "title": "Lists, Tables and Forms", "story": "Organize data and collect user input", "objective": "Create lists, tables, and basic forms", "skills": "ul/ol, table, form, input, button"},
            {"language": LanguageEnum.fr, "title": "Listes, Tableaux et Formulaires", "story": "Organisez les données et collectez les entrées utilisateur", "objective": "Créer des listes, tableaux et formulaires de base", "skills": "ul/ol, table, form, input, button"},
            {"language": LanguageEnum.ar, "title": "القوائم والجداول والنماذج", "story": "نظم البيانات واجمع مدخلات المستخدم", "objective": "إنشاء قوائم، جداول، ونماذج أساسية", "skills": "ul/ol، table، form، input، button"},
        ],
        [
            {"type": "text", "order": 1, "content": "Lists: ul (unordered), ol (ordered), li (items). Tables: table, tr (row), th (header), td (cell). Forms: form, input (text, email, password), button, label."},
            {"type": "code", "order": 2, "content": "Lists, tables, forms:", "code_example": '<ul>\n    <li>HTML</li>\n    <li>CSS</li>\n</ul>\n\n<table>\n    <tr><th>Name</th><th>Role</th></tr>\n    <tr><td>Youssef</td><td>Student</td></tr>\n</table>\n\n<form>\n    <label>Email: <input type="email" name="email"></label>\n    <button type="submit">Submit</button>\n</form>'},
            {"type": "text", "order": 3, "content": "Forms send data to a server. Each input needs a name attribute. Labels improve accessibility by associating text with inputs."},
        ],
        [
            {
                "type": ExerciseTypeEnum.code_writing,
                "order": 1,
                "xp_reward": 10,
                "starter_code": '<form>\n    <label>Name: <input type="____" name="name"></label><br>\n    <label>Email: <input type="____" name="email"></label><br>\n    <button type="____">Subscribe</button>\n</form>',
                "solution_code": '<form>\n    <label>Name: <input type="text" name="name"></label><br>\n    <label>Email: <input type="email" name="email"></label><br>\n    <button type="submit">Subscribe</button>\n</form>',
                # Graded by keywords, not the Python sandbox: this answer is not Python.
                "validation_config": '{"expected_keywords": ["type=\\"text\\"", "type=\\"email\\"", "type=\\"submit\\""]}',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Complete the form with correct input types and button type.", "hint": "text for name, email for email, submit for button", "explanation": "Input types: text, email, password. Button type submit sends form data."},
                    {"language": LanguageEnum.fr, "prompt": "Complétez le formulaire avec les bons types d'input et type de bouton.", "hint": "text pour nom, email pour email, submit pour bouton", "explanation": "Types d'input : text, email, password. Type submit du bouton envoie le formulaire."},
                    {"language": LanguageEnum.ar, "prompt": "أكمل النموذج بأنواع input الصحيحة ونوع الزر.", "hint": "text للاسم، email للإيميل، submit للزر", "explanation": "أنواع input: text، email، password. نوع الزر submit يرسل بيانات النموذج."},
                ]
            }
        ]
    )
    
    # Module 2: CSS Basics
    module2_id = await get_or_create_module(db, course_id, "css-basics", 2, [
        {"language": LanguageEnum.en, "title": "CSS Basics", "description": "Style your web pages with Cascading Style Sheets"},
        {"language": LanguageEnum.fr, "title": "Bases CSS", "description": "Mettez en forme vos pages web avec les Feuilles de Style en Cascade"},
        {"language": LanguageEnum.ar, "title": "أساسيات CSS", "description": "صمم صفحات الويب الخاصة بك مع أوراق الأنماط المتتالية"},
    ])
    
    # Lesson 21: CSS Fundamentals
    await get_or_create_lesson(db, module2_id, "css-fundamentals", 1,
        DifficultyEnum.beginner, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "CSS Fundamentals", "story": "Learn how to style HTML elements with CSS", "objective": "Write CSS rules with selectors, properties, and values", "skills": "CSS syntax, selectors, properties, values, colors"},
            {"language": LanguageEnum.fr, "title": "Fondamentaux CSS", "story": "Apprenez à styliser les éléments HTML avec CSS", "objective": "Écrire des règles CSS avec sélecteurs, propriétés et valeurs", "skills": "Syntaxe CSS, sélecteurs, propriétés, valeurs, couleurs"},
            {"language": LanguageEnum.ar, "title": "أساسيات CSS", "story": "تعلم كيف تصمم عناصر HTML مع CSS", "objective": "كتابة قواعد CSS مع المحددات، الخصائص، والقيم", "skills": "بناء CSS، المحددات، الخصائص، القيم، الألوان"},
        ],
        [
            {"type": "text", "order": 1, "content": "CSS (Cascading Style Sheets) styles HTML. A rule has a selector (which element) and declarations (property: value). Can be inline, internal, or external."},
            {"type": "code", "order": 2, "content": "CSS syntax:", "code_example": '/* External CSS file: styles.css */\nh1 {\n    color: #2c3e50;\n    font-family: Arial, sans-serif;\n    text-align: center;\n}\n\n.highlight {\n    background-color: #f39c12;\n    padding: 10px;\n}'},
            {"type": "text", "order": 3, "content": "Selectors: element (h1), class (.classname), id (#idname). Properties: color, background-color, font-size, margin, padding, border. Values: keywords, hex, rgb, pixels, rem, %."},
        ],
        [
            {
                "type": ExerciseTypeEnum.prediction,
                "order": 1,
                "xp_reward": 10,
                "starter_code": '<style>\n    .highlight { color: red; font-weight: bold; }\n    #special { font-size: 24px; }\n</style>\n<h1 class="highlight">Title</h1>\n<p id="special" class="highlight">Paragraph</p>',
                "solution_code": "Title (red, bold)\nParagraph (red, bold, 24px)",
                "validation_config": '{"expected_output": "Title (red, bold)\\nParagraph (red, bold, 24px)"}',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "What styles apply to each element? Classes can be reused, IDs are unique.", "hint": "Both have .highlight, paragraph also has #special", "explanation": "Classes apply to multiple elements. IDs are unique. Multiple classes can apply to one element."},
                    {"language": LanguageEnum.fr, "prompt": "Quels styles s'appliquent à chaque élément ? Les classes sont réutilisables, les IDs uniques.", "hint": "Les deux ont .highlight, le paragraphe a aussi #special", "explanation": "Les classes s'appliquent à plusieurs éléments. Les IDs sont uniques. Plusieurs classes peuvent s'appliquer à un élément."},
                    {"language": LanguageEnum.ar, "prompt": "ما هي الأنماط التي تنطبق على كل عنصر؟ يمكن إعادة استخدام الـ classes، الـ IDs فريدة.", "hint": "كلاهما لهما .highlight، الفقرة لديها أيضاً #special", "explanation": "يمكن تطبيق الـ classes على عدة عناصر. الـ IDs فريدة. يمكن تطبيق عدة classes على عنصر واحد."},
                ]
            }
        ]
    )
    
    # Lesson 22: Selectors and Properties
    await get_or_create_lesson(db, module2_id, "selectors-properties", 2,
        DifficultyEnum.beginner, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "Selectors and Properties", "story": "Target elements precisely and style them effectively", "objective": "Use descendant, pseudo-class, and attribute selectors", "skills": "Descendant selectors, pseudo-classes, attribute selectors, box model"},
            {"language": LanguageEnum.fr, "title": "Sélecteurs et Propriétés", "story": "Ciblez les éléments précisément et stylisez-les efficacement", "objective": "Utiliser les sélecteurs descendants, pseudo-classes et attributs", "skills": "Sélecteurs descendants, pseudo-classes, sélecteurs d'attributs, modèle de boîte"},
            {"language": LanguageEnum.ar, "title": "المحددات والخصائص", "story": "استهدف العناصر بدقة وصممها بفعالية", "objective": "استخدام المحددات النسبية، الفئات الوهمية، ومحددات السمات", "skills": "المحدودات النسبية، الفئات الوهمية، محددات السمات، نموذج الصندوق"},
        ],
        [
            {"type": "text", "order": 1, "content": "Descendant selector (space): div p targets p inside div. Pseudo-classes: :hover, :focus, :first-child. Attribute: input[type=\"text\"]. Box model: margin, border, padding, content."},
            {"type": "code", "order": 2, "content": "Advanced selectors and box model:", "code_example": '/* Box model */\n.box {\n    width: 300px;\n    padding: 20px;\n    border: 2px solid #333;\n    margin: 10px auto;\n}\n\n/* Pseudo-class */\na:hover { color: red; }\n\n/* Descendant */\nnav a { color: white; }'},
            {"type": "text", "order": 3, "content": "Total width = width + padding + border + margin. box-sizing: border-box includes padding/border in width."},
            # Micro-Quest blocks (hook 0, blueprint 4, exam_tip 5). The blueprint
            # is the match_pairs interaction. Lessons without these render as before.
            *seed_blocks("selectors-properties"),
        ],
        [
            {
                "type": ExerciseTypeEnum.multiple_choice,
                "order": 1,
                "xp_reward": 10,
                "starter_code": "",
                "solution_code": "",
                "validation_config": "",
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Which selector targets links inside a nav element?", "hint": "Descendant selector uses space", "explanation": "nav a selects all <a> elements that are descendants of <nav>."},
                    {"language": LanguageEnum.fr, "prompt": "Quel sélecteur cible les liens dans un élément nav ?", "hint": "Le sélecteur descendant utilise un espace", "explanation": "nav a sélectionne tous les <a> descendants de <nav>."},
                    {"language": LanguageEnum.ar, "prompt": "أي محدد يستهدف الروابط داخل عنصر nav؟", "hint": "المحدد النسل يستخدم مسافة", "explanation": "nav a يختار جميع عناصر <a> التي هي نسل لـ <nav>."},
                ],
                "options": [
                    {"order": 1, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "nav > a"}, {"language": LanguageEnum.fr, "text": "nav > a"}, {"language": LanguageEnum.ar, "text": "nav > a"}]},
                    {"order": 2, "is_correct": True, "translations": [{"language": LanguageEnum.en, "text": "nav a"}, {"language": LanguageEnum.fr, "text": "nav a"}, {"language": LanguageEnum.ar, "text": "nav a"}]},
                    {"order": 3, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "nav + a"}, {"language": LanguageEnum.fr, "text": "nav + a"}, {"language": LanguageEnum.ar, "text": "nav + a"}]},
                    {"order": 4, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "nav ~ a"}, {"language": LanguageEnum.fr, "text": "nav ~ a"}, {"language": LanguageEnum.ar, "text": "nav ~ a"}]},
                ]
            }
        ]
    )
    
    # Lesson 23: Layout with Flexbox
    await get_or_create_lesson(db, module2_id, "flexbox-layout", 3,
        DifficultyEnum.intermediate, 40, 60,
        [
            {"language": LanguageEnum.en, "title": "Layout with Flexbox", "story": "Create flexible, responsive layouts with CSS Flexbox", "objective": "Use flex containers and items for modern layouts", "skills": "Flexbox, flex-direction, justify-content, align-items, gap"},
            {"language": LanguageEnum.fr, "title": "Mise en Page avec Flexbox", "story": "Créez des mises en page flexibles et responsives avec CSS Flexbox", "objective": "Utiliser les conteneurs et éléments flex pour les mises en page modernes", "skills": "Flexbox, flex-direction, justify-content, align-items, gap"},
            {"language": LanguageEnum.ar, "title": "التخطيط مع Flexbox", "story": "أنشئ تخطيطات مرنة ومتجاوبة مع CSS Flexbox", "objective": "استخدام حاويات وعناصر flex للتخطيطات الحديثة", "skills": "Flexbox، flex-direction، justify-content، align-items، gap"},
        ],
        [
            {"type": "text", "order": 1, "content": "Flexbox makes layout easy. Set display: flex on a container. Children become flex items. Control direction, alignment, distribution with properties."},
            {"type": "code", "order": 2, "content": "Flexbox layout:", "code_example": '.container {\n    display: flex;\n    flex-direction: row;\n    justify-content: space-between;\n    align-items: center;\n    gap: 20px;\n}\n\n/* Items can grow/shrink */\n.item { flex: 1; }'},
            {"type": "text", "order": 3, "content": "flex-direction: row (default), column, row-reverse, column-reverse. justify-content: center, space-between, space-around. align-items: center, stretch, flex-start. gap adds spacing between items."},
        ],
        [
            {
                "type": ExerciseTypeEnum.code_writing,
                "order": 1,
                "xp_reward": 15,
                "starter_code": '/* Create a flex container that centers items horizontally\n   and vertically, with 20px gap between them */\n.container {\n    display: ____;\n    justify-content: ____;\n    align-items: ____;\n    gap: ____;\n}',
                "solution_code": '.container {\n    display: flex;\n    justify-content: center;\n    align-items: center;\n    gap: 20px;\n}',
                # Graded by keywords, not the Python sandbox: this answer is not Python.
                "validation_config": '{"expected_keywords": ["display: flex", "justify-content: center", "align-items: center", "gap: 20px"]}',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Write CSS to center flex items both horizontally and vertically with 20px gap.", "hint": "display: flex, justify-content: center, align-items: center, gap: 20px", "explanation": "Flexbox centering uses justify-content for horizontal, align-items for vertical. gap adds spacing."},
                    {"language": LanguageEnum.fr, "prompt": "Écrivez le CSS pour centrer les éléments flex horizontalement et verticalement avec 20px d'écart.", "hint": "display: flex, justify-content: center, align-items: center, gap: 20px", "explanation": "Le centrage Flexbox utilise justify-content pour l'horizontal, align-items pour le vertical. gap ajoute l'espacement."},
                    {"language": LanguageEnum.ar, "prompt": "اكتب CSS لتوسيط عناصر flex أفقياً وعمودياً مع فجوة 20px.", "hint": "display: flex، justify-content: center، align-items: center، gap: 20px", "explanation": "توسيط Flexbox يستخدم justify-content للأفقي، align-items للعمودي. gap تضيف التباعد."},
                ]
            }
        ]
    )
    
    # Lesson 24: Responsive Web Design
    await get_or_create_lesson(db, module2_id, "responsive-design", 4,
        DifficultyEnum.intermediate, 40, 60,
        [
            {"language": LanguageEnum.en, "title": "Responsive Web Design", "story": "Make your websites work on mobile, tablet, and desktop", "objective": "Use media queries, viewport, and fluid layouts", "skills": "Media queries, viewport meta, fluid layouts, mobile-first"},
            {"language": LanguageEnum.fr, "title": "Design Web Responsive", "story": "Faites fonctionner vos sites sur mobile, tablette et bureau", "objective": "Utiliser les media queries, viewport et mises en page fluides", "skills": "Media queries, viewport meta, mises en page fluides, mobile-first"},
            {"language": LanguageEnum.ar, "title": "تصميم الويب المتجاوب", "story": "اجعل مواقعك تعمل على الجوال، التابلت، وسطح المكتب", "objective": "استخدام media queries، viewport، والتخطيطات السائلة", "skills": "Media queries، viewport meta، تخطيطات سائلة، mobile-first"},
        ],
        [
            {"type": "text", "order": 1, "content": "Responsive design adapts to screen sizes. Viewport meta tag enables mobile scaling. Media queries apply CSS at breakpoints. Mobile-first: base styles for mobile, enhance for larger screens."},
            {"type": "code", "order": 2, "content": "Responsive basics:", "code_example": '<meta name="viewport" content="width=device-width, initial-scale=1">\n\n/* Mobile first - base styles */\n.container { padding: 10px; }\n\n/* Tablet and up */\n@media (min-width: 768px) {\n    .container { padding: 20px; }\n}\n\n/* Desktop */\n@media (min-width: 1024px) {\n    .container { padding: 40px; }\n}'},
            {"type": "text", "order": 3, "content": "Common breakpoints: 480px (mobile), 768px (tablet), 1024px (desktop), 1200px (large). Use relative units (%, rem, em) for fluid layouts."},
        ],
        [
            {
                "type": ExerciseTypeEnum.fill_blank,
                "order": 1,
                "xp_reward": 10,
                "starter_code": '<meta name="____" content="width=device-width, initial-scale=1">\n\n@media (min-____: 768px) {\n    .card { flex-direction: ____; }\n}',
                "solution_code": '<meta name="viewport" content="width=device-width, initial-scale=1">\n\n@media (min-width: 768px) {\n    .card { flex-direction: row; }\n}',
                "validation_config": '{"blanks": [{"answer": "viewport"}, {"answer": "width"}, {"answer": "row"}]}',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Fill in the viewport meta tag and media query for tablet layout.", "hint": "viewport, min-width, row (horizontal on tablet)", "explanation": "Viewport enables mobile scaling. Media queries trigger at breakpoints. Tablets often use horizontal flex direction."},
                    {"language": LanguageEnum.fr, "prompt": "Remplissez la balise viewport meta et la media query pour la mise en page tablette.", "hint": "viewport, min-width, row (horizontal sur tablette)", "explanation": "Viewport active le zoom mobile. Les media queries déclenchent aux points de rupture. Tablettes souvent direction flex horizontale."},
                    {"language": LanguageEnum.ar, "prompt": "املأ علامة viewport meta و media query لتخطيط التابلت.", "hint": "viewport، min-width، row (أفقي على التابلت)", "explanation": "Viewport يمكّن التكبير على الجوال. Media queries تعمل عند نقاط الانعطاف. التابلت غالباً يستخدم اتجاه flex أفقي."},
                ]
            }
        ]
    )
    
    print("Web Fundamentals seeded successfully!")