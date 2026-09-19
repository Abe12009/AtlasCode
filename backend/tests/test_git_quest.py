import json

from app.services.git_simulator import evaluate_checklist, initial_state
from app.services.exercise_grading import STRATEGY_GIT_QUEST, resolve_strategy


def cmd(value):
    return {"kind": "command", "value": value}


def edit(file, content):
    return {"kind": "edit", "file": file, "content": content}


class FakeExercise:
    def __init__(self, mission):
        self.exercise_type = _GIT_QUEST_TYPE
        self.test_code = None
        self.validation_config = json.dumps({"mission": mission})


class FakeRequest:
    def __init__(self, answer):
        self.answer = answer
        self.code = ""


from app.models import ExerciseTypeEnum  # noqa: E402
_GIT_QUEST_TYPE = ExerciseTypeEnum.git_quest

BASIC_MISSION = {
    "initial_state": initial_state(),
    "checklist": [
        {"kind": "branch_exists", "branch": "main"},
        {"kind": "file_equals", "file": "app.py", "content": "print('hello')"},
        {"kind": "commit_count_at_least", "branch": "main", "count": 1},
    ],
}

CORRECT_ACTIONS = [
    cmd("git init"),
    edit("app.py", "print('hello')"),
    cmd("git add ."),
    cmd('git commit -m "initial"'),
]


class TestEvaluateChecklist:
    def test_all_criteria_pass_on_a_correct_final_state(self):
        from app.services.git_simulator import replay

        result = replay(BASIC_MISSION["initial_state"], CORRECT_ACTIONS)
        assert evaluate_checklist(result.state, BASIC_MISSION["checklist"]) == []

    def test_unknown_criterion_kind_fails_loudly_not_silently(self):
        failures = evaluate_checklist(initial_state(), [{"kind": "not_a_real_thing"}])
        assert failures and "Unknown" in failures[0]

    def test_merge_commit_exists_criterion(self):
        from app.services.git_simulator import replay

        actions = [
            cmd("git init"),
            edit("app.py", "base"),
            cmd("git add ."),
            cmd('git commit -m "base"'),
            cmd("git checkout -b feature"),
            edit("app.py", "feature"),
            cmd("git add ."),
            cmd('git commit -m "feature"'),
            cmd("git checkout main"),
            edit("app.py", "main"),
            cmd("git add ."),
            cmd('git commit -m "main"'),
            cmd("git merge feature"),
            edit("app.py", "resolved"),
            cmd("git add app.py"),
            cmd('git commit -m "resolve"'),
        ]
        result = replay(initial_state(), actions)
        assert evaluate_checklist(result.state, [{"kind": "merge_commit_exists", "branch": "main"}]) == []
        assert evaluate_checklist(result.state, [{"kind": "no_conflict_markers"}]) == []


class TestGitQuestGrading:
    def test_resolve_strategy_recognizes_a_well_formed_mission(self):
        exercise = FakeExercise(BASIC_MISSION)
        assert resolve_strategy(exercise, []) == STRATEGY_GIT_QUEST

    def test_resolve_strategy_is_ungradable_without_a_checklist(self):
        exercise = FakeExercise({"initial_state": initial_state(), "checklist": []})
        assert resolve_strategy(exercise, []) == "ungradable"

    def test_correct_transcript_is_graded_correct(self):
        from app.services.exercise_grading import grade_exercise

        exercise = FakeExercise(BASIC_MISSION)
        result = grade_exercise(exercise, [], FakeRequest(json.dumps(CORRECT_ACTIONS)))
        assert result.is_correct is True

    def test_wrong_final_content_is_graded_incorrect_with_actionable_feedback(self):
        from app.services.exercise_grading import grade_exercise

        exercise = FakeExercise(BASIC_MISSION)
        wrong = [cmd("git init"), edit("app.py", "print('WRONG')"), cmd("git add ."), cmd('git commit -m "x"')]
        result = grade_exercise(exercise, [], FakeRequest(json.dumps(wrong)))
        assert result.is_correct is False
        assert "app.py" in result.feedback

    def test_a_student_cannot_fabricate_a_final_state_by_tampering_with_the_answer(self):
        """The whole point of replaying server-side: submitting something
        that *isn't* a valid action transcript must never grade as correct,
        no matter what a tampered client sends."""
        from app.services.exercise_grading import grade_exercise

        exercise = FakeExercise(BASIC_MISSION)
        tampered = json.dumps({"commits": {"fake": {}}, "branches": {"main": "fake"}})  # not a list of actions
        result = grade_exercise(exercise, [], FakeRequest(tampered))
        assert result.is_correct is False

    def test_command_error_partway_through_is_graded_incorrect(self):
        from app.services.exercise_grading import grade_exercise

        exercise = FakeExercise(BASIC_MISSION)
        broken = [cmd("git commit -m \"too early\"")]  # before init
        result = grade_exercise(exercise, [], FakeRequest(json.dumps(broken)))
        assert result.is_correct is False
