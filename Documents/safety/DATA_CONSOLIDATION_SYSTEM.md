# Data Consolidation & Cron Job System

> **Last Updated:** December 2025

## Overview

The image-workflow project uses automated cron jobs to maintain data integrity, create backups, and consolidate operational logs. These jobs run daily to ensure the system remains healthy without manual intervention.

---

## Cron Job Schedule

All cron jobs are configured via `scripts/setup_cron.sh`:

| Time | Job | Description |
|------|-----|-------------|
| **2:00 AM** | Legacy Consolidation | Consolidates file operation logs from 2 days ago |
| **2:10 AM** | Daily Backup | Creates daily backup of critical data |
| **2:15 AM** | Snapshot Pipeline | Generates fresh data snapshots for dashboard |
| **Every 6 hours** | Health Check | Monitors backup system health |
| **Sunday 2:10 AM** | Weekly Rollup | Cloud backup consolidation |
| **Sunday 2:30 AM** | Doc Cleanup Report | Generates archive cleanup recommendations |

---

## Key Scripts

### 1. Data Consolidation (`scripts/cleanup_logs.py`)

**Purpose:** Processes file operation logs into daily summaries.

**Why 2-day buffer?** The script processes data from 2 days ago to avoid conflicts with current work sessions. This ensures all operations for a given day are complete before consolidation.

**Usage:**
```bash
# Manual run for specific date
python scripts/cleanup_logs.py --process-date 20251002

# Dry run (no changes)
python scripts/cleanup_logs.py --process-date 20251002 --dry-run

# What cron runs automatically
python scripts/cleanup_logs.py --process-date $(date -d "2 days ago" +%Y%m%d)
```

**What it does:**
1. Reads raw operation logs from `data/file_operations_logs/`
2. Aggregates operations by script and operation type
3. Creates daily summary JSON in `data/daily_summaries/`
4. Verifies dashboard can load the consolidated data

### 2. Snapshot Pipeline

**Purpose:** Generates structured data snapshots for the dashboard.

**Scripts (run in order):**
1. `scripts/data_pipeline/extract_operation_events_v1.py` - Extracts events
2. `scripts/data_pipeline/build_daily_aggregates_v1.py` - Builds aggregates
3. `scripts/data_pipeline/derive_sessions_from_ops_v1.py` - Derives sessions

**Output:** Data stored in `data/snapshot/` directory.

### 3. Daily Backup (`scripts/backup/daily_backup_simple.py`)

**Purpose:** Creates daily backups of critical project data.

**What's backed up:**
- File operation logs
- Daily summaries
- Configuration files
- Snapshot data

### 4. Health Check (`scripts/tools/backup_health_check.py`)

**Purpose:** Monitors backup system health every 6 hours.

**Checks:**
- Backup file existence and freshness
- Disk space availability
- Data integrity verification

---

## Log Files

All cron job output is logged to `data/log_archives/`:

| Log File | Contents |
|----------|----------|
| `cron_consolidation.log` | Legacy consolidation output |
| `cron_snapshot.log` | Snapshot pipeline output |
| `cron_daily_backup.log` | Daily backup status |
| `cron_backup_health.log` | Health check results |
| `cron_weekly_backup.log` | Cloud backup output |
| `cron_doc_cleanup.log` | Archive cleanup reports |

---

## Setup & Installation

### Installing Cron Jobs

```bash
# Run the setup script
./scripts/setup_cron.sh

# Verify installation
crontab -l
```

### Removing Cron Jobs

```bash
# Edit crontab and remove lines
crontab -e

# Or remove all project cron jobs
crontab -l | grep -v "image-workflow" | crontab -
```

---

## Troubleshooting

### Cron Job Not Running

1. **Check if cron daemon is running:**
   ```bash
   pgrep cron
   ```

2. **Check cron logs:**
   ```bash
   tail -f /var/log/syslog | grep CRON
   # or on macOS
   log show --predicate 'subsystem == "com.apple.cron"' --last 1h
   ```

3. **Verify PATH in cron environment:**
   Cron runs with minimal PATH. The setup script uses absolute paths to avoid issues.

### Consolidation Failures

1. **Check the log:**
   ```bash
   tail -50 data/log_archives/cron_consolidation.log
   ```

2. **Run manually to see errors:**
   ```bash
   python scripts/cleanup_logs.py --process-date 20251205 --dry-run
   ```

3. **Common issues:**
   - Missing `data/file_operations_logs/` directory
   - Malformed JSON in log files
   - Dashboard engine import errors

### Backup Failures

1. **Check health status:**
   ```bash
   python scripts/tools/backup_health_check.py
   ```

2. **Verify disk space:**
   ```bash
   df -h
   ```

---

## Data Flow

```
Raw Logs                    Daily Summaries              Dashboard
─────────────────────────────────────────────────────────────────────
data/file_operations_logs/  →  data/daily_summaries/  →  Dashboard UI
        ↓                           ↓
   (cleanup_logs.py)         (data_engine.py loads)
        ↓
data/snapshot/              →  Dashboard (primary source)
   (snapshot pipeline)
```

---

## Safety Considerations

1. **No production file modifications** - Cron jobs only READ from logs and WRITE to designated safe zones (`data/daily_summaries/`, `data/snapshot/`, `data/log_archives/`)

2. **2-day buffer** - Consolidation waits 2 days to ensure work sessions are complete

3. **Dry-run support** - All consolidation can be tested with `--dry-run` before execution

4. **Verification** - Consolidation verifies dashboard can load data before completing

---

## Related Documentation

- `Documents/safety/FILE_SAFETY_SYSTEM.md` - File operation safety rules
- `Documents/data/` - Data pipeline documentation
- `scripts/data_pipeline/README.md` - Snapshot pipeline details

