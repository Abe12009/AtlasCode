"""Achievement award-checking: app.services.achievements."""

from sqlalchemy import select

from app.models import (
    Course,
    CourseProgress,
    Notification,
    NotificationTypeEnum,
    StudentProfile,
    UserAchievement,
)
from app.services.achievements import check_and_award_achievements


async def _user_id(client, headers):
    me = await client.get("/auth/me", headers=headers)
    return me.json()["id"]


async def _profile(db_session, user_id):
    result = await db_session.execute(
        select(StudentProfile).where(StudentProfile.user_id == user_id)
    )
    return result.scalar_one()


class TestAchievementConditions:
    async def test_lessons_completed_condition(self, client, test_user, db_session):
        user_id = await _user_id(client, test_user["headers"])
        profile = await _profile(db_session, user_id)
        profile.completed_lessons = 1
        await db_session.commit()
        await db_session.refresh(profile)

        earned = await check_and_award_achievements(db_session, user_id, profile)
        await db_session.commit()

        assert "first-lesson" in {a.slug for a in earned}
        assert "five-lessons" not in {a.slug for a in earned}

    async def test_projects_completed_condition(self, client, test_user, db_session):
        user_id = await _user_id(client, test_user["headers"])
        profile = await _profile(db_session, user_id)
        profile.completed_projects = 1
        await db_session.commit()
        await db_session.refresh(profile)

        earned = await check_and_award_achievements(db_session, user_id, profile)
        await db_session.commit()

        assert "first-project" in {a.slug for a in earned}

    async def test_streak_condition(self, client, test_user, db_session):
        user_id = await _user_id(client, test_user["headers"])
        profile = await _profile(db_session, user_id)
        profile.streak = 3
        await db_session.commit()
        await db_session.refresh(profile)

        earned = await check_and_award_achievements(db_session, user_id, profile)
        await db_session.commit()

        slugs = {a.slug for a in earned}
        assert "streak-3" in slugs
        assert "streak-7" not in slugs

    async def test_level_condition(self, client, test_user, db_session):
        user_id = await _user_id(client, test_user["headers"])
        profile = await _profile(db_session, user_id)
        profile.xp = 400  # level_for_xp(400) == 400 // 100 + 1 == 5
        await db_session.commit()
        await db_session.refresh(profile)

        earned = await check_and_award_achievements(db_session, user_id, profile)
        await db_session.commit()

        assert "level-5" in {a.slug for a in earned}

    async def test_courses_completed_condition(self, client, test_user, db_session):
        user_id = await _user_id(client, test_user["headers"])
        profile = await _profile(db_session, user_id)
        course = (await db_session.execute(select(Course).limit(1))).scalar_one()
        db_session.add(
            CourseProgress(
                user_id=user_id, course_id=course.id, completed_lessons=5, total_lessons=5, progress_percent=100.0
            )
        )
        await db_session.commit()
        await db_session.refresh(profile)

        earned = await check_and_award_achievements(db_session, user_id, profile)
        await db_session.commit()

        assert "first-course" in {a.slug for a in earned}

    async def test_dynamic_all_lessons_threshold_uses_real_catalog_size(
        self, client, test_user, db_session
    ):
        """Regression test: all-lessons must not fire at the stale seeded
        condition_value (47) when the real catalog has more lessons than
        that -- its threshold is computed from the live Lesson count."""
        from app.models import Lesson

        total_lessons = (await db_session.execute(select(Lesson))).scalars().all()
        total = len(total_lessons)

        user_id = await _user_id(client, test_user["headers"])
        profile = await _profile(db_session, user_id)

        profile.completed_lessons = total - 1
        await db_session.commit()
        await db_session.refresh(profile)
        earned = await check_and_award_achievements(db_session, user_id, profile)
        await db_session.commit()
        assert "all-lessons" not in {a.slug for a in earned}

        profile.completed_lessons = total
        await db_session.commit()
        await db_session.refresh(profile)
        earned = await check_and_award_achievements(db_session, user_id, profile)
        await db_session.commit()
        assert "all-lessons" in {a.slug for a in earned}


class TestAchievementIdempotency:
    async def test_running_checker_twice_does_not_double_award(self, client, test_user, db_session):
        user_id = await _user_id(client, test_user["headers"])
        profile = await _profile(db_session, user_id)
        profile.streak = 3
        await db_session.commit()
        await db_session.refresh(profile)

        first = await check_and_award_achievements(db_session, user_id, profile)
        await db_session.commit()
        await db_session.refresh(profile)

        second = await check_and_award_achievements(db_session, user_id, profile)
        await db_session.commit()

        assert "streak-3" in {a.slug for a in first}
        assert second == []

        from app.models import Achievement

        streak_3_id = (
            await db_session.execute(select(Achievement.id).where(Achievement.slug == "streak-3"))
        ).scalar_one()
        streak_3_rows = (
            await db_session.execute(
                select(UserAchievement).where(
                    UserAchievement.user_id == user_id,
                    UserAchievement.achievement_id == streak_3_id,
                )
            )
        ).scalars().all()
        assert len(streak_3_rows) == 1

    async def test_cascading_award_in_a_single_call(self, client, test_user, db_session):
        """first-lesson's own XP reward (+50) can push xp from 390 (level 4)
        to 440 (level 5) inside one call -- the checker must catch level-5
        in the same pass rather than requiring a second triggering action."""
        user_id = await _user_id(client, test_user["headers"])
        profile = await _profile(db_session, user_id)
        profile.xp = 390
        profile.completed_lessons = 1
        await db_session.commit()
        await db_session.refresh(profile)

        earned = await check_and_award_achievements(db_session, user_id, profile)
        await db_session.commit()

        slugs = {a.slug for a in earned}
        assert "first-lesson" in slugs
        assert "level-5" in slugs


class TestAchievementPublicProfileSerialization:
    async def test_earned_achievement_renders_on_public_profile(
        self, client, test_user, db_session
    ):
        """Regression test: AchievementTranslationResponse was missing
        `Config.from_attributes = True`, so any account with a real,
        earned achievement 500'd on GET /users/{username} instead of
        rendering it -- undetected until the first achievement was ever
        actually awarded, since nothing before this could create one."""
        toggle = await client.patch(
            "/auth/me", headers=test_user["headers"], json={"profile_visibility": "public"}
        )
        assert toggle.status_code == 200

        user_id = await _user_id(client, test_user["headers"])
        profile = await _profile(db_session, user_id)
        profile.completed_lessons = 1
        await db_session.commit()
        await db_session.refresh(profile)
        await check_and_award_achievements(db_session, user_id, profile)
        await db_session.commit()

        response = await client.get(
            f"/users/{test_user['data']['username']}", headers=test_user["headers"]
        )
        assert response.status_code == 200
        slugs = {a["achievement"]["slug"] for a in response.json()["achievements"]}
        assert "first-lesson" in slugs


class TestAchievementNotification:
    async def test_award_creates_a_notification(self, client, test_user, db_session):
        user_id = await _user_id(client, test_user["headers"])
        profile = await _profile(db_session, user_id)
        profile.completed_lessons = 1
        await db_session.commit()
        await db_session.refresh(profile)

        await check_and_award_achievements(db_session, user_id, profile)
        await db_session.commit()

        notifications = (
            await db_session.execute(
                select(Notification).where(
                    Notification.user_id == user_id,
                    Notification.type == NotificationTypeEnum.achievement_earned,
                )
            )
        ).scalars().all()
        assert len(notifications) == 1
