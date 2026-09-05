import pytest
from httpx import AsyncClient


class TestCourses:
    async def test_get_courses_list(self, client: AsyncClient, test_user):
        response = await client.get("/courses", headers=test_user["headers"])
        assert response.status_code == 200
        courses = response.json()
        assert isinstance(courses, list)
        assert len(courses) >= 2
        
        course_slugs = {c["slug"] for c in courses}
        assert "python-basics" in course_slugs
        assert "web-basics" in course_slugs

    async def test_get_course_detail(self, client: AsyncClient, test_user):
        response = await client.get("/courses/1", headers=test_user["headers"])
        assert response.status_code == 200
        course = response.json()
        assert course["id"] == 1
        assert "modules" in course
        assert len(course["modules"]) > 0

    async def test_get_all_course_details(self, client: AsyncClient, test_user):
        for course_id in [1, 2]:
            response = await client.get(f"/courses/{course_id}", headers=test_user["headers"])
            assert response.status_code == 200
            course = response.json()
            assert course["id"] == course_id
            assert "modules" in course

    async def test_course_progress(self, client: AsyncClient, test_user):
        response = await client.get("/courses/1/progress", headers=test_user["headers"])
        assert response.status_code == 200
        progress = response.json()
        assert progress["course_id"] == 1
        assert "completed_lessons" in progress
        assert "total_lessons" in progress
        assert "progress_percent" in progress

    async def test_unauthenticated_courses(self, client: AsyncClient):
        response = await client.get("/courses")
        assert response.status_code == 401