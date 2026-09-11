# Python Common Errors and Solutions

## ModuleNotFoundError

### What is ModuleNotFoundError?
`ModuleNotFoundError` is raised when Python cannot find the module you are trying to import. This is a subclass of `ImportError`.

### Common causes:
1. **Module not installed**: The package hasn't been installed via pip
2. **Wrong Python environment**: The module is installed in a different Python installation or virtual environment
3. **Incorrect module name**: Typo in the import statement or confusion between package name and import name
4. **Path issues**: The module's directory is not in `sys.path`

### Solutions:
```bash
# Install the missing module
pip install module_name

# If using a virtual environment, make sure it's activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Verify installation
python -m pip list | grep module_name

# Use python -m pip to ensure you're using the right pip
python -m pip install module_name
```

### Package name vs import name differences:
| pip install name | import name |
|------------------|-------------|
| Pillow | PIL |
| scikit-learn | sklearn |
| python-dateutil | dateutil |
| beautifulsoup4 | bs4 |
| opencv-python | cv2 |
| PyYAML | yaml |

## ImportError

### What is ImportError?
`ImportError` is raised when an import statement fails to find the module or when a `from ... import` fails to find a name in the module.

### Common forms:
- `ImportError: cannot import name 'X' from 'Y'` - The name doesn't exist in the module
- `ImportError: attempted relative import with no known parent package` - Relative import outside a package
- `ImportError: DLL load failed` - Missing system library (Windows)

### Solutions for "cannot import name":
1. Check the module's documentation for the correct import path
2. The name may have been renamed or removed in a newer version
3. Check for circular imports between modules

### Solutions for relative import:
```bash
# Run as a module instead of a script
python -m package.module

# Instead of
python package/module.py
```

## SyntaxError

### Common SyntaxError causes:
1. **Missing colons** after if, for, while, def, class statements
2. **Mismatched brackets** - parentheses, brackets, or braces not closed
3. **Invalid Python 2 syntax** in Python 3 (e.g., `print "hello"` → `print("hello")`)
4. **Using reserved keywords** as variable names
5. **Invalid f-string syntax** in older Python versions

### Examples and fixes:
```python
# Wrong: Missing colon
if x == 5
    print(x)

# Right
if x == 5:
    print(x)

# Wrong: Print statement (Python 2)
print "Hello"

# Right: Print function (Python 3)
print("Hello")

# Wrong: f-string in Python < 3.6
f"Hello {name}"

# Right for older Python
"Hello {}".format(name)
```

## PermissionError

### Common causes:
1. **Installing packages globally** without admin rights
2. **File locked** by another process
3. **Read-only file system** or directory

### Solutions:
```bash
# Use virtual environments instead of global install
python -m venv myenv
myenv\Scripts\activate  # Windows
pip install package

# Or install for current user only
pip install --user package

# On Linux, NEVER use sudo pip install
# Use venv instead
```

## FileNotFoundError

### Common causes:
1. **Wrong file path** - typo or incorrect directory
2. **Relative path issues** - script is run from a different directory
3. **Missing file** - file was moved or deleted

### Solutions:
```python
from pathlib import Path

# Use pathlib for cross-platform paths
file_path = Path(__file__).parent / "data" / "file.txt"

# Check if file exists before opening
if file_path.exists():
    content = file_path.read_text()

# Use absolute paths when possible
import os
abs_path = os.path.abspath("relative/path/file.txt")
```

## TypeError

### Common TypeError patterns:
```python
# 'NoneType' object is not subscriptable
# A function returned None when you expected a list/dict
result = some_function()  # Returns None
result[0]  # TypeError!
# Fix: Check return value
if result is not None:
    print(result[0])

# 'int' object is not iterable
for i in 5:  # TypeError!
    print(i)
# Fix:
for i in range(5):
    print(i)

# Missing required argument
def greet(name):
    return f"Hello {name}"
greet()  # TypeError: missing argument
# Fix:
greet("World")
```

## KeyError

### Solutions:
```python
# Use .get() with default value
value = my_dict.get("key", "default")

# Check before accessing
if "key" in my_dict:
    value = my_dict["key"]

# Use collections.defaultdict
from collections import defaultdict
d = defaultdict(list)
d["missing_key"].append("value")  # No KeyError
```
