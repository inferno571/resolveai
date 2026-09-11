# pip — Python Package Installer Reference

## Installation Basics

### Installing packages
```bash
pip install package_name
pip install package_name==1.2.3    # Specific version
pip install package_name>=1.0      # Minimum version
pip install package_name~=1.4.0    # Compatible release (~=1.4.0 means >=1.4.0, <1.5.0)
```

### Installing from requirements file
```bash
pip install -r requirements.txt
pip install -r requirements.txt --no-cache-dir  # Skip cache
```

### Installing in editable/development mode
```bash
pip install -e .                  # From current directory
pip install -e ./path/to/project  # From path
```

### User-level installation (no admin/root needed)
```bash
pip install --user package_name
```

## Virtual Environments

### Why use virtual environments?
- Isolate project dependencies from system Python
- Avoid version conflicts between projects
- Reproducible environments across machines
- No need for admin/root privileges

### Creating and using venv (built-in)
```bash
# Create
python -m venv myenv

# Activate
# Windows CMD:
myenv\Scripts\activate.bat
# Windows PowerShell:
myenv\Scripts\Activate.ps1
# Linux/macOS:
source myenv/bin/activate

# Deactivate
deactivate

# Verify you're in the venv
which python  # Linux/macOS
where python  # Windows
```

### PowerShell execution policy (Windows)
If activation fails with "running scripts is disabled":
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Common pip Errors and Solutions

### ERROR: Could not build wheels
**Cause**: Package has C extensions requiring compilation
```bash
# Option 1: Install pre-built binary
pip install --only-binary :all: package_name

# Option 2: Install build tools
# Windows: Install Visual Studio Build Tools with C++ workload
# Linux: sudo apt install build-essential python3-dev
# macOS: xcode-select --install

# Option 3: Use conda
conda install package_name
```

### PermissionError during install
**Cause**: Trying to install globally without admin rights
```bash
# BEST: Use a virtual environment
python -m venv myenv
myenv\Scripts\activate
pip install package_name

# Alternative: User install
pip install --user package_name

# BAD: Don't use sudo pip install on Linux
```

### pip's dependency resolver conflicts
**Cause**: Two packages need different versions of same dependency
```bash
# See what conflicts exist
pip check

# Visualize dependency tree
pip install pipdeptree
pipdeptree --warn

# Start fresh
python -m venv fresh_env
fresh_env\Scripts\activate
pip install package_a package_b  # Let pip resolve together
```

### No matching distribution found
**Cause**: Package version not available for your Python version or OS
```bash
# See available versions
pip install package_name==

# Check your Python version
python --version

# Check your platform
python -c "import platform; print(platform.platform())"

# Try without version pin
pip install package_name
```

### SSL/TLS errors
**Cause**: SSL certificates issue or corporate proxy
```bash
# Temporary fix (not recommended for production)
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org package_name

# Better: Update certificates
pip install --upgrade certifi

# Corporate proxy
pip install --proxy http://proxy:port package_name
```

### pip install hangs or is very slow
```bash
# Increase timeout
pip install --timeout 120 package_name

# Use a mirror
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple package_name

# Clear cache
pip cache purge
pip install --no-cache-dir package_name

# Verbose mode to see where it stalls
pip install -v package_name
```

## Useful pip Commands

```bash
# List installed packages
pip list

# Show package info
pip show package_name

# Check for outdated packages
pip list --outdated

# Freeze requirements
pip freeze > requirements.txt

# Uninstall
pip uninstall package_name

# Clear download cache
pip cache purge

# Upgrade pip itself
python -m pip install --upgrade pip

# Check for dependency issues
pip check
```

## requirements.txt Format

```txt
# Exact version
numpy==1.24.0

# Minimum version
pandas>=2.0.0

# Version range
scipy>=1.10.0,<2.0.0

# Compatible release
requests~=2.28.0

# From git repository
git+https://github.com/user/repo.git@main#egg=package

# Local package in editable mode
-e ./my_package

# Extra dependencies
package[extra1,extra2]
```
