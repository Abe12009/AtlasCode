"""Course catalog sections: the top-level grouping shown in the course list.

Separate from the roadmap (app.curriculum): the roadmap orders *every* course
into one continuous degree-style sequence via stage/prerequisite, while a
Section is a coarser, browsable subject area (Programming, Networking, ...)
that a student picks from directly. A course can belong to at most one
section; foundational/theory courses that underpin every section are left
unsectioned on purpose (section_id stays NULL) rather than forced into one.

Idempotent by slug at both levels, same as every other seeder in this
package: rerunning never creates a duplicate section and never moves a course
that a prior run already placed unless this file's mapping changed it.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Course, Section, SectionTranslation

from .authoring import T, _merge


@dataclass(frozen=True)
class SectionSpec:
    slug: str
    icon: str
    title: T
    description: T
    #: Course slugs placed in this section, in display order. A slug with no
    #: matching seeded course is skipped rather than failing the whole pass,
    #: so this list can stay ahead of what content actually exists yet.
    course_slugs: tuple[str, ...]


SECTIONS: tuple[SectionSpec, ...] = (
    SectionSpec(
        "programming",
        "💻",
        T("Programming", "Programmation", "البرمجة"),
        T(
            "Learn to write real software in the languages the industry actually uses.",
            "Apprenez à écrire de vrais logiciels dans les langages réellement utilisés par l'industrie.",
            "تعلّم كتابة برمجيات حقيقية باللغات التي تستخدمها الصناعة فعليًا.",
        ),
        ("python-basics", "python-in-depth", "web-basics", "javascript", "java"),
    ),
    SectionSpec(
        "data-structures-algorithms",
        "🌳",
        T("Data Structures & Algorithms", "Structures de Données & Algorithmes", "هياكل البيانات والخوارزميات"),
        T(
            "The building blocks and problem-solving patterns behind every technical interview and every fast program.",
            "Les briques de base et les schémas de résolution derrière chaque entretien technique et chaque programme rapide.",
            "اللبنات الأساسية وأنماط حل المسائل وراء كل مقابلة تقنية وكل برنامج سريع.",
        ),
        ("data-structures-algorithms", "algorithms-complexity"),
    ),
    SectionSpec(
        "computer-systems",
        "🖥️",
        T("Computer Systems", "Systèmes Informatiques", "أنظمة الحاسوب"),
        T(
            "What actually happens inside a computer: CPUs, memory, storage, and the operating system tying it together.",
            "Ce qui se passe réellement à l'intérieur d'un ordinateur : CPU, mémoire, stockage, et le système d'exploitation qui relie tout.",
            "ما يحدث فعليًا داخل الحاسوب: المعالجات والذاكرة والتخزين ونظام التشغيل الذي يربط كل ذلك.",
        ),
        ("computer-systems", "computer-architecture", "operating-systems", "advanced-computing"),
    ),
    SectionSpec(
        "networking",
        "🌐",
        T("Networking", "Réseaux", "الشبكات"),
        T(
            "How devices actually talk to each other, from a single cable to the global internet.",
            "Comment les appareils communiquent réellement entre eux, d'un simple câble à l'internet mondial.",
            "كيف تتواصل الأجهزة فعليًا فيما بينها، من كابل واحد إلى الإنترنت العالمي.",
        ),
        ("networking",),
    ),
    SectionSpec(
        "databases",
        "🗄️",
        T("Databases", "Bases de Données", "قواعد البيانات"),
        T(
            "Model, store, and query data reliably — from your first SQL query to schema design that scales.",
            "Modélisez, stockez et interrogez les données de façon fiable — de votre première requête SQL à une conception de schéma qui tient à l'échelle.",
            "نمذجة البيانات وتخزينها والاستعلام عنها بموثوقية — من أول استعلام SQL إلى تصميم مخطط قابل للتوسّع.",
        ),
        ("sql-databases", "database-design"),
    ),
    SectionSpec(
        "software-engineering",
        "🏗️",
        T("Software Engineering", "Génie Logiciel", "هندسة البرمجيات"),
        T(
            "The practices that turn code that works into software a team can build on: version control, architecture, and process.",
            "Les pratiques qui transforment du code qui fonctionne en logiciel sur lequel une équipe peut s'appuyer : contrôle de version, architecture et processus.",
            "الممارسات التي تحوّل الكود العامل إلى برمجيات يمكن لفريق البناء عليها: التحكّم بالإصدارات، والمعمارية، والمنهجية.",
        ),
        ("git-github", "software-engineering"),
    ),
    SectionSpec(
        "ai-machine-learning",
        "🤖",
        T("AI & Machine Learning", "IA & Apprentissage Automatique", "الذكاء الاصطناعي وتعلّم الآلة"),
        T(
            "What AI actually is, how machine learning works under the hood, and how to use it responsibly.",
            "Ce qu'est réellement l'IA, comment fonctionne l'apprentissage automatique en coulisses, et comment l'utiliser de façon responsable.",
            "ما هو الذكاء الاصطناعي فعليًا، وكيف يعمل تعلّم الآلة من الداخل، وكيف تستخدمه بمسؤولية.",
        ),
        ("ai-foundations", "machine-learning-fundamentals", "ai-literacy", "natural-language-processing"),
    ),
    SectionSpec(
        "cybersecurity",
        "🛡️",
        T("Cybersecurity", "Cybersécurité", "الأمن السيبراني"),
        T(
            "Defend systems and data: the principles, cryptography, and secure-development practices behind real security work.",
            "Défendez les systèmes et les données : les principes, la cryptographie et les pratiques de développement sécurisé derrière le vrai travail de sécurité.",
            "الدفاع عن الأنظمة والبيانات: المبادئ والتشفير وممارسات التطوير الآمن وراء عمل الأمن الحقيقي.",
        ),
        ("cybersecurity-foundations", "network-security-fundamentals", "secure-software-development", "security-architecture"),
    ),
)


async def _get_or_create_section(db: AsyncSession, spec: SectionSpec, order: int) -> int:
    result = await db.execute(select(Section).where(Section.slug == spec.slug))
    section = result.scalar_one_or_none()
    if section is None:
        section = Section(slug=spec.slug, order=order, icon=spec.icon)
        db.add(section)
        await db.flush()
        for row in _merge(spec.title.rows("title"), spec.description.rows("description")):
            db.add(SectionTranslation(section_id=section.id, **row))
        await db.flush()
    return section.id


async def seed_sections(db: AsyncSession) -> int:
    """Create every section and assign its courses. Returns rows changed.

    Only ever sets `section_id` on a course that exists and whose section
    differs from what's declared here — never touches a course's content,
    id, slug, or any other placement metadata (stage/order/track stay
    exactly what app.seed.roadmap set them to).
    """
    changed = 0
    for position, spec in enumerate(SECTIONS, start=1):
        section_id = await _get_or_create_section(db, spec, position)

        result = await db.execute(select(Course).where(Course.slug.in_(spec.course_slugs)))
        for course in result.scalars().all():
            if course.section_id != section_id:
                course.section_id = section_id
                changed += 1

    return changed
