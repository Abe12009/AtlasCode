import pytest
from httpx import AsyncClient


class TestNotifications:
    async def test_welcome_notification_created_on_register(self, client: AsyncClient, test_user):
        response = await client.get("/notifications", headers=test_user["headers"])
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(n["type"] == "welcome" for n in data)

    async def test_unread_count_reflects_welcome_notification(self, client: AsyncClient, test_user):
        response = await client.get("/notifications/unread-count", headers=test_user["headers"])
        assert response.status_code == 200
        assert response.json()["count"] >= 1

    async def test_created_at_is_serialized_as_utc(self, client: AsyncClient, test_user):
        # created_at is stored as a naive UTC datetime; the API must mark it
        # explicitly (e.g. "+00:00"/"Z") so clients never parse it as local time.
        response = await client.get("/notifications", headers=test_user["headers"])
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        created_at = data[0]["created_at"]
        assert created_at.endswith("+00:00") or created_at.endswith("Z"), created_at

    async def test_newest_notifications_first(self, client: AsyncClient, test_user):
        await client.post("/exercises/1/submit", headers=test_user["headers"], json={
            "exercise_id": 1,
            "code": "print('Hello, World!')"
        })
        response = await client.get("/notifications", headers=test_user["headers"])
        data = response.json()
        timestamps = [n["created_at"] for n in data]
        assert timestamps == sorted(timestamps, reverse=True)

    async def test_xp_earned_notification_on_correct_submit(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/submit", headers=test_user["headers"], json={
            "exercise_id": 1,
            "code": "print('Hello, World!')"
        })
        assert response.status_code == 200
        assert response.json()["is_correct"] is True

        notifications = (await client.get("/notifications", headers=test_user["headers"])).json()
        xp_notifs = [n for n in notifications if n["type"] == "xp_earned"]
        assert len(xp_notifs) == 1
        assert xp_notifs[0]["data"]["xp"] == 10
        assert xp_notifs[0]["is_read"] is False

    async def test_no_duplicate_xp_notification_on_resubmit(self, client: AsyncClient, test_user):
        payload = {"exercise_id": 1, "code": "print('Hello, World!')"}
        await client.post("/exercises/1/submit", headers=test_user["headers"], json=payload)
        await client.post("/exercises/1/submit", headers=test_user["headers"], json=payload)

        notifications = (await client.get("/notifications", headers=test_user["headers"])).json()
        xp_notifs = [n for n in notifications if n["type"] == "xp_earned"]
        assert len(xp_notifs) == 1

    async def test_lesson_completed_notification(self, client: AsyncClient, test_user):
        await client.get("/lessons/1", headers=test_user["headers"])
        await client.post("/lessons/1/start", headers=test_user["headers"])

        await client.post("/exercises/1/submit", headers=test_user["headers"], json={
            "exercise_id": 1, "code": "print('Hello, World!')"
        })
        await client.post("/exercises/2/submit", headers=test_user["headers"], json={
            "exercise_id": 2, "code": "print('Hello, World!')\nprint('Welcome to MoroccoCode!')"
        })
        # Exercise 3 is a prediction: the answer is the output the code
        # produces, not the code itself.
        await client.post("/exercises/3/submit", headers=test_user["headers"], json={
            "exercise_id": 3, "answer": "Line 1\nLine 2\nLine 3"
        })

        notifications = (await client.get("/notifications?limit=20", headers=test_user["headers"])).json()
        lesson_notifs = [n for n in notifications if n["type"] == "lesson_completed"]
        assert len(lesson_notifs) == 1
        assert lesson_notifs[0]["data"]["lesson_id"] == 1

    async def test_project_completed_notification(self, client: AsyncClient, test_user, db_session):
        """Completing every task of a project raises exactly one project_completed."""
        from sqlalchemy import select
        from app.models import LessonProgress, MissionStatusEnum

        user_id = (await client.get("/auth/me", headers=test_user["headers"])).json()["id"]

        # Lesson 5 is the calculator project's prerequisite.
        result = await db_session.execute(
            select(LessonProgress).where(
                LessonProgress.user_id == user_id, LessonProgress.lesson_id == 5
            )
        )
        progress = result.scalar_one_or_none()
        if progress is None:
            progress = LessonProgress(user_id=user_id, lesson_id=5)
            db_session.add(progress)
        progress.status = MissionStatusEnum.completed
        await db_session.commit()

        assert (await client.post("/projects/1/start", headers=test_user["headers"])).status_code == 200

        codes = {
            1: 'def add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b\n\ndef multiply(a, b):\n    return a * b\n\ndef divide(a, b):\n    if b == 0:\n        return "Error: Division by zero"\n    return a / b\n',
            2: 'def calculate(choice, num1, num2):\n    if choice == "1":\n        return num1 + num2\n    if choice == "2":\n        return num1 - num2\n    if choice == "3":\n        return num1 * num2\n    if choice == "4":\n        if num2 == 0:\n            return "Error: Division by zero"\n        return num1 / num2\n    return "Error: Invalid choice"\n',
            3: 'def process_operations(operations):\n    results = []\n    for choice, num1, num2 in operations:\n        if choice == "5":\n            break\n        if choice == "1":\n            results.append(num1 + num2)\n        elif choice == "2":\n            results.append(num1 - num2)\n        elif choice == "3":\n            results.append(num1 * num2)\n        elif choice == "4":\n            if num2 == 0:\n                results.append("Error: Division by zero")\n            else:\n                results.append(num1 / num2)\n    return results\n',
            4: 'def safe_calculate(choice, num1, num2):\n    if choice not in ["1", "2", "3", "4"]:\n        return (False, "Invalid choice! Please enter 1, 2, 3, or 4.")\n    try:\n        num1 = float(num1)\n        num2 = float(num2)\n    except (ValueError, TypeError):\n        return (False, "Invalid input! Please enter valid numbers.")\n    if choice == "1":\n        return (True, num1 + num2)\n    if choice == "2":\n        return (True, num1 - num2)\n    if choice == "3":\n        return (True, num1 * num2)\n    if num2 == 0:\n        return (False, "Error: Division by zero")\n    return (True, num1 / num2)\n',
        }
        tasks = (await client.get("/projects/1", headers=test_user["headers"])).json()["tasks"]
        for task in sorted(tasks, key=lambda t: t["order"]):
            r = await client.post(
                "/projects/1/submit-task",
                headers=test_user["headers"],
                json={"task_id": task["id"], "code": codes[task["id"]]},
            )
            assert r.status_code == 200, r.text
            assert r.json()["success"] is True, r.text

        notifications = (await client.get("/notifications?limit=50", headers=test_user["headers"])).json()
        project_notifs = [n for n in notifications if n["type"] == "project_completed"]
        assert len(project_notifs) == 1, [n["type"] for n in notifications]
        assert project_notifs[0]["data"]["project_id"] == 1

    async def test_mark_one_read(self, client: AsyncClient, test_user):
        notifications = (await client.get("/notifications", headers=test_user["headers"])).json()
        target_id = notifications[0]["id"]

        response = await client.post(f"/notifications/{target_id}/read", headers=test_user["headers"])
        assert response.status_code == 200
        assert response.json()["is_read"] is True

        unread = (await client.get("/notifications/unread-count", headers=test_user["headers"])).json()
        assert unread["count"] == 0

    async def test_mark_all_read(self, client: AsyncClient, test_user):
        await client.post("/exercises/1/submit", headers=test_user["headers"], json={
            "exercise_id": 1, "code": "print('Hello, World!')"
        })
        before = (await client.get("/notifications/unread-count", headers=test_user["headers"])).json()
        assert before["count"] >= 2

        response = await client.post("/notifications/read-all", headers=test_user["headers"])
        assert response.status_code == 200

        after = (await client.get("/notifications/unread-count", headers=test_user["headers"])).json()
        assert after["count"] == 0

    async def test_unauthenticated_requests_rejected(self, client: AsyncClient):
        assert (await client.get("/notifications")).status_code == 401
        assert (await client.get("/notifications/unread-count")).status_code == 401
        assert (await client.post("/notifications/1/read")).status_code == 401
        assert (await client.post("/notifications/read-all")).status_code == 401

    async def test_cannot_read_nonexistent_notification(self, client: AsyncClient, test_user):
        response = await client.post("/notifications/999999/read", headers=test_user["headers"])
        assert response.status_code == 404

    async def test_isolation_user_cannot_list_or_mark_another_users_notification(
        self, client: AsyncClient, test_user, second_user
    ):
        own_notifications = (await client.get("/notifications", headers=test_user["headers"])).json()
        own_id = own_notifications[0]["id"]

        other_notifications = (await client.get("/notifications", headers=second_user["headers"])).json()
        other_ids = {n["id"] for n in other_notifications}
        assert own_id not in other_ids

        response = await client.post(f"/notifications/{own_id}/read", headers=second_user["headers"])
        assert response.status_code == 404

        # Confirm it's genuinely untouched from the owner's perspective.
        refreshed = (await client.get("/notifications", headers=test_user["headers"])).json()
        assert next(n for n in refreshed if n["id"] == own_id)["is_read"] is False
