# Git Common Operations and Troubleshooting

## Git Basics

### Configuration
```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
git config --global init.defaultBranch main
git config --list  # View all settings
```

### Repository Setup
```bash
# Initialize new repository
git init

# Clone existing repository
git clone https://github.com/user/repo.git
git clone git@github.com:user/repo.git  # SSH

# Add remote
git remote add origin https://github.com/user/repo.git
git remote -v  # View remotes
git remote set-url origin NEW_URL  # Change remote URL
```

## Common Git Errors and Solutions

### Push Rejected: Remote Contains Work You Don't Have
```
error: failed to push some refs to 'origin'
hint: Updates were rejected because the remote contains work that you do not have locally.
```

**Solution:**
```bash
# Pull and rebase
git pull origin main --rebase

# Resolve any conflicts if they appear
# Then push
git push origin main
```

**WARNING**: Avoid `--force` unless you understand the consequences. Use `--force-with-lease` if you must:
```bash
git push --force-with-lease origin main
```

### Merge Conflicts
```
CONFLICT (content): Merge conflict in file.py
Automatic merge failed; fix conflicts and then commit the result.
```

**How to resolve:**
1. Open conflicted files — look for markers:
```
<<<<<<< HEAD
Your changes
=======
Their changes
>>>>>>> branch-name
```
2. Edit to keep the desired code, remove markers
3. Stage and commit:
```bash
git add resolved_file.py
git commit -m "Resolve merge conflict"
```

**Using a merge tool:**
```bash
git mergetool  # Opens configured visual tool
```

### Detached HEAD State
```
You are in 'detached HEAD' state.
```

**What it means**: You've checked out a specific commit, not a branch.

**Solutions:**
```bash
# Go back to a branch
git checkout main

# Keep commits made in detached state
git branch save-my-work  # Create branch at current point
git checkout main
git merge save-my-work

# Prevent: Use switch instead of checkout
git switch main
git switch -c new-branch  # Create and switch
```

### Refusing to Merge Unrelated Histories
```
fatal: refusing to merge unrelated histories
```

**Common cause**: GitHub repo initialized with README, then local repo pushed to it.

**Solution:**
```bash
git pull origin main --allow-unrelated-histories
# Resolve any conflicts, then commit

# Prevention: Don't initialize GitHub repo with README when pushing existing code
```

### Repository Not Found (Private Repos)
```
fatal: repository 'https://github.com/user/repo.git/' not found
```

**Cause**: GitHub returns "not found" for private repos you can't access.

**Solutions:**
```bash
# HTTPS with Personal Access Token
git clone https://TOKEN@github.com/user/private-repo.git

# SSH (preferred)
git clone git@github.com:user/private-repo.git

# GitHub CLI
gh auth login
gh repo clone user/repo
```

### Authentication Keeps Being Asked
**Cause**: Remote URL uses HTTPS but you want SSH key auth.

```bash
# Check current remote
git remote -v

# Switch from HTTPS to SSH
git remote set-url origin git@github.com:user/repo.git

# Or cache HTTPS credentials
git config --global credential.helper cache
git config --global credential.helper 'cache --timeout=3600'

# Windows: Use credential manager
git config --global credential.helper manager
```

## Stashing Changes

```bash
# Stash uncommitted changes
git stash
git stash push -m "description of changes"

# List stashes
git stash list

# Apply most recent stash (keeps in list)
git stash apply

# Apply and remove from list
git stash pop

# Apply specific stash
git stash apply stash@{2}

# Create branch from stash (avoids conflicts)
git stash branch new-branch stash@{0}

# Drop a stash
git stash drop stash@{0}

# Clear all stashes
git stash clear
```

### Stash Pop Conflict Resolution
If `git stash pop` causes conflicts:
1. Resolve conflicts in files
2. Stage resolved files: `git add file.py`
3. Stash is NOT auto-dropped on conflict — drop manually: `git stash drop`

## Undoing Changes

```bash
# Discard changes in working directory
git checkout -- file.py    # Old way
git restore file.py        # New way (Git 2.23+)

# Unstage a file
git reset HEAD file.py     # Old way
git restore --staged file.py  # New way

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes) — DANGEROUS
git reset --hard HEAD~1

# Create a new commit that undoes a previous one (safe)
git revert COMMIT_HASH

# Amend last commit message
git commit --amend -m "New message"
```

## Branching

```bash
# Create and switch to new branch
git checkout -b feature-branch
git switch -c feature-branch    # New way

# List branches
git branch          # Local
git branch -r       # Remote
git branch -a       # All

# Delete branch
git branch -d branch-name       # Safe (only if merged)
git branch -D branch-name       # Force delete

# Rename branch
git branch -m old-name new-name

# Track remote branch
git checkout --track origin/branch-name
```

## .gitignore

### Common Python .gitignore entries
```
# Virtual environments
venv/
env/
.env

# Python cache
__pycache__/
*.py[cod]
*.pyo
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment variables
.env
.env.local
```

### .gitignore not working?
If files are already tracked, .gitignore won't affect them:
```bash
# Remove from tracking (keep file locally)
git rm --cached file_to_ignore
git commit -m "Remove tracked file"

# Remove directory from tracking
git rm -r --cached directory_to_ignore/
```
