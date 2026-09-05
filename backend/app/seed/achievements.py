from .base import LanguageEnum
from app.models import Achievement, AchievementTranslation
from sqlalchemy import select


async def seed_achievements(db):
    print("Seeding Achievements...")
    
    achievements = [
        Achievement(slug="first-lesson", icon="🎓", xp_reward=50, condition_type="lessons_completed", condition_value=1),
        Achievement(slug="five-lessons", icon="📚", xp_reward=100, condition_type="lessons_completed", condition_value=5),
        Achievement(slug="ten-lessons", icon="🏅", xp_reward=200, condition_type="lessons_completed", condition_value=10),
        Achievement(slug="twenty-lessons", icon="🌟", xp_reward=500, condition_type="lessons_completed", condition_value=20),
        Achievement(slug="all-lessons", icon="🎯", xp_reward=1000, condition_type="lessons_completed", condition_value=47),
        Achievement(slug="first-course", icon="🏆", xp_reward=200, condition_type="courses_completed", condition_value=1),
        Achievement(slug="three-courses", icon="🥇", xp_reward=500, condition_type="courses_completed", condition_value=3),
        Achievement(slug="all-courses", icon="👑", xp_reward=1000, condition_type="courses_completed", condition_value=5),
        Achievement(slug="streak-3", icon="🔥", xp_reward=50, condition_type="streak", condition_value=3),
        Achievement(slug="streak-7", icon="🔥🔥", xp_reward=100, condition_type="streak", condition_value=7),
        Achievement(slug="streak-14", icon="🔥🔥🔥", xp_reward=200, condition_type="streak", condition_value=14),
        Achievement(slug="streak-30", icon="🏅🔥", xp_reward=500, condition_type="streak", condition_value=30),
        Achievement(slug="level-5", icon="⭐", xp_reward=100, condition_type="level", condition_value=5),
        Achievement(slug="level-10", icon="⭐⭐", xp_reward=300, condition_type="level", condition_value=10),
        Achievement(slug="level-20", icon="⭐⭐⭐", xp_reward=1000, condition_type="level", condition_value=20),
        Achievement(slug="first-project", icon="🚀", xp_reward=200, condition_type="projects_completed", condition_value=1),
        Achievement(slug="three-projects", icon="🚀🚀", xp_reward=500, condition_type="projects_completed", condition_value=3),
        Achievement(slug="all-projects", icon="🚀🚀🚀", xp_reward=1000, condition_type="projects_completed", condition_value=5),
    ]
    db.add_all(achievements)
    await db.flush()
    
    for ach in achievements:
        ach_translations = [
            AchievementTranslation(achievement_id=ach.id, language=LanguageEnum.en, 
                title=ach.slug.replace("-", " ").title(), 
                description=f"Earned for {ach.condition_type.replace('_', ' ')} {ach.condition_value}"),
            AchievementTranslation(achievement_id=ach.id, language=LanguageEnum.fr, 
                title=ach.slug.replace("-", " ").title(), 
                description=f"Gagné pour {ach.condition_type.replace('_', ' ')} {ach.condition_value}"),
            AchievementTranslation(achievement_id=ach.id, language=LanguageEnum.ar, 
                title=ach.slug.replace("-", " ").title(), 
                description=f"تم الحصول عليه لـ {ach.condition_type.replace('_', ' ')} {ach.condition_value}"),
        ]
        db.add_all(ach_translations)
    
    print("Achievements seeded successfully!")