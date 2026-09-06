"""Additions to courses that already exist.

These fill genuine gaps in courses that are otherwise good, rather than
replacing them. Everything is keyed on a new module slug, so existing modules,
lessons and student progress are never touched.
"""

from app.models import DifficultyEnum as D
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Course

from .authoring import (
    Code,
    CodeWriting,
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
)
from .base import get_or_create_lesson, get_or_create_module

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


async def _add_modules(db: AsyncSession, course_slug: str, modules, first_order: int) -> None:
    """Append modules to an existing course, skipping any already present."""
    result = await db.execute(select(Course).where(Course.slug == course_slug))
    course = result.scalar_one_or_none()
    if course is None:
        return

    from .authoring import _merge  # local import: shared translation-row merge

    for offset, module in enumerate(modules):
        module_id = await get_or_create_module(
            db,
            course.id,
            module.slug,
            first_order + offset,
            _merge(module.title.rows("title"), module.description.rows("description")),
        )
        for lesson_index, lesson in enumerate(module.lessons, start=1):
            await get_or_create_lesson(
                db,
                module_id,
                lesson.slug,
                lesson_index,
                lesson.difficulty,
                lesson.minutes,
                lesson.xp,
                _merge(
                    lesson.title.rows("title"),
                    lesson.story.rows("story"),
                    lesson.objective.rows("objective"),
                    lesson.skills.rows("skills"),
                ),
                [block.to_seed(i + 1) for i, block in enumerate(lesson.blocks)],
                [exercise.to_seed(i + 1) for i, exercise in enumerate(lesson.exercises)],
            )


async def seed_expansions(db: AsyncSession) -> None:
    """Fill the gaps in the courses that predate the roadmap."""
    print("Seeding curriculum expansions...")
    # Existing networking modules occupy orders 1-6; DSA occupies 1-12. New
    # modules are appended after them so nothing is renumbered.
    await _add_modules(db, "networking", NETWORKING_MODULES, first_order=7)
    await _add_modules(db, "data-structures-algorithms", DSA_MODULES, first_order=13)
