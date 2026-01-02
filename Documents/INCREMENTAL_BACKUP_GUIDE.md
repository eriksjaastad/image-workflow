# Smart Incremental Backup System

## The Problem

The old backup system copied **ALL files every single night**, even when nothing changed:
- 541 MB copied every night = ~16 GB per month
- When using a mobile hotspot, this burned through data allowance
- Created dozens of identical backup copies wasting disk space

## The Solution

New **incremental backup system** that:
1. ✅ **Only backs up new or modified files**
2. ✅ **Hardlinks unchanged files** (instant, zero disk space)
3. ✅ **Dry-run mode** to preview before backing up
4. ✅ **Smart analysis** to find and clean up redundant old backups

## How It Works

### Incremental Backup Logic

```
For each file:
  1. Check if it exists in previous backup
  2. Compare size and modification time
  
  If unchanged:
    → Create hardlink (instant, no network transfer, no disk space)
  
  If new or modified:
    → Copy file (only transfers what changed)
```

### Hardlinks Explained

A hardlink is like a "reference" to the same file on disk:
- Multiple directory entries point to the same data
- Instant creation (no copying)
- Takes zero additional disk space
- If you delete one hardlink, the data stays (other links remain)

**Example**: If you have 500 MB of unchanged files across 10 backups:
- Old system: 500 MB × 10 = 5 GB disk space
- New system: 500 MB × 1 = 500 MB disk space (other 9 are hardlinks)

## Usage

### 1. Preview What Would Be Backed Up (Dry Run)

```bash
cd /Users/eriksjaastad/projects/image-workflow
python scripts/backup/incremental_backup.py --dry-run
```

This shows:
- How many files are new/modified/unchanged
- How much bandwidth would be used
- What percentage is saved through deduplication

### 2. Run Actual Backup

```bash
python scripts/backup/incremental_backup.py
```

Default destination: `~/project-data-archives/image-workflow/YYYY-MM-DD/`

### 3. Custom Destination

```bash
python scripts/backup/incremental_backup.py --dest /path/to/backups
```

### 4. Analyze Existing Backups

Find redundant backups (identical copies):

```bash
python scripts/backup/analyze_backups.py
```

Shows:
- How many backups are identical
- Which ones can be deleted
- How much disk space can be freed

### 5. Clean Up Redundant Backups

```bash
python scripts/backup/analyze_backups.py --cleanup
```

**⚠️ Warning**: This deletes redundant backups! It keeps the most recent of each group.

## Example Output

### Incremental Backup (Dry Run)

```
[2025-12-28] INFO: 🚀 Starting Smart Incremental Backup
[2025-12-28] INFO: 📂 Previous backup found: 2025-12-27
[2025-12-28] INFO: 📂 Backup destination: 2025-12-28

📁 Processing: File operations logs
   Total files: 45
   New files: 2 (1.2 MB)
   Modified files: 0
   Unchanged files: 43 (12.3 MB)

📁 Processing: Snapshot data
   Total files: 1,234
   New files: 0 (0 B)
   Modified files: 0
   Unchanged files: 1,234 (89.4 MB)

📁 Processing: Training data
   Total files: 3,456
   New files: 15 (45.6 MB)
   Modified files: 2 (3.4 MB)
   Unchanged files: 3,439 (387.2 MB)

==============================================================
📊 BACKUP SUMMARY
==============================================================
Total data to transfer: 50.2 MB
Total data deduplicated: 488.9 MB
Bandwidth saved: 90.7%

🔍 This was a DRY RUN - no files were copied
```

### Backup Analysis

```
📊 Backup Analysis
==============================================================
Found 60 backups

Unique backups: 5
Redundant backups: 55

Total space used: 32.5 GB
Space for unique backups: 2.7 GB
Wasted space: 29.8 GB
Potential savings: 91.7%

📋 Redundant Backup Groups
==============================================================

🔄 Identical backups (45 copies, 541 MB each):
  ❌ 2025-10-30 - DELETE (redundant)
  ❌ 2025-10-31 - DELETE (redundant)
  ...
  ❌ 2025-12-27 - DELETE (redundant)
  ✅ 2025-12-28 - KEEP (newest)
```

## When to Use

### Use Incremental Backup When:
- ✅ You have ongoing work with new files being created
- ✅ You're on a limited bandwidth connection (mobile hotspot)
- ✅ You want to minimize backup time and data transfer

### Skip Backup When:
- ❌ No work for weeks/months (nothing new to back up)
- ❌ Project is inactive/archived

## Setup for Automated Backups

### Update Cron Job (if you want to re-enable backups)

Edit: `/Users/eriksjaastad/projects/image-workflow/scripts/backup/setup_cron_backup.sh`

Change the backup script from `daily_backup.py` to `incremental_backup.py`:

```bash
#!/bin/bash
PROJECT_DIR="/Users/eriksjaastad/projects/image-workflow"
DEST_DIR="$HOME/project-data-archives/image-workflow"
PY_BIN="$PROJECT_DIR/.venv311/bin/python"

# Run at 2:00 PM instead of 2:00 AM
CRON_LINE="0 14 * * * /bin/bash -lc 'cd \"$PROJECT_DIR\" && \"$PY_BIN\" scripts/backup/incremental_backup.py --dest \"$DEST_DIR\" >> \"$DEST_DIR/backup.log\" 2>&1'"

# Install cron job
crontab -l 2>/dev/null | grep -v "incremental_backup.py" > /tmp/crontab_new.txt
echo "$CRON_LINE" >> /tmp/crontab_new.txt
crontab /tmp/crontab_new.txt
rm /tmp/crontab_new.txt

echo "✅ Incremental backup scheduled for 2:00 PM daily"
```

Then run:
```bash
bash scripts/backup/setup_cron_backup.sh
```

## Comparison: Old vs New

| Feature | Old System | New System |
|---------|-----------|------------|
| **Daily backup size** | 541 MB (always) | 1-50 MB (typically) |
| **Monthly data usage** | ~16 GB | ~0.5-1.5 GB |
| **Disk space (60 backups)** | 32.5 GB | 2-3 GB |
| **Backup time** | 5-10 minutes | 30 seconds |
| **Handles unchanged files** | Copies everything | Hardlinks (instant) |
| **Bandwidth on hotspot** | Expensive! 💸 | Minimal ✅ |

## Recovery

Both old and new backups work the same way for recovery:
1. Navigate to backup date: `~/project-data-archives/image-workflow/2025-12-28/`
2. Copy files back to project
3. Each backup is complete and standalone (thanks to hardlinks)

## Maintenance

### Monthly Cleanup Recommended

```bash
# Analyze backups
python scripts/backup/analyze_backups.py

# Clean up if there are many redundant copies
python scripts/backup/analyze_backups.py --cleanup
```

This keeps your backup directory lean and efficient.

---

**TL;DR**: New backup system only transfers what changed, saving 90%+ bandwidth and disk space! 🎉

