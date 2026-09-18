"""Orientini seed data: institutions and the matching quiz.

Every institution's ``trait_weights`` (used for matching, see
app.services.orientini) reflects general, defensible characterizations of how
each institution type is known to work (hands-on vs. theoretical, exam-driven
vs. project-driven, etc.) -- these are qualitative judgment calls, not cited
facts, and are fine to seed directly.

``InstitutionRequirement`` is different: min Bac averages, entrance exam
names/formats, and Bac-track eligibility are specific, consequential facts a
real student could rely on. None of those are seeded here -- every requirement
row is created with every factual field NULL and ``data_verified=False``, so
the API/frontend surface them as "needs verification" rather than fact. Fill
these in (and flip ``data_verified``) only once the real figures are
confirmed.

Idempotent by slug, same as every other seeder in this package.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Institution,
    InstitutionRequirement,
    InstitutionTranslation,
    InstitutionTypeEnum,
    OrientiniOption,
    OrientiniOptionTranslation,
    OrientiniQuestion,
    OrientiniQuestionTranslation,
)

from .authoring import T, _merge


@dataclass(frozen=True)
class InstitutionSpec:
    slug: str
    type: InstitutionTypeEnum
    icon: str
    name: T
    description: T
    career_outcomes: T
    #: trait_key -> weight, see app.services.orientini.TRAIT_KEYS.
    trait_weights: dict


INSTITUTIONS: tuple[InstitutionSpec, ...] = (
    InstitutionSpec(
        "1337",
        InstitutionTypeEnum.code_school,
        "🧩",
        T("1337 Coding School", "1337 Coding School", "مدرسة 1337 للبرمجة"),
        T(
            "A tuition-free, peer-to-peer coding school with no teachers and no lectures — you learn entirely by building projects and getting help from other students.",
            "Une école de code gratuite, en pair-à-pair, sans professeurs ni cours magistraux — vous apprenez uniquement en réalisant des projets et en vous entraidant entre étudiants.",
            "مدرسة برمجة مجانية تعتمد التعلم بين الأقران، دون أساتذة أو محاضرات — تتعلم فيها فقط عبر إنجاز المشاريع ومساعدة الطلاب الآخرين.",
        ),
        T(
            "Software development, systems programming, and roles at tech companies that value hands-on project portfolios over diplomas.",
            "Développement logiciel, programmation système, et postes dans des entreprises tech qui valorisent un portfolio de projets concrets plutôt qu'un diplôme classique.",
            "تطوير البرمجيات، برمجة الأنظمة، ووظائف في شركات تقنية تُقدّر ملف الإنجازات العملي أكثر من الشهادة التقليدية.",
        ),
        {"hands_on": 3, "theory": -1, "competitive_exam": 1, "research_academic": -1, "entrepreneurial": 1},
    ),
    InstitutionSpec(
        "youcode",
        InstitutionTypeEnum.code_school,
        "💻",
        T("YouCode", "YouCode", "يوكود"),
        T(
            "A project-based coding bootcamp network (part of the UM6P ecosystem) focused on practical software development skills over a few intensive years.",
            "Un réseau d'écoles de code basées sur les projets (au sein de l'écosystème UM6P), axé sur des compétences pratiques en développement logiciel sur quelques années intensives.",
            "شبكة مدارس برمجة قائمة على المشاريع (ضمن منظومة UM6P)، تركز على مهارات التطوير العملي للبرمجيات خلال سنوات مكثفة.",
        ),
        T(
            "Web/mobile development and junior software engineering roles, with an emphasis on a hands-on portfolio.",
            "Développement web/mobile et postes de développeur junior, avec un accent sur un portfolio pratique.",
            "تطوير الويب والتطبيقات ووظائف مهندس برمجيات مبتدئ، مع التركيز على ملف إنجازات عملي.",
        ),
        {"hands_on": 3, "theory": -1, "entrepreneurial": 2},
    ),
    InstitutionSpec(
        "est",
        InstitutionTypeEnum.est,
        "🛠️",
        T("EST — École Supérieure de Technologie", "EST — École Supérieure de Technologie", "المدرسة العليا للتكنولوجيا (EST)"),
        T(
            "Public two-year technical institutes offering applied, hands-on training across technology specialties, with an option to continue toward a licence professionnelle.",
            "Instituts techniques publics de deux ans offrant une formation appliquée dans diverses spécialités technologiques, avec une possibilité de poursuivre vers une licence professionnelle.",
            "معاهد تقنية عمومية مدتها سنتان تقدم تكوينًا تطبيقيًا في تخصصات تكنولوجية متعددة، مع إمكانية متابعة الدراسة نحو إجازة مهنية.",
        ),
        T(
            "Technician and applied-engineering roles, or a bridge into a longer engineering track.",
            "Postes de technicien et d'ingénierie appliquée, ou passerelle vers un cursus d'ingénieur plus long.",
            "وظائف تقني ومهندس تطبيقي، أو جسر نحو مسار هندسي أطول.",
        ),
        {"hands_on": 2, "math_intensity": 1},
    ),
    InstitutionSpec(
        "fst",
        InstitutionTypeEnum.fst,
        "🔬",
        T("FST — Faculté des Sciences et Techniques", "FST — Faculté des Sciences et Techniques", "كلية العلوم والتقنيات (FST)"),
        T(
            "Public science and technology faculties offering longer academic degrees with a stronger theoretical and research grounding than the ESTs.",
            "Facultés publiques des sciences et techniques proposant des cursus académiques plus longs, avec un ancrage théorique et scientifique plus poussé que les EST.",
            "كليات عمومية للعلوم والتقنيات تقدم مسارات أكاديمية أطول، بتأسيس نظري وعلمي أعمق مقارنة بالمعاهد العليا للتكنولوجيا.",
        ),
        T(
            "Roles requiring deeper theoretical grounding, further graduate study, or research.",
            "Postes nécessitant une base théorique plus approfondie, poursuite d'études supérieures, ou recherche.",
            "وظائف تتطلب تأسيسًا نظريًا أعمق، أو متابعة الدراسات العليا، أو البحث العلمي.",
        ),
        {"theory": 2, "math_intensity": 2, "research_academic": 2, "entrepreneurial": -1},
    ),
    InstitutionSpec(
        "cpge",
        InstitutionTypeEnum.cpge,
        "📐",
        T("CPGE — Classes Préparatoires", "CPGE — Classes Préparatoires", "الأقسام التحضيرية (CPGE)"),
        T(
            "An intensive two-year academic track that prepares students for competitive entrance exams into top engineering and business schools, in Morocco and abroad.",
            "Un cursus académique intensif de deux ans préparant aux concours d'entrée dans les grandes écoles d'ingénieurs et de commerce, au Maroc et à l'étranger.",
            "مسار أكاديمي مكثف مدته سنتان يُحضّر الطلاب لمباريات ولوج المدارس العليا للهندسة والتجارة، داخل المغرب وخارجه.",
        ),
        T(
            "Entry into selective engineering/business grandes écoles; a demanding, exam-driven path.",
            "Accès à des grandes écoles sélectives d'ingénieurs ou de commerce ; un parcours exigeant, rythmé par les concours.",
            "الولوج إلى مدارس عليا انتقائية للهندسة أو التجارة؛ مسار صعب يعتمد على المباريات.",
        ),
        {"hands_on": -2, "theory": 3, "math_intensity": 3, "competitive_exam": 3, "research_academic": 1, "entrepreneurial": -1},
    ),
    InstitutionSpec(
        "engineering-school",
        InstitutionTypeEnum.engineering_school,
        "⚙️",
        T("Engineering School (Grande École d'Ingénieurs)", "École d'Ingénieurs (Grande École)", "مدرسة مهندسين (مدرسة عليا)"),
        T(
            "Multi-year engineering programs (public or private) combining theory, applied projects, and internships, generally entered via a competitive exam or selective file-based process.",
            "Cursus d'ingénieur pluriannuels (publics ou privés) combinant théorie, projets appliqués et stages, généralement accessibles via concours ou dossier sélectif.",
            "مسارات هندسية متعددة السنوات (عمومية أو خاصة) تجمع بين النظري والمشاريع التطبيقية والتداريب، يتم الولوج إليها عادة عبر مباراة أو ملف انتقائي.",
        ),
        T(
            "Engineering roles across industries — the traditional route into Morocco's engineering profession.",
            "Postes d'ingénieur dans divers secteurs — la voie traditionnelle vers la profession d'ingénieur au Maroc.",
            "وظائف هندسية في مختلف القطاعات — المسار التقليدي لمهنة الهندسة في المغرب.",
        ),
        {"hands_on": 1, "theory": 2, "math_intensity": 2, "competitive_exam": 2, "research_academic": 1, "entrepreneurial": 1},
    ),
)


@dataclass(frozen=True)
class OptionSpec:
    text: T
    trait_weights: dict


@dataclass(frozen=True)
class QuestionSpec:
    text: T
    options: tuple[OptionSpec, ...]


QUESTIONS: tuple[QuestionSpec, ...] = (
    QuestionSpec(
        T(
            "When you build something, what feels most satisfying?",
            "Quand vous construisez quelque chose, qu'est-ce qui vous procure le plus de satisfaction ?",
            "عندما تصنع شيئًا، ما الذي يمنحك أكبر قدر من الرضا؟",
        ),
        (
            OptionSpec(T("Seeing it work immediately, hands-on", "Le voir fonctionner immédiatement, en pratique", "رؤيته يعمل فورًا، بشكل عملي"), {"hands_on": 3, "theory": -1}),
            OptionSpec(T("Understanding deeply why it works", "Comprendre en profondeur pourquoi ça fonctionne", "فهم سبب عمله بعمق"), {"theory": 3, "research_academic": 2}),
            OptionSpec(T("Solving a hard technical puzzle under pressure", "Résoudre un problème technique difficile sous pression", "حل مسألة تقنية صعبة تحت الضغط"), {"competitive_exam": 2, "math_intensity": 2}),
            OptionSpec(T("Turning it into something people would pay for", "En faire quelque chose que les gens paieraient", "تحويله إلى شيء يدفع الناس مقابله"), {"entrepreneurial": 3}),
        ),
    ),
    QuestionSpec(
        T(
            "How do you feel about math-heavy coursework?",
            "Que pensez-vous des cursus très chargés en mathématiques ?",
            "ما رأيك في المقررات الدراسية التي تعتمد بكثافة على الرياضيات؟",
        ),
        (
            OptionSpec(T("Love it, the harder the better", "J'adore, plus c'est difficile mieux c'est", "أحبها، وكلما كانت أصعب كان أفضل"), {"math_intensity": 3, "theory": 1}),
            OptionSpec(T("Fine in moderation", "Ça va, avec modération", "لا بأس بها باعتدال"), {"math_intensity": 1}),
            OptionSpec(T("Prefer to minimize it", "Je préfère en avoir le moins possible", "أفضّل تقليلها قدر الإمكان"), {"math_intensity": -2, "hands_on": 1}),
            OptionSpec(T("Depends whether it's applied to something real", "Ça dépend si c'est appliqué à quelque chose de concret", "يعتمد الأمر على ما إذا كانت مطبقة على شيء واقعي"), {"math_intensity": 1, "hands_on": 1}),
        ),
    ),
    QuestionSpec(
        T(
            "How do you feel about competitive, high-stakes entrance exams (concours)?",
            "Que pensez-vous des concours d'entrée compétitifs et à fort enjeu ?",
            "ما رأيك في مباريات الولوج التنافسية وذات الرهان العالي؟",
        ),
        (
            OptionSpec(T("Bring it on, I thrive under pressure", "Je suis prêt, je m'épanouis sous pression", "أنا مستعد، أتألق تحت الضغط"), {"competitive_exam": 3}),
            OptionSpec(T("I'd rather prove myself through projects over time", "Je préfère faire mes preuves à travers des projets, avec le temps", "أفضّل إثبات نفسي عبر المشاريع مع مرور الوقت"), {"competitive_exam": -2, "hands_on": 2}),
            OptionSpec(T("Open to it if well-prepared", "Ouvert à l'idée si je suis bien préparé", "منفتح على الفكرة إذا كنت مستعدًا جيدًا"), {"competitive_exam": 1}),
            OptionSpec(T("Strongly prefer to avoid it", "Je préfère fortement l'éviter", "أفضّل بشدة تجنب ذلك"), {"competitive_exam": -3}),
        ),
    ),
    QuestionSpec(
        T(
            "Which learning environment excites you more?",
            "Quel environnement d'apprentissage vous motive le plus ?",
            "أي بيئة تعليمية تثير حماسك أكثر؟",
        ),
        (
            OptionSpec(T("An intensive peer-learning coding bootcamp with no lectures", "Un bootcamp de code intensif en pair-à-pair, sans cours magistraux", "معسكر برمجة مكثف قائم على التعلم بين الأقران، دون محاضرات"), {"hands_on": 3, "entrepreneurial": 1, "theory": -2}),
            OptionSpec(T("A traditional university with professors and research labs", "Une université traditionnelle avec professeurs et laboratoires de recherche", "جامعة تقليدية بأساتذة ومختبرات بحثية"), {"theory": 2, "research_academic": 3}),
            OptionSpec(T("A selective two-year prep track before a top engineering school", "Un cursus préparatoire sélectif de deux ans avant une grande école d'ingénieurs", "مسار تحضيري انتقائي مدته سنتان قبل الولوج لمدرسة مهندسين مرموقة"), {"competitive_exam": 2, "theory": 2, "math_intensity": 2}),
            OptionSpec(T("A technical school mixing theory and hands-on practice", "Une école technique alliant théorie et pratique", "مدرسة تقنية تجمع بين النظري والتطبيقي"), {"hands_on": 1, "theory": 1}),
        ),
    ),
    QuestionSpec(
        T(
            "What's your longer-term goal?",
            "Quel est votre objectif à long terme ?",
            "ما هو هدفك على المدى الطويل؟",
        ),
        (
            OptionSpec(T("Start my own company or product", "Créer ma propre entreprise ou mon propre produit", "تأسيس شركتي أو منتجي الخاص"), {"entrepreneurial": 3}),
            OptionSpec(T("Become a specialized engineer at a top firm", "Devenir ingénieur spécialisé dans une entreprise de premier plan", "أن أصبح مهندسًا متخصصًا في شركة رائدة"), {"theory": 1, "competitive_exam": 1, "math_intensity": 1}),
            OptionSpec(T("Do research or pursue further academic study", "Faire de la recherche ou poursuivre des études académiques", "القيام بالبحث العلمي أو متابعة الدراسات الأكاديمية"), {"research_academic": 3, "theory": 2}),
            OptionSpec(T("Get a solid, practical job quickly", "Obtenir rapidement un emploi solide et concret", "الحصول على عمل عملي وثابت بسرعة"), {"hands_on": 2, "entrepreneurial": 1}),
        ),
    ),
    QuestionSpec(
        T(
            "How do you prefer to learn?",
            "Comment préférez-vous apprendre ?",
            "كيف تفضّل التعلم؟",
        ),
        (
            OptionSpec(T("By building projects and debugging real code", "En construisant des projets et en déboguant du vrai code", "من خلال بناء مشاريع وتصحيح أخطاء برمجية حقيقية"), {"hands_on": 3}),
            OptionSpec(T("Through lectures, textbooks, and problem sets", "Par des cours magistraux, manuels et séries d'exercices", "عبر المحاضرات والكتب المدرسية وسلاسل التمارين"), {"theory": 3}),
            OptionSpec(T("In structured, exam-driven prep with a class cohort", "Dans une préparation structurée, rythmée par les examens, avec une promotion", "في تحضير منظم يعتمد على الامتحانات ضمن فوج دراسي"), {"competitive_exam": 2, "theory": 1}),
            OptionSpec(T("A mix of internships and coursework", "Un mélange de stages et de cours", "مزيج من التداريب والمقررات الدراسية"), {"hands_on": 1, "theory": 1}),
        ),
    ),
    QuestionSpec(
        T(
            "A 2-3 year fast track vs. a longer 5-year engineering degree — how do you feel?",
            "Une filière rapide de 2-3 ans vs. un cursus d'ingénieur plus long de 5 ans — qu'en pensez-vous ?",
            "مسار سريع من سنتين إلى ثلاث سنوات مقابل شهادة هندسة أطول مدتها خمس سنوات — ما رأيك؟",
        ),
        (
            OptionSpec(T("Faster is better, I want to work ASAP", "Plus rapide c'est mieux, je veux travailler au plus vite", "الأسرع أفضل، أريد العمل في أقرب وقت ممكن"), {"hands_on": 2, "entrepreneurial": 1, "theory": -1}),
            OptionSpec(T("I don't mind the longer path if it leads somewhere prestigious", "Le parcours plus long ne me dérange pas s'il mène quelque part de prestigieux", "لا يزعجني المسار الأطول إذا كان يؤدي إلى شيء مرموق"), {"theory": 1, "competitive_exam": 2}),
            OptionSpec(T("Doesn't matter as long as I learn deeply", "Peu importe tant que j'apprends en profondeur", "لا يهم طالما أتعلم بعمق"), {"theory": 2, "research_academic": 1}),
            OptionSpec(T("I'd like flexibility to decide later", "J'aimerais garder de la flexibilité pour décider plus tard", "أرغب في الاحتفاظ بمرونة لاتخاذ القرار لاحقًا"), {"hands_on": 0}),
        ),
    ),
    QuestionSpec(
        T(
            "Which subject do you enjoy most in your Bac track?",
            "Quelle matière préférez-vous dans votre filière du Bac ?",
            "أي مادة تفضّلها في شعبتك بالباكالوريا؟",
        ),
        (
            OptionSpec(T("Programming / technology-related subjects", "Programmation / matières liées à la technologie", "البرمجة / المواد المرتبطة بالتكنولوجيا"), {"hands_on": 2}),
            OptionSpec(T("Pure mathematics", "Mathématiques pures", "الرياضيات المحضة"), {"math_intensity": 3, "theory": 1}),
            OptionSpec(T("Physics / engineering sciences", "Physique / sciences de l'ingénieur", "الفيزياء / العلوم الهندسية"), {"math_intensity": 2, "theory": 1}),
            OptionSpec(T("Life sciences (SVT)", "Sciences de la vie et de la terre (SVT)", "علوم الحياة والأرض"), {"research_academic": 1, "theory": 1}),
        ),
    ),
)


async def _get_or_create_institution(db: AsyncSession, spec: InstitutionSpec, order: int) -> Institution:
    result = await db.execute(select(Institution).where(Institution.slug == spec.slug))
    institution = result.scalar_one_or_none()
    if institution is None:
        institution = Institution(
            slug=spec.slug,
            type=spec.type,
            icon=spec.icon,
            order=order,
            trait_weights=json.dumps(spec.trait_weights),
        )
        db.add(institution)
        await db.flush()
        for row in _merge(
            spec.name.rows("name"),
            spec.description.rows("description"),
            spec.career_outcomes.rows("career_outcomes"),
        ):
            db.add(InstitutionTranslation(institution_id=institution.id, **row))
        db.add(
            InstitutionRequirement(
                institution_id=institution.id,
                data_verified=False,
                verification_notes=(
                    "Admission requirements (Bac-track eligibility, minimum average, "
                    "entrance exam name/format, application window) have not been "
                    "confirmed against an authoritative source yet."
                ),
            )
        )
        await db.flush()
    return institution


async def _get_or_create_question(db: AsyncSession, spec: QuestionSpec, order: int) -> None:
    result = await db.execute(
        select(OrientiniQuestion)
        .join(OrientiniQuestionTranslation)
        .where(OrientiniQuestionTranslation.text == spec.text.en)
    )
    if result.scalars().first() is not None:
        return

    question = OrientiniQuestion(order=order)
    db.add(question)
    await db.flush()
    for row in spec.text.rows("text"):
        db.add(OrientiniQuestionTranslation(question_id=question.id, **row))

    for option_order, option_spec in enumerate(spec.options, start=1):
        option = OrientiniOption(
            question_id=question.id,
            order=option_order,
            trait_weights=json.dumps(option_spec.trait_weights),
        )
        db.add(option)
        await db.flush()
        for row in option_spec.text.rows("text"):
            db.add(OrientiniOptionTranslation(option_id=option.id, **row))


async def seed_orientini(db: AsyncSession) -> None:
    for position, spec in enumerate(INSTITUTIONS, start=1):
        await _get_or_create_institution(db, spec, position)

    for position, spec in enumerate(QUESTIONS, start=1):
        await _get_or_create_question(db, spec, position)
