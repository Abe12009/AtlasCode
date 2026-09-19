"""Git & Open-Source Quests -- the live interactive terminal.

One stateless endpoint: the frontend holds the current repo state (see
app.services.git_simulator's plain-dict shape) and sends it, plus one typed
command or file edit, to get back the next state -- the same
frontend-holds-the-state / backend-computes-the-next-step shape Circuit Lab's
`/circuits/evaluate` already established. Grading is a separate concern (see
app.services.exercise_grading.STRATEGY_GIT_QUEST): it never calls this
endpoint, it replays the student's full action transcript server-side from
the mission's own authored starting state.
"""

from fastapi import APIRouter, Depends

from app.core.dependencies import get_current_user
from app.schemas import GitQuestExecuteRequest, GitQuestExecuteResponse
from app.services.git_simulator import apply_action

router = APIRouter(prefix="/git-quest", tags=["git-quest"])


@router.post("/execute", response_model=GitQuestExecuteResponse)
async def execute_action(
    request: GitQuestExecuteRequest,
    current_user=Depends(get_current_user),
):
    action = request.action.model_dump(exclude_none=True)
    result = apply_action(request.state, action)
    return GitQuestExecuteResponse(state=result.state, output=result.output, error=result.error)
