# Claude Code Project Instructions

This file provides project-specific instructions for Claude Code when working on this repository.

## 📚 Required Reading Before Writing Code

**You MUST read and follow these rules:**

1. **Code Quality Rules:** `Documents/reference/CODE_QUALITY_RULES.md`
   - Python 3.11 modern typing (use `dict`, `list`, `X | None` - NOT `Dict`, `List`, `Optional`)
   - Ruff linting standards
   - Exception handling patterns
   - pathlib over os.path

2. **File Safety Rules:** `.cursorrules`
   - NEVER modify existing image/YAML files in-place
   - Use FileTracker for all file operations
   - Move files, don't modify them

## Quick Summary

### Python 3.11 Typing (CRITICAL)

```python
# ✅ CORRECT
from typing import Any
data: dict[str, Any] = {}
items: list[int] = []
value: str | None = None

# ❌ WRONG - Never use these
from typing import Dict, List, Optional  # NO!
```

### File Safety

- **NEVER** modify existing PNG/YAML/caption files
- **ALWAYS** use `move_file_with_all_companions()` for file moves
- **ALWAYS** use `send2trash()` for deletions
- **ALWAYS** log operations via FileTracker

### Validation

After making changes, run:
```bash
ruff check scripts/
mypy scripts --ignore-missing-imports --allow-untyped-defs --no-warn-return-any --disable-error-code=union-attr
```

## Project Structure

- `scripts/` - Main Python codebase
- `scripts/utils/` - Library code (use logging, not print)
- `scripts/tools/` - CLI tools (prints OK)
- `scripts/[0-9][0-9]_*.py` - Workflow scripts (prints OK)
- `Documents/reference/` - Documentation and rules

