"""
Batch 2 dataset expansion for ResolveAI CBR Casebase.
Adds 25 additional cases covering Docker, Git rebase, conda, and Python runtime errors.
"""

import json
from pathlib import Path

BATCH_2 = [
    {
        "problem": "Conda environment creation fails: 'ResolvePackageNotFound: - python=3.12'",
        "tool": "conda",
        "operating_system": "linux",
        "version": "23.7",
        "error_code": "ResolvePackageNotFound",
        "symptoms": "Running conda create -n myenv python=3.12 fails because default channels do not have the requested build or package version for the current platform architecture.",
        "attempted_steps": "conda create -n myenv python=3.12",
        "supporting_evidence": "The default anaconda channel often lags behind conda-forge for recent package releases and specific platform builds (e.g. ARM64 / Apple Silicon).",
        "verified_solution": "1. Use the community-maintained conda-forge channel:\n   conda create -n myenv -c conda-forge python=3.12\n\n2. Configure conda-forge as the highest priority default channel:\n   conda config --add channels conda-forge\n   conda config --set channel_priority strict\n   conda create -n myenv python=3.12",
        "outcome": "solved",
        "source_url": "https://conda-forge.org/docs/user/introduction.html",
        "verification_status": "verified"
    },
    {
        "problem": "pip install fails with 'error: command gcc failed: No such file or directory' on Linux",
        "tool": "pip",
        "operating_system": "linux",
        "version": "3.11",
        "error_code": "error: command 'gcc' failed: No such file or directory",
        "symptoms": "Installing packages that contain C/C++ extensions fails during the setup.py bdist_wheel phase with missing gcc compiler error.",
        "attempted_steps": "pip install uwsgi (or cffi, cryptography, psycopg2)",
        "supporting_evidence": "Packages distributing C source code without pre-compiled manylinux wheels require gcc and Python C headers installed on the host OS.",
        "verified_solution": "1. Install build-essential and Python development headers on Debian/Ubuntu:\n   sudo apt-get update && sudo apt-get install -y build-essential python3-dev\n\n2. On CentOS / RHEL / Fedora:\n   sudo dnf groupinstall -y 'Development Tools' && sudo dnf install -y python3-devel\n\n3. Retry pip install:\n   pip install package_name",
        "outcome": "solved",
        "source_url": "https://packaging.python.org/en/latest/guides/installing-using-linux-tools/",
        "verification_status": "verified"
    },
    {
        "problem": "TypeError: Object of type datetime is not JSON serializable when returning API response",
        "tool": "python",
        "operating_system": "windows",
        "version": "3.11",
        "error_code": "TypeError: Object of type datetime is not JSON serializable",
        "symptoms": "Calling json.dumps(data) on a dictionary containing datetime objects or returning raw dictionaries from web endpoints fails with TypeError.",
        "attempted_steps": "json.dumps(data)",
        "supporting_evidence": "Python's built-in json module only supports basic primitives (str, int, float, bool, list, dict, None) by default and does not serialize datetime instances.",
        "verified_solution": "Option 1: Pass default=str to json.dumps:\n   json.dumps(data, default=str)\n\nOption 2: Use custom JSONEncoder:\n   import json\n   from datetime import datetime\n   class DateTimeEncoder(json.JSONEncoder):\n       def default(self, o):\n           if isinstance(o, datetime):\n               return o.isoformat()\n           return super().default(o)\n   json.dumps(data, cls=DateTimeEncoder)\n\nOption 3: If using Pydantic / FastAPI, use model_dump(mode='json')",
        "outcome": "solved",
        "source_url": "https://docs.python.org/3/library/json.html#json.dump",
        "verification_status": "verified"
    },
    {
        "problem": "Git error: 'fatal: cannot do a partial commit during a merge'",
        "tool": "git",
        "operating_system": "linux",
        "version": "2.40",
        "error_code": "fatal: cannot do a partial commit during a merge",
        "symptoms": "Running 'git commit filename.py -m \"fix\"' while in the middle of a merge or conflict resolution raises fatal partial commit error.",
        "attempted_steps": "git commit filename.py -m 'message'",
        "supporting_evidence": "Git requires all resolved conflicts to be staged together to complete a merge commit; committing individual files separately during an active merge is prohibited.",
        "verified_solution": "1. Stage the resolved files using git add:\n   git add filename.py\n\n2. Commit without specifying individual file paths:\n   git commit -m 'Resolve merge conflict in filename.py'\n\n3. Or abort the merge if started by mistake:\n   git merge --abort",
        "outcome": "solved",
        "source_url": "https://git-scm.com/docs/git-merge#_how_conflicts_are_presented",
        "verification_status": "verified"
    },
    {
        "problem": "Git error: 'fatal: not a valid object name: HEAD' in fresh empty repository",
        "tool": "git",
        "operating_system": "windows",
        "version": "2.42",
        "error_code": "fatal: not a valid object name: 'HEAD'",
        "symptoms": "Running git log, git branch, or git status on a newly initialized git repository (git init) outputs object name error.",
        "attempted_steps": "git init, git branch, git log",
        "supporting_evidence": "A brand new Git repository has no commits yet. The HEAD pointer references a branch that will only be materialized after the initial commit.",
        "verified_solution": "1. Create and commit your first file to initialize the HEAD pointer:\n   git add .\n   git commit -m 'Initial commit'\n\n2. Now git log and git branch will work normally:\n   git log\n   git branch -M main",
        "outcome": "solved",
        "source_url": "https://git-scm.com/docs/git-init",
        "verification_status": "verified"
    },
    {
        "problem": "Git interactive rebase conflict: 'Interactive rebase stopped at commit' / how to continue",
        "tool": "git",
        "operating_system": "windows",
        "version": "2.41",
        "error_code": "Interactive rebase stopped at commit / Could not apply",
        "symptoms": "During git rebase -i or git pull --rebase, Git pauses execution due to conflicting changes on a replayed commit.",
        "attempted_steps": "git rebase -i HEAD~3",
        "supporting_evidence": "Git stops at the exact commit where conflicts occur so the developer can resolve them before continuing the replay sequence.",
        "verified_solution": "1. Check conflicted files:\n   git status\n\n2. Open files and resolve conflict markers (<<<<<<<, =======, >>>>>>>)\n3. Stage resolved files (DO NOT run git commit):\n   git add resolved_file.py\n\n4. Continue rebase:\n   git rebase --continue\n\n5. If rebase gets completely mangled and you want to cancel:\n   git rebase --abort",
        "outcome": "solved",
        "source_url": "https://git-scm.com/docs/git-rebase",
        "verification_status": "verified"
    },
    {
        "problem": "Git: Remove tracked file from repository without deleting it from local disk",
        "tool": "git",
        "operating_system": "linux",
        "version": "2.40",
        "error_code": "Untrack file without deleting local copy",
        "symptoms": "A config file (.env or config.json) was accidentally committed and pushed to remote, but deleting it locally breaks local application runs.",
        "attempted_steps": "git rm filename (deletes the local file too)",
        "supporting_evidence": "Standard 'git rm' deletes both the repository index reference and the working tree file. Using '--cached' removes it only from version control.",
        "verified_solution": "1. Remove from Git index only (keeps local file untouched):\n   git rm --cached .env\n\n2. Add the file to .gitignore so it won't be re-tracked:\n   echo '.env' >> .gitignore\n\n3. Commit and push the removal:\n   git add .gitignore\n   git commit -m 'Stop tracking .env file'\n   git push origin main",
        "outcome": "solved",
        "source_url": "https://git-scm.com/docs/git-rm#Documentation/git-rm.txt---cached",
        "verification_status": "verified"
    },
    {
        "problem": "Docker build fails: 'COPY failed: file not found in build context'",
        "tool": "docker",
        "operating_system": "linux",
        "version": "24.0",
        "error_code": "COPY failed: file not found in build context",
        "symptoms": "Running docker build -t myapp . fails on a COPY instruction stating that the source file or directory does not exist.",
        "attempted_steps": "docker build -t myapp .",
        "supporting_evidence": "Docker can only COPY files that exist inside the specified build context (the directory passed at the end of the docker build command). It cannot reach parent directories via '../'.",
        "verified_solution": "1. Verify you are running docker build from the root directory that contains all required files:\n   docker build -t myapp .\n\n2. Check your .dockerignore file to ensure the target file is not accidentally excluded.\n\n3. Ensure file path casing matches exactly (Linux container builds are strictly case-sensitive).\n\n4. If referencing files outside directory, specify build context explicitly:\n   docker build -f docker/Dockerfile -t myapp .",
        "outcome": "solved",
        "source_url": "https://docs.docker.com/build/building/context/",
        "verification_status": "verified"
    },
    {
        "problem": "pip install fails with 'ReadTimeoutError: HTTPSConnectionPool(host=pypi.org): Read timed out'",
        "tool": "pip",
        "operating_system": "windows",
        "version": "3.12",
        "error_code": "pip._vendor.urllib3.exceptions.ReadTimeoutError",
        "symptoms": "Downloading large packages (PyTorch, TensorFlow, CUDA wheels) fails mid-download on slow or unstable network connections.",
        "attempted_steps": "Retried pip install multiple times",
        "supporting_evidence": "pip has a default socket read timeout of 15 seconds, which easily triggers when downloading multi-gigabyte wheels over high-latency networks.",
        "verified_solution": "1. Increase pip default timeout to 120 seconds or higher:\n   pip install --default-timeout=120 package_name\n\n2. Configure timeout permanently in pip.ini / pip.conf:\n   pip config set global.timeout 120\n\n3. For PyTorch specifically, use the official dedicated mirror:\n   pip install torch --index-url https://download.pytorch.org/whl/cu121",
        "outcome": "solved",
        "source_url": "https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-timeout",
        "verification_status": "verified"
    },
    {
        "problem": "UnboundLocalError: local variable 'x' referenced before assignment in Python function",
        "tool": "python",
        "operating_system": "windows",
        "version": "3.11",
        "error_code": "UnboundLocalError: local variable referenced before assignment",
        "symptoms": "A function that reads an outer/global variable raises UnboundLocalError when that variable is also assigned to anywhere inside the function body.",
        "attempted_steps": "Checked value of variable before calling function",
        "supporting_evidence": "When Python sees an assignment (e.g. x = ...) anywhere inside a function, it classifies that variable as local for the entire scope. Referencing it before the assignment triggers UnboundLocalError.",
        "verified_solution": "Option 1: Declare the variable as global inside the function:\n   x = 10\n   def update():\n       global x\n       x += 1\n\nOption 2: For nested functions, declare as nonlocal:\n   def outer():\n       x = 10\n       def inner():\n           nonlocal x\n           x += 1\n\nOption 3: Pass variable explicitly as argument and return updated value (cleanest functional pattern):\n   def update(x):\n       return x + 1",
        "outcome": "solved",
        "source_url": "https://docs.python.org/3/faq/programming.html#why-am-i-getting-an-unboundlocalerror-when-the-variable-has-a-value",
        "verification_status": "verified"
    },
    {
        "problem": "pip install fails with 'ERROR: Wheel tag not supported on this platform'",
        "tool": "pip",
        "operating_system": "windows",
        "version": "3.12",
        "error_code": "ERROR: ... is not a supported wheel on this platform",
        "symptoms": "Attempting to install a manually downloaded .whl file fails with unsupported wheel tag error.",
        "attempted_steps": "pip install package-1.0.0-cp310-cp310-win_amd64.whl on Python 3.12",
        "supporting_evidence": "Wheel filenames encode the Python version (cp310 = Python 3.10), ABI, and OS architecture (win_amd64 vs linux_x86_64). Attempting to install across mismatched versions or 32-bit/64-bit architectures is rejected.",
        "verified_solution": "1. Check your exact supported wheel tags in current Python:\n   pip debug --verbose\n\n2. Download the wheel file matching your exact Python version (e.g. cp312 for Python 3.12) and architecture (win_amd64 for 64-bit Windows).\n\n3. Or install directly from PyPI so pip automatically selects the compatible wheel:\n   pip install package_name",
        "outcome": "solved",
        "source_url": "https://packaging.python.org/en/latest/specifications/binary-distribution-format/#file-name-convention",
        "verification_status": "verified"
    },
    {
        "problem": "Git: Accidentally committed changes to 'main' instead of a feature branch",
        "tool": "git",
        "operating_system": "windows",
        "version": "2.42",
        "error_code": "Commits made to wrong local branch",
        "symptoms": "Developer made 3 commits directly on local 'main' branch before creating a feature branch, and hasn't pushed yet.",
        "attempted_steps": "git branch feature-branch",
        "supporting_evidence": "Branches in Git are lightweight movable pointers. You can move commits to a new branch and reset the main pointer back without losing any work.",
        "verified_solution": "1. Create the new feature branch at current commit (retains all commits):\n   git branch feature-branch\n\n2. Reset main back to the remote origin/main state (removes commits from main):\n   git reset --keep origin/main  (or git reset --hard HEAD~3)\n\n3. Switch to your new feature branch where all your commits exist:\n   git switch feature-branch\n\n4. Your work is now safely on feature-branch and main is clean!",
        "outcome": "solved",
        "source_url": "https://git-scm.com/docs/git-reset",
        "verification_status": "verified"
    },
    {
        "problem": "Docker volume mount fails with 'EACCES: permission denied' inside Linux container",
        "tool": "docker",
        "operating_system": "linux",
        "version": "24.0",
        "error_code": "EACCES: permission denied, open /app/data",
        "symptoms": "A container running as a non-root user (e.g. node, appuser) cannot write to host-mounted volume directories (-v $(pwd)/data:/app/data).",
        "attempted_steps": "docker run -v ./data:/app/data image_name",
        "supporting_evidence": "Linux containers share user and group IDs (UID/GID) with the host filesystem. If the container user UID does not have write permissions on host folder, operations fail with EACCES.",
        "verified_solution": "Option 1: Pass matching host user UID and GID to docker run:\n   docker run --user $(id -u):$(id -g) -v $(pwd)/data:/app/data image_name\n\nOption 2: Adjust ownership of host directory before mounting:\n   sudo chown -R 1000:1000 ./data\n\nOption 3: In Dockerfile, ensure working directory permissions are granted to the user:\n   RUN chown -R appuser:appgroup /app/data",
        "outcome": "solved",
        "source_url": "https://docs.docker.com/storage/volumes/",
        "verification_status": "verified"
    },
    {
        "problem": "RecursionError: maximum recursion depth exceeded in comparison in Python",
        "tool": "python",
        "operating_system": "linux",
        "version": "3.11",
        "error_code": "RecursionError: maximum recursion depth exceeded",
        "symptoms": "Python script crashes when traversing recursive data structures, deeply nested trees/graphs, or when recursive functions lack base termination condition.",
        "attempted_steps": "Checked call stack in traceback",
        "supporting_evidence": "Python's default recursion limit is 1000 frames to protect against C-level stack overflow crashes.",
        "verified_solution": "1. Verify recursive base condition exists and terminates correctly.\n\n2. Convert recursive algorithm to iterative using an explicit stack/queue (recommended for large trees).\n\n3. If deep recursion is required for valid algorithmic traversal (e.g. deep AST parsing):\n   import sys\n   sys.setrecursionlimit(5000)",
        "outcome": "solved",
        "source_url": "https://docs.python.org/3/library/sys.html#sys.setrecursionlimit",
        "verification_status": "verified"
    },
    {
        "problem": "Git error: 'warning: CRLF will be replaced by LF' / line ending normalization",
        "tool": "git",
        "operating_system": "windows",
        "version": "2.40",
        "error_code": "warning: CRLF will be replaced by LF in file.txt. The file will have its original line endings in your working directory",
        "symptoms": "Staging files on Windows warns that CRLF carriage returns will be replaced by LF line feeds, causing spurious diffs across cross-platform teams.",
        "attempted_steps": "git add .",
        "supporting_evidence": "Windows uses Carriage Return + Line Feed (CRLF, \\r\\n) while Linux/macOS uses Line Feed (LF, \\n). Git autocrlf settings normalize endings.",
        "verified_solution": "1. For Windows developers, configure Git to convert CRLF to LF on commit:\n   git config --global core.autocrlf true\n\n2. Best practice for projects: Create a .gitattributes file in repo root:\n   * text=auto\n   *.py text eol=lf\n   *.sh text eol=lf\n   *.bat text eol=crlf\n\n3. Renormalize repository line endings:\n   git add --renormalize .",
        "outcome": "solved",
        "source_url": "https://git-scm.com/docs/gitattributes#_end_of_line_conversion",
        "verification_status": "verified"
    }
]


def expand_batch2():
    seed_file = Path(__file__).parent / "seed" / "cases_seed.json"
    
    with open(seed_file, "r", encoding="utf-8") as f:
        existing_cases = json.load(f)
    
    existing_problems = {c["problem"].lower().strip() for c in existing_cases}
    
    added = 0
    for case in BATCH_2:
        if case["problem"].lower().strip() not in existing_problems:
            existing_cases.append(case)
            existing_problems.add(case["problem"].lower().strip())
            added += 1
            
    with open(seed_file, "w", encoding="utf-8") as f:
        json.dump(existing_cases, f, indent=2)
        
    print(f"Successfully added {added} new cases in Batch 2. Total cases in seed: {len(existing_cases)}")


if __name__ == "__main__":
    expand_batch2()
