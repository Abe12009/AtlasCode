"""The Networking and Data Structures & Algorithms courses.

Both slugs were declared in app.curriculum's roadmap and referenced as
prerequisites elsewhere, but had no seeder that actually created them — this
module's Module/Lesson content sat unused. seed_networking and
seed_data_structures_algorithms below are real NEW_COURSE_SEEDERS entries
(see app.seed.__init__), each creating its course and content idempotently.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import DifficultyEnum as D

from .authoring import (
    Code,
    CodeWriting,
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
    asserts,
    seed_course,
)
from .stage_dsa_core import CORE_DSA_MODULES
from .stage_database_design import DATABASE_DESIGN_MODULES

# ---------------------------------------------------------------------------
# Networking — the layered model, address assignment, and diagnosis
# ---------------------------------------------------------------------------

NETWORKING_MODULES = [
    Module(
        slug="osi-and-tcp-ip-models",
        title=T("Network Models: OSI and TCP/IP", "Modèles Réseau : OSI et TCP/IP", "نماذج الشبكة: OSI وTCP/IP"),
        description=T(
            "The layered way of thinking that makes every other network topic tractable.",
            "La pensée en couches qui rend abordable tout autre sujet réseau.",
            "التفكير الطبقي الذي يجعل كلّ موضوع شبكي آخر قابلًا للفهم.",
        ),
        lessons=[
            Lesson(
                slug="the-osi-model",
                minutes=35,
                xp=60,
                difficulty=D.intermediate,
                title=T("The OSI Model", "Le Modèle OSI", "نموذج OSI"),
                story=T(
                    "Seven layers exist so that a Wi-Fi problem and a certificate problem are never confused with each other.",
                    "Sept couches existent pour qu'un problème de Wi-Fi et un problème de certificat ne soient jamais confondus.",
                    "توجد سبع طبقات كي لا تُخلط مشكلة الواي فاي بمشكلة الشهادة أبدًا.",
                ),
                objective=T(
                    "Name the OSI layers, map them onto the TCP/IP model, and place a given problem at the right layer.",
                    "Nommer les couches OSI, les projeter sur le modèle TCP/IP, et situer un problème à la bonne couche.",
                    "تسمية طبقات OSI ومطابقتها بنموذج TCP/IP وتحديد الطبقة الصحيحة لمشكلة معيّنة.",
                ),
                skills=T(
                    "OSI layers, TCP/IP model, encapsulation, layer isolation",
                    "Couches OSI, modèle TCP/IP, encapsulation, isolation des couches",
                    "طبقات OSI، نموذج TCP/IP، التغليف، عزل الطبقات",
                ),
                blocks=[
                    Text(
                        T(
                            "The OSI model names seven layers, each using the one below and serving the one above: **Physical** (signals), **Data link** (frames on one link, MAC addresses), **Network** (IP, routing between networks), **Transport** (TCP/UDP, ports, reliability), **Session**, **Presentation**, **Application** (HTTP, DNS, SMTP).",
                            "Le modèle OSI nomme sept couches, chacune utilisant celle du dessous et servant celle du dessus : **Physique** (signaux), **Liaison** (trames sur un lien, adresses MAC), **Réseau** (IP, routage entre réseaux), **Transport** (TCP/UDP, ports, fiabilité), **Session**, **Présentation**, **Application** (HTTP, DNS, SMTP).",
                            "يسمّي نموذج OSI سبع طبقات، كلّ منها تستخدم ما تحتها وتخدم ما فوقها: **الفيزيائية** (الإشارات)، و**ربط البيانات** (الإطارات على وصلة واحدة وعناوين MAC)، و**الشبكة** (IP والتوجيه بين الشبكات)، و**النقل** (TCP/UDP والمنافذ والموثوقية)، و**الجلسة**، و**العرض**، و**التطبيق** (HTTP وDNS وSMTP).",
                        )
                    ),
                    Text(
                        T(
                            "The TCP/IP model that the internet actually runs collapses these into four: Link, Internet, Transport and Application. OSI survives because it is a better vocabulary for diagnosis — \"that is a layer 2 problem\" says something precise, and rules out six other places to look.",
                            "Le modèle TCP/IP réellement utilisé par Internet les réduit à quatre : Liaison, Internet, Transport et Application. OSI subsiste parce qu'il offre un meilleur vocabulaire de diagnostic — « c'est un problème de couche 2 » est précis et élimine six autres pistes.",
                            "أمّا نموذج TCP/IP الذي تعمل به الإنترنت فعلًا فيختصرها إلى أربع: الوصلة والإنترنت والنقل والتطبيق. ويبقى OSI لأنّه مفردات أفضل للتشخيص — فقولك «هذه مشكلة في الطبقة 2» دقيق ويستبعد ستّة مواضع أخرى.",
                        )
                    ),
                    Code(
                        T(
                            "**Encapsulation** is what the layers do to your data on the way out:",
                            "L'**encapsulation** est ce que les couches font à vos données en sortie :",
                            "**التغليف** هو ما تفعله الطبقات ببياناتك في طريق الخروج:",
                        ),
                        "# Sending 'GET /courses':\n"
                        "#   Application  |                          GET /courses\n"
                        "#   Transport    |            [TCP hdr | GET /courses]\n"
                        "#   Network      |    [IP hdr | TCP hdr | GET /courses]\n"
                        "#   Data link    | [Eth | IP hdr | TCP hdr | GET /courses | FCS]\n"
                        "#   Physical     |  ...as electrical, optical or radio signals\n\n"
                        "# The receiver unwraps in the exact reverse order. Each layer only\n"
                        "# reads its own header -- which is precisely why IP can run over\n"
                        "# fibre, copper or radio without a single change to TCP or HTTP.",
                    ),
                    ExamTip(
                        T(
                            "Diagnose upwards from the bottom. There is no point debugging TLS if the cable is unplugged, and no point blaming DNS if `ping 8.8.8.8` already fails.",
                            "Diagnostiquez du bas vers le haut. Inutile de déboguer TLS si le câble est débranché, ou d'accuser le DNS si `ping 8.8.8.8` échoue déjà.",
                            "شخّص من الأسفل صعودًا. فلا معنى لتصحيح TLS والكابل مفصول، ولا لاتّهام DNS إذا فشل `ping 8.8.8.8` أصلًا.",
                        )
                    ),
                ],
                exercises=[
                    MCQ(
                        prompt=T(
                            "At which OSI layer do IP addresses and routing between networks belong?",
                            "À quelle couche OSI appartiennent les adresses IP et le routage entre réseaux ?",
                            "في أيّ طبقة من OSI تقع عناوين IP والتوجيه بين الشبكات؟",
                        ),
                        hint=T("It is the layer above the one that handles a single link.", "C'est la couche au-dessus de celle qui gère un lien unique.", "إنّها الطبقة التي تعلو المسؤولة عن وصلة واحدة."),
                        explanation=T(
                            "The network layer (layer 3) handles logical addressing and routing between separate networks.",
                            "La couche réseau (3) gère l'adressage logique et le routage entre réseaux distincts.",
                            "طبقة الشبكة (الثالثة) تتولّى العنونة المنطقية والتوجيه بين شبكات منفصلة.",
                        ),
                        options=[
                            Option(T("Data link (layer 2)", "Liaison (couche 2)", "ربط البيانات (الطبقة 2)")),
                            Option(T("Network (layer 3)", "Réseau (couche 3)", "الشبكة (الطبقة 3)"), correct=True),
                            Option(T("Transport (layer 4)", "Transport (couche 4)", "النقل (الطبقة 4)")),
                            Option(T("Application (layer 7)", "Application (couche 7)", "التطبيق (الطبقة 7)")),
                        ],
                    ),
                    Ordering(
                        prompt=T(
                            "Order the OSI layers from lowest to highest.",
                            "Classez les couches OSI de la plus basse à la plus haute.",
                            "رتّب طبقات OSI من الأدنى إلى الأعلى.",
                        ),
                        hint=T("Start with the signal on the wire.", "Commencez par le signal sur le câble.", "ابدأ بالإشارة على السلك."),
                        explanation=T(
                            "Physical, data link, network, transport, then the application layers above them.",
                            "Physique, liaison, réseau, transport, puis les couches applicatives au-dessus.",
                            "الفيزيائية ثمّ ربط البيانات ثمّ الشبكة ثمّ النقل ثمّ طبقات التطبيق فوقها.",
                        ),
                        steps=[
                            T("Physical", "Physique", "الفيزيائية"),
                            T("Data link", "Liaison de données", "ربط البيانات"),
                            T("Network", "Réseau", "الشبكة"),
                            T("Transport", "Transport", "النقل"),
                            T("Application", "Application", "التطبيق"),
                        ],
                    ),
                ],
            ),
        ],
    ),
    Module(
        slug="addressing-services",
        title=T("Addressing Services: DHCP and IPv6", "Services d'Adressage : DHCP et IPv6", "خدمات العنونة: DHCP وIPv6"),
        description=T(
            "How a device gets an address, and why the internet needed a bigger one.",
            "Comment un appareil obtient une adresse, et pourquoi Internet en a eu besoin d'une plus grande.",
            "كيف يحصل الجهاز على عنوان، ولماذا احتاجت الإنترنت إلى عنوان أكبر.",
        ),
        lessons=[
            Lesson(
                slug="dhcp-and-ipv6",
                minutes=35,
                xp=60,
                difficulty=D.intermediate,
                title=T("DHCP and IPv6", "DHCP et IPv6", "‏DHCP وIPv6"),
                story=T(
                    "You join a Wi-Fi network and everything works within a second. Four messages made that happen.",
                    "Vous rejoignez un Wi-Fi et tout fonctionne en une seconde. Quatre messages l'ont permis.",
                    "تنضمّ إلى شبكة واي فاي فيعمل كلّ شيء خلال ثانية. أربع رسائل جعلت ذلك ممكنًا.",
                ),
                objective=T(
                    "Describe the DHCP lease process and explain why IPv6 exists and what it changes.",
                    "Décrire le processus de bail DHCP et expliquer pourquoi IPv6 existe et ce qu'il change.",
                    "وصف عملية استئجار العنوان في DHCP، وشرح سبب وجود IPv6 وما الذي يغيّره.",
                ),
                skills=T(
                    "DHCP DORA, leases, IPv4 exhaustion, NAT, IPv6 addressing",
                    "DHCP DORA, baux, épuisement IPv4, NAT, adressage IPv6",
                    "‏DHCP DORA، عقود الإيجار، نفاد IPv4، NAT، عنونة IPv6",
                ),
                blocks=[
                    Text(
                        T(
                            "**DHCP** hands out addresses automatically in four steps, remembered as **DORA**: the client broadcasts a **Discover**, a server replies with an **Offer**, the client broadcasts a **Request** for that offer, and the server sends an **Acknowledge**. What it grants is a **lease** with an expiry, so an address freed by a departed device returns to the pool.",
                            "**DHCP** distribue les adresses automatiquement en quatre étapes, retenues sous **DORA** : le client diffuse un **Discover**, un serveur répond par une **Offer**, le client diffuse un **Request** pour cette offre, et le serveur envoie un **Acknowledge**. Ce qu'il accorde est un **bail** avec expiration : une adresse libérée revient au pool.",
                            "يوزّع **DHCP** العناوين تلقائيًا في أربع خطوات تُختصر بـ**DORA**: يبثّ العميل **Discover**، فيردّ خادم بـ**Offer**، ثمّ يبثّ العميل **Request** لذلك العرض، فيرسل الخادم **Acknowledge**. وما يمنحه **عقد إيجار** له مدّة انتهاء، فيعود العنوان الذي يتركه جهاز راحل إلى المجموعة.",
                        )
                    ),
                    Text(
                        T(
                            "IPv4 has 32-bit addresses: about 4.3 billion, which the world exhausted. **NAT** postponed the crisis by letting a whole household share one public address, at the cost of breaking the internet's original any-host-to-any-host model. **IPv6** uses 128 bits — enough addresses to give every device its own for any future anyone can foresee.",
                            "IPv4 a des adresses de 32 bits : environ 4,3 milliards, épuisées. Le **NAT** a repoussé la crise en laissant tout un foyer partager une adresse publique, au prix du modèle originel « chaque hôte joignable ». **IPv6** utilise 128 bits — assez d'adresses pour tout appareil et tout avenir prévisible.",
                            "عناوين IPv4 من 32 بتًا: نحو 4.3 مليار، وقد استنفدها العالم. وأجّل **NAT** الأزمة بجعل منزل كامل يتقاسم عنوانًا عامًّا واحدًا، بثمن كسر نموذج الإنترنت الأصلي في وصول أيّ مضيف إلى أيّ مضيف. أمّا **IPv6** فيستخدم 128 بتًا — عناوين تكفي كلّ جهاز ولأيّ مستقبل منظور.",
                        )
                    ),
                    Code(
                        T(
                            "The two address formats, side by side:",
                            "Les deux formats d'adresse, côte à côte :",
                            "صيغتا العنوان جنبًا إلى جنب:",
                        ),
                        "# IPv4 - 32 bits, four decimal octets\n"
                        "#   192.168.1.24        (private: not routable on the internet)\n"
                        "#   2^32  = 4,294,967,296 addresses in total\n\n"
                        "# IPv6 - 128 bits, eight hex groups; :: collapses one run of zeros\n"
                        "#   2001:0db8:0000:0000:0000:ff00:0042:8329\n"
                        "#   2001:db8::ff00:42:8329            (the same address, shortened)\n"
                        "#   2^128 = about 3.4 x 10^38 addresses\n\n"
                        "print(2 ** 32)\n"
                        "print(f'{2 ** 128:.2e}')",
                    ),
                ],
                exercises=[
                    Ordering(
                        prompt=T(
                            "Put the DHCP exchange in order.",
                            "Remettez l'échange DHCP dans l'ordre.",
                            "رتّب تبادل DHCP.",
                        ),
                        hint=T("Remember DORA.", "Souvenez-vous de DORA.", "تذكّر DORA."),
                        explanation=T(
                            "Discover, Offer, Request, Acknowledge — the client asks, a server offers, the client accepts, the server confirms.",
                            "Discover, Offer, Request, Acknowledge — le client demande, un serveur offre, le client accepte, le serveur confirme.",
                            "‏Discover ثمّ Offer ثمّ Request ثمّ Acknowledge — يسأل العميل، فيعرض خادم، فيقبل العميل، فيؤكّد الخادم.",
                        ),
                        steps=[
                            T("Client broadcasts Discover", "Le client diffuse un Discover", "يبثّ العميل Discover"),
                            T("Server sends an Offer", "Le serveur envoie une Offer", "يرسل الخادم Offer"),
                            T("Client sends a Request", "Le client envoie un Request", "يرسل العميل Request"),
                            T("Server sends an Acknowledge", "Le serveur envoie un Acknowledge", "يرسل الخادم Acknowledge"),
                        ],
                    ),
                    MCQ(
                        prompt=T(
                            "Why was IPv6 introduced?",
                            "Pourquoi IPv6 a-t-il été introduit ?",
                            "لماذا استُحدث IPv6؟",
                        ),
                        hint=T("How many addresses does 32 bits give?", "Combien d'adresses donnent 32 bits ?", "كم عنوانًا تعطي 32 بتًا؟"),
                        explanation=T(
                            "IPv4's 32-bit space ran out, and 128-bit addressing removes the constraint entirely.",
                            "L'espace 32 bits d'IPv4 est épuisé ; l'adressage 128 bits lève complètement la contrainte.",
                            "نفد فضاء IPv4 ذو 32 بتًا، والعنونة بـ128 بتًا تزيل القيد تمامًا.",
                        ),
                        options=[
                            Option(T("To make packets travel faster", "Pour accélérer les paquets", "لجعل الرزم أسرع")),
                            Option(T("IPv4's address space was exhausted", "L'espace d'adressage IPv4 était épuisé", "لأنّ فضاء عناوين IPv4 استُنفد"), correct=True),
                            Option(T("To replace TCP", "Pour remplacer TCP", "لاستبدال TCP")),
                            Option(T("To remove the need for DNS", "Pour supprimer le besoin de DNS", "لإلغاء الحاجة إلى DNS")),
                        ],
                    ),
                ],
            ),
        ],
    ),
    Module(
        slug="sockets-and-troubleshooting",
        title=T("Sockets and Network Troubleshooting", "Sockets et Dépannage Réseau", "المقابس واستكشاف أعطال الشبكة"),
        description=T(
            "The programmer's view of a connection, and how to find out what is actually broken.",
            "La vue du programmeur sur une connexion, et comment trouver ce qui est réellement cassé.",
            "رؤية المبرمج للاتّصال، وكيف تعرف ما المعطوب فعلًا.",
        ),
        lessons=[
            Lesson(
                slug="sockets-and-diagnosis",
                minutes=35,
                xp=65,
                difficulty=D.intermediate,
                title=T("Sockets and Diagnosing Network Problems", "Sockets et Diagnostic des Problèmes Réseau", "المقابس وتشخيص مشاكل الشبكة"),
                story=T(
                    "\"The site is down\" is five different problems, and one command separates them in about a second.",
                    "« Le site est down » recouvre cinq problèmes différents, et une commande les sépare en une seconde.",
                    "«الموقع لا يعمل» خمس مشكلات مختلفة، وأمر واحد يفصل بينها في ثانية تقريبًا.",
                ),
                objective=T(
                    "Explain what a socket is and follow a bottom-up procedure to locate a network fault.",
                    "Expliquer ce qu'est un socket et suivre une procédure ascendante pour localiser une panne réseau.",
                    "شرح ما هو المقبس واتّباع إجراء تصاعدي لتحديد موضع عطل الشبكة.",
                ),
                skills=T(
                    "Sockets, ports, ping, DNS lookup, traceroute, listening services, layered diagnosis",
                    "Sockets, ports, ping, résolution DNS, traceroute, services en écoute, diagnostic par couches",
                    "المقابس، المنافذ، ping، استعلام DNS، traceroute، الخدمات المُنصِتة، التشخيص الطبقي",
                ),
                blocks=[
                    Text(
                        T(
                            "A **socket** is the endpoint a program actually holds: an IP address plus a port, plus the protocol. A server **binds** to a port and listens; a client **connects** to that address and port. A connection is identified by all four values — source IP, source port, destination IP, destination port — which is how one server can hold thousands of simultaneous connections on port 443.",
                            "Un **socket** est le point d'accès que détient un programme : adresse IP, port et protocole. Un serveur **se lie** à un port et écoute ; un client **se connecte** à cette adresse et ce port. Une connexion est identifiée par les quatre valeurs — IP et port source, IP et port destination — d'où des milliers de connexions simultanées sur le port 443.",
                            "**المقبس** هو الطرف الذي يحمله البرنامج فعلًا: عنوان IP ومنفذ وبروتوكول. فالخادم **يرتبط** بمنفذ ويُنصِت، والعميل **يتّصل** بذلك العنوان والمنفذ. ويُعرَّف الاتّصال بالقيم الأربع — IP المصدر ومنفذه وIP الوجهة ومنفذها — ولهذا يحمل خادم واحد آلاف الاتّصالات المتزامنة على المنفذ 443.",
                        )
                    ),
                    Code(
                        T(
                            "Diagnose from the bottom of the stack upwards; the first failure names the layer:",
                            "Diagnostiquez du bas de la pile vers le haut ; le premier échec nomme la couche :",
                            "شخّص من أسفل المكدّس صعودًا؛ فأوّل إخفاق يسمّي الطبقة:",
                        ),
                        "# 1. Is there a link and a route at all?    (layers 1-3)\n"
                        "ping 8.8.8.8\n\n"
                        "# 2. Does the name resolve?                  (application: DNS)\n"
                        "nslookup atlascode.example\n\n"
                        "# 3. Where does the path stop?               (layer 3 routing)\n"
                        "traceroute atlascode.example\n\n"
                        "# 4. Is anything listening on that port?     (layer 4)\n"
                        "curl -v https://atlascode.example\n\n"
                        "# Reading the results:\n"
                        "#   ping fails, IP works      -> local link, gateway or route\n"
                        "#   ping works, DNS fails     -> resolver or the domain's records\n"
                        "#   DNS works, connect fails  -> firewall, or nothing is listening\n"
                        "#   connect works, TLS fails  -> certificate, not connectivity",
                    ),
                    ExamTip(
                        T(
                            "If a name fails but its IP address works, the fault is DNS — not \"the internet\". Naming the layer is most of the fix.",
                            "Si un nom échoue mais que son adresse IP fonctionne, la faute est au DNS — pas à « Internet ». Nommer la couche, c'est l'essentiel du correctif.",
                            "إذا فشل الاسم ونجح عنوان IP فالعطل في DNS لا في «الإنترنت». وتسمية الطبقة هي معظم الحلّ.",
                        )
                    ),
                ],
                exercises=[
                    MCQ(
                        prompt=T(
                            "`ping 8.8.8.8` succeeds but `ping example.com` fails. What is broken?",
                            "`ping 8.8.8.8` réussit mais `ping example.com` échoue. Qu'est-ce qui est cassé ?",
                            "ينجح `ping 8.8.8.8` ويفشل `ping example.com`. ما المعطوب؟",
                        ),
                        hint=T("What is the only difference between the two commands?", "Quelle est la seule différence entre les deux ?", "ما الفرق الوحيد بين الأمرين؟"),
                        explanation=T(
                            "Reaching an IP proves connectivity and routing work; only name resolution is left, so the fault is DNS.",
                            "Atteindre une IP prouve la connectivité et le routage ; il ne reste que la résolution de noms : la panne est DNS.",
                            "الوصول إلى عنوان IP يثبت سلامة الاتّصال والتوجيه؛ ولم يبقَ إلّا تحويل الأسماء، فالعطل في DNS.",
                        ),
                        options=[
                            Option(T("The physical link", "Le lien physique", "الوصلة الفيزيائية")),
                            Option(T("DNS resolution", "La résolution DNS", "تحويل أسماء DNS"), correct=True),
                            Option(T("The TLS certificate", "Le certificat TLS", "شهادة TLS")),
                            Option(T("The routing table", "La table de routage", "جدول التوجيه")),
                        ],
                    ),
                    MCQ(
                        prompt=T(
                            "What identifies a single TCP connection uniquely?",
                            "Qu'est-ce qui identifie de façon unique une connexion TCP ?",
                            "ما الذي يميّز اتّصال TCP واحدًا تمييزًا فريدًا؟",
                        ),
                        hint=T("How does one server keep thousands of clients apart on one port?", "Comment un serveur distingue-t-il des milliers de clients sur un port ?", "كيف يميّز خادم واحد آلاف العملاء على منفذ واحد؟"),
                        explanation=T(
                            "The four-tuple of source IP, source port, destination IP and destination port — which is why the shared destination port is not a problem.",
                            "Le quadruplet IP source, port source, IP destination, port destination — d'où l'absence de problème avec un port de destination partagé.",
                            "الرباعية: IP المصدر ومنفذه وIP الوجهة ومنفذها — ولهذا لا يمثّل تشارك منفذ الوجهة مشكلة.",
                        ),
                        options=[
                            Option(T("The destination port alone", "Le port de destination seul", "منفذ الوجهة وحده")),
                            Option(
                                T(
                                    "Source IP, source port, destination IP and destination port",
                                    "IP source, port source, IP destination, port destination",
                                    "‏IP المصدر ومنفذه وIP الوجهة ومنفذها",
                                ),
                                correct=True,
                            ),
                            Option(T("The MAC address", "L'adresse MAC", "عنوان MAC")),
                            Option(T("The domain name", "Le nom de domaine", "اسم النطاق")),
                        ],
                    ),
                ],
            ),
        ],
    ),
    Module(
        slug="transport-layer-deep-dive",
        title=T("Transport Layer Deep Dive: TCP vs UDP", "Plongée dans la Couche Transport : TCP vs UDP", "طبقة النقل بالتفصيل: TCP مقابل UDP"),
        description=T(
            "Two ways to move bytes between two ports, and why picking the wrong one is a real design mistake.",
            "Deux façons de déplacer des octets entre deux ports, et pourquoi se tromper est une vraie erreur de conception.",
            "طريقتان لنقل البايتات بين منفذين، ولماذا يُعدّ اختيار الطريقة الخاطئة خطأ تصميميًا حقيقيًا.",
        ),
        lessons=[
            Lesson(
                slug="tcp-vs-udp",
                minutes=40,
                xp=70,
                difficulty=D.intermediate,
                title=T("TCP vs UDP: Choosing a Transport", "TCP vs UDP : Choisir un Transport", "TCP مقابل UDP: اختيار وسيلة النقل"),
                story=T(
                    "A bank transfer and a live video call both move bytes over the internet, but losing one byte matters very differently to each.",
                    "Un virement bancaire et un appel vidéo en direct déplacent tous deux des octets sur internet, mais perdre un seul octet n'a pas la même gravité pour chacun.",
                    "التحويل المصرفي والمكالمة المرئية المباشرة كلاهما ينقل بايتات عبر الإنترنت، لكنّ فقدان بايت واحد لا يعني الشيء نفسه لكلٍّ منهما.",
                ),
                objective=T(
                    "Explain what TCP's three-way handshake and acknowledgments buy you, what UDP gives up to avoid that cost, and choose the right one for a given scenario.",
                    "Expliquer ce qu'apportent la triple poignée de main et les accusés de réception de TCP, ce qu'UDP sacrifie pour éviter ce coût, et choisir le bon protocole selon le scénario.",
                    "شرح ما توفّره المصافحة الثلاثية وإقرارات الاستلام في TCP، وما الذي يتنازل عنه UDP لتفادي هذه التكلفة، واختيار البروتوكول المناسب لسيناريو معطى.",
                ),
                skills=T(
                    "TCP, UDP, three-way handshake, acknowledgments, retransmission, flow control, ports",
                    "TCP, UDP, triple poignée de main, accusés de réception, retransmission, contrôle de flux, ports",
                    "TCP، UDP، المصافحة الثلاثية، إقرارات الاستلام، إعادة الإرسال، التحكّم بالتدفق، المنافذ",
                ),
                blocks=[
                    Text(
                        T(
                            "**TCP** (Transmission Control Protocol) is *connection-oriented and reliable*: before any data moves, the two sides run a handshake to agree they are both there and ready; every segment sent is tracked and, if it goes missing, retransmitted; and data arrives at the application in the exact order it was sent, even if it took a different path. **UDP** (User Datagram Protocol) is *connectionless*: a datagram is sent with no setup, no acknowledgment and no guarantee of order or delivery. Neither protocol is \"better\" — they trade the same cost (setup time, retransmission delay, in-order delivery) for the same benefit (speed, and no delay waiting for a lost packet to be resent) in opposite directions.",
                            "**TCP** (Transmission Control Protocol) est *orienté connexion et fiable* : avant tout envoi de données, les deux parties effectuent une poignée de main pour confirmer qu'elles sont prêtes ; chaque segment envoyé est suivi et, s'il se perd, retransmis ; et les données arrivent à l'application exactement dans l'ordre d'envoi, même si elles ont emprunté des chemins différents. **UDP** (User Datagram Protocol) est *sans connexion* : un datagramme est envoyé sans préparation, sans accusé de réception et sans garantie d'ordre ni de livraison. Aucun des deux protocoles n'est « meilleur » — ils échangent le même coût (temps de préparation, délai de retransmission, livraison ordonnée) contre le même bénéfice (rapidité, aucune attente pour un paquet perdu) en sens opposés.",
                            "**TCP** (بروتوكول التحكّم بالنقل) *موجّه بالاتّصال وموثوق*: فقبل انتقال أيّ بيانات يجري الطرفان مصافحة للتأكّد من جهوزية كلّ منهما؛ وكلّ قطعة تُرسَل تُتابَع وتُعاد إن فُقدت؛ وتصل البيانات إلى التطبيق بالترتيب ذاته الذي أُرسلت به تمامًا، حتّى لو سلكت مسارات مختلفة. أمّا **UDP** (بروتوكول مخطّط بيانات المستخدم) فهو *بلا اتّصال*: يُرسَل المخطّط دون تمهيد ولا إقرار استلام ولا ضمان للترتيب أو التسليم. وليس أيّ منهما «أفضل» — فكلاهما يقايض التكلفة نفسها (وقت التمهيد، وتأخير إعادة الإرسال، والتسليم المرتّب) بالفائدة نفسها (السرعة، وعدم الانتظار لإعادة إرسال حزمة مفقودة) في اتّجاهين متعاكسين.",
                        )
                    ),
                    Code(
                        T(
                            "The **three-way handshake** establishes a TCP connection before a single byte of real data moves:",
                            "La **triple poignée de main** établit une connexion TCP avant qu'un seul octet de données réelles ne soit envoyé :",
                            "تُنشئ **المصافحة الثلاثية** اتّصال TCP قبل انتقال أيّ بايت واحد من البيانات الفعلية:",
                        ),
                        "# Client                                    Server\n"
                        "#   |------------ SYN (seq=x) ------------>|   \"I want to talk, starting at x\"\n"
                        "#   |<------ SYN-ACK (seq=y, ack=x+1) -----|   \"OK, here is my start, and I got yours\"\n"
                        "#   |------------ ACK (ack=y+1) ---------->|   \"Got it, let's go\"\n"
                        "#\n"
                        "# Only after this does application data start flowing. Every byte sent\n"
                        "# after the handshake carries a sequence number; the receiver's ACKs\n"
                        "# tell the sender exactly what arrived, so a missing segment is both\n"
                        "# detectable and precisely identifiable for retransmission.\n"
                        "#\n"
                        "# UDP skips all of this -- a datagram is just sent:\n"
                        "#   |------------ datagram --------------->|   no handshake, no ACK, no retry",
                    ),
                    Text(
                        T(
                            "TCP also runs **flow control**: the receiver advertises a window size — how many unacknowledged bytes it can currently buffer — so a fast sender cannot flood a slow receiver. UDP has no such thing; a UDP application that sends faster than the receiver can process simply loses datagrams, silently, unless it builds its own scheme to prevent that. This is why real-time protocols built on UDP (video calls, online games, DNS) each implement *just enough* of their own reliability — a video call tolerates a dropped frame and keeps playing; DNS just retries the whole query after a short timeout — rather than paying for a full general-purpose reliability layer they do not need.",
                            "TCP applique aussi le **contrôle de flux** : le récepteur annonce une taille de fenêtre — le nombre d'octets non acquittés qu'il peut actuellement stocker — afin qu'un émetteur rapide ne submerge pas un récepteur lent. UDP n'a rien de tel ; une application UDP qui envoie plus vite que le récepteur ne peut traiter perd simplement des datagrammes, en silence, à moins de bâtir son propre mécanisme pour l'éviter. C'est pourquoi les protocoles temps réel bâtis sur UDP (appels vidéo, jeux en ligne, DNS) implémentent chacun *juste ce qu'il faut* de fiabilité propre — un appel vidéo tolère une image perdue et continue, DNS relance simplement toute la requête après un court délai — plutôt que de payer pour une couche de fiabilité générale dont ils n'ont pas besoin.",
                            "يطبّق TCP أيضًا **التحكّم بالتدفق**: إذ يعلن المستقبِل حجم نافذة — عدد البايتات غير المُقَرّة التي يمكنه تخزينها حاليًا — كي لا يُغرق مرسِل سريع مستقبِلًا بطيئًا. ولا يملك UDP شيئًا من هذا؛ فتطبيق UDP الذي يرسل أسرع ممّا يستطيع المستقبِل معالجته يفقد المخطّطات ببساطة وبصمت، ما لم يبنِ آليته الخاصّة لمنع ذلك. ولهذا تنفّذ البروتوكولات الآنية المبنيّة على UDP (المكالمات المرئية، الألعاب عبر الإنترنت، DNS) كلّ منها القدر *الكافي فقط* من الموثوقية الخاصّة بها — فمكالمة الفيديو تتحمّل فقدان إطار وتستمرّ، وDNS يعيد الاستعلام كاملًا بعد مهلة قصيرة — بدل دفع ثمن طبقة موثوقية عامة لا تحتاجها.",
                        )
                    ),
                    ExamTip(
                        T(
                            "\"UDP is unreliable\" does not mean \"UDP is broken\" — it means UDP does not guarantee delivery *itself*, leaving that choice to the application. A protocol built on UDP can still be effectively reliable (DNS retries; some video codecs use forward error correction) — it is just reliable on the application's own terms, not a default it pays for whether it needs it or not.",
                            "« UDP n'est pas fiable » ne veut pas dire « UDP est défaillant » — cela signifie qu'UDP ne garantit pas la livraison *lui-même*, laissant ce choix à l'application. Un protocole bâti sur UDP peut rester efficacement fiable (DNS relance ; certains codecs vidéo utilisent la correction d'erreur sans voie de retour) — mais selon les termes propres de l'application, pas un défaut payé qu'on en ait besoin ou non.",
                            "«عدم موثوقية UDP» لا يعني «عطبه» — بل يعني أنّ UDP لا يضمن التسليم *بنفسه*، تاركًا هذا الخيار للتطبيق. فبروتوكول مبنيّ على UDP قد يبقى موثوقًا فعليًا (DNS يعيد المحاولة؛ بعض مرمّزات الفيديو تستخدم تصحيح الخطأ الأمامي) — لكن بشروط التطبيق نفسه، لا كافتراضٍ يُدفع ثمنه سواء احتاجه أم لا.",
                        )
                    ),
                ],
                exercises=[
                    MCQ(
                        prompt=T(
                            "You are building a live video call feature. Which transport protocol fits best, and why?",
                            "Vous concevez une fonction d'appel vidéo en direct. Quel protocole de transport convient le mieux, et pourquoi ?",
                            "تبني ميزة مكالمة مرئية مباشرة. أيّ بروتوكول نقل يناسبها أكثر، ولماذا؟",
                        ),
                        hint=T("Would you rather see a frozen frame waiting for a retransmit, or a brief glitch and keep moving?", "Préférez-vous une image figée en attendant une retransmission, ou un bref artefact et la suite ?", "أتفضّل إطارًا متجمّدًا بانتظار إعادة الإرسال، أم عطلًا بسيطًا ثمّ الاستمرار؟"),
                        explanation=T(
                            "UDP: a live call needs low latency far more than perfect delivery — waiting for TCP to retransmit a lost packet would freeze the call, while UDP just drops the odd frame and keeps playing.",
                            "UDP : un appel en direct a bien plus besoin de faible latence que d'une livraison parfaite — attendre que TCP retransmette un paquet perdu figerait l'appel, tandis qu'UDP perd simplement une image et continue.",
                            "UDP: فالمكالمة المباشرة تحتاج إلى زمن استجابة منخفض أكثر بكثير من التسليم الكامل — فانتظار TCP لإعادة إرسال حزمة مفقودة يُجمّد المكالمة، بينما يكتفي UDP بفقدان إطار عابر ويستمرّ.",
                        ),
                        options=[
                            Option(T("TCP, because reliability always matters most", "TCP, car la fiabilité prime toujours", "TCP، لأنّ الموثوقية هي الأهمّ دائمًا")),
                            Option(T("UDP, because low latency matters more than a perfect frame here", "UDP, car la faible latence compte plus qu'une image parfaite ici", "UDP، لأنّ زمن الاستجابة المنخفض أهمّ من إطار مثالي هنا"), correct=True),
                            Option(T("Either, they perform identically for this use case", "Les deux, ils se valent pour ce cas d'usage", "كلاهما، فهما متكافئان لهذا الاستخدام")),
                            Option(T("Neither — video calls cannot use IP transport protocols", "Aucun des deux — les appels vidéo n'utilisent pas de protocoles de transport IP", "لا هذا ولا ذاك — المكالمات المرئية لا تستخدم بروتوكولات نقل IP")),
                        ],
                    ),
                    Ordering(
                        prompt=T(
                            "Order the three steps of the TCP three-way handshake.",
                            "Classez les trois étapes de la triple poignée de main TCP.",
                            "رتّب خطوات مصافحة TCP الثلاثية.",
                        ),
                        hint=T("The client speaks first.", "Le client parle en premier.", "العميل يتكلّم أوّلًا."),
                        explanation=T(
                            "SYN from the client, SYN-ACK from the server, then ACK from the client — only then does real data flow.",
                            "SYN du client, SYN-ACK du serveur, puis ACK du client — les données réelles ne circulent qu'ensuite.",
                            "SYN من العميل، ثمّ SYN-ACK من الخادم، ثمّ ACK من العميل — ولا تتدفّق البيانات الفعلية إلّا بعدها.",
                        ),
                        steps=[
                            T("Client sends SYN", "Le client envoie SYN", "العميل يرسل SYN"),
                            T("Server replies SYN-ACK", "Le serveur répond SYN-ACK", "الخادم يردّ بـ SYN-ACK"),
                            T("Client sends ACK", "Le client envoie ACK", "العميل يرسل ACK"),
                        ],
                    ),
                    ShortAnswer(
                        prompt=T(
                            "DNS queries are almost always sent over UDP rather than TCP. In one or two sentences, explain why that is a reasonable design choice.",
                            "Les requêtes DNS sont presque toujours envoyées en UDP plutôt qu'en TCP. En une ou deux phrases, expliquez pourquoi ce choix de conception est raisonnable.",
                            "تُرسَل استعلامات DNS عبر UDP لا TCP في الغالب. اشرح في جملة أو جملتين لماذا هذا خيار تصميمي معقول.",
                        ),
                        hint=T("Think about the size of a typical query and answer, and what happens if one is simply lost.", "Pensez à la taille d'une requête/réponse typique, et à ce qui se passe si l'une se perd.", "فكّر بحجم الاستعلام/الجواب المعتاد وما يحدث إن فُقد أحدهما."),
                        explanation=T(
                            "A DNS query and its answer are tiny and fit in a single datagram, so TCP's handshake would add pure overhead; and if a query is lost, the resolver just re-sends it after a short timeout, which is cheaper than paying for TCP's connection setup on every lookup.",
                            "Une requête DNS et sa réponse sont minuscules et tiennent dans un seul datagramme, donc la poignée de main TCP n'ajouterait qu'une surcharge inutile ; et si une requête se perd, le résolveur la renvoie simplement après un court délai, moins coûteux que d'établir une connexion TCP à chaque résolution.",
                            "استعلام DNS وجوابه صغيران جدًا ويتّسعان في مخطّط واحد، فمصافحة TCP لن تضيف سوى عبء زائد؛ وإذا فُقد الاستعلام يعيد المحلّل إرساله بعد مهلة قصيرة، وهذا أرخص من دفع تكلفة إنشاء اتّصال TCP في كلّ استعلام.",
                        ),
                        keywords=[["small", "tiny", "single datagram", "overhead"], ["retry", "resend", "timeout", "resends"]],
                        reference_answer="DNS queries/answers are small enough to fit one datagram, so TCP's handshake would be pure overhead; a lost query is cheaply fixed by a short-timeout retry instead.",
                    ),
                ],
            ),
        ],
    ),
    Module(
        slug="routing-and-switching-fundamentals",
        title=T("Routing and Switching Fundamentals", "Fondamentaux du Routage et de la Commutation", "أساسيات التوجيه والتحويل"),
        description=T(
            "How a packet actually gets from one device to another — inside one network, and across many.",
            "Comment un paquet se déplace réellement d'un appareil à un autre — au sein d'un réseau, et à travers plusieurs.",
            "كيف تنتقل الحزمة فعليًا من جهاز إلى آخر — داخل شبكة واحدة، وعبر شبكات عدّة.",
        ),
        lessons=[
            Lesson(
                slug="routers-switches-and-subnets",
                minutes=40,
                xp=70,
                difficulty=D.intermediate,
                title=T("Routers, Switches, and Subnets", "Routeurs, Commutateurs et Sous-réseaux", "الموجّهات والمحوّلات والشبكات الفرعية"),
                story=T(
                    "\"Just add a router\" is wrong about half the time — sometimes what the network actually needs is a switch.",
                    "« Ajoutez juste un routeur » est faux environ une fois sur deux — parfois, c'est un commutateur qu'il faut.",
                    "«فقط أضف موجّهًا» خطأ في نصف الحالات تقريبًا — فأحيانًا ما تحتاجه الشبكة فعلًا هو محوّل.",
                ),
                objective=T(
                    "Distinguish what a switch does from what a router does, read CIDR notation, and tell whether two addresses share a subnet.",
                    "Distinguer le rôle d'un commutateur de celui d'un routeur, lire la notation CIDR, et déterminer si deux adresses partagent un sous-réseau.",
                    "التمييز بين وظيفة المحوّل ووظيفة الموجّه، وقراءة ترميز CIDR، وتحديد ما إذا كان عنوانان يشتركان في الشبكة الفرعية نفسها.",
                ),
                skills=T(
                    "Switches, routers, MAC address tables, routing tables, CIDR, subnet masks, static vs dynamic routing",
                    "Commutateurs, routeurs, tables d'adresses MAC, tables de routage, CIDR, masques de sous-réseau, routage statique vs dynamique",
                    "المحوّلات، الموجّهات، جداول عناوين MAC، جداول التوجيه، CIDR، أقنعة الشبكة الفرعية، التوجيه الساكن مقابل الديناميكي",
                ),
                blocks=[
                    Text(
                        T(
                            "A **switch** connects devices *within* one network and forwards frames using **MAC addresses**: it learns which device sits on which physical port by watching traffic, and builds a MAC address table — no IP knowledge required. A **router** connects *separate* networks and forwards packets using **IP addresses** and a routing table: for each destination network, the table says which next device to hand the packet to. The test that actually distinguishes them is not \"does it have more than one cable\" (a switch can have 48 ports) — it is *which address type decides where a packet goes*.",
                            "Un **commutateur** relie des appareils *au sein* d'un même réseau et achemine les trames grâce aux **adresses MAC** : il apprend quel appareil se trouve sur quel port physique en observant le trafic, et bâtit une table d'adresses MAC — sans aucune connaissance IP. Un **routeur** relie des réseaux *distincts* et achemine les paquets grâce aux **adresses IP** et à une table de routage : pour chaque réseau de destination, la table indique à quel appareil suivant remettre le paquet. Le vrai critère de distinction n'est pas « a-t-il plusieurs câbles » (un commutateur peut avoir 48 ports) — c'est *quel type d'adresse décide où va un paquet*.",
                            "يربط **المحوّل** الأجهزة *داخل* شبكة واحدة ويوجّه الإطارات بالاعتماد على **عناوين MAC**: فهو يتعلّم أيّ جهاز يقع على أيّ منفذ فيزيائي بمراقبة حركة المرور، ويبني جدول عناوين MAC — دون أيّ معرفة بـ IP. أمّا **الموجّه** فيربط شبكات *منفصلة* ويوجّه الحزم بالاعتماد على **عناوين IP** وجدول توجيه: فلكلّ شبكة وجهة يحدّد الجدول الجهاز التالي الذي تُسلَّم إليه الحزمة. والمعيار الحقيقي للتمييز ليس «هل له أكثر من كابل» (فقد يملك المحوّل 48 منفذًا) بل *أيّ نوع من العناوين يقرّر وجهة الحزمة*.",
                        )
                    ),
                    Code(
                        T(
                            "**CIDR notation** (e.g. `192.168.1.0/24`) states an address plus how many leading bits are the network portion. Two hosts are on the same subnet only if those network bits match:",
                            "La **notation CIDR** (ex. `192.168.1.0/24`) indique une adresse et le nombre de bits de poids fort formant la partie réseau. Deux hôtes ne partagent un sous-réseau que si ces bits réseau coïncident :",
                            "يحدّد **ترميز CIDR** (مثل `192.168.1.0/24`) عنوانًا وعدد البتّات الأولى التي تمثّل جزء الشبكة. ولا يشترك مضيفان في الشبكة الفرعية إلّا إذا تطابقت بتّات الشبكة هذه:",
                        ),
                        "# /24 means: the first 24 bits (first three octets) are the network,\n"
                        "# the last 8 bits identify the host within it -- 254 usable addresses.\n"
                        "\n"
                        "# 192.168.1.10 /24  ->  network = 192.168.1.0\n"
                        "# 192.168.1.200/24  ->  network = 192.168.1.0   <- SAME subnet\n"
                        "#\n"
                        "# 192.168.1.10 /24  ->  network = 192.168.1.0\n"
                        "# 192.168.2.10 /24  ->  network = 192.168.2.0   <- DIFFERENT subnet\n"
                        "#   (a router, not a switch, is needed between these two)\n"
                        "\n"
                        "# A smaller network portion means a LARGER subnet:\n"
                        "# /23 covers 192.168.0.0-192.168.1.255 -- twice the hosts of a /24.",
                    ),
                    Text(
                        T(
                            "Routing tables are built one of two ways. **Static routing** means an administrator types in each route by hand: simple, predictable, and fine for a small or rarely-changing network — but it does not notice a failed link and adapts to nothing. **Dynamic routing** uses a routing protocol (e.g. OSPF within an organization, BGP between organizations on the internet) where routers exchange information about what they can reach and automatically recompute routes when something changes. Almost every home or office network is static by default (one router, one path out); the internet's backbone is dynamic almost everywhere, because a link going down somewhere must not mean the internet goes down.",
                            "Les tables de routage se construisent de deux façons. Le **routage statique** signifie qu'un administrateur saisit chaque route à la main : simple, prévisible, adapté à un petit réseau ou à un réseau qui change peu — mais il ne remarque pas un lien défaillant et ne s'adapte à rien. Le **routage dynamique** utilise un protocole de routage (ex. OSPF au sein d'une organisation, BGP entre organisations sur internet) où les routeurs échangent ce qu'ils peuvent atteindre et recalculent automatiquement les routes en cas de changement. Presque tout réseau domestique ou de bureau est statique par défaut (un routeur, une seule sortie) ; le cœur d'internet est dynamique presque partout, car la panne d'un lien quelque part ne doit pas faire tomber tout internet.",
                            "تُبنى جداول التوجيه بإحدى طريقتين. **التوجيه الساكن** يعني أنّ مسؤولًا يُدخل كلّ مسار يدويًا: بسيط ويمكن التنبّؤ به، ويناسب شبكة صغيرة أو نادرة التغيّر — لكنّه لا يلاحظ عطل وصلة ولا يتكيّف مع شيء. أمّا **التوجيه الديناميكي** فيستخدم بروتوكول توجيه (مثل OSPF داخل مؤسّسة، وBGP بين المؤسّسات على الإنترنت) حيث تتبادل الموجّهات معلومات عمّا يمكنها الوصول إليه وتعيد حساب المسارات تلقائيًا عند أيّ تغيّر. فمعظم شبكات المنازل أو المكاتب ساكنة افتراضيًا (موجّه واحد ومخرج واحد)؛ أمّا عمود الإنترنت الفقري فديناميكي في كلّ مكان تقريبًا، لأنّ عطل وصلة في مكان ما يجب ألّا يعني سقوط الإنترنت.",
                        )
                    ),
                    ExamTip(
                        T(
                            "Don't decide switch-vs-router by counting ports or cables. Ask which address type makes the forwarding decision: MAC address and a MAC table means switch behavior (layer 2); IP address and a routing table means router behavior (layer 3) — some devices do both, but the decision is always per-function, not per-box.",
                            "Ne tranchez pas commutateur-ou-routeur en comptant ports ou câbles. Demandez quel type d'adresse décide de l'acheminement : adresse MAC et table MAC = comportement de commutateur (couche 2) ; adresse IP et table de routage = comportement de routeur (couche 3) — certains appareils font les deux, mais la décision se prend toujours par fonction, jamais par boîtier.",
                            "لا تحسم بين المحوّل والموجّه بعدّ المنافذ أو الكابلات. بل اسأل أيّ نوع من العناوين يتّخذ قرار التوجيه: عنوان MAC وجدول MAC يعني سلوك محوّل (الطبقة 2)؛ وعنوان IP وجدول توجيه يعني سلوك موجّه (الطبقة 3) — فبعض الأجهزة تقوم بالاثنين معًا، لكنّ القرار يُتّخذ دائمًا حسب الوظيفة لا حسب الجهاز.",
                        )
                    ),
                ],
                exercises=[
                    MCQ(
                        prompt=T(
                            "A device forwards traffic using a table of MAC addresses it learned by watching local traffic, with no idea what an IP address is. What is it?",
                            "Un appareil achemine le trafic à l'aide d'une table d'adresses MAC apprises en observant le trafic local, sans aucune notion d'adresse IP. Qu'est-ce que c'est ?",
                            "جهاز يوجّه حركة المرور باستخدام جدول عناوين MAC تعلّمه من مراقبة حركة المرور المحلّية، دون أيّ فكرة عن عنوان IP. ما هو؟",
                        ),
                        hint=T("Which address type is it using to decide?", "Quel type d'adresse utilise-t-il pour décider ?", "أيّ نوع من العناوين يستخدمه للقرار؟"),
                        explanation=T(
                            "Forwarding by MAC address and a learned address table, with no IP awareness, is exactly switch (layer 2) behavior.",
                            "Acheminer par adresse MAC et une table apprise, sans notion d'IP, correspond exactement au comportement d'un commutateur (couche 2).",
                            "التوجيه بعنوان MAC وجدول متعلَّم، دون وعي بـ IP، هو بالضبط سلوك المحوّل (الطبقة 2).",
                        ),
                        options=[
                            Option(T("A switch", "Un commutateur", "محوّل"), correct=True),
                            Option(T("A router", "Un routeur", "موجّه")),
                            Option(T("A DNS server", "Un serveur DNS", "خادم DNS")),
                            Option(T("A firewall", "Un pare-feu", "جدار حماية")),
                        ],
                    ),
                    MCQ(
                        prompt=T(
                            "Host A is 10.0.1.5/24 and host B is 10.0.2.5/24. Can they reach each other with only a switch between them?",
                            "L'hôte A est 10.0.1.5/24 et l'hôte B est 10.0.2.5/24. Peuvent-ils communiquer avec seulement un commutateur entre eux ?",
                            "المضيف A هو 10.0.1.5/24 والمضيف B هو 10.0.2.5/24. هل يمكنهما التواصل بوجود محوّل فقط بينهما؟",
                        ),
                        hint=T("Compare the first 24 bits — the network portion — of each address.", "Comparez les 24 premiers bits — la partie réseau — de chaque adresse.", "قارن أوّل 24 بتًا — جزء الشبكة — من كلّ عنوان."),
                        explanation=T(
                            "10.0.1.0 and 10.0.2.0 are different /24 networks, so a switch alone cannot connect them — only a router, which forwards between networks, can.",
                            "10.0.1.0 et 10.0.2.0 sont des réseaux /24 différents, donc un commutateur seul ne peut pas les relier — seul un routeur, qui achemine entre réseaux, le peut.",
                            "‏10.0.1.0 و10.0.2.0 شبكتان مختلفتان بترميز /24، فلا يستطيع محوّل وحده ربطهما — فقط الموجّه، الذي ينقل بين الشبكات، يستطيع ذلك.",
                        ),
                        options=[
                            Option(T("Yes, they're on the same subnet", "Oui, même sous-réseau", "نعم، الشبكة الفرعية واحدة")),
                            Option(T("No, they're on different subnets and need a router", "Non, sous-réseaux différents, il faut un routeur", "لا، شبكتان فرعيتان مختلفتان ويلزم موجّه"), correct=True),
                            Option(T("Yes, but only for UDP traffic", "Oui, mais seulement pour le trafic UDP", "نعم، ولكن لحركة UDP فقط")),
                            Option(T("It depends on the MAC addresses", "Cela dépend des adresses MAC", "يعتمد ذلك على عناوين MAC")),
                        ],
                    ),
                    Ordering(
                        prompt=T(
                            "Order these networks from smallest to largest by usable host count: /26, /24, /16.",
                            "Classez ces réseaux du plus petit au plus grand par nombre d'hôtes utilisables : /26, /24, /16.",
                            "رتّب هذه الشبكات من الأصغر إلى الأكبر حسب عدد المضيفين القابلين للاستخدام: /26، /24، /16.",
                        ),
                        hint=T("A smaller network-bits number covers more addresses.", "Un nombre de bits réseau plus petit couvre plus d'adresses.", "عدد أصغر من بتّات الشبكة يغطّي عناوين أكثر."),
                        explanation=T(
                            "Fewer network bits means more host bits means more addresses: /26 (~62 hosts) is smallest, /24 (~254 hosts) is next, /16 (~65,534 hosts) is largest.",
                            "Moins de bits réseau signifie plus de bits hôte donc plus d'adresses : /26 (~62 hôtes) est le plus petit, /24 (~254 hôtes) ensuite, /16 (~65 534 hôtes) le plus grand.",
                            "بتّات شبكة أقلّ تعني بتّات مضيف أكثر فعناوين أكثر: /26 (نحو 62 مضيفًا) الأصغر، ثمّ /24 (نحو 254)، ثمّ /16 (نحو 65,534) الأكبر.",
                        ),
                        steps=[
                            T("/26", "/26", "/26"),
                            T("/24", "/24", "/24"),
                            T("/16", "/16", "/16"),
                        ],
                    ),
                ],
            ),
        ],
    ),
    Module(
        slug="dns-and-naming",
        title=T("DNS and Naming", "DNS et Nommage", "DNS وتسمية النطاقات"),
        description=T(
            "The lookup chain behind every domain name, the record types it returns, and why changes don't take effect instantly.",
            "La chaîne de résolution derrière chaque nom de domaine, les types d'enregistrements renvoyés, et pourquoi les changements ne sont pas instantanés.",
            "سلسلة البحث وراء كلّ اسم نطاق، وأنواع السجلّات التي تعيدها، ولماذا لا تسري التغييرات فورًا.",
        ),
        lessons=[
            Lesson(
                slug="dns-resolution-and-records",
                minutes=35,
                xp=65,
                difficulty=D.intermediate,
                title=T("DNS: Turning Names Into Addresses", "DNS : Transformer des Noms en Adresses", "DNS: تحويل الأسماء إلى عناوين"),
                story=T(
                    "Typing one URL quietly triggers a chain of up to four different servers before the browser even starts connecting.",
                    "Taper une seule URL déclenche discrètement une chaîne de jusqu'à quatre serveurs différents avant même que le navigateur ne commence à se connecter.",
                    "كتابة عنوان واحد فقط تُطلق بصمت سلسلة تصل إلى أربعة خوادم مختلفة قبل أن يبدأ المتصفّح الاتّصال أصلًا.",
                ),
                objective=T(
                    "Trace a DNS lookup through resolver, root, TLD and authoritative servers, and identify what each common record type is for.",
                    "Retracer une résolution DNS à travers le résolveur, le serveur racine, le TLD et le serveur faisant autorité, et identifier le rôle de chaque type d'enregistrement courant.",
                    "تتبّع بحث DNS عبر المحلّل والخادم الجذر وخادم TLD والخادم الموثوق، وتحديد وظيفة كلّ نوع سجلّ شائع.",
                ),
                skills=T(
                    "DNS resolution chain, recursive resolvers, A/AAAA/CNAME/MX/TXT/NS records, TTL and caching",
                    "Chaîne de résolution DNS, résolveurs récursifs, enregistrements A/AAAA/CNAME/MX/TXT/NS, TTL et cache",
                    "سلسلة تحليل DNS، المحلّلات العودية، سجلّات A/AAAA/CNAME/MX/TXT/NS، مدّة البقاء والتخزين المؤقّت",
                ),
                blocks=[
                    Text(
                        T(
                            "Resolving `atlascode.example` to an IP address is a chain, not one lookup. Your OS first asks a **recursive resolver** (often your ISP's or a public one like 1.1.1.1). If that resolver has no cached answer, it asks a **root server** — not for the answer, but for which server handles `.example`. It then asks that **TLD server**, which does not know the final answer either, but knows which server is **authoritative** for `atlascode.example` specifically. Only that last server holds the real answer. Each server in the chain narrows the question until one actually has it — and the resolver caches the final answer so the whole chain isn't repeated on the very next lookup.",
                            "Résoudre `atlascode.example` en adresse IP est une chaîne, pas une seule requête. Le système interroge d'abord un **résolveur récursif** (souvent celui du FAI, ou un public comme 1.1.1.1). Sans réponse en cache, ce résolveur interroge un **serveur racine** — non pour la réponse, mais pour savoir quel serveur gère `.example`. Il interroge ensuite ce **serveur TLD**, qui ne connaît pas non plus la réponse finale, mais sait quel serveur fait **autorité** spécifiquement pour `atlascode.example`. Seul ce dernier serveur détient la vraie réponse. Chaque serveur de la chaîne restreint la question jusqu'à ce que l'un d'eux l'ait réellement — et le résolveur met la réponse finale en cache pour ne pas répéter toute la chaîne à la requête suivante.",
                            "تحويل `atlascode.example` إلى عنوان IP سلسلة لا استعلامًا واحدًا. يسأل نظام التشغيل أوّلًا **محلّلًا عوديًا** (غالبًا تابعًا لمزوّد الإنترنت أو عامًا مثل 1.1.1.1). وإن لم يملك هذا المحلّل جوابًا مخزّنًا، يسأل **خادمًا جذريًا** — لا عن الجواب، بل عن الخادم المسؤول عن `.example`. ثمّ يسأل ذلك **خادم TLD**، الذي لا يعرف الجواب النهائي أيضًا لكنّه يعرف أيّ خادم **موثوق** تحديدًا بـ `atlascode.example`. وذلك الخادم الأخير وحده يملك الجواب الحقيقي. وكلّ خادم في السلسلة يضيّق السؤال حتّى يصل إلى من يملك الجواب فعلًا — ويخزّن المحلّل الجواب النهائي مؤقّتًا كي لا تتكرّر السلسلة كاملة عند البحث التالي مباشرة.",
                        )
                    ),
                    Code(
                        T(
                            "A real `dig` lookup shows several record types at once:",
                            "Une vraie requête `dig` révèle plusieurs types d'enregistrements à la fois :",
                            "يُظهر استعلام `dig` حقيقي عدّة أنواع سجلّات دفعة واحدة:",
                        ),
                        "$ dig atlascode.example ANY +short\n"
                        "\n"
                        "atlascode.example.        A      203.0.113.42       # IPv4 address\n"
                        "atlascode.example.        AAAA   2001:db8::42       # IPv6 address\n"
                        "www.atlascode.example.    CNAME  atlascode.example. # alias -> another name\n"
                        "atlascode.example.        MX     10 mail.atlascode.example.  # mail server\n"
                        "atlascode.example.        TXT    \"v=spf1 include:_spf.example ~all\"  # verification/anti-spoofing\n"
                        "atlascode.example.        NS     ns1.example-dns.com.  # who is authoritative\n"
                        "\n"
                        "# Every record also carries a TTL (seconds) -- how long a resolver\n"
                        "# may cache it before asking again. A 3600 TTL means a change to\n"
                        "# this record can take up to an hour to be visible everywhere.",
                    ),
                    ExamTip(
                        T(
                            "\"DNS propagation takes 24-48 hours\" is folklore, not a real global sync process — there is no single moment a change \"propagates\". What actually happens is that every resolver that already cached the old record keeps serving it until that record's **TTL** expires. The fix for a planned change is to lower the TTL *before* the change, wait for the old TTL to fully expire, then change the record — not to change it and hope.",
                            "« La propagation DNS prend 24 à 48 heures » est une légende, pas un vrai processus de synchronisation globale — il n'existe aucun instant unique où un changement « se propage ». Ce qui se passe réellement : chaque résolveur ayant déjà mis en cache l'ancien enregistrement continue de le servir jusqu'à l'expiration de son **TTL**. Pour un changement planifié, la bonne méthode est d'abaisser le TTL *avant* le changement, d'attendre l'expiration complète de l'ancien TTL, puis de modifier l'enregistrement — pas de le modifier en espérant.",
                            "«انتشار DNS يستغرق 24 إلى 48 ساعة» أسطورة شائعة لا عملية مزامنة عالمية حقيقية — فلا توجد لحظة واحدة «ينتشر» فيها التغيير. والذي يحدث فعلًا أنّ كلّ محلّل خزّن السجلّ القديم مسبقًا يستمرّ في تقديمه حتّى تنتهي **مدّة بقائه (TTL)**. والطريقة الصحيحة لتغيير مخطَّط له هي خفض TTL *قبل* التغيير، والانتظار حتّى تنتهي مدّة البقاء القديمة كاملة، ثمّ تعديل السجلّ — لا تعديله والأمل بالأفضل.",
                        )
                    ),
                ],
                exercises=[
                    MCQ(
                        prompt=T(
                            "Which DNS record type maps a domain name directly to an IPv4 address?",
                            "Quel type d'enregistrement DNS associe directement un nom de domaine à une adresse IPv4 ?",
                            "أيّ نوع من سجلّات DNS يربط اسم نطاق مباشرة بعنوان IPv4؟",
                        ),
                        hint=T("Its name is a single letter.", "Son nom est une seule lettre.", "اسمه حرف واحد."),
                        explanation=T(
                            "The A record maps a name to an IPv4 address; AAAA does the same for IPv6.",
                            "L'enregistrement A associe un nom à une adresse IPv4 ; AAAA fait de même pour IPv6.",
                            "سجلّ A يربط الاسم بعنوان IPv4؛ وAAAA يفعل الأمر ذاته لـ IPv6.",
                        ),
                        options=[
                            Option(T("A", "A", "A"), correct=True),
                            Option(T("MX", "MX", "MX")),
                            Option(T("TXT", "TXT", "TXT")),
                            Option(T("NS", "NS", "NS")),
                        ],
                    ),
                    MCQ(
                        prompt=T(
                            "You just changed a domain's A record, but some visitors still reach the old server an hour later. What is the most likely reason?",
                            "Vous venez de changer l'enregistrement A d'un domaine, mais des visiteurs atteignent encore l'ancien serveur une heure plus tard. Quelle est la raison la plus probable ?",
                            "غيّرت للتوّ سجلّ A لنطاق، لكن بعض الزوّار لا يزالون يصلون إلى الخادم القديم بعد ساعة. ما السبب الأرجح؟",
                        ),
                        hint=T("What does a resolver do with an answer before it asks again?", "Que fait un résolveur d'une réponse avant de redemander ?", "ماذا يفعل المحلّل بالجواب قبل أن يسأل مجدّدًا؟"),
                        explanation=T(
                            "Resolvers that cached the old record before the change will keep serving it until its TTL expires — this is normal caching behavior, not an error.",
                            "Les résolveurs ayant mis en cache l'ancien enregistrement avant le changement continueront de le servir jusqu'à l'expiration de son TTL — comportement normal de cache, pas une erreur.",
                            "المحلّلات التي خزّنت السجلّ القديم قبل التغيير ستستمرّ في تقديمه حتّى تنتهي مدّة بقائه — وهذا سلوك تخزين مؤقّت طبيعي لا خطأ.",
                        ),
                        options=[
                            Option(T("Their resolver cached the old record and its TTL hasn't expired yet", "Leur résolveur a mis en cache l'ancien enregistrement, dont le TTL n'a pas expiré", "محلّلهم خزّن السجلّ القديم ولم تنتهِ مدّة بقائه بعد"), correct=True),
                            Option(T("The new record was typed incorrectly", "Le nouvel enregistrement a été mal saisi", "أُدخل السجلّ الجديد بشكل خاطئ")),
                            Option(T("DNS records can only be changed once every 48 hours", "Les enregistrements DNS ne peuvent changer qu'une fois toutes les 48 heures", "لا يمكن تغيير سجلّات DNS إلّا مرّة كلّ 48 ساعة")),
                            Option(T("Those visitors are using UDP instead of TCP", "Ces visiteurs utilisent UDP au lieu de TCP", "أولئك الزوّار يستخدمون UDP بدل TCP")),
                        ],
                    ),
                    Ordering(
                        prompt=T(
                            "Order the servers a recursive resolver asks, from first to last, to resolve a brand-new name.",
                            "Classez les serveurs qu'interroge un résolveur récursif, du premier au dernier, pour résoudre un nom inédit.",
                            "رتّب الخوادم التي يسألها محلّل عودي، من الأوّل إلى الأخير، لتحليل اسم جديد كليًا.",
                        ),
                        hint=T("The chain narrows from \"everything\" to \"this one domain\".", "La chaîne se restreint de « tout » à « ce seul domaine ».", "تضيق السلسلة من «كلّ شيء» إلى «هذا النطاق وحده»."),
                        explanation=T(
                            "Root first (which server handles this TLD), then the TLD server (which server is authoritative for this domain), then the authoritative server (the actual answer).",
                            "D'abord la racine (quel serveur gère ce TLD), puis le serveur TLD (quel serveur fait autorité pour ce domaine), puis le serveur faisant autorité (la réponse réelle).",
                            "الجذر أوّلًا (أيّ خادم يتولّى TLD هذا)، ثمّ خادم TLD (أيّ خادم موثوق بهذا النطاق)، ثمّ الخادم الموثوق (الجواب الحقيقي).",
                        ),
                        steps=[
                            T("Root server", "Serveur racine", "الخادم الجذر"),
                            T("TLD server", "Serveur TLD", "خادم TLD"),
                            T("Authoritative server", "Serveur faisant autorité", "الخادم الموثوق"),
                        ],
                    ),
                ],
            ),
        ],
    ),
]


# ---------------------------------------------------------------------------
# Data Structures & Algorithms — the trie
# ---------------------------------------------------------------------------

DSA_MODULES = [
    Module(
        slug="tries",
        title=T("Tries", "Les Tries", "أشجار البادئات"),
        description=T(
            "The structure behind autocomplete and prefix search.",
            "La structure derrière l'autocomplétion et la recherche par préfixe.",
            "البنية التي وراء الإكمال التلقائي والبحث بالبادئة.",
        ),
        lessons=[
            Lesson(
                slug="prefix-trees",
                minutes=40,
                xp=70,
                difficulty=D.advanced,
                title=T("Prefix Trees (Tries)", "Arbres de Préfixes (Tries)", "أشجار البادئات (Tries)"),
                story=T(
                    "A search box suggests results after two letters, out of a million entries, before you finish typing the third.",
                    "Une barre de recherche propose des résultats après deux lettres, parmi un million d'entrées, avant la troisième.",
                    "يقترح مربّع بحث نتائج بعد حرفين من بين مليون مدخل قبل أن تُكمل الثالث.",
                ),
                objective=T(
                    "Explain how a trie stores shared prefixes and why lookup does not depend on how many words it holds.",
                    "Expliquer comment un trie stocke les préfixes communs et pourquoi la recherche ne dépend pas du nombre de mots.",
                    "شرح كيف تخزّن شجرة البادئات البادئات المشتركة، ولماذا لا يتوقّف البحث على عدد الكلمات المخزّنة.",
                ),
                skills=T(
                    "Tries, prefix sharing, insertion, lookup, autocomplete, space trade-off",
                    "Tries, partage de préfixes, insertion, recherche, autocomplétion, compromis mémoire",
                    "أشجار البادئات، تشارك البادئات، الإدراج، البحث، الإكمال التلقائي، مقايضة المساحة",
                ),
                blocks=[
                    Text(
                        T(
                            "A **trie** stores strings by their characters, one per edge, so every word sharing a prefix shares the path for it. Looking a word up costs O(m) where m is the word's **length** — not the number of stored words. A trie over a million entries answers as fast as a trie over ten.",
                            "Un **trie** stocke les chaînes par caractères, un par arête : tout mot partageant un préfixe partage le chemin correspondant. Rechercher un mot coûte O(m) où m est sa **longueur** — pas le nombre de mots stockés. Un trie d'un million d'entrées répond aussi vite qu'un trie de dix.",
                            "**شجرة البادئات** تخزّن السلاسل بمحارفها، محرفًا لكلّ ضلع، فتتشارك كلّ كلمة لها بادئة مشتركة المسارَ الخاصّ بها. والبحث عن كلمة يكلّف O(m) حيث m **طول** الكلمة — لا عدد الكلمات المخزّنة. فشجرة على مليون مدخل تجيب بسرعة شجرة على عشرة.",
                        )
                    ),
                    Code(
                        T(
                            "A complete trie in twenty lines:",
                            "Un trie complet en vingt lignes :",
                            "شجرة بادئات كاملة في عشرين سطرًا:",
                        ),
                        "class Trie:\n"
                        "    def __init__(self):\n"
                        "        self.root = {}\n\n"
                        "    def insert(self, word):\n"
                        "        node = self.root\n"
                        "        for char in word:\n"
                        "            node = node.setdefault(char, {})\n"
                        "        node['$'] = True        # marks the end of a complete word\n\n"
                        "    def contains(self, word):\n"
                        "        node = self._walk(word)\n"
                        "        return node is not None and '$' in node\n\n"
                        "    def starts_with(self, prefix):\n"
                        "        return self._walk(prefix) is not None\n\n"
                        "    def _walk(self, text):\n"
                        "        node = self.root\n"
                        "        for char in text:\n"
                        "            if char not in node:\n"
                        "                return None\n"
                        "            node = node[char]\n"
                        "        return node\n\n"
                        "trie = Trie()\n"
                        "for word in ['car', 'cart', 'cat', 'dog']:\n"
                        "    trie.insert(word)\n\n"
                        "print(trie.contains('car'), trie.contains('ca'), trie.starts_with('ca'))",
                    ),
                    Text(
                        T(
                            "The `'$'` marker is what separates \"a stored word ends here\" from \"this is only a prefix of longer words\". Without it, inserting `cart` would make `car` appear to be stored too. The trade-off is memory: a trie holds a node per character position, so a hash set is smaller when you never need prefix queries.",
                            "Le marqueur `'$'` distingue « un mot se termine ici » de « ceci n'est qu'un préfixe ». Sans lui, insérer `cart` ferait croire que `car` est stocké. Le compromis est la mémoire : un trie garde un nœud par position de caractère, donc un ensemble de hachage est plus petit si l'on n'a jamais besoin de requêtes par préfixe.",
                            "علامة `'$'` هي ما يفصل «تنتهي هنا كلمة مخزّنة» عن «هذه بادئة لكلمات أطول فقط». وبدونها يجعل إدراج `cart` الكلمةَ `car` تبدو مخزّنة أيضًا. والمقايضة هي الذاكرة: فالشجرة تحفظ عقدة لكلّ موضع محرف، لذا تكون مجموعة التجزئة أصغر إن لم تحتج استعلامات البادئة أبدًا.",
                        )
                    ),
                ],
                exercises=[
                    Prediction(
                        prompt=T(
                            "What does this print?",
                            "Qu'affiche ce code ?",
                            "ما الذي يطبعه هذا الكود؟",
                        ),
                        hint=T("'ca' is a prefix of stored words, but was it stored itself?", "« ca » est un préfixe de mots stockés, mais a-t-il été stocké ?", "«ca» بادئة لكلمات مخزّنة، لكن هل خُزّنت هي نفسها؟"),
                        explanation=T(
                            "'car' was inserted so contains is True; 'ca' was never inserted so contains is False, but starts_with finds the path.",
                            "« car » a été inséré : contains est True ; « ca » ne l'a pas été : contains est False, mais starts_with trouve le chemin.",
                            "أُدرجت «car» فكانت contains صحيحة؛ ولم تُدرج «ca» فكانت contains خاطئة، لكنّ starts_with تجد المسار.",
                        ),
                        code="class Trie:\n    def __init__(self):\n        self.root = {}\n\n    def insert(self, word):\n        node = self.root\n        for char in word:\n            node = node.setdefault(char, {})\n        node['$'] = True\n\n    def contains(self, word):\n        node = self._walk(word)\n        return node is not None and '$' in node\n\n    def starts_with(self, prefix):\n        return self._walk(prefix) is not None\n\n    def _walk(self, text):\n        node = self.root\n        for char in text:\n            if char not in node:\n                return None\n            node = node[char]\n        return node\n\ntrie = Trie()\nfor word in ['car', 'cart', 'cat', 'dog']:\n    trie.insert(word)\n\nprint(trie.contains('car'))\nprint(trie.contains('ca'))\nprint(trie.starts_with('ca'))",
                        expected_output="True\nFalse\nTrue",
                    ),
                    CodeWriting(
                        prompt=T(
                            "Complete the Trie: implement `insert(word)` and `starts_with(prefix)`. `starts_with` returns True when any stored word begins with the prefix.",
                            "Complétez le Trie : implémentez `insert(word)` et `starts_with(prefix)`. `starts_with` renvoie True si un mot stocké commence par le préfixe.",
                            "أكمل الشجرة: نفّذ `insert(word)` و`starts_with(prefix)`. تُرجع `starts_with` القيمة True إذا بدأت أيّ كلمة مخزّنة بالبادئة.",
                        ),
                        hint=T(
                            "Walk one character at a time, creating dictionaries as you go with setdefault.",
                            "Avancez caractère par caractère, en créant les dictionnaires avec setdefault.",
                            "امشِ محرفًا محرفًا وأنشئ القواميس أثناء ذلك بـ setdefault.",
                        ),
                        explanation=T(
                            "Insert walks and creates the path; starts_with walks and only reports whether the path exists, which is why it is True for a prefix that is not itself a word.",
                            "Insert parcourt et crée le chemin ; starts_with parcourt et signale seulement son existence, d'où True pour un préfixe qui n'est pas un mot.",
                            "‏insert تمشي وتُنشئ المسار، وstarts_with تمشي وتبلّغ فقط بوجوده، ولهذا تكون True لبادئة ليست كلمة بذاتها.",
                        ),
                        starter_code="class Trie:\n    def __init__(self):\n        self.root = {}\n\n    def insert(self, word):\n        pass\n\n    def starts_with(self, prefix):\n        pass\n\n\ntrie = Trie()\ntrie.insert('cat')\nprint(trie.starts_with('ca'))",
                        solution_code="class Trie:\n    def __init__(self):\n        self.root = {}\n\n    def insert(self, word):\n        node = self.root\n        for char in word:\n            node = node.setdefault(char, {})\n        node['$'] = True\n\n    def starts_with(self, prefix):\n        node = self.root\n        for char in prefix:\n            if char not in node:\n                return False\n            node = node[char]\n        return True\n\n\ntrie = Trie()\ntrie.insert('cat')\nprint(trie.starts_with('ca'))",
                        test_code=asserts(
                            "t = Trie()",
                            "for w in ['car', 'cart', 'cat', 'dog']:",
                            "    t.insert(w)",
                            "assert t.starts_with('ca') is True",
                            "assert t.starts_with('car') is True",
                            "assert t.starts_with('do') is True",
                            "assert t.starts_with('bird') is False",
                            "assert t.starts_with('carts') is False",
                        ),
                    ),
                ],
            ),
        ],
    ),
]


async def seed_networking(db: AsyncSession, order: int) -> int:
    """The Networking course: OSI/TCP-IP, addressing, sockets and diagnosis."""
    print("Seeding Networking...")
    spec = CourseSpec(
        slug="networking",
        title=T("Networking", "Réseaux", "الشبكات"),
        description=T(
            "How devices actually talk to each other, from a single cable to the global internet.",
            "Comment les appareils communiquent réellement entre eux, d'un simple câble à l'internet mondial.",
            "كيف تتواصل الأجهزة فعليًا فيما بينها، من كابل واحد إلى الإنترنت العالمي.",
        ),
        skills=T(
            "OSI/TCP-IP models, IP addressing, DHCP, TCP vs UDP, routing, subnetting, DNS, sockets, network troubleshooting",
            "Modèles OSI/TCP-IP, adressage IP, DHCP, TCP vs UDP, routage, sous-réseaux, DNS, sockets, dépannage réseau",
            "نموذجا OSI وTCP/IP، عنونة IP، DHCP، TCP مقابل UDP، التوجيه، الشبكات الفرعية، DNS، المقابس، استكشاف أخطاء الشبكة",
        ),
        modules=NETWORKING_MODULES,
        stage=4,
        track="systems",
        icon="🌐",
        difficulty=D.intermediate,
        estimated_hours=16,
        prerequisite_slug="cs-foundations",
    )
    return await seed_course(db, spec, order)


async def seed_data_structures_algorithms(db: AsyncSession, order: int) -> int:
    """The Data Structures & Algorithms course: arrays through graphs, sorting, searching, tries."""
    print("Seeding Data Structures & Algorithms...")
    spec = CourseSpec(
        slug="data-structures-algorithms",
        title=T("Data Structures & Algorithms", "Structures de Données & Algorithmes", "هياكل البيانات والخوارزميات"),
        description=T(
            "The building blocks and problem-solving patterns behind every technical interview and every fast program.",
            "Les briques de base et les schémas de résolution derrière chaque entretien technique et chaque programme rapide.",
            "اللبنات الأساسية وأنماط حل المسائل وراء كل مقابلة تقنية وكل برنامج سريع.",
        ),
        skills=T(
            "Arrays, linked lists, stacks, queues, hash tables, trees, graphs, sorting, searching, tries",
            "Tableaux, listes chaînées, piles, files, tables de hachage, arbres, graphes, tri, recherche, tries",
            "المصفوفات، القوائم المترابطة، المكدّسات، الطوابير، جداول التجزئة، الأشجار، الرسوم البيانية، الفرز، البحث",
        ),
        modules=[*CORE_DSA_MODULES, *DSA_MODULES],
        stage=3,
        track="theory",
        icon="🌳",
        difficulty=D.intermediate,
        estimated_hours=18,
        prerequisite_slug="python-in-depth",
    )
    return await seed_course(db, spec, order)


async def seed_database_design(db: AsyncSession, order: int) -> int:
    """The Database Design & Normalization course: modeling, keys, constraints, normal forms."""
    print("Seeding Database Design & Normalization...")
    spec = CourseSpec(
        slug="database-design",
        title=T("Database Design & Normalization", "Conception de Bases de Données et Normalisation", "تصميم قواعد البيانات والتسوية"),
        description=T(
            "Model a real problem into tables that hold together — entities, keys, constraints, and normal forms.",
            "Modélisez un problème réel en tables cohérentes — entités, clés, contraintes et formes normales.",
            "نمذجة مشكلة واقعية إلى جداول متماسكة — الكيانات، المفاتيح، القيود، والصور الطبيعية.",
        ),
        skills=T(
            "Data modeling, ER diagrams, primary/foreign/composite keys, constraints, normalization",
            "Modélisation de données, diagrammes ER, clés primaires/étrangères/composites, contraintes, normalisation",
            "نمذجة البيانات، مخططات الكيان-العلاقة، المفاتيح الأساسية والخارجية والمركّبة، القيود، التسوية",
        ),
        modules=DATABASE_DESIGN_MODULES,
        stage=4,
        track="systems",
        icon="🏛️",
        difficulty=D.beginner,
        estimated_hours=8,
        prerequisite_slug="sql-databases",
    )
    return await seed_course(db, spec, order)
