"""Orientini coverage: the matching/scoring engine as pure unit tests against
known input vectors, plus the submit/results endpoints. Not as deep as
Circuit Lab's suite -- no compile/replay engine here, just a scoring
function -- but the ranking logic and the "never trust nothing" endpoint
paths (empty answers, unknown option ids, unauthenticated) are covered."""

import json
from types import SimpleNamespace

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models import BacTrackEnum, StudentProfile, User
from app.services.orientini import TRAIT_KEYS, compute_student_vector, score_institutions


def _option(**weights):
    return SimpleNamespace(trait_weights=json.dumps(weights))


def _institution(id, eligible_bac_tracks=None, **weights):
    requirement = None
    if eligible_bac_tracks is not None:
        requirement = SimpleNamespace(eligible_bac_tracks=json.dumps(eligible_bac_tracks))
    return SimpleNamespace(id=id, trait_weights=json.dumps(weights), requirement=requirement)


class TestComputeStudentVector:
    def test_sums_selected_options(self):
        options = [_option(hands_on=3, theory=-1), _option(hands_on=1, entrepreneurial=2)]
        vector = compute_student_vector(options)
        assert vector["hands_on"] == 4
        assert vector["theory"] == -1
        assert vector["entrepreneurial"] == 2

    def test_empty_selection_is_the_zero_vector(self):
        vector = compute_student_vector([])
        assert set(vector.keys()) == set(TRAIT_KEYS)
        assert all(v == 0.0 for v in vector.values())

    def test_ignores_trait_keys_outside_the_fixed_space(self):
        # Defensive: a stray key in stored JSON shouldn't leak into the
        # fixed trait space or crash the sum.
        vector = compute_student_vector([_option(hands_on=1, made_up_trait=99)])
        assert "made_up_trait" not in vector
        assert vector["hands_on"] == 1


class TestScoreInstitutions:
    def test_ranks_the_closer_direction_higher(self):
        # A hands-on-leaning student should score a hands-on school above a
        # theory-heavy one, even though both vectors have equal magnitude.
        student_vector = compute_student_vector([_option(hands_on=3, theory=-1)])
        hands_on_school = _institution(1, hands_on=3, theory=-1)
        theory_school = _institution(2, theory=3, hands_on=-1)

        results = score_institutions(student_vector, [hands_on_school, theory_school], bac_track=None)

        assert [r.institution_id for r in results] == [1, 2]
        assert results[0].score > results[1].score

    def test_score_rewards_direction_not_answer_count(self):
        # Cosine similarity: a student who answered once in a school's exact
        # direction should score it the same as one who answered several
        # questions all pointing the same way, not lower for "less data".
        one_answer = compute_student_vector([_option(hands_on=1)])
        five_answers = compute_student_vector([_option(hands_on=1)] * 5)
        school = _institution(1, hands_on=1)

        one_score = score_institutions(one_answer, [school], bac_track=None)[0].score
        five_score = score_institutions(five_answers, [school], bac_track=None)[0].score

        assert one_score == pytest.approx(five_score)

    def test_zero_vector_scores_zero_not_a_crash(self):
        zero_vector = {k: 0.0 for k in TRAIT_KEYS}
        school = _institution(1, hands_on=3)
        results = score_institutions(zero_vector, [school], bac_track=None)
        assert results[0].score == 0.0

    def test_ineligible_institutions_are_flagged_but_not_dropped(self):
        # Best trait match, but the track isn't in its eligible list -- must
        # still appear in results, just ranked behind eligible ones.
        student_vector = compute_student_vector([_option(math_intensity=3, theory=3)])
        best_match_ineligible = _institution(1, eligible_bac_tracks=["svt"], math_intensity=3, theory=3)
        worse_match_eligible = _institution(2, eligible_bac_tracks=["sciences_math_a"], math_intensity=1)

        results = score_institutions(
            student_vector,
            [best_match_ineligible, worse_match_eligible],
            bac_track=BacTrackEnum.sciences_math_a,
        )

        by_id = {r.institution_id: r for r in results}
        assert by_id[1].eligible is False
        assert by_id[2].eligible is True
        assert by_id[1].score > by_id[2].score  # genuinely the better trait match...
        assert [r.institution_id for r in results] == [2, 1]  # ...but ranked below eligible ones

    def test_no_requirement_row_means_always_eligible(self):
        student_vector = compute_student_vector([_option(hands_on=1)])
        school = _institution(1, hands_on=1)
        results = score_institutions(student_vector, [school], bac_track=BacTrackEnum.svt)
        assert results[0].eligible is True

    def test_unknown_bac_track_does_not_hide_institutions(self):
        student_vector = compute_student_vector([_option(hands_on=1)])
        school = _institution(1, eligible_bac_tracks=["svt"], hands_on=1)
        results = score_institutions(student_vector, [school], bac_track=None)
        assert results[0].eligible is True


class TestQuestionsAndInstitutionsEndpoints:
    async def test_get_questions_returns_seeded_content(self, client: AsyncClient, test_user):
        response = await client.get("/orientini/questions", headers=test_user["headers"])
        assert response.status_code == 200
        questions = response.json()
        assert len(questions) >= 1
        first = questions[0]
        assert first["translations"]
        assert len(first["options"]) >= 2
        assert first["options"][0]["translations"]

    async def test_get_institutions_returns_seeded_content(self, client: AsyncClient, test_user):
        response = await client.get("/orientini/institutions", headers=test_user["headers"])
        assert response.status_code == 200
        institutions = response.json()
        slugs = {i["slug"] for i in institutions}
        assert "cpge" in slugs
        assert "1337" in slugs
        # Every requirement row is seeded unverified by design until a human
        # confirms the real figures -- see seed/orientini.py's module note.
        for institution in institutions:
            assert institution["requirement"]["data_verified"] is False

    async def test_unauthenticated_questions_rejected(self, client: AsyncClient):
        response = await client.get("/orientini/questions")
        assert response.status_code == 401

    async def test_unauthenticated_institutions_rejected(self, client: AsyncClient):
        response = await client.get("/orientini/institutions")
        assert response.status_code == 401


async def _first_option_per_question(client: AsyncClient, headers: dict) -> dict:
    response = await client.get("/orientini/questions", headers=headers)
    return {q["id"]: q["options"][0]["id"] for q in response.json()}


class TestSubmitQuiz:
    async def test_submit_computes_and_stores_a_ranked_result(self, client: AsyncClient, test_user):
        answers = await _first_option_per_question(client, test_user["headers"])
        response = await client.post(
            "/orientini/submit",
            headers=test_user["headers"],
            json={"answers": answers, "bac_track": "sciences_math_a"},
        )
        assert response.status_code == 200
        result = response.json()
        assert result["bac_track"] == "sciences_math_a"
        assert len(result["scores"]) >= 1

        institutions = (await client.get("/orientini/institutions", headers=test_user["headers"])).json()
        assert {s["institution_id"] for s in result["scores"]} == {i["id"] for i in institutions}

        # Ranked: scores are sorted, eligible group first, non-increasing
        # within it (all seeded institutions are eligible for every track,
        # since eligible_bac_tracks is unset -- see seed/orientini.py).
        scores = [s["score"] for s in result["scores"]]
        assert scores == sorted(scores, reverse=True)

    async def test_rejects_empty_answers(self, client: AsyncClient, test_user):
        response = await client.post(
            "/orientini/submit", headers=test_user["headers"], json={"answers": {}, "bac_track": None}
        )
        assert response.status_code == 400

    async def test_rejects_unknown_option_id(self, client: AsyncClient, test_user):
        response = await client.post(
            "/orientini/submit",
            headers=test_user["headers"],
            json={"answers": {"1": 999999}, "bac_track": None},
        )
        assert response.status_code == 400

    async def test_unauthenticated_submit_rejected(self, client: AsyncClient):
        response = await client.post("/orientini/submit", json={"answers": {"1": 1}})
        assert response.status_code == 401

    async def test_submit_with_bac_track_updates_the_student_profile(
        self, client: AsyncClient, test_user, db_session
    ):
        answers = await _first_option_per_question(client, test_user["headers"])
        response = await client.post(
            "/orientini/submit",
            headers=test_user["headers"],
            json={"answers": answers, "bac_track": "ste"},
        )
        assert response.status_code == 200

        user = (
            await db_session.execute(select(User).where(User.email == test_user["data"]["email"]))
        ).scalar_one()
        profile = (
            await db_session.execute(select(StudentProfile).where(StudentProfile.user_id == user.id))
        ).scalar_one()
        assert profile.bac_track == BacTrackEnum.ste

    async def test_submit_without_bac_track_leaves_profile_untouched(
        self, client: AsyncClient, test_user, db_session
    ):
        answers = await _first_option_per_question(client, test_user["headers"])
        response = await client.post(
            "/orientini/submit", headers=test_user["headers"], json={"answers": answers, "bac_track": None}
        )
        assert response.status_code == 200

        user = (
            await db_session.execute(select(User).where(User.email == test_user["data"]["email"]))
        ).scalar_one()
        profile = (
            await db_session.execute(select(StudentProfile).where(StudentProfile.user_id == user.id))
        ).scalar_one()
        assert profile.bac_track is None


class TestLatestResult:
    async def test_returns_the_most_recently_submitted_result(self, client: AsyncClient, test_user):
        answers = await _first_option_per_question(client, test_user["headers"])
        first = await client.post(
            "/orientini/submit", headers=test_user["headers"], json={"answers": answers, "bac_track": "pc"}
        )
        second = await client.post(
            "/orientini/submit", headers=test_user["headers"], json={"answers": answers, "bac_track": "svt"}
        )
        assert first.status_code == 200 and second.status_code == 200

        latest = await client.get("/orientini/results/latest", headers=test_user["headers"])
        assert latest.status_code == 200
        assert latest.json()["id"] == second.json()["id"]
        assert latest.json()["bac_track"] == "svt"

    async def test_404_when_the_student_has_never_submitted(self, client: AsyncClient, second_user):
        response = await client.get("/orientini/results/latest", headers=second_user["headers"])
        assert response.status_code == 404

    async def test_unauthenticated_latest_result_rejected(self, client: AsyncClient):
        response = await client.get("/orientini/results/latest")
        assert response.status_code == 401
