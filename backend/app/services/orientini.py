"""Orientini's matching algorithm -- scores institutions against a student's
quiz answers.

Each quiz option and each institution carries a trait vector (JSON object of
trait_key -> weight, in the same fixed trait space defined by TRAIT_KEYS). A
student's vector is the sum of the trait vectors of the options they picked.
An institution's score is the cosine similarity between the student's vector
and the institution's target vector -- this rewards *direction* (which traits
matter to the student) over raw magnitude, so a student who answered fewer
questions isn't penalized relative to one who answered more.

Eligibility (Bac track) is a hard filter applied before scoring, not folded
into the trait vector -- a student ineligible for an institution's track
shouldn't see it ranked highly just because their interests match.
"""

import json
import math
from dataclasses import dataclass
from typing import Optional

from app.models import BacTrackEnum, Institution

#: Fixed trait space every quiz option and institution vector is expressed in.
#: Kept small and stable -- adding a trait key means re-authoring every
#: existing institution's trait_weights to stay meaningful.
TRAIT_KEYS = (
    "hands_on",       # building/making vs. studying theory
    "theory",         # depth of abstract/theoretical grounding
    "math_intensity",
    "competitive_exam",  # tolerance for concours-style selection
    "research_academic",
    "entrepreneurial",
)


def _parse_vector(raw: str) -> dict:
    data = json.loads(raw)
    return {k: float(v) for k, v in data.items() if k in TRAIT_KEYS}


def _cosine_similarity(a: dict, b: dict) -> float:
    keys = TRAIT_KEYS
    dot = sum(a.get(k, 0.0) * b.get(k, 0.0) for k in keys)
    norm_a = math.sqrt(sum(a.get(k, 0.0) ** 2 for k in keys))
    norm_b = math.sqrt(sum(b.get(k, 0.0) ** 2 for k in keys))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


@dataclass
class InstitutionScore:
    institution_id: int
    score: float  # cosine similarity in [-1, 1]
    eligible: bool
    trait_breakdown: dict  # per-trait contribution to the score, for the "why" UI


def compute_student_vector(selected_options: list) -> dict:
    """Sums the trait_weights of the chosen OrientiniOption rows."""
    vector: dict = {k: 0.0 for k in TRAIT_KEYS}
    for option in selected_options:
        for key, weight in _parse_vector(option.trait_weights).items():
            vector[key] += weight
    return vector


def _is_eligible(institution: Institution, bac_track: Optional[BacTrackEnum]) -> bool:
    requirement = institution.requirement
    if requirement is None or requirement.eligible_bac_tracks is None:
        return True
    if bac_track is None:
        return True  # unknown track: don't hide institutions, just don't gate on it
    eligible = json.loads(requirement.eligible_bac_tracks)
    return bac_track.value in eligible


def score_institutions(
    student_vector: dict,
    institutions: list,
    bac_track: Optional[BacTrackEnum],
) -> list:
    """Ranks institutions by cosine similarity to student_vector. Ineligible
    institutions (per Bac track) are still scored but flagged, not dropped --
    the frontend decides whether to hide or gray them out."""
    results = []
    for institution in institutions:
        target_vector = _parse_vector(institution.trait_weights)
        score = _cosine_similarity(student_vector, target_vector)
        breakdown = {
            k: student_vector.get(k, 0.0) * target_vector.get(k, 0.0) for k in TRAIT_KEYS
        }
        results.append(
            InstitutionScore(
                institution_id=institution.id,
                score=score,
                eligible=_is_eligible(institution, bac_track),
                trait_breakdown=breakdown,
            )
        )
    results.sort(key=lambda r: (r.eligible, r.score), reverse=True)
    return results
