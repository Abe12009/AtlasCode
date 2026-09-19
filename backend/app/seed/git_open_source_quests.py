"""Git & Open-Source Quests -- a hands-on companion to the existing
``git-github`` course (see app.seed.git_github), which teaches the vocabulary
(branch, merge, remote, pull request) entirely through fill-in-the-command and
prediction exercises and never once shows a real repo state or a real
conflict happening. This course is where a student actually does it, against
a simulated repo (see app.services.git_simulator) -- not real git, for the
reasons in the Feature 4 proposal (sandbox surface, deterministic NPC
conflicts, a shared reproducible "community project" for the final stage).

Three missions, one per lesson:
  1. Your First Commits -- init, add, commit, push. The basics.
  2. The Merge Conflict -- a teammate's commit is already waiting on `main`
     when the student's own already-committed feature branch gets merged
     back in; both changed the same line, so it's a real conflict, not a
     staged one. Authored, not generated (see GitQuest's docstring).
  3. Open a Pull Request -- branch, make a real change to a shared
     "community" file, push. Grading is an automated checklist (file
     content present, branch pushed, no leftover conflict markers), not a
     simulated human reviewer -- see the Feature 4 proposal on why that's
     out of scope for v1.
"""

from app.models import DifficultyEnum as D

from .authoring import CourseSpec, GitQuest, Lesson, Module, T, Text, seed_course


def _base_state(files: dict) -> dict:
    """An initialized repo with one commit on `main` holding `files`."""
    return {
        "commits": {"c1": {"parents": [], "message": "Initial commit", "files": dict(files)}},
        "branches": {"main": "c1"},
        "remote_branches": {},
        "head": {"branch": "main"},
        "working_files": dict(files),
        "staged_files": {},
        "merge_in_progress": None,
        "initialized": True,
    }


# ---------------------------------------------------------------------------
# Mission 1 -- Your First Commits
# ---------------------------------------------------------------------------

MISSION_1_INITIAL = {
    "commits": {},
    "branches": {},
    "remote_branches": {},
    "head": None,
    "working_files": {},
    "staged_files": {},
    "merge_in_progress": None,
    "initialized": False,
}

MISSION_1_CHECKLIST = [
    {"kind": "branch_exists", "branch": "main"},
    {
        "kind": "file_equals", "file": "hello.py", "content": "print('Hello, Open Source!')",
        "description": "hello.py should contain exactly: print('Hello, Open Source!')",
    },
    {"kind": "commit_count_at_least", "branch": "main", "count": 1},
    {
        "kind": "remote_branch_matches_local", "branch": "main",
        "description": "Your commit should be pushed to origin -- don't forget 'git push'.",
    },
]

MISSION_1_SOLUTION = [
    {"kind": "command", "value": "git init"},
    {"kind": "edit", "file": "hello.py", "content": "print('Hello, Open Source!')"},
    {"kind": "command", "value": "git add ."},
    {"kind": "command", "value": 'git commit -m "Add hello.py"'},
    {"kind": "command", "value": "git push"},
]


# ---------------------------------------------------------------------------
# Mission 2 -- The Merge Conflict
# ---------------------------------------------------------------------------

_M2_BASE_CONFIG = "DEBUG = False\n"

MISSION_2_INITIAL = {
    "commits": {
        "c1": {"parents": [], "message": "Initial commit", "files": {"config.py": _M2_BASE_CONFIG}},
        # The student's own already-committed feature-branch work.
        "c2": {
            "parents": ["c1"], "message": "Add staging debug flag",
            "files": {"config.py": "DEBUG = True  # staging\n"},
        },
        # A teammate's commit, already sitting on main -- authored directly
        # into the starting state, not generated at merge time.
        "c3": {
            "parents": ["c1"], "message": "Disable debug for prod safety",
            "files": {"config.py": "DEBUG = False  # locked for prod\n"},
        },
    },
    "branches": {"main": "c3", "feature/staging-debug": "c2"},
    "remote_branches": {"main": "c3"},
    "head": {"branch": "feature/staging-debug"},
    "working_files": {"config.py": "DEBUG = True  # staging\n"},
    "staged_files": {},
    "merge_in_progress": None,
    "initialized": True,
}

MISSION_2_CHECKLIST = [
    {"kind": "merge_commit_exists", "branch": "main", "description": "main should contain a merge commit."},
    {"kind": "no_conflict_markers", "description": "No file should still contain <<<<<<< / ======= / >>>>>>> markers."},
    {"kind": "commit_count_at_least", "branch": "main", "count": 3},
]

MISSION_2_SOLUTION = [
    {"kind": "command", "value": "git checkout main"},
    {"kind": "command", "value": "git merge feature/staging-debug"},  # produces a conflict
    {"kind": "edit", "file": "config.py", "content": "DEBUG = False  # locked for prod; use .env for staging\n"},
    {"kind": "command", "value": "git add config.py"},
    {"kind": "command", "value": 'git commit -m "Merge staging-debug, keep prod locked"'},
]


# ---------------------------------------------------------------------------
# Mission 3 -- Open a Pull Request
# ---------------------------------------------------------------------------

_COMMUNITY_NOTES = "# Community Notes\n\n- Be kind in code review.\n"
_NEW_TIP = "- Always write a clear PR description."

MISSION_3_INITIAL = _base_state({"community_notes.md": _COMMUNITY_NOTES})
MISSION_3_INITIAL["remote_branches"] = {"main": "c1"}

MISSION_3_CHECKLIST = [
    {"kind": "branch_exists", "branch": "add-my-tip"},
    {
        "kind": "file_contains", "branch": "add-my-tip", "file": "community_notes.md", "text": _NEW_TIP,
        "description": f"community_notes.md on 'add-my-tip' should contain: {_NEW_TIP}",
    },
    {
        "kind": "remote_branch_matches_local", "branch": "add-my-tip",
        "description": "Push your branch to origin to open the PR -- 'git push'.",
    },
    {"kind": "no_conflict_markers"},
]

MISSION_3_SOLUTION = [
    {"kind": "command", "value": "git checkout -b add-my-tip"},
    {"kind": "edit", "file": "community_notes.md", "content": _COMMUNITY_NOTES + _NEW_TIP + "\n"},
    {"kind": "command", "value": "git add ."},
    {"kind": "command", "value": 'git commit -m "Add PR description tip"'},
    {"kind": "command", "value": "git push"},
]


GIT_OPEN_SOURCE_QUESTS = CourseSpec(
    slug="git-open-source-quests",
    stage=5,
    track="engineering",
    icon="🗺️",
    difficulty=D.intermediate,
    estimated_hours=6,
    prerequisite_slug="git-github",
    title=T(
        "Git & Open-Source Quests",
        "Quêtes Git & Open Source",
        "مهام Git ومفتوح المصدر",
    ),
    description=T(
        "Put the Git commands you already know to work in a real (simulated) repository -- commit, push, resolve a real merge conflict, and open your first pull request.",
        "Mettez en pratique les commandes Git que vous connaissez déjà dans un dépôt réel (simulé) -- committez, poussez, résolvez un vrai conflit de fusion, et ouvrez votre première pull request.",
        "طبّق أوامر Git التي تعرفها بالفعل في مستودع حقيقي (محاكى) — قم بالـ commit والـ push، وحلّ تعارض دمج حقيقي، وافتح أول pull request لك.",
    ),
    skills=T(
        "git init/add/commit/push/pull, branching, merge conflicts, pull requests",
        "git init/add/commit/push/pull, branches, conflits de fusion, pull requests",
        "git init/add/commit/push/pull، الفروع، تعارضات الدمج، طلبات السحب",
    ),
    modules=[
        Module(
            slug="git-open-source-quests",
            title=T("Quests", "Quêtes", "المهام"),
            description=T(
                "Three missions, each a real (simulated) repository to work in.",
                "Trois missions, chacune un dépôt réel (simulé) à mettre en pratique.",
                "ثلاث مهام، كل واحدة مستودع حقيقي (محاكى) للعمل فيه.",
            ),
            lessons=[
                Lesson(
                    slug="your-first-commits",
                    minutes=20,
                    xp=40,
                    difficulty=D.beginner,
                    title=T("Your First Commits", "Vos Premiers Commits", "أول عمليات commit لك"),
                    story=T(
                        "A fresh, empty repository is waiting. Get your first change committed and pushed.",
                        "Un dépôt tout neuf et vide vous attend. Committez et poussez votre premier changement.",
                        "مستودع جديد وفارغ في انتظارك. قم بعمل commit و push لأول تغيير لك.",
                    ),
                    objective=T(
                        "Initialize a repository, commit a file, and push it.",
                        "Initialisez un dépôt, committez un fichier, et poussez-le.",
                        "قم بتهيئة مستودع، وعمل commit لملف، ثم ادفعه.",
                    ),
                    skills=T("git init, add, commit, push", "git init, add, commit, push", "git init، add، commit، push"),
                    blocks=[
                        Text(T(
                            "This is a real (simulated) terminal -- every command you type actually runs against a real repository state. Type 'git init' to start, create hello.py with the editor panel, then 'git add .', 'git commit -m \"...\"', and 'git push'.",
                            "Ceci est un vrai terminal (simulé) -- chaque commande tapée s'exécute réellement sur un état de dépôt réel. Tapez « git init » pour commencer, créez hello.py avec le panneau éditeur, puis « git add . », « git commit -m \"...\" », et « git push ».",
                            "هذه واجهة طرفية حقيقية (محاكاة) — كل أمر تكتبه يُنفَّذ فعليًا على حالة مستودع حقيقية. اكتب 'git init' للبدء، أنشئ hello.py عبر لوحة التحرير، ثم 'git add .' و 'git commit -m \"...\"' و 'git push'.",
                        )),
                    ],
                    exercises=[
                        GitQuest(
                            prompt=T(
                                "Initialize a repository, create hello.py containing exactly: print('Hello, Open Source!'), commit it, and push.",
                                "Initialisez un dépôt, créez hello.py contenant exactement : print('Hello, Open Source!'), committez-le, et poussez.",
                                "قم بتهيئة مستودع، أنشئ hello.py يحتوي بالضبط على: print('Hello, Open Source!')، اعمل له commit، ثم push.",
                            ),
                            hint=T(
                                "git init, then edit hello.py, then git add ., git commit -m \"...\", git push.",
                                "git init, puis éditez hello.py, puis git add ., git commit -m \"...\", git push.",
                                "git init، ثم عدّل hello.py، ثم git add .، و git commit -m \"...\"، و git push.",
                            ),
                            explanation=T(
                                "git init creates the repository; git add stages a file; git commit records a snapshot; git push sends it to the remote.",
                                "git init crée le dépôt ; git add prépare un fichier ; git commit enregistre un instantané ; git push l'envoie vers le distant.",
                                "git init ينشئ المستودع؛ git add يجهّز ملفًا؛ git commit يسجّل لقطة؛ git push يرسلها إلى المستودع البعيد.",
                            ),
                            initial_state=MISSION_1_INITIAL,
                            checklist=MISSION_1_CHECKLIST,
                            solution_actions=MISSION_1_SOLUTION,
                            xp=40,
                        ),
                    ],
                ),
                Lesson(
                    slug="the-merge-conflict",
                    minutes=25,
                    xp=50,
                    difficulty=D.intermediate,
                    title=T("The Merge Conflict", "Le Conflit de Fusion", "تعارض الدمج"),
                    story=T(
                        "While you were working on your branch, a teammate pushed a change to the same line on main. Time to merge -- and resolve it.",
                        "Pendant que vous travailliez sur votre branche, un coéquipier a poussé un changement sur la même ligne dans main. Il est temps de fusionner -- et de résoudre le conflit.",
                        "بينما كنت تعمل على فرعك، دفع زميل تغييرًا على نفس السطر في main. حان وقت الدمج — وحل التعارض.",
                    ),
                    objective=T(
                        "Merge your branch into main, resolve the real conflict it produces, and commit.",
                        "Fusionnez votre branche dans main, résolvez le vrai conflit produit, et committez.",
                        "ادمج فرعك في main، وحل التعارض الحقيقي الناتج، ثم اعمل commit.",
                    ),
                    skills=T("git checkout, merge, conflict resolution", "git checkout, merge, résolution de conflits", "git checkout، merge، حل التعارضات"),
                    blocks=[
                        Text(T(
                            "You're already on 'feature/staging-debug', which you already committed to. main has moved on too -- a teammate's commit is already there. Checkout main, then merge your branch in. Git will report a real conflict in config.py: edit the file to remove the <<<<<<< / ======= / >>>>>>> markers with content you choose, then git add and git commit to finish the merge.",
                            "Vous êtes déjà sur « feature/staging-debug », où vous avez déjà committé. main a aussi avancé -- un commit d'un coéquipier y est déjà. Basculez sur main, puis fusionnez votre branche. Git signalera un vrai conflit dans config.py : éditez le fichier pour retirer les marqueurs <<<<<<< / ======= / >>>>>>> avec le contenu de votre choix, puis git add et git commit pour terminer la fusion.",
                            "أنت بالفعل على 'feature/staging-debug'، حيث قمت بعمل commit مسبقًا. تقدّم main أيضًا — commit من زميل موجود فيه بالفعل. انتقل إلى main، ثم ادمج فرعك. سيُبلغ Git عن تعارض حقيقي في config.py: عدّل الملف لإزالة علامات <<<<<<< / ======= / >>>>>>> بالمحتوى الذي تختاره، ثم نفّذ git add و git commit لإنهاء الدمج.",
                        )),
                    ],
                    exercises=[
                        GitQuest(
                            prompt=T(
                                "Checkout main, merge feature/staging-debug, resolve the conflict in config.py, and commit the merge.",
                                "Basculez sur main, fusionnez feature/staging-debug, résolvez le conflit dans config.py, et committez la fusion.",
                                "انتقل إلى main، وادمج feature/staging-debug، وحل التعارض في config.py، ثم اعمل commit للدمج.",
                            ),
                            hint=T(
                                "git checkout main, git merge feature/staging-debug, edit config.py to remove the conflict markers, git add config.py, git commit -m \"...\".",
                                "git checkout main, git merge feature/staging-debug, éditez config.py pour retirer les marqueurs, git add config.py, git commit -m \"...\".",
                                "git checkout main، و git merge feature/staging-debug، عدّل config.py لإزالة علامات التعارض، و git add config.py، و git commit -m \"...\".",
                            ),
                            explanation=T(
                                "Both branches changed the same line since they diverged, so git can't auto-merge -- it writes both versions into the file for you to reconcile by hand.",
                                "Les deux branches ont modifié la même ligne depuis leur divergence, donc git ne peut pas fusionner automatiquement -- il écrit les deux versions dans le fichier pour que vous les réconciliez à la main.",
                                "غيّر كلا الفرعين نفس السطر منذ تباعدهما، لذا لا يستطيع git الدمج التلقائي — فيكتب كلا النسختين في الملف لتوفّق بينهما يدويًا.",
                            ),
                            initial_state=MISSION_2_INITIAL,
                            checklist=MISSION_2_CHECKLIST,
                            solution_actions=MISSION_2_SOLUTION,
                            xp=50,
                        ),
                    ],
                ),
                Lesson(
                    slug="open-a-pull-request",
                    minutes=20,
                    xp=45,
                    difficulty=D.intermediate,
                    title=T("Open a Pull Request", "Ouvrir une Pull Request", "افتح Pull Request"),
                    story=T(
                        "A shared community project is waiting for a contribution. Add your tip and open your first PR.",
                        "Un projet communautaire partagé attend une contribution. Ajoutez votre astuce et ouvrez votre première PR.",
                        "مشروع مجتمعي مشترك في انتظار مساهمة. أضف نصيحتك وافتح أول PR لك.",
                    ),
                    objective=T(
                        "Branch, add your entry to the shared file, and push to open the PR.",
                        "Créez une branche, ajoutez votre entrée au fichier partagé, et poussez pour ouvrir la PR.",
                        "أنشئ فرعًا، أضف إدخالك إلى الملف المشترك، وادفع لفتح الـ PR.",
                    ),
                    skills=T("branching, contributing, pull requests", "branches, contribution, pull requests", "الفروع، المساهمة، طلبات السحب"),
                    blocks=[
                        Text(T(
                            "community_notes.md already has a couple of entries from other contributors. Create a branch called add-my-tip, add the line \"- Always write a clear PR description.\" to the file, commit, and push -- pushing your branch is how you open the PR in this quest.",
                            "community_notes.md contient déjà quelques entrées d'autres contributeurs. Créez une branche nommée add-my-tip, ajoutez la ligne « - Always write a clear PR description. » au fichier, committez, et poussez -- pousser votre branche, c'est ouvrir la PR dans cette quête.",
                            "يحتوي community_notes.md بالفعل على بعض الإدخالات من مساهمين آخرين. أنشئ فرعًا باسم add-my-tip، وأضف السطر \"- Always write a clear PR description.\" إلى الملف، ثم اعمل commit و push -- دفع فرعك هو طريقة فتح الـ PR في هذه المهمة.",
                        )),
                    ],
                    exercises=[
                        GitQuest(
                            prompt=T(
                                "Create branch add-my-tip, add \"- Always write a clear PR description.\" to community_notes.md, commit, and push to open the PR.",
                                "Créez la branche add-my-tip, ajoutez « - Always write a clear PR description. » à community_notes.md, committez, et poussez pour ouvrir la PR.",
                                "أنشئ فرع add-my-tip، وأضف \"- Always write a clear PR description.\" إلى community_notes.md، واعمل commit ثم push لفتح الـ PR.",
                            ),
                            hint=T(
                                "git checkout -b add-my-tip, edit community_notes.md, git add ., git commit -m \"...\", git push.",
                                "git checkout -b add-my-tip, éditez community_notes.md, git add ., git commit -m \"...\", git push.",
                                "git checkout -b add-my-tip، عدّل community_notes.md، و git add .، و git commit -m \"...\"، و git push.",
                            ),
                            explanation=T(
                                "A pull request is a pushed branch asking to merge into the project -- the branch and the push are the real mechanics behind the button on GitHub's website.",
                                "Une pull request est une branche poussée demandant à être fusionnée dans le projet -- la branche et le push sont le mécanisme réel derrière le bouton du site GitHub.",
                                "طلب السحب (Pull Request) هو فرع تم دفعه يطلب الدمج في المشروع — الفرع والـ push هما الآلية الحقيقية وراء الزر الموجود في موقع GitHub.",
                            ),
                            initial_state=MISSION_3_INITIAL,
                            checklist=MISSION_3_CHECKLIST,
                            solution_actions=MISSION_3_SOLUTION,
                            xp=45,
                        ),
                    ],
                ),
            ],
        ),
    ],
)


async def seed_git_open_source_quests(db, order: int) -> int:
    print("Seeding Git & Open-Source Quests...")
    return await seed_course(db, GIT_OPEN_SOURCE_QUESTS, order)
