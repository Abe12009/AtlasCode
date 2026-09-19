import pytest

from app.services.git_simulator import MAX_FILE_CONTENT_BYTES, apply_action, execute, initial_state, replay


def run(state, commands):
    for command in commands:
        result = execute(state, command)
        state = result.state
    return state


def cmd(value):
    return {"kind": "command", "value": value}


def edit(file, content):
    return {"kind": "edit", "file": file, "content": content}


class TestBasicWorkflow:
    def test_init_add_commit(self):
        state = initial_state()
        state = run(state, ["git init"])
        state["working_files"]["app.py"] = "print('hello')"
        state = run(state, ['git add .', 'git commit -m "initial"'])

        assert len(state["commits"]) == 1
        commit = next(iter(state["commits"].values()))
        assert commit["message"] == "initial"
        assert commit["files"] == {"app.py": "print('hello')"}

    def test_commit_without_staging_is_rejected(self):
        state = initial_state()
        state = run(state, ["git init"])
        state["working_files"]["app.py"] = "print('hello')"
        result = execute(state, 'git commit -m "nothing staged"')
        assert result.error is not None
        assert len(result.state["commits"]) == 0

    def test_commands_before_init_are_rejected(self):
        state = initial_state()
        result = execute(state, 'git commit -m "too early"')
        assert result.error is not None


class TestBranchingAndMerging:
    def test_fast_forward_merge(self):
        state = initial_state()
        state = run(state, ["git init"])
        state["working_files"]["app.py"] = "v1"
        state = run(state, ['git add .', 'git commit -m "v1"'])
        state = run(state, ["git checkout -b feature"])
        state["working_files"]["app.py"] = "v2"
        state = run(state, ['git add .', 'git commit -m "v2"'])
        state = run(state, ["git checkout main"])

        result = execute(state, "git merge feature")
        assert result.error is None
        assert "Fast-forward" in result.output
        assert result.state["branches"]["main"] == result.state["branches"]["feature"]

    def test_conflicting_merge_produces_conflict_markers(self):
        state = initial_state()
        state = run(state, ["git init"])
        state["working_files"]["app.py"] = "base"
        state = run(state, ['git add .', 'git commit -m "base"'])
        state = run(state, ["git checkout -b feature"])
        state["working_files"]["app.py"] = "feature version"
        state = run(state, ['git add .', 'git commit -m "feature change"'])
        state = run(state, ["git checkout main"])
        state["working_files"]["app.py"] = "main version"
        state = run(state, ['git add .', 'git commit -m "main change"'])

        result = execute(state, "git merge feature")
        assert result.error == "conflict"
        content = result.state["working_files"]["app.py"]
        assert "<<<<<<< HEAD" in content
        assert "main version" in content
        assert "feature version" in content
        assert ">>>>>>> feature" in content
        assert result.state["merge_in_progress"]["conflicted_files"] == ["app.py"]

    def test_commit_blocked_while_conflict_markers_remain(self):
        state = initial_state()
        state = run(state, ["git init"])
        state["working_files"]["app.py"] = "base"
        state = run(state, ['git add .', 'git commit -m "base"'])
        state = run(state, ["git checkout -b feature"])
        state["working_files"]["app.py"] = "feature"
        state = run(state, ['git add .', 'git commit -m "feature"'])
        state = run(state, ["git checkout main"])
        state["working_files"]["app.py"] = "main"
        state = run(state, ['git add .', 'git commit -m "main"'])
        result = execute(state, "git merge feature")
        state = result.state

        # Student tries to commit without resolving.
        blocked = execute(state, 'git commit -m "did not fix it"')
        assert blocked.error is not None
        assert "Unresolved" in blocked.error

    def test_resolving_a_conflict_and_committing_produces_a_merge_commit(self):
        state = initial_state()
        state = run(state, ["git init"])
        state["working_files"]["app.py"] = "base"
        state = run(state, ['git add .', 'git commit -m "base"'])
        state = run(state, ["git checkout -b feature"])
        state["working_files"]["app.py"] = "feature"
        state = run(state, ['git add .', 'git commit -m "feature"'])
        state = run(state, ["git checkout main"])
        state["working_files"]["app.py"] = "main"
        state = run(state, ['git add .', 'git commit -m "main"'])
        state = execute(state, "git merge feature").state

        state["working_files"]["app.py"] = "resolved"
        state = run(state, ["git add app.py", 'git commit -m "resolve"'])

        final_commit_id = state["branches"]["main"]
        final_commit = state["commits"][final_commit_id]
        assert final_commit["files"]["app.py"] == "resolved"
        assert len(final_commit["parents"]) == 2

    def test_merging_an_unrelated_change_does_not_conflict(self):
        """Only-one-side-changed files auto-merge without any marker."""
        state = initial_state()
        state = run(state, ["git init"])
        state["working_files"] = {"a.py": "a", "b.py": "b"}
        state = run(state, ['git add .', 'git commit -m "base"'])
        state = run(state, ["git checkout -b feature"])
        state["working_files"]["a.py"] = "a-changed"
        state = run(state, ['git add .', 'git commit -m "change a"'])
        state = run(state, ["git checkout main"])
        state["working_files"]["b.py"] = "b-changed"
        state = run(state, ['git add .', 'git commit -m "change b"'])

        result = execute(state, "git merge feature")
        assert result.error is None
        assert result.state["working_files"] == {"a.py": "a-changed", "b.py": "b-changed"}


class TestRemote:
    def test_push_then_pull_fast_forwards(self):
        state = initial_state()
        state = run(state, ["git init"])
        state["working_files"]["README.md"] = "v1"
        state = run(state, ['git add .', 'git commit -m "init"', "git push"])
        assert state["remote_branches"]["main"] == state["branches"]["main"]

        # A teammate's commit lands directly on the remote (mission-authored NPC change).
        state["commits"]["npc1"] = {
            "parents": [state["remote_branches"]["main"]],
            "message": "teammate change",
            "files": {"README.md": "from teammate"},
        }
        state["remote_branches"]["main"] = "npc1"

        result = execute(state, "git pull")
        assert result.error is None
        assert result.state["working_files"]["README.md"] == "from teammate"

    def test_pull_conflict_never_leaks_the_internal_synthetic_branch_name(self):
        state = initial_state()
        state = run(state, ["git init"])
        state["working_files"]["README.md"] = "v1"
        state = run(state, ['git add .', 'git commit -m "init"', "git push"])
        state["working_files"]["README.md"] = "local change"
        state = run(state, ['git add .', 'git commit -m "local edit"'])
        state["commits"]["npc1"] = {
            "parents": [state["remote_branches"]["main"]],
            "message": "teammate change",
            "files": {"README.md": "teammate change"},
        }
        state["remote_branches"]["main"] = "npc1"

        result = execute(state, "git pull")
        assert result.error == "conflict"
        assert "__remote_tracking__" not in result.output
        assert "__remote_tracking__" not in result.state["merge_in_progress"]["other_branch"]
        assert "__remote_tracking__" not in result.state["branches"]


class TestUnsupportedAndReplay:
    def test_unrecognized_command_is_rejected_cleanly(self):
        state = initial_state()
        state = run(state, ["git init"])
        result = execute(state, "git rebase main")
        assert result.error is not None
        assert "not a supported command" in result.error

    def test_replay_stops_at_the_first_real_error(self):
        state = initial_state()
        actions = [
            cmd("git init"),
            cmd("git branch feature"),
            cmd('git commit -m "nothing staged"'),
            cmd("git checkout feature"),
        ]
        result = replay(state, actions)
        assert result.error is not None
        # The checkout after the failed commit must never have run.
        assert result.state.get("head", {}).get("branch") == "main"

    def test_replay_applies_file_edits_between_commands(self):
        actions = [
            cmd("git init"),
            edit("x.py", "1"),
            cmd("git add ."),
            cmd('git commit -m "one"'),
        ]
        result = replay(initial_state(), actions)
        assert result.error is None
        commit = next(iter(result.state["commits"].values()))
        assert commit["files"] == {"x.py": "1"}

    def test_edit_action_rejects_oversized_content(self):
        state = run(initial_state(), ["git init"])
        result = apply_action(state, edit("huge.py", "x" * (MAX_FILE_CONTENT_BYTES + 1)))
        assert result.error is not None
        assert "too large" in result.error

    def test_edit_action_accepts_content_at_the_limit(self):
        state = run(initial_state(), ["git init"])
        result = apply_action(state, edit("ok.py", "x" * MAX_FILE_CONTENT_BYTES))
        assert result.error is None
        assert result.state["working_files"]["ok.py"] == "x" * MAX_FILE_CONTENT_BYTES

    def test_replay_resolves_a_conflict_via_edit_action(self):
        actions = [
            cmd("git init"),
            edit("app.py", "base"),
            cmd("git add ."),
            cmd('git commit -m "base"'),
            cmd("git checkout -b feature"),
            edit("app.py", "feature version"),
            cmd("git add ."),
            cmd('git commit -m "feature change"'),
            cmd("git checkout main"),
            edit("app.py", "main version"),
            cmd("git add ."),
            cmd('git commit -m "main change"'),
            cmd("git merge feature"),  # produces a conflict, not a stopping error
            edit("app.py", "resolved version"),
            cmd("git add app.py"),
            cmd('git commit -m "resolve"'),
        ]
        result = replay(initial_state(), actions)
        assert result.error is None
        final_commit = result.state["commits"][result.state["branches"]["main"]]
        assert final_commit["files"]["app.py"] == "resolved version"
        assert len(final_commit["parents"]) == 2

    def test_replay_reproduces_the_same_final_state_as_stepwise_execution(self):
        state_a = run(initial_state(), ["git init"])
        state_a["working_files"]["x.py"] = "1"
        state_a = run(state_a, ['git add .', 'git commit -m "one"'])

        state_b = replay(initial_state(), [
            cmd("git init"),
            edit("x.py", "1"),
            cmd("git add ."),
            cmd('git commit -m "one"'),
        ]).state

        assert state_a["commits"] == state_b["commits"]
        assert state_a["branches"] == state_b["branches"]
