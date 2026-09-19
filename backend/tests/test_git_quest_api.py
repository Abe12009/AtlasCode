import pytest
from httpx import AsyncClient

from app.services.git_simulator import initial_state


class TestGitQuestExecuteEndpoint:
    async def test_execute_a_command_via_the_api(self, client: AsyncClient, test_user):
        response = await client.post(
            "/git-quest/execute",
            headers=test_user["headers"],
            json={"state": initial_state(), "action": {"kind": "command", "value": "git init"}},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["error"] is None
        assert body["state"]["initialized"] is True

    async def test_execute_an_edit_action_via_the_api(self, client: AsyncClient, test_user):
        init_response = await client.post(
            "/git-quest/execute",
            headers=test_user["headers"],
            json={"state": initial_state(), "action": {"kind": "command", "value": "git init"}},
        )
        state = init_response.json()["state"]
        response = await client.post(
            "/git-quest/execute",
            headers=test_user["headers"],
            json={"state": state, "action": {"kind": "edit", "file": "app.py", "content": "print(1)"}},
        )
        assert response.status_code == 200
        assert response.json()["state"]["working_files"]["app.py"] == "print(1)"

    async def test_unauthenticated_execute_is_rejected(self, client: AsyncClient):
        response = await client.post(
            "/git-quest/execute",
            json={"state": initial_state(), "action": {"kind": "command", "value": "git init"}},
        )
        assert response.status_code == 401
