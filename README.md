# image-workflow

**AI-assisted image processing workflow for selecting, cropping, and managing AI-generated images at scale.**

## What Is This?

A production-grade system for processing thousands of AI-generated images through a multi-stage workflow:
1. **Select** the best version from each generation batch (stage1 → stage1.5 → stage2)
2. **Crop** faces/characters with AI assistance
3. **Sort** into character groups
4. **Review** and deduplicate
5. **Package** for delivery

Built to handle 10,000+ images per project with full audit trails, AI training data collection, and productivity dashboards.

## Why Does It Exist?

AI image generation produces multiple versions per prompt (upscales, face swaps, etc.). This workflow:
- **Reduces 12,000 images → 4,000 selected → 2,000 final crops** in ~18 hours
- **Trains AI models** from your decisions (selection + crop preferences)
- **Tracks productivity** with real-time dashboards
- **Ensures safety** - production images are read-only, all operations logged

## What To Know Before Touching

### Critical Safety Rules (NEVER VIOLATE)

1. **Production images are READ-ONLY** - Move, don't modify
2. **Only `02_ai_desktop_multi_crop.py` writes new images** (cropped outputs)
3. **Always move companions together** - `.yaml` + `.caption` + `.png` as a unit
4. **Use `trash` for deletions** - Recoverable from macOS Trash
5. **All file operations are logged** - `data/file_operations_logs/`

See `__Knowledge/image-workflow/file-safety.md` for full safety system.

### Architecture Overview

```
Production Images (read-only):
  mojo1/, mojo2/, mojo3/     → Raw AI-generated images
  __selected/                → Best versions selected
  __crop/                    → Queued for cropping
  __cropped/                 → Final cropped outputs
  __character_group_1/2/3/   → Sorted by character

Data Layer (append-only):
  data/file_operations_logs/ → All file moves/crops/deletes
  data/training/             → AI training data (SQLite v3)
  data/snapshot/             → Dashboard aggregates
  data/schema/               → JSON/SQL schemas

Code:
  scripts/00-07_*.py         → Main workflow scripts
  scripts/dashboard/         → Flask API + Chart.js UI
  scripts/data_pipeline/     → Extract → aggregate → snapshot
  scripts/ai/                → Training utilities
  scripts/tools/             → Maintenance utilities
  scripts/utils/             → Shared helpers
  scripts/tests/             → Unit/integration/Selenium tests
```

### Data Flow

**1. Image Processing Workflow:**
```
Raw Images (mojo3/)
  ↓ 01_ai_assisted_reviewer.py (AI suggests best version)
__selected/ or __crop/
  ↓ 02_ai_desktop_multi_crop.py (AI suggests crop, you refine)
__cropped/
  ↓ 03_web_character_sorter.py (sort by character)
__character_group_1/2/3/
  ↓ 07_finish_project.py (package for delivery)
ZIP file ready for client
```

**2. AI Training Data (SQLite v3):**
```
01_ai_assisted_reviewer.py → Logs selection + AI crop suggestion
  ↓ Creates .decision sidecar in __crop/
02_ai_desktop_multi_crop.py → Reads sidecar, logs final crop
  ↓ Updates SQLite with match flags
data/training/ai_training_decisions/{project}.db
  ↓ Used by scripts/ai/train_*.py
Trained AI models in data/ai_data/models/
```

**3. Dashboard Data:**
```
All file operations → data/file_operations_logs/*.log
  ↓ scripts/data_pipeline/extract_operation_events_v1.py
data/snapshot/operation_events_v1/
  ↓ scripts/data_pipeline/build_daily_aggregates_v1.py
data/snapshot/daily_aggregates_v1/
  ↓ scripts/dashboard/productivity_dashboard.py (Flask API)
dashboard_template.html (Chart.js UI)
```

## Key Files

### Main Workflow Scripts (Run These)

| Script | Purpose | When To Use |
|--------|---------|-------------|
| `scripts/00_start_project.py` | Create project manifest | Start of new project |
| `scripts/01_ai_assisted_reviewer.py` | Select best versions + AI crop suggestions | First step after raw images |
| `scripts/02_ai_desktop_multi_crop.py` | Crop faces with AI assistance | After selection |
| `scripts/03_web_character_sorter.py` | Sort into character groups | After cropping |
| `scripts/05_web_multi_directory_viewer.py` | Review all groups | Before finishing |
| `scripts/06_web_duplicate_finder.py` | Find and remove duplicates | Optional cleanup |
| `scripts/07_finish_project.py` | Package for delivery | End of project |

### Dashboard & Analytics

| Script | Purpose |
|--------|---------|
| `scripts/dashboard/run_dashboard.py` | Launch productivity dashboard |
| `scripts/data_pipeline/extract_operation_events_v1.py` | Update dashboard data |
| `scripts/data_pipeline/build_daily_aggregates_v1.py` | Pre-aggregate for performance |

### AI Training

| Script | Purpose |
|--------|---------|
| `scripts/ai/train_ranker_v3.py` | Train selection model |
| `scripts/ai/train_crop_proposer_v2.py` | Train crop suggestion model |
| `scripts/ai/backfill_*.py` | Extract historical training data |

## How To Get Started

### 1. Start a New Project
```bash
python scripts/00_start_project.py ../mojo4
# Creates manifest in data/projects/mojo4.project.json
```

### 2. Process Images
```bash
# Step 1: Select best versions (AI-assisted)
python scripts/01_ai_assisted_reviewer.py ../mojo4

# Step 2: Crop faces (AI suggests, you refine)
python scripts/02_ai_desktop_multi_crop.py

# Step 3: Sort by character
python scripts/03_web_character_sorter.py __selected
```

### 3. Launch Dashboard (Optional)
```bash
python scripts/dashboard/run_dashboard.py --host 127.0.0.1 --port 5001
# Open scripts/dashboard/dashboard_template.html in browser
```

### 4. Finish Project
```bash
# Preview first (dry run)
python scripts/07_finish_project.py --project-id mojo4

# Commit (creates ZIP for delivery)
python scripts/07_finish_project.py --project-id mojo4 --commit
```

## Operational Wisdom

**See `__Knowledge/image-workflow/` for hard-won lessons:**
- `disaster-recovery.md` - What's backed up, recovery procedures
- `file-safety.md` - Safety rules, companion files, .decision pattern
- `ai-training.md` - SQLite v3 system, two-stage logging
- `data-operations.md` - "Always inspect first" rule
- `testing-lessons.md` - "Tests were failing us" lessons
- `workflow-patterns.md` - "Simple is better" triplet detection
- `performance-gotchas.md` - Matplotlib crashes, CSV lag fixes
- `dashboard-architecture.md` - Data contracts, timing systems

## Common Tasks

**Update dashboard data:**
```bash
python scripts/data_pipeline/extract_operation_events_v1.py
python scripts/data_pipeline/build_daily_aggregates_v1.py
```

**Check project status:**
```bash
cat data/projects/mojo3.project.json | jq '.status, .counts'
```

**Audit file safety:**
```bash
python scripts/tools/audit_file_safety.py
```

**Validate training data:**
```bash
python scripts/ai/validate_databases.py
```

## Testing

```bash
# Run all tests
pytest scripts/tests/

# Run specific test suite
pytest scripts/tests/test_dashboard_core.py

# Run with coverage
python scripts/tests/run_coverage.py
```

## Related Documentation

- **Project Lifecycle:** `Documents/PROJECT_LIFECYCLE_SCRIPTS.md`
- **Architecture:** `Documents/core/ARCHITECTURE_OVERVIEW.md`
- **Dashboard Guide:** `Documents/dashboard/DASHBOARD_GUIDE.md`
- **File Safety:** `Documents/safety/FILE_SAFETY_SYSTEM.md`
- [scripts/warden_audit.py|warden_audit.py](scripts/warden_audit.py|warden_audit.py)

## Status
- **Current Phase:** [Phase Name]
- **Status:** #status/active
## CI / Automated Code Review

Pull requests are automatically reviewed by Claude Sonnet via a [centralized reusable workflow](https://github.com/eriksjaastad/tools/blob/main/.github/workflows/claude-review-reusable.yml) hosted in the `tools` repo.

**On every PR:**
- Tests run (if any exist)
- AI reviews the diff against project standards and governance protocol
- Posts a sticky review comment and a `claude-review` commit status
- Auto-merges on APPROVE, blocks on REQUEST_CHANGES

See [tools repo](https://github.com/eriksjaastad/tools) for configuration details.
