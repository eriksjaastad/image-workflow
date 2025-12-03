# Code Quality Rules (Ruff + Pre-commit)

**Audience:** Developers & AI Assistants  
**Last Updated:** December 2, 2025

---

## 🎯 Philosophy

**Strict but pragmatic:** Catch real bugs and enforce clean, modern Python, without making trivial things painful.

Ruff is the **source of truth** for style and linting. The relevant config lives in `pyproject.toml` under `[tool.ruff]` and `[tool.ruff.lint]`.

- **Target Python:** 3.11 (`target-version = "py311"`)
- **Main rule families enabled:**
  - `E`, `F`, `I` – pycodestyle, pyflakes, import sorting
  - `B`, `BLE` – common bug patterns, broad exceptions
  - `C4` – comprehensions
  - `DTZ` – timezone-aware datetimes
  - `T10`, `T20` – debuggers & print statements
  - `EM`, `ISC`, `G` – error messages, implicit string concat, logging style
  - `PIE`, `SIM`, `TID`, `UP`, `PL`, `RUF` – miscellaneous quality + modern syntax + pylint-ish rules
  - `S` – security checks (with a few pragmatic ignores)
  - `ARG`, `PTH` – unused arguments, prefer `pathlib`
  - `D` – docstrings (Google style, enforced selectively via ignores/per-file rules)
  - `PT` – pytest style (with some relaxations in tests)

Per-file ignores exist only to tolerate **legacy code**. New code should not rely on them.

---

## 🚨 Rules That Will FAIL Pre-commit (or Should Be Treated as Hard Errors)

These are enforced by Ruff and pre-commit and should be considered **non-negotiable** in new or edited code.

### 1. Silent Broad Exceptions (`BLE`, `S110`, `S112` + custom hook)

❌ **FORBIDDEN:**

```python
try:
    risky_operation()
except:  # Catches everything, hides bugs
    pass

try:
    risky_operation()
except Exception:  # Too broad, silent
    pass
```

✅ **REQUIRED:**

```python
try:
    risky_operation()
except FileNotFoundError as exc:
    logger.error("File not found: %s", exc)
    raise

try:
    risky_operation()
except Exception as exc:
    logger.error("Unexpected error in risky_operation: %s", exc)
    raise  # Re-raise after logging
```

**Rule of thumb:**

- Catch specific exceptions whenever possible.
- If you really must catch `Exception`, log and re-raise.
- Bare `except:` is almost never acceptable.

---

### 2. Print Statements in Library Code (T201)

Library and shared code must not use `print()` for normal behavior.

❌ **FORBIDDEN in:** `scripts/utils/`, `scripts/ai/`, and any shared modules

```python
def process_data(data):
    print("Processing...")  # Don't print in libraries
    return data
```

✅ **USE LOGGING INSTEAD:**

```python
import logging

logger = logging.getLogger(__name__)

def process_data(data):
    logger.info("Processing %d items", len(data))
    return data
```

✅ **PRINTS ALLOWED ONLY IN THESE LOCATIONS** (matching Ruff config):

- `scripts/[0-9][0-9]*_*.py` – numbered workflow scripts (e.g., `01_import_data.py`)
- `scripts/tools/**` – CLI tools
- `scripts/dashboard/**` – dashboard app
- `**/tests/**` – tests

If a file doesn't match one of those patterns, assume `print()` is not allowed.

---

### 3. Undefined Names (F821)

❌ **FORBIDDEN:**

```python
result = undefined_variable  # Typo or missing import
```

✅ **REQUIRED:**

```python
from scripts.utils.parsers import parse_record

result = parse_record(line)
```

Always import what you use, and never rely on globals that aren't clearly defined.

---

### 4. Unused Imports (F401)

❌ **FORBIDDEN:**

```python
import os
import sys  # Never used - remove it
```

✅ **REQUIRED:**

```python
import os  # Only import what you actually use
```

Ruff will remove many of these automatically via `--fix`. New code should be written so that no unused imports are introduced.

---

### 5. Imports & Sorting (`I`, `TID`, isort settings)

Imports are automatically sorted and grouped:

1. Standard library
2. Third-party
3. First-party (`scripts`)

**Example:**

```python
# 1. Standard library
from pathlib import Path
import sys

# 2. Third-party
import click

# 3. First-party
from scripts.utils.paths import DATA_DIR
```

- No wildcard imports (`from x import *`).
- Avoid imports inside functions unless there's a clear reason (circular imports, optional deps).
- First-party imports are recognized via `known-first-party = ["scripts"]`.

---

### 6. Debugger Left in Code (T10)

❌ **FORBIDDEN:**

```python
import pdb; pdb.set_trace()
breakpoint()
```

Remove all debugger statements before committing.

---

### 7. Poor Error Messages (EM)

Don't embed complex f-strings directly in `raise` calls.

❌ **LESS PREFERRED:**

```python
raise ValueError(f"Invalid value: {value}")
```

✅ **PREFERRED:**

```python
msg = f"Invalid value: {value}"
raise ValueError(msg)
```

This makes messages easier to test, re-use, and refactor.

---

### 8. Timezone-Naive Datetimes (DTZ)

❌ **DANGEROUS:**

```python
from datetime import datetime

now = datetime.now()  # Naive - timezone unclear
```

✅ **SAFE:**

```python
from datetime import datetime, timezone

now = datetime.now(timezone.utc)  # Explicit UTC
```

New code should prefer timezone-aware datetimes. Legacy code may have per-file ignores, but don't copy that pattern.

---

### 9. Path Handling – Always Prefer `pathlib` (PTH)

New code should not use `os.path` and bare `open()`.

❌ **AVOID IN NEW CODE:**

```python
import os

config_path = os.path.join("config", "settings.yml")
with open(config_path, "r", encoding="utf-8") as f:
    data = f.read()
```

✅ **PREFERRED:**

```python
from pathlib import Path

config_path = Path("config") / "settings.yml"
data = config_path.read_text(encoding="utf-8")
```

Some legacy files have `PTH123` ignored; this is for backwards compatibility only.

---

## ⚠️ Warnings (Won't Fail, But Review)

These are disabled as hard failures but should still prompt a quick review when Ruff flags them.

### Complexity (`PLR0911`, `PLR0912`, `PLR0913`, `PLR0915`)

- Too many returns
- Too many branches
- Too many arguments
- Too many statements

**Action:**
If you see these, consider refactoring or adding helpers. They won't block a commit, but they usually mean "this function is doing too much."

---

## ✅ Allowed / Encouraged Patterns

### 1. Prints in CLI Scripts

```python
# scripts/01_start_project.py - OK!
print("Project started successfully")
```

These are user-facing and intentionally chatty.

### 2. Flexible Test Assertions and Debugging (`**/tests/**`)

```python
def test_parse_line() -> None:
    line = "foo,123"
    result = parse_line(line)
    assert result.name == "foo"
    assert result.count == 123

print("Debug:", result)  # OK to leave short-term, try to clean up over time
```

- `assert` is allowed (`S101` ignored in tests).
- Magic values (`PLR2004`) are fine in tests.
- Some strict pytest-style rules are relaxed (`PT009`, `PT027`).

### 3. Magic Values in Tests

```python
assert count == 42  # No need for EXPECTED_COUNT = 42 in tests
```

Use constants in production code where they help clarity; tests can be looser.

---

## 📚 Docstrings & Style (`D*`)

We use **Google-style docstrings** where docstrings are present.

Many strict docstring rules are globally ignored (e.g., missing module/class/function docstrings), especially for small scripts.

For shared utilities / library-like modules, prefer docstrings on:

- Public functions
- Public classes
- Modules that are reused in multiple scripts

**Example:**

```python
def load_records(path: Path) -> list[Record]:
    """Load records from a JSONL file.

    Args:
        path: Path to the JSONL file.

    Returns:
        A list of parsed `Record` objects.
    """
```

---

## 🧪 Tests & Pytest Style (`PT*`)

In `**/tests/**`:

- Prefer pytest-style tests (`assert` statements, fixtures).
- Some pytest-style strictness is relaxed to avoid noise, but:
  - Avoid overly clever assertions.
  - Keep tests readable and focused.

---

## 🔄 Modern Python (`UP`, `SIM`, `PIE`)

New code should use:

- **f-strings** for non-logging string formatting.
- **Comprehensions** instead of long loops where clear.
- **Idiomatic helpers** like `any()`, `all()`, `sum()` where appropriate.

Avoid unnecessary cleverness; readability beats micro-optimizations.

We intentionally ignore a few "overly opinionated" simplifications:

- `SIM108` – ternary instead of if/else
- `SIM105` – `contextlib.suppress` instead of explicit try/except

Use whichever is clearer.

---

## 🔧 Running Checks Manually

```bash
# Run Ruff on specific files
ruff check scripts/your_file.py

# Run Ruff on everything
ruff check scripts/

# Auto-fix what can be fixed
ruff check --fix scripts/

# Run pre-commit on staged files
pre-commit run

# Run pre-commit on all files
pre-commit run --all-files
```

---

## 📝 Quick Reference for AI Models

When generating code:

1. **Decide file type:**
   - If under `scripts/utils/**`, `scripts/ai/**` → treat as library code (no prints, logging only).
   - If under `scripts/tools/**`, `scripts/dashboard/**`, or a numbered script `scripts/NN_*.py` → prints are OK.

2. **Exceptions:**
   - Never use bare `except:`.
   - Avoid `except Exception` unless you log and re-raise.
   - Prefer catching specific exception types.

3. **I/O & Paths:**
   - Use `pathlib.Path` everywhere (PTH rules).
   - Avoid `os.path` and bare `open()` in new code.

4. **Datetime:**
   - Use timezone-aware datetimes:

   ```python
   from datetime import datetime, timezone
   now = datetime.now(timezone.utc)
   ```

5. **Imports:**
   - Group as stdlib / third-party / first-party.
   - Import only what you use; no unused imports.

6. **Logging & Errors:**
   - Use `logging` in libraries; don't `print()`.
   - Build error message strings separately, then raise.

7. **Format & Lint:**
   - Assume `ruff format` + `ruff check --fix` will be run and write code that passes without needing `# noqa`.
