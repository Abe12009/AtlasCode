from .base import (
    get_or_create_course, get_or_create_module, get_or_create_lesson,
    LanguageEnum, DifficultyEnum, ExerciseTypeEnum
)
from .microquest_content import seed_blocks


async def seed_git_github(db):
    print("Seeding Git & GitHub...")
    
    course_id = await get_or_create_course(db, "git-github", 4, [
        {"language": LanguageEnum.en, "title": "Git & GitHub", "description": "Version control and collaboration with Git and GitHub", "skills": "Git, GitHub, version control, branching, collaboration"},
        {"language": LanguageEnum.fr, "title": "Git et GitHub", "description": "Contrôle de version et collaboration avec Git et GitHub", "skills": "Git, GitHub, contrôle de version, branches, collaboration"},
        {"language": LanguageEnum.ar, "title": "Git و GitHub", "description": "التحكم في الإصدار والتعاون مع Git و GitHub", "skills": "Git، GitHub، التحكم في الإصدار، الفروع، التعاون"},
    ])
    
    module_id = await get_or_create_module(db, course_id, "git-github", 1, [
        {"language": LanguageEnum.en, "title": "Git & GitHub", "description": "Master version control and collaboration"},
        {"language": LanguageEnum.fr, "title": "Git et GitHub", "description": "Maîtrisez le contrôle de version et la collaboration"},
        {"language": LanguageEnum.ar, "title": "Git و GitHub", "description": "أتقن التحكم في الإصدار والتعاون"},
    ])
    
    # Lesson 30: Version Control and Git
    await get_or_create_lesson(db, module_id, "version-control-git", 1,
        DifficultyEnum.beginner, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "Version Control and Git", "story": "Learn why version control matters and how Git works", "objective": "Explain version control concepts and initialize a Git repository", "skills": "Version control, Git, repository, commits"},
            {"language": LanguageEnum.fr, "title": "Contrôle de Version et Git", "story": "Apprenez pourquoi le contrôle de version est important et comment Git fonctionne", "objective": "Expliquer les concepts de contrôle de version et initialiser un dépôt Git", "skills": "Contrôle de version, Git, dépôt, commits"},
            {"language": LanguageEnum.ar, "title": "التحكم في الإصدار و Git", "story": "تعلم لماذا يهم التحكم في الإصدار وكيف يعمل Git", "objective": "شرح مفاهيم التحكم في الإصدار وتهيئة مستودع Git", "skills": "التحكم في الإصدار، Git، المستودع، الـ commits"},
        ],
        [
            {"type": "text", "order": 1, "content": "Version control tracks changes to files over time. Git is a distributed version control system. Every developer has a full copy of the repository. Key concepts: repository, commit, staging area, working directory."},
            {"type": "code", "order": 2, "content": "Basic Git workflow:", "code_example": '# Initialize a repository\ngit init\n\n# Check status\ngit status\n\n# Stage changes\ngit add file.py\n# or stage all\ngit add .\n\n# Commit with message\ngit commit -m "Add initial files"'},
            {"type": "text", "order": 3, "content": "git init creates a new repo. git add stages changes. git commit saves a snapshot. Commits should be atomic (one logical change) with clear messages."},
        ],
        [
            {
                "type": ExerciseTypeEnum.multiple_choice,
                "order": 1,
                "xp_reward": 10,
                "starter_code": "",
                "solution_code": "",
                "validation_config": "",
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "What does git add do?", "hint": "Prepares changes for commit", "explanation": "git add stages changes in the staging area, preparing them for the next commit."},
                    {"language": LanguageEnum.fr, "prompt": "Que fait git add ?", "hint": "Prépare les changements pour le commit", "explanation": "git add met les changements en zone de staging, les préparant pour le prochain commit."},
                    {"language": LanguageEnum.ar, "prompt": "ماذا يفعل git add؟", "hint": "يجهز التغييرات للـ commit", "explanation": "git add يضع التغييرات في منطقة الـ staging، مجهزة للـ commit التالي."},
                ],
                "options": [
                    {"order": 1, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "Commits changes permanently"}, {"language": LanguageEnum.fr, "text": "Valide les changements définitivement"}, {"language": LanguageEnum.ar, "text": "يثبت التغييرات نهائياً"}]},
                    {"order": 2, "is_correct": True, "translations": [{"language": LanguageEnum.en, "text": "Stages changes for commit"}, {"language": LanguageEnum.fr, "text": "Met en zone de staging pour commit"}, {"language": LanguageEnum.ar, "text": "يجهز التغييرات للـ commit"}]},
                    {"order": 3, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "Pushes to remote"}, {"language": LanguageEnum.fr, "text": "Pousse vers le distant"}, {"language": LanguageEnum.ar, "text": "يرفع للمستودع البعيد"}]},
                    {"order": 4, "is_correct": False, "translations": [{"language": LanguageEnum.en, "text": "Creates a branch"}, {"language": LanguageEnum.fr, "text": "Crée une branche"}, {"language": LanguageEnum.ar, "text": "ينشئ فرعاً"}]},
                ]
            }
        ]
    )
    
    # Lesson 31: Commits and History
    await get_or_create_lesson(db, module_id, "commits-and-history", 2,
        DifficultyEnum.beginner, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "Commits and History", "story": "Navigate and understand your project history", "objective": "View commit history, compare changes, and write good commit messages", "skills": "git log, git diff, commit messages, history"},
            {"language": LanguageEnum.fr, "title": "Commits et Historique", "story": "Naviguez et comprenez l'historique de votre projet", "objective": "Voir l'historique des commits, comparer les changements, écrire de bons messages", "skills": "git log, git diff, messages de commit, historique"},
            {"language": LanguageEnum.ar, "title": "الـ Commits والتاريخ", "story": "تنقل وافهم تاريخ مشروعك", "objective": "عرض تاريخ الـ commits، مقارنة التغييرات، وكتابة رسائل commit جيدة", "skills": "git log، git diff، رسائل commit، التاريخ"},
        ],
        [
            {"type": "text", "order": 1, "content": "git log shows commit history. git diff shows changes between commits or working directory. Good commit messages: short summary (50 chars), blank line, detailed explanation if needed. Use imperative mood: \"Add feature\" not \"Added feature\"."},
            {"type": "code", "order": 2, "content": "History commands:", "code_example": '# View history\ngit log\n# One line per commit\ngit log --oneline\n# Show changes in last commit\ngit show HEAD\n# Compare working dir with last commit\ngit diff\n# Compare staged changes\ngit diff --staged'},
            {"type": "text", "order": 3, "content": "HEAD is the current commit. HEAD~1 is parent. Use git log --oneline --graph for visual history. Write meaningful messages for your future self."},
            # Micro-Quest blocks (hook 0, blueprint 4, exam_tip 5). The blueprint
            # is the match_pairs interaction. Lessons without these render as before.
            *seed_blocks("commits-and-history"),
        ],
        [
            {
                "type": ExerciseTypeEnum.ordering,
                "order": 1,
                "xp_reward": 10,
                "starter_code": "",
                "solution_code": "",
                "validation_config": "",
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Order the commands to create a commit and view history.", "hint": "Init, add, commit, then log", "explanation": "Initialize repo, stage files, commit with message, then view history."},
                    {"language": LanguageEnum.fr, "prompt": "Ordonnez les commandes pour créer un commit et voir l'historique.", "hint": "Init, add, commit, puis log", "explanation": "Initialisez le repo, mettez en staging, commitez avec message, puis voyez l'historique."},
                    {"language": LanguageEnum.ar, "prompt": "رتب الأوامر لإنشاء commit وعرض التاريخ.", "hint": "init، add، commit، ثم log", "explanation": "هيئ المستودع، ضع الملفات في الـ staging، اعمل commit برسالة، ثم اعرض التاريخ."},
                ],
                "options": [
                    {"order": 1, "is_correct": True, "translations": [{"language": LanguageEnum.en, "text": "git init"}, {"language": LanguageEnum.fr, "text": "git init"}, {"language": LanguageEnum.ar, "text": "git init"}]},
                    {"order": 2, "is_correct": True, "translations": [{"language": LanguageEnum.en, "text": "git add ."}, {"language": LanguageEnum.fr, "text": "git add ."}, {"language": LanguageEnum.ar, "text": "git add ."}]},
                    {"order": 3, "is_correct": True, "translations": [{"language": LanguageEnum.en, "text": "git commit -m \"Initial commit\""}, {"language": LanguageEnum.fr, "text": "git commit -m \"Commit initial\""}, {"language": LanguageEnum.ar, "text": "git commit -m \"الـ commit الأول\""}]},
                    {"order": 4, "is_correct": True, "translations": [{"language": LanguageEnum.en, "text": "git log --oneline"}, {"language": LanguageEnum.fr, "text": "git log --oneline"}, {"language": LanguageEnum.ar, "text": "git log --oneline"}]},
                ]
            }
        ]
    )
    
    # Lesson 32: Branches and Merging
    await get_or_create_lesson(db, module_id, "branches-and-merging", 3,
        DifficultyEnum.intermediate, 40, 60,
        [
            {"language": LanguageEnum.en, "title": "Branches and Merging", "story": "Work on features independently and combine them", "objective": "Create, switch, merge, and delete branches", "skills": "git branch, checkout, merge, branch deletion, conflicts"},
            {"language": LanguageEnum.fr, "title": "Branches et Fusion", "story": "Travaillez sur des fonctionnalités indépendamment et combinez-les", "objective": "Créer, basculer, fusionner et supprimer des branches", "skills": "git branch, checkout, merge, suppression de branches, conflits"},
            {"language": LanguageEnum.ar, "title": "الفروع والدمج", "story": "اعمل على الميزات بشكل مستقل واجمعها", "objective": "إنشاء، تبديل، دمج، وحذف الفروع", "skills": "git branch، checkout، merge، حذف الفروع، التعارضات"},
        ],
        [
            {"type": "text", "order": 1, "content": "Branches let you work on features without affecting main. git branch creates, git checkout (or git switch) switches. Merge combines branches. Conflicts happen when same lines changed differently - resolve manually."},
            {"type": "code", "order": 2, "content": "Branch workflow:", "code_example": '# Create and switch to new branch\ngit checkout -b feature/login\n\n# Work on feature... make commits\n\n# Switch back to main\ngit checkout main\n\n# Merge feature into main\ngit merge feature/login\n\n# Delete merged branch\ngit branch -d feature/login'},
            {"type": "text", "order": 3, "content": "Fast-forward merge when no new commits on main. Merge commit when both branches have new commits. Resolve conflicts by editing files, then git add and git commit."},
        ],
        [
            {
                "type": ExerciseTypeEnum.debugging,
                "order": 1,
                "xp_reward": 15,
                "starter_code": '# You are on main branch\n# A feature branch "feature/dashboard" exists\n# Merge it into main\n\ngit merge ____',
                "solution_code": 'git merge feature/dashboard',
                "test_code": '',
                "validation_config": '{"expected_keywords": ["merge", "feature/dashboard"]}',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Complete the command to merge the feature/dashboard branch into main.", "hint": "git merge branch-name", "explanation": "git merge <branch> merges the specified branch into the current branch (main)."},
                    {"language": LanguageEnum.fr, "prompt": "Complétez la commande pour fusionner la branche feature/dashboard dans main.", "hint": "git merge nom-branche", "explanation": "git merge <branche> fusionne la branche spécifiée dans la branche courante (main)."},
                    {"language": LanguageEnum.ar, "prompt": "أكمل الأمر لدمج فرع feature/dashboard في main.", "hint": "git merge اسم-الفرع", "explanation": "git merge <فرع> يدمج الفرع المحدد في الفرع الحالي (main)."},
                ]
            }
        ]
    )
    
    # Lesson 33: GitHub and Remote Repositories
    await get_or_create_lesson(db, module_id, "github-remote-repos", 4,
        DifficultyEnum.beginner, 35, 50,
        [
            {"language": LanguageEnum.en, "title": "GitHub and Remote Repositories", "story": "Share your code and collaborate with remote repositories", "objective": "Push, pull, clone, and work with GitHub remotes", "skills": "git remote, push, pull, clone, GitHub"},
            {"language": LanguageEnum.fr, "title": "GitHub et Dépôts Distants", "story": "Partagez votre code et collaborez avec des dépôts distants", "objective": "Pousser, tirer, cloner et travailler avec les dépôts GitHub", "skills": "git remote, push, pull, clone, GitHub"},
            {"language": LanguageEnum.ar, "title": "GitHub والمستودعات البعيدة", "story": "شارك كودك وتعاون مع المستودعات البعيدة", "objective": "الدفع، السحب، الاستنساخ، والعمل مع مستودعات GitHub البعيدة", "skills": "git remote، push، pull، clone، GitHub"},
        ],
        [
            {"type": "text", "order": 1, "content": "Remote repositories (like GitHub) enable collaboration. git remote add origin <url> links local to remote. git push sends commits. git pull fetches and merges. git clone copies a remote repo locally."},
            {"type": "code", "order": 2, "content": "Remote workflow:", "code_example": '# Add remote\ngit remote add origin https://github.com/user/repo.git\n\n# Push to GitHub\ngit push -u origin main\n\n# Later: pull changes\ngit pull\n\n# Clone a repo\ngit clone https://github.com/user/repo.git'},
            {"type": "text", "order": 3, "content": "origin is the default remote name. -u sets upstream tracking. SSH or HTTPS for authentication. GitHub provides web interface for issues, PRs, actions."},
        ],
        [
            {
                "type": ExerciseTypeEnum.code_writing,
                "order": 1,
                "xp_reward": 10,
                "starter_code": '# Clone a repository from GitHub\n# Command: git clone ____',
                "solution_code": 'git clone https://github.com/username/repository.git',
                "test_code": '',
                "validation_config": '{"expected_keywords": ["clone", "github.com"]}',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Write the command to clone a GitHub repository.", "hint": "git clone https://github.com/...", "explanation": "git clone creates a local copy of a remote repository with full history."},
                    {"language": LanguageEnum.fr, "prompt": "Écrivez la commande pour cloner un dépôt GitHub.", "hint": "git clone https://github.com/...", "explanation": "git clone crée une copie locale d'un dépôt distant avec tout l'historique."},
                    {"language": LanguageEnum.ar, "prompt": "اكتب الأمر لاستنساخ مستودع GitHub.", "hint": "git clone https://github.com/...", "explanation": "git clone ينشئ نسخة محلية من مستودع بعيد مع كامل التاريخ."},
                ]
            }
        ]
    )
    
    # Lesson 34: Collaboration and Pull Requests
    await get_or_create_lesson(db, module_id, "collaboration-pull-requests", 5,
        DifficultyEnum.intermediate, 40, 60,
        [
            {"language": LanguageEnum.en, "title": "Collaboration and Pull Requests", "story": "Use GitHub's collaboration features for team development", "objective": "Create pull requests, review code, and merge on GitHub", "skills": "Pull requests, code review, forking, issues, GitHub workflow"},
            {"language": LanguageEnum.fr, "title": "Collaboration et Pull Requests", "story": "Utilisez les fonctionnalités de collaboration GitHub pour le développement d'équipe", "objective": "Créer des pull requests, reviewer le code, et fusionner sur GitHub", "skills": "Pull requests, review de code, forking, issues, workflow GitHub"},
            {"language": LanguageEnum.ar, "title": "التعاون و Pull Requests", "story": "استخدم ميزات تعاون GitHub للتطوير الجماعي", "objective": "إنشاء pull requests، مراجعة الكود، والدمج على GitHub", "skills": "Pull requests، مراجعة الكود، forking، issues، workflow GitHub"},
        ],
        [
            {"type": "text", "order": 1, "content": "Pull Requests (PRs) propose changes for review. Fork -> clone -> branch -> commit -> push -> PR. Reviewers comment, approve, request changes. Merge on GitHub (merge, squash, rebase). Issues track bugs/features."},
            {"type": "code", "order": 2, "content": "PR workflow:", "code_example": '# Fork repo on GitHub\n# Clone your fork\ngit clone https://github.com/yourname/repo.git\n\n# Create branch\ngit checkout -b fix/bug\n\n# Make changes, commit, push\ngit push origin fix/bug\n\n# Open PR on GitHub website'},
            {"type": "text", "order": 3, "content": "Keep PRs small and focused. Write clear descriptions. Respond to reviews promptly. Delete branch after merge. GitHub Actions can run tests automatically on PRs."},
        ],
        [
            {
                "type": ExerciseTypeEnum.prediction,
                "order": 1,
                "xp_reward": 10,
                "starter_code": '# GitHub collaboration flow:\n# 1. Fork repo\n# 2. ____\n# 3. Create branch\n# 4. Make changes & commit\n# 5. Push to fork\n# 6. ____',
                "solution_code": "Clone your fork\nOpen Pull Request",
                "validation_config": '{"expected_keywords": ["clone", ["pull request", "pr"]]}',
                "translations": [
                    {"language": LanguageEnum.en, "prompt": "Fill in the missing steps in the GitHub collaboration flow.", "hint": "After forking, you clone. After pushing, you open a PR.", "explanation": "Standard flow: Fork -> Clone -> Branch -> Commit -> Push -> Pull Request."},
                    {"language": LanguageEnum.fr, "prompt": "Remplissez les étapes manquantes du flux de collaboration GitHub.", "hint": "Après le fork, on clone. Après le push, on ouvre une PR.", "explanation": "Flux standard : Fork -> Clone -> Branche -> Commit -> Push -> Pull Request."},
                    {"language": LanguageEnum.ar, "prompt": "املأ الخطوات المفقودة في تدفق تعاون GitHub.", "hint": "بعد الـ fork، تقوم بـ clone. بعد الـ push، تفتح PR.", "explanation": "التدفق القياسي: Fork -> Clone -> Branch -> Commit -> Push -> Pull Request."},
                ]
            }
        ]
    )
    
    print("Git & GitHub seeded successfully!")