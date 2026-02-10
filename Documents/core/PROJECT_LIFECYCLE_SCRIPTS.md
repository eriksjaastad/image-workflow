# Project Lifecycle Management Scripts
**Status:** Active
**Audience:** Developers

**Last Updated:** 2025-10-26


These scripts standardize project creation and completion to ensure consistent manifests, proper timestamps, and accurate tracking.

## Overview

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `00_start_project.py` | Create new project manifest | Beginning of each project |
| `07_finish_project.py` | Mark project as complete | When project is ready for delivery |
| `prezip_stager.py` | Package for delivery | Final step before client handoff |

## 🚀 Starting a New Project

### Interactive Mode (Recommended)
```bash
python scripts/00_start_project.py
```

The script will prompt you for:
- **Project ID**: e.g., `mojo3`, `batch5`, `client_abc`
- **Content Directory**: Path to your image directory
- **Project Title**: Human-readable name (optional)

### Command-Line Mode
```bash
python scripts/00_start_project.py \
  --project-id mojo3 \
  --content-dir ../mojo3 \
  --title "Mojo Project 3"
```

### What It Does
✅ Creates `data/projects/{project-id}.project.json`  
✅ Sets `startedAt` with proper UTC timestamp (Z suffix)  
✅ Counts PNG images and sets `initialImages`  
✅ Creates all required manifest fields  
✅ Backs up existing manifest before overwriting  

### Example Output
```
===========================================================
✅ SUCCESS!
===========================================================
Manifest created: data/projects/mojo3.project.json
Project ID:       mojo3
Initial Images:   8,432
Started At:       2025-10-15T19:30:00Z

🎯 Next steps:
   1. Run your image processing tools
   2. When complete, run the prezip_stager to finish the project
===========================================================
```

## 🏁 Finishing a Project

### Interactive Mode (Recommended)
```bash
python scripts/07_finish_project.py
```

The script will:
- List all active projects
- Prompt for which project to finish
- Auto-count final images
- Offer dry-run preview first (safe!)
- Run `prezip_stager` to create delivery ZIP

### Command-Line Mode
```bash
# Dry run (preview only - safe to test)
python scripts/07_finish_project.py --project-id mojo3

# Commit (finalize and create ZIP)
python scripts/07_finish_project.py --project-id mojo3 --commit
```

### What It Does
✅ Validates directory state (FULL check)  
✅ Creates delivery ZIP with allowlist filtering  
✅ Sets `finishedAt` with proper UTC timestamp  
✅ Updates `finalImages` count automatically  
✅ Adds stager metrics (file counts by extension)  
✅ Changes status to `finished`  
✅ Creates backup before updating  

**Note**: This script wraps `scripts/tools/prezip_stager.py` to provide a friendly interface for project completion.

### Example Output
```
======================================================================
✅ SUCCESS!
======================================================================
Manifest updated:  data/projects/mojo3.project.json
Project ID:        mojo3
Finished At:       2025-10-25T14:20:00Z
Final Images:      5,432
Output ZIP:        exports/mojo3_final.zip
ZIP Contents:      15,487 files

🎯 Next steps:
   • Upload: exports/mojo3_final.zip
   • View dashboard for final metrics
======================================================================
```

## 📦 Complete Project Workflow

### 1. Start Project
```bash
python scripts/00_start_project.py
# Enter: mojo3, ../mojo3, "Mojo Project 3"
```

### 2. Process Images
```bash
# Run your normal workflow
python scripts/01_ai_assisted_reviewer.py ../mojo3
python scripts/03_web_character_sorter.py selected
python scripts/02_ai_desktop_multi_crop.py
```

### 3. Finish Project (with automatic ZIP creation)
```bash
# Preview first (dry run)
python scripts/07_finish_project.py --project-id mojo3

# If preview looks good, commit
python scripts/07_finish_project.py --project-id mojo3 --commit
```

**Note**: Step 3 automatically runs `prezip_stager` to create the delivery ZIP and update the manifest. No need to run prezip_stager separately!

## 🎯 Benefits

### Before (Manual Process)
- ❌ Manually editing JSON files
- ❌ Timezone format inconsistencies (Z vs +00:00 vs naive)
- ❌ Forgetting to count images
- ❌ Typos in project IDs
- ❌ Missing required fields
- ❌ Dashboard date filtering broken

### After (Automated Scripts)
- ✅ Consistent UTC timestamps with Z suffix
- ✅ Automatic image counting
- ✅ Validated project IDs
- ✅ All required fields included
- ✅ Backup before overwriting
- ✅ Dashboard date filtering works correctly
- ✅ Accurate hours/days calculations per project

## 📊 Dashboard Integration

These scripts ensure that:
- **Hours**: Calculated correctly from file operations within project date range
- **Days**: Counted accurately based on unique active dates
- **Project filtering**: Works properly because timestamps match format
- **Metrics**: End-to-end throughput computed automatically

## 🔧 Advanced Usage

### Force Overwrite Existing Manifest
```bash
pyt... [truncated]
