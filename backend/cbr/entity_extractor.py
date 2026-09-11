"""
ResolveAI — Entity Extractor

Extracts structured entities from problem descriptions and error logs:
- Error codes and exception names
- Tool names (python, pip, git, npm, etc.)
- Package names
- Version numbers
- OS indicators
- File paths
- Commands

Uses regex patterns — no heavy NLP dependency.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class ExtractedEntities:
    """Structured entities extracted from text."""
    error_codes: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    packages: list[str] = field(default_factory=list)
    versions: list[str] = field(default_factory=list)
    os_indicators: list[str] = field(default_factory=list)
    file_paths: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "error_codes": self.error_codes,
            "tools": self.tools,
            "packages": self.packages,
            "versions": self.versions,
            "os_indicators": self.os_indicators,
            "file_paths": self.file_paths,
            "commands": self.commands,
        }

    def all_entities(self) -> list[str]:
        """Flatten all entities into a single list (for overlap scoring)."""
        return (
            self.error_codes + self.tools + self.packages +
            self.versions + self.os_indicators + self.commands
        )


# ── Known patterns ────────────────────────────────────────────────

PYTHON_ERRORS = [
    "ModuleNotFoundError", "ImportError", "SyntaxError", "IndentationError",
    "TabError", "TypeError", "ValueError", "KeyError", "IndexError",
    "AttributeError", "NameError", "FileNotFoundError", "PermissionError",
    "OSError", "IOError", "RuntimeError", "StopIteration", "RecursionError",
    "MemoryError", "OverflowError", "ZeroDivisionError", "UnicodeDecodeError",
    "UnicodeEncodeError", "ConnectionError", "TimeoutError", "JSONDecodeError",
    "subprocess.CalledProcessError", "PackageNotFoundError",
    "DistributionNotFound", "VersionConflict", "InvalidRequirement",
]

KNOWN_TOOLS = [
    "python", "python3", "pip", "pip3", "pipx", "pipenv", "poetry",
    "conda", "mamba", "virtualenv", "venv", "pyenv",
    "git", "github", "gitlab", "npm", "node", "docker",
    "pytest", "unittest", "setuptools", "wheel", "twine",
]

OS_KEYWORDS = {
    "windows": ["windows", "win32", "win64", "cmd", "powershell", "ntfs", "\\\\"],
    "linux": ["linux", "ubuntu", "debian", "fedora", "centos", "apt", "apt-get", "yum", "dnf", "bash"],
    "macos": ["macos", "mac os", "darwin", "homebrew", "brew", "osx"],
}


def extract_entities(text: str) -> ExtractedEntities:
    """Extract structured entities from problem text or error log."""
    entities = ExtractedEntities()
    text_lower = text.lower()

    # ── Error codes / exception names ──────────────────────────
    # Python exceptions
    for error in PYTHON_ERRORS:
        if error.lower() in text_lower or error in text:
            entities.error_codes.append(error)

    # Generic error patterns: "error: ...", "Error:", "ERROR"
    error_patterns = re.findall(
        r"(?:error|exception|fatal|critical)[\s:]+([^\n]{5,60})",
        text, re.IGNORECASE,
    )
    for match in error_patterns[:5]:  # limit to avoid noise
        clean = match.strip().rstrip(".")
        if clean and clean not in entities.error_codes:
            entities.error_codes.append(clean)

    # Exit codes
    exit_codes = re.findall(r"exit\s*(?:code|status)\s*[=:]?\s*(\d+)", text_lower)
    for code in exit_codes:
        entities.error_codes.append(f"exit code {code}")

    # ── Tool names ─────────────────────────────────────────────
    for tool in KNOWN_TOOLS:
        # Match as whole word
        if re.search(rf"\b{re.escape(tool)}\b", text_lower):
            entities.tools.append(tool)

    # ── Package names ──────────────────────────────────────────
    # pip install <package>
    pip_packages = re.findall(
        r"pip\s+install\s+(?:-[a-zA-Z]+\s+)*([a-zA-Z0-9_-]+)",
        text, re.IGNORECASE,
    )
    entities.packages.extend(pip_packages)

    # import <package> / from <package>
    import_packages = re.findall(
        r"(?:import|from)\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        text,
    )
    entities.packages.extend(import_packages[:10])

    # ModuleNotFoundError: No module named '<package>'
    missing_modules = re.findall(
        r"No module named\s+['\"]([a-zA-Z0-9_.-]+)['\"]",
        text,
    )
    entities.packages.extend(missing_modules)

    # ── Version numbers ────────────────────────────────────────
    versions = re.findall(
        r"(?:version|v|==|>=|<=)\s*(\d+\.\d+(?:\.\d+)?)",
        text, re.IGNORECASE,
    )
    entities.versions.extend(versions[:5])

    # Python version
    py_versions = re.findall(r"python\s*(\d\.\d+(?:\.\d+)?)", text_lower)
    entities.versions.extend(py_versions)

    # ── OS indicators ──────────────────────────────────────────
    for os_name, keywords in OS_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                if os_name not in entities.os_indicators:
                    entities.os_indicators.append(os_name)
                break

    # ── File paths ─────────────────────────────────────────────
    # Windows paths
    win_paths = re.findall(r"[A-Z]:\\[^\s\"']+", text)
    entities.file_paths.extend(win_paths[:5])

    # Unix paths
    unix_paths = re.findall(r"(?:/[a-zA-Z0-9._-]+){2,}", text)
    entities.file_paths.extend(unix_paths[:5])

    # ── Commands ───────────────────────────────────────────────
    # Lines starting with $ or > (command prompt indicators)
    cmd_lines = re.findall(r"^[\$\>]\s*(.+)$", text, re.MULTILINE)
    entities.commands.extend(cmd_lines[:5])

    # Common command patterns
    cmd_patterns = re.findall(
        r"(?:pip|python|git|npm|conda)\s+[a-z]+(?:\s+[^\n]{3,40})?",
        text_lower,
    )
    for cmd in cmd_patterns[:5]:
        if cmd not in entities.commands:
            entities.commands.append(cmd)

    # Deduplicate all lists
    entities.error_codes = list(dict.fromkeys(entities.error_codes))
    entities.tools = list(dict.fromkeys(entities.tools))
    entities.packages = list(dict.fromkeys(entities.packages))
    entities.versions = list(dict.fromkeys(entities.versions))
    entities.os_indicators = list(dict.fromkeys(entities.os_indicators))
    entities.file_paths = list(dict.fromkeys(entities.file_paths))
    entities.commands = list(dict.fromkeys(entities.commands))

    return entities
