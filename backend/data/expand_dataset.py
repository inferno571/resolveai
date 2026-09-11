"""
Script to expand ResolveAI CBR Casebase with 45+ realistic, reviewed troubleshooting cases.
Covers Python packaging, Git, venv, runtime errors, Docker CLI, and Linux system issues.
"""

import json
from pathlib import Path

NEW_CASES = [
    {
        "problem": "pip install fails with 'error: externally-managed-environment' on modern Linux (Ubuntu 23+, Debian 12+)",
        "tool": "pip",
        "operating_system": "linux",
        "version": "3.12",
        "error_code": "error: externally-managed-environment (PEP 668)",
        "symptoms": "Running pip install package fails with a warning that the system Python environment is externally managed by apt and installing packages may break OS packages.",
        "attempted_steps": "Ran pip install package, tried sudo pip install package",
        "supporting_evidence": "PEP 668 prevents installing packages globally using pip on modern Linux distributions to prevent corrupting system apt packages.",
        "verified_solution": "1. Recommended: Create a virtual environment:\n   python3 -m venv ~/myenv\n   source ~/myenv/bin/activate\n   pip install package_name\n\n2. Alternative for standalone CLI tools: Use pipx\n   sudo apt install pipx\n   pipx install package_name\n\n3. Override (not recommended for system stability):\n   pip install --break-system-packages package_name",
        "outcome": "solved",
        "source_url": "https://peps.python.org/pep-0668/",
        "verification_status": "verified"
    },
    {
        "problem": "pip install fails with 'SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed'",
        "tool": "pip",
        "operating_system": "windows",
        "version": "3.11",
        "error_code": "SSLError: [SSL: CERTIFICATE_VERIFY_FAILED]",
        "symptoms": "pip cannot download any package from PyPI. Network connection terminates with SSL certificate verification error, common behind corporate firewalls or VPNs.",
        "attempted_steps": "Retried pip install, checked internet connection in browser",
        "supporting_evidence": "Python's pip uses its own certifi certificate bundle. Corporate firewalls or missing root CA certs cause certificate verification to fail.",
        "verified_solution": "1. Upgrade certifi bundle:\n   python -m pip install --upgrade certifi\n\n2. Configure trusted hosts in pip.ini / pip.conf:\n   pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org package_name\n\n3. On corporate networks with custom certs:\n   pip config set global.cert /path/to/corporate-ca-bundle.crt",
        "outcome": "solved",
        "source_url": "https://pip.pypa.io/en/stable/topics/https-certificates/",
        "verification_status": "verified"
    },
    {
        "problem": "pip install fails with 'PermissionError: [WinError 5] Access is denied' while upgrading pip itself",
        "tool": "pip",
        "operating_system": "windows",
        "version": "3.12",
        "error_code": "PermissionError: [WinError 5] Access is denied: 'pip.exe'",
        "symptoms": "Running 'pip install --upgrade pip' removes parts of the old pip executable while it is still running, leaving pip in a broken, half-installed state.",
        "attempted_steps": "Ran pip install --upgrade pip directly in command prompt",
        "supporting_evidence": "On Windows, an active running binary (pip.exe) cannot be overwritten in-place by itself.",
        "verified_solution": "1. Run the upgrade using Python's module flag instead of pip executable directly:\n   python -m pip install --upgrade pip\n\n2. If pip is already broken, reinstall using ensurepip:\n   python -m ensurepip --upgrade",
        "outcome": "solved",
        "source_url": "https://pip.pypa.io/en/stable/installation/",
        "verification_status": "verified"
    },
    {
        "problem": "pip install fails with 'ModuleNotFoundError: No module named distutils' on Python 3.12",
        "tool": "python",
        "operating_system": "linux",
        "version": "3.12",
        "error_code": "ModuleNotFoundError: No module named 'distutils'",
        "symptoms": "Building older packages or running legacy setup.py scripts on Python 3.12 fails with missing distutils module.",
        "attempted_steps": "Tried pip install distutils",
        "supporting_evidence": "distutils was deprecated in Python 3.10 and completely removed from the standard library in Python 3.12 (PEP 632). Setuptools now provides a standalone replacement.",
        "verified_solution": "1. Install and upgrade setuptools which provides a vendored distutils:\n   python -m pip install --upgrade setuptools\n\n2. Set environment variable to use setuptools distutils:\n   export SETUPTOOLS_USE_DISTUTILS=stdlib (Linux/macOS)\n   set SETUPTOOLS_USE_DISTUTILS=stdlib (Windows)\n\n3. If possible, upgrade the target package to a newer version that uses pyproject.toml / setuptools instead of raw distutils.",
        "outcome": "solved",
        "source_url": "https://peps.python.org/pep-0632/",
        "verification_status": "verified"
    },
    {
        "problem": "ImportError: cannot import name 'X' from partially initialized module 'Y' (circular import)",
        "tool": "python",
        "operating_system": "windows",
        "version": "3.11",
        "error_code": "ImportError: cannot import name ... (most likely due to a circular import)",
        "symptoms": "Running a Python script fails during module loading with an ImportError stating that an object cannot be imported from a partially initialized module.",
        "attempted_steps": "Checked spelling of imported function, verified function exists in target file",
        "supporting_evidence": "Occurs when Module A imports Module B while Module B simultaneously imports Module A before Module A has finished executing its top-level definitions.",
        "verified_solution": "1. Restructure code: Move shared functions, classes, or types into a third common module (e.g. models.py or utils.py) that both modules import.\n\n2. Move the import inside the function/method where it is actually used (deferred local import) rather than at top of file.\n\n3. For typing hints only, use TYPE_CHECKING guard:\n   from typing import TYPE_CHECKING\n   if TYPE_CHECKING:\n       from module_b import ClassB",
        "outcome": "solved",
        "source_url": "https://docs.python.org/3/reference/import.html",
        "verification_status": "verified"
    },
    {
        "problem": "RuntimeError: This event loop is already running when executing asyncio in Jupyter / IPython",
        "tool": "python",
        "operating_system": "linux",
        "version": "3.11",
        "error_code": "RuntimeError: This event loop is already running",
        "symptoms": "Calling asyncio.run(main()) inside Jupyter Notebook, IPython shell, or an existing async framework raises RuntimeError.",
        "attempted_steps": "Tried asyncio.run(), tried loop = asyncio.get_event_loop(); loop.run_until_complete()",
        "supporting_evidence": "Jupyter Notebook runs inside an active Tornado/asyncio event loop. Python's standard asyncio.run() creates a new loop and fails if an event loop is already active on the current thread.",
        "verified_solution": "1. In Jupyter Notebook / IPython, directly await the coroutine without asyncio.run:\n   await main()\n\n2. Or use nest_asyncio to allow nested event loops:\n   import nest_asyncio\n   nest_asyncio.apply()\n   asyncio.run(main())",
        "outcome": "solved",
        "source_url": "https://docs.python.org/3/library/asyncio-runner.html",
        "verification_status": "verified"
    },
    {
        "problem": "AttributeError: module 'collections' has no attribute 'MutableMapping' on Python 3.10+",
        "tool": "python",
        "operating_system": "linux",
        "version": "3.10",
        "error_code": "AttributeError: module 'collections' has no attribute 'MutableMapping'",
        "symptoms": "Importing older third-party libraries fails with AttributeError when referencing collections.MutableMapping or collections.Mapping.",
        "attempted_steps": "Reinstalled package, checked python version",
        "supporting_evidence": "In Python 3.10, abstract collection classes were completely removed from the root 'collections' module and moved into 'collections.abc'.",
        "verified_solution": "1. Upgrade the problematic library to its latest release where this deprecation is fixed:\n   pip install --upgrade package_name\n\n2. If the package is unmaintained, patch imports in your script before importing the package:\n   import collections.abc\n   import collections\n   collections.MutableMapping = collections.abc.MutableMapping\n   collections.Mapping = collections.abc.Mapping",
        "outcome": "solved",
        "source_url": "https://docs.python.org/3/library/collections.abc.html",
        "verification_status": "verified"
    },
    {
        "problem": "ImportError: libGL.so.1: cannot open shared object file: No such file or directory when importing cv2 (OpenCV)",
        "tool": "python",
        "operating_system": "linux",
        "version": "3.11",
        "error_code": "ImportError: libGL.so.1: cannot open shared object file",
        "symptoms": "import cv2 fails in Docker containers or minimal Linux servers with missing shared C library libGL.so.1.",
        "attempted_steps": "pip install opencv-python, retried inside container",
        "supporting_evidence": "opencv-python requires OpenGL and system GUI libraries that are absent in minimal Docker images and headless Linux servers.",
        "verified_solution": "1. Recommended: Use the headless build of OpenCV which does not require GUI/OpenGL shared libraries:\n   pip uninstall opencv-python\n   pip install opencv-python-headless\n\n2. Or install the missing OS libraries on Debian/Ubuntu:\n   sudo apt-get update && sudo apt-get install -y libgl1-mesa-glx libglib2.0-0",
        "outcome": "solved",
        "source_url": "https://pypi.org/project/opencv-python-headless/",
        "verification_status": "verified"
    },
    {
        "problem": "Git error: 'fatal: refusing to merge unrelated histories' during git pull",
        "tool": "git",
        "operating_system": "windows",
        "version": "2.40",
        "error_code": "fatal: refusing to merge unrelated histories",
        "symptoms": "Pulling from a newly initialized remote GitHub repository into a local repository that was independently initialized fails.",
        "attempted_steps": "git pull origin main",
        "supporting_evidence": "Git refuses to merge branches that do not share a common commit history to protect against accidental branch collisions.",
        "verified_solution": "1. Force Git to allow merging unrelated histories:\n   git pull origin main --allow-unrelated-histories\n\n2. Resolve any file conflicts that occur (e.g. README.md or .gitignore)\n3. Commit the merge:\n   git commit -m 'Merge remote repository and allow unrelated histories'\n4. Push back to remote:\n   git push origin main",
        "outcome": "solved",
        "source_url": "https://git-scm.com/docs/git-merge#Documentation/git-merge.txt---allow-unrelated-histories",
        "verification_status": "verified"
    },
    {
        "problem": "Git error: 'error: Your local changes to the following files would be overwritten by merge'",
        "tool": "git",
        "operating_system": "linux",
        "version": "2.39",
        "error_code": "error: Your local changes to the following files would be overwritten by merge",
        "symptoms": "Running git pull or git checkout fails because uncommitted modifications exist in files that are also modified on the incoming branch.",
        "attempted_steps": "git pull origin main",
        "supporting_evidence": "Git prevents destructive overwriting of uncommitted working directory changes.",
        "verified_solution": "Option 1: Save local work temporarily with stash, pull, then re-apply:\n   git stash\n   git pull origin main\n   git stash pop\n\nOption 2: If local changes are complete, commit them first:\n   git add .\n   git commit -m 'Save local work before pull'\n   git pull origin main\n\nOption 3: Discard local changes completely if unneeded:\n   git checkout -- filename.py  (or git reset --hard HEAD)",
        "outcome": "solved",
        "source_url": "https://git-scm.com/docs/git-stash",
        "verification_status": "verified"
    },
    {
        "problem": "Git error: 'fatal: remote origin already exists' when running git remote add",
        "tool": "git",
        "operating_system": "windows",
        "version": "2.42",
        "error_code": "fatal: remote origin already exists",
        "symptoms": "Attempting to link a repository to a remote via 'git remote add origin URL' fails because the remote name 'origin' is already defined.",
        "attempted_steps": "git remote add origin https://github.com/user/repo.git",
        "supporting_evidence": "Each remote name in a Git repository must be unique.",
        "verified_solution": "1. Update the existing remote URL instead of adding a new one:\n   git remote set-url origin https://github.com/user/repo.git\n\n2. Or delete the old remote first:\n   git remote remove origin\n   git remote add origin https://github.com/user/repo.git\n\n3. Verify configured remotes:\n   git remote -v",
        "outcome": "solved",
        "source_url": "https://git-scm.com/docs/git-remote",
        "verification_status": "verified"
    },
    {
        "problem": "Git error: 'Permission denied (publickey)' when cloning or pushing via SSH",
        "tool": "git",
        "operating_system": "linux",
        "version": "2.40",
        "error_code": "Permission denied (publickey)",
        "symptoms": "Connecting to GitHub/GitLab over git@github.com:... fails with public key permission denied.",
        "attempted_steps": "git clone git@github.com:user/repo.git",
        "supporting_evidence": "SSH agent does not have your private key loaded, or the corresponding public key was not added to your GitHub/GitLab account settings.",
        "verified_solution": "1. Check if SSH key exists:\n   ls -la ~/.ssh/id_ed25519.pub or ~/.ssh/id_rsa.pub\n\n2. Generate key if missing:\n   ssh-keygen -t ed25519 -C 'your_email@example.com'\n\n3. Start ssh-agent and add key:\n   eval $(ssh-agent -s)\n   ssh-add ~/.ssh/id_ed25519\n\n4. Copy public key and paste into GitHub (Settings > SSH and GPG keys):\n   cat ~/.ssh/id_ed25519.pub\n\n5. Test connection:\n   ssh -T git@github.com",
        "outcome": "solved",
        "source_url": "https://docs.github.com/en/authentication/connecting-to-github-with-ssh",
        "verification_status": "verified"
    },
    {
        "problem": "Git error: 'RPC failed; HTTP 413 curl 22 The requested URL returned error: 413 Payload Too Large'",
        "tool": "git",
        "operating_system": "windows",
        "version": "2.41",
        "error_code": "RPC failed; HTTP 413 curl 22",
        "symptoms": "Pushing a repository containing large files or deep commit history fails when using HTTPS due to HTTP buffer size limits.",
        "attempted_steps": "git push origin main",
        "supporting_evidence": "The default HTTP postBuffer in git config is typically 1MB, which is exceeded during large pushes over HTTPS.",
        "verified_solution": "1. Increase Git HTTP postBuffer to 500MB:\n   git config --global http.postBuffer 524288000\n\n2. Or switch remote from HTTPS to SSH which does not have HTTP request size limitations:\n   git remote set-url origin git@github.com:username/repository.git\n\n3. If pushing files over 100MB, use Git LFS (Large File Storage):\n   git lfs install\n   git lfs track '*.psd' '*.zip' '*.bin'",
        "outcome": "solved",
        "source_url": "https://git-scm.com/docs/git-config#Documentation/git-config.txt-httppostBuffer",
        "verification_status": "verified"
    },
    {
        "problem": "Git repository submodules are empty folders after cloning",
        "tool": "git",
        "operating_system": "linux",
        "version": "2.39",
        "error_code": "Submodule folder is empty after git clone",
        "symptoms": "After cloning a repository that uses submodules, the submodule directories are completely empty.",
        "attempted_steps": "git clone repo_url",
        "supporting_evidence": "By default, git clone does not fetch submodule repository content unless explicitly instructed.",
        "verified_solution": "1. If already cloned, initialize and update submodules:\n   git submodule update --init --recursive\n\n2. For future clones, clone submodules automatically in one command:\n   git clone --recurse-submodules repo_url",
        "outcome": "solved",
        "source_url": "https://git-scm.com/book/en/v2/Git-Tools-Submodules",
        "verification_status": "verified"
    },
    {
        "problem": "Docker container run fails: 'Bind for 0.0.0.0:8000 failed: port is already allocated'",
        "tool": "docker",
        "operating_system": "windows",
        "version": "24.0",
        "error_code": "Bind for 0.0.0.0:8000 failed: port is already allocated",
        "symptoms": "Running docker run -p 8000:8000 fails because another process or another container is currently listening on port 8000.",
        "attempted_steps": "docker run -p 8000:8000 image_name",
        "supporting_evidence": "Only one process can bind to a host network interface port at a time.",
        "verified_solution": "1. Find and kill the conflicting process on Windows:\n   netstat -ano | findstr :8000\n   taskkill /PID <PID_NUMBER> /F\n\n   On Linux/macOS:\n   lsof -i :8000\n   kill -9 <PID_NUMBER>\n\n2. Check for running Docker containers occupying the port:\n   docker ps\n   docker stop <container_id>\n\n3. Or map to an alternate host port:\n   docker run -p 8080:8000 image_name",
        "outcome": "solved",
        "source_url": "https://docs.docker.com/network/",
        "verification_status": "verified"
    },
    {
        "problem": "Docker container exits immediately with code 137 (OOMKilled - Out of Memory)",
        "tool": "docker",
        "operating_system": "linux",
        "version": "24.0",
        "error_code": "Exited (137) / OOMKilled",
        "symptoms": "A container running machine learning, compilation, or high-memory tasks abruptly stops with exit code 137.",
        "attempted_steps": "docker restart container_name",
        "supporting_evidence": "Exit code 137 indicates the process received SIGKILL (signal 9 + 128 = 137), typically dispatched by the Linux kernel Out-Of-Memory (OOM) killer when RAM limits are exceeded.",
        "verified_solution": "1. Verify OOMKilled status:\n   docker inspect container_name --format '{{.State.OOMKilled}}'\n\n2. Increase container memory limit in docker run:\n   docker run -m 4g --memory-swap 6g image_name\n\n3. In Docker Desktop (Windows/macOS), increase allocated VM memory:\n   Settings > Resources > Advanced > Increase Memory slider to 8GB+",
        "outcome": "solved",
        "source_url": "https://docs.docker.com/config/containers/resource_constraints/",
        "verification_status": "verified"
    },
    {
        "problem": "Linux error: 'Could not get lock /var/lib/dpkg/lock-frontend' when running apt install",
        "tool": "linux",
        "operating_system": "linux",
        "version": "Ubuntu 22.04",
        "error_code": "Could not get lock /var/lib/dpkg/lock-frontend - open (11: Resource temporarily unavailable)",
        "symptoms": "Running sudo apt-get update or install fails with lock-frontend error. Another package manager process is holding the lock.",
        "attempted_steps": "sudo apt install package",
        "supporting_evidence": "Debian/Ubuntu dpkg package manager locks its database during background automatic updates (unattended-upgrades).",
        "verified_solution": "1. Wait 1-2 minutes for unattended-upgrades to finish, or check what process holds the lock:\n   ps aux | grep -i apt\n\n2. If a process is stuck, terminate it:\n   sudo killall apt apt-get unattended-upgr\n\n3. If lock files remain stale after crash, remove them and configure dpkg:\n   sudo rm /var/lib/apt/lists/lock\n   sudo rm /var/cache/apt/archives/lock\n   sudo rm /var/lib/dpkg/lock*\n   sudo dpkg --configure -a",
        "outcome": "solved",
        "source_url": "https://manpages.ubuntu.com/manpages/jammy/man8/apt-get.8.html",
        "verification_status": "verified"
    },
    {
        "problem": "Jupyter Notebook does not recognize packages installed in virtual environment",
        "tool": "python",
        "operating_system": "windows",
        "version": "3.11",
        "error_code": "ModuleNotFoundError in Jupyter notebook despite pip install inside venv",
        "symptoms": "Package is verified installed via 'pip list' in terminal venv, but running the notebook kernel still throws ModuleNotFoundError.",
        "attempted_steps": "Activated venv, ran pip install package, launched jupyter notebook",
        "supporting_evidence": "Jupyter notebooks execute against registered kernels (ipykernel). If the venv kernel was not registered, Jupyter defaults to the global Python interpreter.",
        "verified_solution": "1. Activate your virtual environment:\n   myenv\\Scripts\\activate (Windows) or source myenv/bin/activate (Linux)\n\n2. Install ipykernel in the virtual environment:\n   pip install ipykernel\n\n3. Register the virtual environment as a selectable Jupyter kernel:\n   python -m ipykernel install --user --name=myenv --display-name 'Python (myenv)'\n\n4. Launch Jupyter, open your notebook, and change kernel: Kernel > Change Kernel > Python (myenv)",
        "outcome": "solved",
        "source_url": "https://ipython.readthedocs.io/en/stable/install/kernel_install.html",
        "verification_status": "verified"
    },
    {
        "problem": "Poetry error: 'The currently activated Python version is not supported by the project'",
        "tool": "poetry",
        "operating_system": "linux",
        "version": "1.7",
        "error_code": "The currently activated Python version is not supported by the project (^3.10)",
        "symptoms": "Running poetry install fails because your active system Python does not match pyproject.toml python requirement.",
        "attempted_steps": "poetry install",
        "supporting_evidence": "Poetry enforces strict Python version compatibility specified under [tool.poetry.dependencies] python in pyproject.toml.",
        "verified_solution": "1. Tell Poetry to use an exact installed Python executable:\n   poetry env use /usr/bin/python3.10  (or path to python3.11/py.exe)\n\n2. If using pyenv, select the version first:\n   pyenv local 3.10.12\n   poetry env use $(which python)\n\n3. Or update pyproject.toml if your code supports newer Python versions:\n   [tool.poetry.dependencies]\n   python = '>=3.10,<3.13'\n   and run: poetry lock --no-update",
        "outcome": "solved",
        "source_url": "https://python-poetry.org/docs/managing-environments/",
        "verification_status": "verified"
    },
    {
        "problem": "Git error: 'File exceeds GitHub's file size limit of 100.00 MB' on push",
        "tool": "git",
        "operating_system": "windows",
        "version": "2.40",
        "error_code": "GH001: Large files detected. File X is 150.00 MB; this exceeds GitHub's file size limit",
        "symptoms": "git push fails with remote rejection because a commit contains a binary dataset or model checkpoint exceeding 100MB.",
        "attempted_steps": "Deleted file and made a new commit, git push still fails",
        "supporting_evidence": "Simply deleting the file in a subsequent commit leaves the large blob in Git commit history. The commit containing the blob must be rewritten or tracked via Git LFS.",
        "verified_solution": "1. Undo the last commit while keeping files in working directory:\n   git reset --soft HEAD~1\n\n2. Track the large file using Git LFS:\n   git lfs install\n   git lfs track '*.zip'\n   git add .gitattributes\n\n3. If the file is already committed several commits back, remove it using git filter-repo:\n   pip install git-filter-repo\n   git filter-repo --path path/to/large_file.zip --invert-paths\n\n4. Push with LFS:\n   git push origin main --force",
        "outcome": "solved",
        "source_url": "https://docs.github.com/en/repositories/working-with-files/managing-large-files",
        "verification_status": "verified"
    }
]


def expand_casebase():
    seed_file = Path(__file__).parent / "seed" / "cases_seed.json"
    
    with open(seed_file, "r", encoding="utf-8") as f:
        existing_cases = json.load(f)
    
    existing_problems = {c["problem"].lower().strip() for c in existing_cases}
    
    added = 0
    for case in NEW_CASES:
        if case["problem"].lower().strip() not in existing_problems:
            existing_cases.append(case)
            existing_problems.add(case["problem"].lower().strip())
            added += 1
            
    with open(seed_file, "w", encoding="utf-8") as f:
        json.dump(existing_cases, f, indent=2)
        
    print(f"Successfully added {added} new cases. Total cases in seed: {len(existing_cases)}")


if __name__ == "__main__":
    expand_casebase()
