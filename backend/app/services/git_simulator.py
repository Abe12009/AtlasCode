"""Git & Open-Source Quests' simulation engine: a small, deterministic model
of a git repository -- a commit DAG, movable branch pointers, a staging area
-- driven by a tiny allow-listed command grammar, not a shell parser and
never real git.

Simulated, not real, on purpose (see the Feature 4 proposal): shelling out to
real git is a far larger sandbox-escape surface than app.services.code_executor
was ever built to contain, and a simulation gives full deterministic control
over the "teammate already pushed a conflicting commit" mechanic (an author
writes that commit directly into a mission's starting state -- nothing here
generates or randomizes it) and over the final "PR to a shared community
project" stage (the same starting state for every student, not a real shared
host).

Full-file snapshots per commit, not blobs/trees/diffs -- this is a teaching
model of git's mental shape (commits, branches-as-pointers, merge, conflict),
not a reimplementation of its object model. A small, fixed set of pedagogical
files per mission is the intended scale.

One engine, two call sites (the same relationship compile_circuit /
evaluate_circuit have in circuit_evaluator.py):
* the frontend calls `execute` once per command the student types, to drive
  the live interactive terminal;
* grading (see app.services.exercise_grading's STRATEGY_GIT_QUEST) replays a
  student's full submitted command list through `execute` itself, starting
  from the mission's authored initial state, so the final state graded
  against a checklist is always server-computed -- a student can never submit
  a fabricated "final state" directly.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

#: Safety cap on commands accepted in one replay -- generous for any
#: authored mission, a firm backstop against a pathological submission.
MAX_COMMANDS = 200


def initial_state() -> Dict[str, Any]:
    """A brand-new, uninitialized working directory -- before `git init`."""
    return {
        "commits": {},
        "branches": {},
        "remote_branches": {},
        "head": None,
        "working_files": {},
        "staged_files": {},
        "merge_in_progress": None,
        "initialized": False,
    }


@dataclass
class ExecuteResult:
    state: Dict[str, Any]
    output: str = ""
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None


def _current_branch(state: Dict[str, Any]) -> Optional[str]:
    head = state["head"]
    return head["branch"] if head and "branch" in head else None


def _current_commit_id(state: Dict[str, Any]) -> Optional[str]:
    head = state["head"]
    if head is None:
        return None
    if "branch" in head:
        return state["branches"].get(head["branch"])
    return head.get("commit")


def _commit_files(state: Dict[str, Any], commit_id: Optional[str]) -> Dict[str, str]:
    if commit_id is None:
        return {}
    return dict(state["commits"][commit_id]["files"])


def _next_commit_id(state: Dict[str, Any]) -> str:
    return f"c{len(state['commits']) + 1}"


def _ancestors(state: Dict[str, Any], commit_id: Optional[str]) -> set:
    seen: set = set()
    stack = [commit_id] if commit_id else []
    while stack:
        cid = stack.pop()
        if cid is None or cid in seen:
            continue
        seen.add(cid)
        stack.extend(state["commits"][cid]["parents"])
    return seen


def _merge_base(state: Dict[str, Any], a: Optional[str], b: Optional[str]) -> Optional[str]:
    """Nearest common ancestor, found by walking `a`'s ancestry outward and
    returning the first commit also reachable from `b`. Good enough for the
    small, mostly-linear histories a mission authors -- not a general
    lowest-common-ancestor algorithm for arbitrary octopus topologies."""
    b_ancestors = _ancestors(state, b)
    stack = [a]
    seen: set = set()
    while stack:
        cid = stack.pop(0)
        if cid is None or cid in seen:
            continue
        if cid in b_ancestors:
            return cid
        seen.add(cid)
        stack.extend(state["commits"][cid]["parents"])
    return None


def _error(state: Dict[str, Any], message: str) -> ExecuteResult:
    return ExecuteResult(state=state, error=message)


def _cmd_init(state: Dict[str, Any], args: List[str]) -> ExecuteResult:
    if state["initialized"]:
        return _error(state, "Already a git repository.")
    state = copy.deepcopy(state)
    state["initialized"] = True
    state["branches"]["main"] = None
    state["head"] = {"branch": "main"}
    return ExecuteResult(state=state, output="Initialized empty Git repository.")


def _require_init(state: Dict[str, Any]) -> Optional[ExecuteResult]:
    if not state["initialized"]:
        return _error(state, "Not a git repository (run 'git init' first).")
    return None


def _cmd_add(state: Dict[str, Any], args: List[str]) -> ExecuteResult:
    if err := _require_init(state):
        return err
    if not args:
        return _error(state, "Nothing specified, nothing added.")
    state = copy.deepcopy(state)
    if args == ["."]:
        state["staged_files"].update(state["working_files"])
        return ExecuteResult(state=state, output="Staged all changes.")
    for name in args:
        if name not in state["working_files"]:
            return _error(state, f"pathspec '{name}' did not match any files")
        state["staged_files"][name] = state["working_files"][name]
    return ExecuteResult(state=state, output=f"Staged {', '.join(args)}.")


def _cmd_commit(state: Dict[str, Any], args: List[str], message: Optional[str]) -> ExecuteResult:
    if err := _require_init(state):
        return err
    if not message:
        return _error(state, "commit requires -m \"<message>\"")
    merge = state["merge_in_progress"]
    if merge:
        unresolved = [f for f in merge["conflicted_files"] if "<<<<<<<" in state["working_files"].get(f, "")]
        if unresolved:
            return _error(state, f"Unresolved conflicts remain in: {', '.join(unresolved)}")
    if not state["staged_files"] and not merge:
        return _error(state, "Nothing to commit -- stage changes with 'git add' first.")

    state = copy.deepcopy(state)
    branch = _current_branch(state)
    if branch is None:
        return _error(state, "Not on a branch (detached HEAD) -- cannot commit here.")
    parent = state["branches"][branch]
    parents = [parent] if parent else []
    files = _commit_files(state, parent)
    files.update(state["staged_files"])
    # A conflicted merge writes resolved content straight into working_files
    # once the student edits it; that resolved content becomes the commit.
    if merge:
        for name in merge["conflicted_files"]:
            files[name] = state["working_files"][name]
        parents = [p for p in [parent, merge["other_commit"]] if p]

    commit_id = _next_commit_id(state)
    state["commits"][commit_id] = {"parents": parents, "message": message, "files": files}
    state["branches"][branch] = commit_id
    state["staged_files"] = {}
    state["merge_in_progress"] = None
    return ExecuteResult(state=state, output=f"[{branch} {commit_id}] {message}")


def _cmd_branch(state: Dict[str, Any], args: List[str]) -> ExecuteResult:
    if err := _require_init(state):
        return err
    if not args:
        return ExecuteResult(state=state, output="\n".join(sorted(state["branches"])))
    name = args[0]
    if name in state["branches"]:
        return _error(state, f"branch '{name}' already exists")
    state = copy.deepcopy(state)
    state["branches"][name] = _current_commit_id(state)
    return ExecuteResult(state=state, output=f"Created branch '{name}'.")


def _checkout_branch(state: Dict[str, Any], name: str) -> ExecuteResult:
    if name not in state["branches"]:
        return _error(state, f"pathspec '{name}' did not match any branch known to git")
    state = copy.deepcopy(state)
    state["head"] = {"branch": name}
    state["working_files"] = _commit_files(state, state["branches"][name])
    state["staged_files"] = {}
    return ExecuteResult(state=state, output=f"Switched to branch '{name}'.")


def _cmd_checkout(state: Dict[str, Any], args: List[str]) -> ExecuteResult:
    if err := _require_init(state):
        return err
    if not args:
        return _error(state, "checkout requires a branch name")
    if args[0] == "-b":
        if len(args) < 2:
            return _error(state, "checkout -b requires a branch name")
        branch_result = _cmd_branch(state, [args[1]])
        if not branch_result.ok:
            return branch_result
        return _checkout_branch(branch_result.state, args[1])
    return _checkout_branch(state, args[0])


def _cmd_merge(state: Dict[str, Any], args: List[str]) -> ExecuteResult:
    if err := _require_init(state):
        return err
    if not args:
        return _error(state, "merge requires a branch name")
    other = args[0]
    if other not in state["branches"]:
        return _error(state, f"'{other}' does not point to a commit")
    current_branch = _current_branch(state)
    if current_branch is None:
        return _error(state, "Not on a branch (detached HEAD) -- cannot merge here.")

    current_commit = state["branches"][current_branch]
    other_commit = state["branches"][other]

    if other_commit == current_commit:
        return ExecuteResult(state=state, output="Already up to date.")

    base = _merge_base(state, current_commit, other_commit)
    if base == current_commit:
        # Fast-forward: just move the pointer.
        state = copy.deepcopy(state)
        state["branches"][current_branch] = other_commit
        state["working_files"] = _commit_files(state, other_commit)
        return ExecuteResult(state=state, output=f"Fast-forward merge of '{other}'.")

    base_files = _commit_files(state, base)
    current_files = _commit_files(state, current_commit)
    other_files = _commit_files(state, other_commit)

    merged_files: Dict[str, str] = dict(current_files)
    conflicted: List[str] = []
    for name in set(current_files) | set(other_files):
        base_content = base_files.get(name)
        cur_content = current_files.get(name)
        oth_content = other_files.get(name)
        if oth_content == cur_content:
            continue  # identical on both sides, nothing to do
        if cur_content == base_content:
            merged_files[name] = oth_content  # only the other side changed
            continue
        if oth_content == base_content:
            continue  # only our side changed, current_files already has it
        # Both sides changed the same file differently -- a real conflict.
        conflicted.append(name)
        merged_files[name] = (
            f"<<<<<<< HEAD\n{cur_content or ''}\n=======\n{oth_content or ''}\n>>>>>>> {other}\n"
        )

    state = copy.deepcopy(state)
    state["working_files"] = merged_files

    if conflicted:
        state["merge_in_progress"] = {"other_branch": other, "other_commit": other_commit, "conflicted_files": conflicted}
        return ExecuteResult(
            state=state,
            output=f"Auto-merging...\nCONFLICT: content conflict in {', '.join(conflicted)}\n"
                   "Fix conflicts and then run 'git add <file>' and 'git commit'.",
            error="conflict",
        )

    commit_id = _next_commit_id(state)
    state["commits"][commit_id] = {
        "parents": [current_commit, other_commit],
        "message": f"Merge branch '{other}'",
        "files": merged_files,
    }
    state["branches"][current_branch] = commit_id
    state["staged_files"] = {}
    return ExecuteResult(state=state, output=f"Merge made by the 'recursive' strategy.")


def _cmd_status(state: Dict[str, Any], args: List[str]) -> ExecuteResult:
    if err := _require_init(state):
        return err
    lines = [f"On branch {_current_branch(state) or '(detached HEAD)'}"]
    if state["merge_in_progress"]:
        lines.append(f"Merging with '{state['merge_in_progress']['other_branch']}' -- fix conflicts:")
        lines.extend(f"  both modified: {f}" for f in state["merge_in_progress"]["conflicted_files"])
    if state["staged_files"]:
        lines.append("Changes to be committed:")
        lines.extend(f"  {f}" for f in state["staged_files"])
    if not state["staged_files"] and not state["merge_in_progress"]:
        lines.append("nothing to commit, working tree clean")
    return ExecuteResult(state=state, output="\n".join(lines))


def _cmd_log(state: Dict[str, Any], args: List[str]) -> ExecuteResult:
    if err := _require_init(state):
        return err
    lines = []
    cid = _current_commit_id(state)
    seen: set = set()
    while cid and cid not in seen:
        seen.add(cid)
        commit = state["commits"][cid]
        lines.append(f"commit {cid}\n    {commit['message']}")
        cid = commit["parents"][0] if commit["parents"] else None
    return ExecuteResult(state=state, output="\n\n".join(lines) if lines else "No commits yet.")


def _cmd_push(state: Dict[str, Any], args: List[str]) -> ExecuteResult:
    if err := _require_init(state):
        return err
    branch = _current_branch(state)
    if branch is None:
        return _error(state, "Not on a branch (detached HEAD) -- cannot push here.")
    state = copy.deepcopy(state)
    state["remote_branches"][branch] = state["branches"][branch]
    return ExecuteResult(state=state, output=f"To origin\n   {branch} -> {branch}")


def _cmd_pull(state: Dict[str, Any], args: List[str]) -> ExecuteResult:
    if err := _require_init(state):
        return err
    branch = _current_branch(state)
    if branch is None or branch not in state["remote_branches"]:
        return _error(state, "There is no tracked remote branch to pull.")
    remote_commit = state["remote_branches"][branch]
    if remote_commit == state["branches"][branch]:
        return ExecuteResult(state=state, output="Already up to date.")
    # Pulling is fetch + merge of the remote-tracking branch into the
    # current one -- reuse the merge machinery against a scratch copy that
    # briefly carries a same-named branch pointing at the remote commit, so
    # fast-forward/conflict logic isn't duplicated. The scratch branch is
    # discarded either way; only the current branch's own pointer is real.
    scratch = copy.deepcopy(state)
    scratch["branches"]["__remote_tracking__"] = remote_commit
    result = _cmd_merge(scratch, ["__remote_tracking__"])
    result.state["branches"].pop("__remote_tracking__", None)
    result.output = result.output.replace("__remote_tracking__", f"origin/{branch}")
    if result.state.get("merge_in_progress"):
        result.state["merge_in_progress"]["other_branch"] = f"origin/{branch}"
    return result


COMMANDS = {
    "init": _cmd_init,
    "add": _cmd_add,
    "branch": _cmd_branch,
    "checkout": _cmd_checkout,
    "switch": _cmd_checkout,
    "merge": _cmd_merge,
    "status": _cmd_status,
    "log": _cmd_log,
    "push": _cmd_push,
    "pull": _cmd_pull,
}


def _tokenize(command_line: str) -> tuple[str, List[str], Optional[str]]:
    """Splits `git <subcommand> [args...] [-m "message"]` into
    (subcommand, positional args, commit message). Not a shell -- quoting is
    only ever recognized around a trailing -m message, nothing else."""
    text = command_line.strip()
    message = None
    if ' -m "' in text or text.endswith(' -m'):
        marker = text.find(" -m ")
        if marker != -1:
            head, rest = text[:marker], text[marker + 4:].strip()
            if rest.startswith('"') and rest.endswith('"') and len(rest) >= 2:
                message = rest[1:-1]
                text = head
    parts = text.split()
    if not parts or parts[0] != "git":
        return "", [], message
    if len(parts) < 2:
        return "", [], message
    return parts[1], parts[2:], message


def execute(state: Dict[str, Any], command_line: str) -> ExecuteResult:
    """Runs one command line against `state`, returning a new state --
    `state` itself is never mutated, so a caller can always fall back to it
    on error."""
    subcommand, args, message = _tokenize(command_line)
    if not subcommand:
        return _error(state, f"Not a recognized command: {command_line!r}")
    if subcommand == "commit":
        return _cmd_commit(state, args, message)
    handler = COMMANDS.get(subcommand)
    if handler is None:
        return _error(state, f"git: '{subcommand}' is not a supported command in this quest.")
    return handler(state, args)


def apply_action(state: Dict[str, Any], action: Dict[str, Any]) -> ExecuteResult:
    """One transcript entry: either a typed git command, or a file edit.

    A file edit is not a git command (real git has no "edit" subcommand --
    you change a file with an editor, then `git add` it) and file *content*
    can never be expressed as a command string. So the transcript this quest
    submits for grading/replay is a mixed list of
    ``{"kind": "command", "value": "git add ."}`` and
    ``{"kind": "edit", "file": "app.py", "content": "..."}`` entries -- the
    same two action types the interactive frontend terminal performs live
    (typing at the prompt, and editing a conflicted file in its own panel).
    """
    kind = action.get("kind")
    if kind == "edit":
        file_name = action.get("file")
        if not file_name:
            return _error(state, "Malformed edit action: missing 'file'.")
        state = copy.deepcopy(state)
        state["working_files"][file_name] = action.get("content", "")
        return ExecuteResult(state=state, output=f"Edited {file_name}.")
    if kind == "command":
        return execute(state, action.get("value", ""))
    return _error(state, f"Unknown action kind: {kind!r}")


def replay(start_state: Dict[str, Any], actions: List[Dict[str, Any]]) -> ExecuteResult:
    """Applies `actions` (see `apply_action`) in order from `start_state`,
    stopping at the first real error (a mission's checklist is expected to
    be satisfiable by a fully successful sequence -- an erroring action
    mid-way is always a student mistake, not something to silently skip
    past). A mid-sequence merge conflict is not itself a stopping error --
    the very next actions are expected to be the edit(s) that resolve it."""
    if len(actions) > MAX_COMMANDS:
        return _error(start_state, f"Too many actions (max {MAX_COMMANDS}).")
    state = start_state
    last_output = ""
    for action in actions:
        result = apply_action(state, action)
        state = result.state
        last_output = result.output
        if result.error and result.error != "conflict":
            return ExecuteResult(state=state, output=last_output, error=result.error)
    return ExecuteResult(state=state, output=last_output)


def _branch_files(state: Dict[str, Any], branch: str) -> Optional[Dict[str, str]]:
    commit_id = state["branches"].get(branch)
    if commit_id is None:
        return None
    return _commit_files(state, commit_id)


def evaluate_checklist(state: Dict[str, Any], checklist: List[Dict[str, Any]]) -> List[str]:
    """Checks a mission's pass/fail criteria against a (server-replayed)
    final state. Returns the human-readable description of every criterion
    that failed -- empty means every criterion passed. Grading (see
    app.services.exercise_grading's STRATEGY_GIT_QUEST) is `not failures`;
    the descriptions are surfaced to the student as feedback either way, so
    each one is written as something a student can act on, not a code."""
    failures: List[str] = []
    for criterion in checklist:
        kind = criterion.get("kind")
        # An author-written description always wins; otherwise each branch
        # below falls back to its own specific, actionable message -- never
        # to the bare `kind` string, which wouldn't mean anything to a
        # student.
        description = criterion.get("description")

        if kind == "branch_exists":
            if criterion["branch"] not in state["branches"]:
                failures.append(description or f"Branch '{criterion['branch']}' should exist.")

        elif kind == "file_equals":
            files = _branch_files(state, criterion["branch"]) if "branch" in criterion else state["working_files"]
            if files is None or files.get(criterion["file"]) != criterion["content"]:
                failures.append(description or f"'{criterion['file']}' should contain exactly the expected content.")

        elif kind == "file_contains":
            files = _branch_files(state, criterion["branch"]) if "branch" in criterion else state["working_files"]
            content = (files or {}).get(criterion["file"], "")
            if criterion["text"] not in content:
                failures.append(description or f"'{criterion['file']}' should contain {criterion['text']!r}.")

        elif kind == "no_conflict_markers":
            branch = criterion.get("branch")
            files = _branch_files(state, branch) if branch else state["working_files"]
            if any("<<<<<<<" in content for content in (files or {}).values()):
                failures.append(description or "No file should still contain unresolved conflict markers.")

        elif kind == "commit_count_at_least":
            branch = criterion["branch"]
            count = 0
            cid = state["branches"].get(branch)
            seen: set = set()
            while cid and cid not in seen:
                seen.add(cid)
                count += 1
                cid = state["commits"][cid]["parents"][0] if state["commits"][cid]["parents"] else None
            if count < criterion["count"]:
                failures.append(description or f"'{branch}' should have at least {criterion['count']} commit(s).")

        elif kind == "remote_branch_matches_local":
            branch = criterion["branch"]
            if state["remote_branches"].get(branch) != state["branches"].get(branch):
                failures.append(description or f"'{branch}' should be pushed to origin.")

        elif kind == "merge_commit_exists":
            branch = criterion["branch"]
            if not any(
                len(commit["parents"]) >= 2
                for cid, commit in state["commits"].items()
                if cid in _ancestors(state, state["branches"].get(branch))
            ):
                failures.append(description or f"'{branch}' should contain a merge commit.")

        else:
            failures.append(f"Unknown checklist criterion: {kind!r}")

    return failures
