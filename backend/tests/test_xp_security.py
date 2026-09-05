import pytest
from httpx import AsyncClient


class TestXPAndAchievements:
    async def test_xp_awarded_on_exercise_submit(self, client: AsyncClient, test_user):
        initial_profile = await client.get("/auth/profile", headers=test_user["headers"])
        initial_xp = initial_profile.json()["xp"]

        response = await client.post("/exercises/1/submit", headers=test_user["headers"], json={
            "code": 'print("Hello, World!")',
            "exercise_id": 1
        })

        if response.status_code == 200 and response.json().get("is_correct"):
            final_profile = await client.get("/auth/profile", headers=test_user["headers"])
            final_xp = final_profile.json()["xp"]
            assert final_xp >= initial_xp

    async def test_xp_not_duplicated(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/submit", headers=test_user["headers"], json={
            "code": 'print("Hello, World!")',
            "exercise_id": 1
        })

        if response.status_code == 200 and response.json().get("is_correct"):
            initial_xp = response.json()["xp_earned"]

            response2 = await client.post("/exercises/1/submit", headers=test_user["headers"], json={
                "code": 'print("Hello, World!")',
                "exercise_id": 1
            })

            if response2.status_code == 200:
                duplicate_xp = response2.json()["xp_earned"]
                assert duplicate_xp == 0

    async def test_level_calculation(self, client: AsyncClient, test_user):
        response = await client.get("/auth/profile", headers=test_user["headers"])
        profile = response.json()

        expected_level = (profile["xp"] // 100) + 1
        assert profile["level"] == expected_level

    async def test_achievement_conditions(self, client: AsyncClient, test_user):
        response = await client.get("/dashboard", headers=test_user["headers"])
        dashboard = response.json()

        for achievement in dashboard["recent_achievements"]:
            assert "achievement" in achievement
            assert "earned_at" in achievement
            assert "xp_reward" in achievement["achievement"]


class TestSecurity:
    async def test_reject_os_import(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "import os\nprint(os.listdir('.'))",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False
        assert "not allowed" in result.get("feedback", "").lower() or "validation" in result.get("error", "").lower()

    async def test_reject_subprocess_import(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "import subprocess\nsubprocess.run(['ls'])",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_reject_filesystem_access(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "open('/etc/passwd').read()",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_reject_environment_access(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "import os\nprint(os.environ)",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_timeout_infinite_loop(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "while True:\n    pass",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False
        assert "timed out" in result.get("error", "").lower() or "timeout" in result.get("error", "").lower()

    async def test_timeout_infinite_loop_submit(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/submit", headers=test_user["headers"], json={
            "code": "while True:\n    pass",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False
        assert "timed out" in result.get("error", "").lower() or "timeout" in result.get("error", "").lower()

    async def test_api_remains_responsive_after_timeout(self, client: AsyncClient, test_user):
        await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "while True:\n    pass",
            "exercise_id": 1
        })
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": 'print("Hello, World!")\nprint("Hello after timeout")',
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is True
        assert "Hello, World!" in result.get("output", "")
        assert "Hello after timeout" in result.get("output", "")

    async def test_reject_pathlib_import(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "import pathlib\nprint(pathlib.Path('.').read_text())",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_reject_socket_import(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "import socket\ns = socket.socket()",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_reject_sys_import(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "import sys\nprint(sys.version)",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_reject_eval(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "eval('print(1)')",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_reject_exec(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "exec('print(1)')",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_reject_compile(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "compile('print(1)', '<string>', 'exec')",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_reject___import__(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "__import__('os')",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_reject_open(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "open('test.txt', 'w').write('x')",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_reject_input(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "x = input()",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_reject_getattr(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "getattr(__builtins__, 'eval')('print(1)')",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_reject_globals(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "globals()['__builtins__']['eval']('print(1)')",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_reject_locals(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "locals()['__builtins__']['eval']('print(1)')",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_reject_dunder_access(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "().__class__.__bases__[0].__subclasses__()",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_reject_os_system_attribute(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "import os\nos.system('ls')",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_excessive_output(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "print('x' * 1000000)",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False or len(result.get("output", "")) < 100000

    async def test_excessive_output_truncated(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "print('x' * 200000)",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        output = result.get("output", "")
        assert len(output) <= 101000

    async def test_normal_execution(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": 'print("Hello, World!")',
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is True
        assert "Hello, World!" in result.get("output", "")

    async def test_normal_execution_with_loops(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": 'print("Hello, World!")\nfor i in range(5):\n    print(i)',
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is True
        assert "Hello, World!" in result.get("output", "")
        assert "0" in result.get("output", "")
        assert "4" in result.get("output", "")

    async def test_normal_execution_with_functions(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": 'print("Hello, World!")\ndef add(a, b):\n    return a + b\nprint(add(2, 3))',
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is True
        assert "Hello, World!" in result.get("output", "")
        assert "5" in result.get("output", "")

    async def test_normal_execution_with_lists(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": 'print("Hello, World!")\nitems = [1, 2, 3]\nfor item in items:\n    print(item * 2)',
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is True
        assert "Hello, World!" in result.get("output", "")
        assert "2" in result.get("output", "")
        assert "6" in result.get("output", "")

    async def test_normal_execution_with_dicts(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": 'print("Hello, World!")\nd = {"a": 1, "b": 2}\nprint(d["a"] + d["b"])',
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is True
        assert "Hello, World!" in result.get("output", "")
        assert "3" in result.get("output", "")

    async def test_syntax_error_handling(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "print('missing paren",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False
        assert "syntax" in result.get("error", "").lower() or "syntax" in result.get("feedback", "").lower()

    async def test_runtime_error_handling(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "x = 1 / 0",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False
        assert "zerodivision" in result.get("error", "").lower() or "division by zero" in result.get("error", "").lower()

    async def test_urllib_import_blocked(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "import urllib.request\nurllib.request.urlopen('http://example.com')",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_multiprocessing_blocked(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "import multiprocessing\nmultiprocessing.Process().start()",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_threading_blocked(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "import threading\nthreading.Thread(target=print).start()",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_ctypes_blocked(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "import ctypes\nctypes.CDLL('kernel32.dll')",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_shutil_blocked(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "import shutil\nshutil.rmtree('/')",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_pickle_blocked(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "import pickle\npickle.loads(b'')",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_importlib_blocked(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "import importlib\nimportlib.import_module('os')",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_breakpoint_blocked(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "breakpoint()",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_exit_quit_blocked(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "exit()",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_help_license_blocked(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": "help()",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False


class TestVisualProgrammingSecurity:
    async def test_visual_compile_generates_safe_code(self, client: AsyncClient, test_user):
        response = await client.post("/visual/compile", headers=test_user["headers"], json={
            "nodes": [
                {"id": "1", "type": "start", "config": {}},
                {"id": "2", "type": "variable", "config": {"name": "x", "value": "10"}},
                {"id": "3", "type": "output", "config": {"value": "x"}},
                {"id": "4", "type": "end", "config": {}}
            ],
            "edges": [
                {"source": "1", "target": "2"},
                {"source": "2", "target": "3"},
                {"source": "3", "target": "4"}
            ]
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_valid"] is True
        assert "x = 10" in result["python_code"]
        assert "print(x)" in result["python_code"]
        assert "input" not in result["python_code"]

    async def test_visual_run_executes_safely(self, client: AsyncClient, test_user):
        response = await client.post("/visual/1/run", headers=test_user["headers"], json={
            "code": 'print("Hello, World!")\nx = 10\nprint(x)',
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is True
        assert "Hello, World!" in result.get("output", "")
        assert "10" in result.get("output", "")

    async def test_visual_rejects_dangerous_code(self, client: AsyncClient, test_user):
        response = await client.post("/visual/1/run", headers=test_user["headers"], json={
            "code": "import os\nprint(os.listdir('.'))",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False

    async def test_visual_infinite_loop_blocked(self, client: AsyncClient, test_user):
        response = await client.post("/visual/1/run", headers=test_user["headers"], json={
            "code": "while True:\n    pass",
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False
        assert "timed out" in result.get("error", "").lower() or "timeout" in result.get("error", "").lower()


class TestProjectSecurity:
    async def test_project_submit_task_blocks_dangerous_code(self, client: AsyncClient, test_user):
        start_response = await client.post("/projects/1/start", headers=test_user["headers"])
        if start_response.status_code == 403:
            pytest.skip("Project is locked")

        response = await client.post("/projects/1/submit-task", headers=test_user["headers"], json={
            "task_id": 1,
            "code": "import os\nprint(os.listdir('.'))"
        })
        assert response.status_code in [200, 403]
        if response.status_code == 200:
            result = response.json()
            assert result["success"] is False

    async def test_project_submit_task_blocks_infinite_loop(self, client: AsyncClient, test_user):
        start_response = await client.post("/projects/1/start", headers=test_user["headers"])
        if start_response.status_code == 403:
            pytest.skip("Project is locked")

        response = await client.post("/projects/1/submit-task", headers=test_user["headers"], json={
            "task_id": 1,
            "code": "while True:\n    pass"
        })
        assert response.status_code in [200, 403]
        if response.status_code == 200:
            result = response.json()
            assert result["success"] is False

    async def test_project_submit_task_normal_execution(self, client: AsyncClient, test_user):
        start_response = await client.post("/projects/1/start", headers=test_user["headers"])
        if start_response.status_code == 403:
            pytest.skip("Project is locked")

        response = await client.post("/projects/1/submit-task", headers=test_user["headers"], json={
            "task_id": 1,
            "code": "def add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b\n\ndef multiply(a, b):\n    return a * b\n\ndef divide(a, b):\n    if b != 0:\n        return a / b\n    return \"Error: Division by zero\"\n\nprint(add(2, 3))"
        })
        assert response.status_code in [200, 403]
        if response.status_code == 200:
            result = response.json()
            assert result["success"] is True


class TestRunVsSubmitSemantics:
    async def test_run_earns_zero_xp(self, client: AsyncClient, test_user):
        initial_profile = await client.get("/auth/profile", headers=test_user["headers"])
        initial_xp = initial_profile.json()["xp"]

        response = await client.post("/exercises/1/run", headers=test_user["headers"], json={
            "code": 'print("Hello, World!")',
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["xp_earned"] == 0

        final_profile = await client.get("/auth/profile", headers=test_user["headers"])
        final_xp = final_profile.json()["xp"]
        assert final_xp == initial_xp

    async def test_submit_earns_xp_first_time(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/submit", headers=test_user["headers"], json={
            "code": 'print("Hello, World!")',
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        if result["is_correct"]:
            assert result["xp_earned"] > 0

    async def test_submit_no_xp_on_duplicate(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/submit", headers=test_user["headers"], json={
            "code": 'print("Hello, World!")',
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        if result["is_correct"]:
            first_xp = result["xp_earned"]
            assert first_xp > 0

            response2 = await client.post("/exercises/1/submit", headers=test_user["headers"], json={
                "code": 'print("Hello, World!")',
                "exercise_id": 1
            })
            assert response2.status_code == 200
            result2 = response2.json()
            assert result2["is_correct"] is True
            assert result2["xp_earned"] == 0

    async def test_submit_no_xp_on_incorrect(self, client: AsyncClient, test_user):
        response = await client.post("/exercises/1/submit", headers=test_user["headers"], json={
            "code": 'print("Wrong")',
            "exercise_id": 1
        })
        assert response.status_code == 200
        result = response.json()
        assert result["is_correct"] is False
        assert result["xp_earned"] == 0