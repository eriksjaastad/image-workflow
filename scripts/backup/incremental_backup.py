#!/usr/bin/env python3
"""
Smart Incremental Backup System
================================
Only backs up files that are NEW or CHANGED since the last backup.

Key Features:
- Compares against most recent backup to avoid duplicating unchanged files
- Hardlinks unchanged files (zero copy, instant, no disk space)
- Only transfers new/modified files over the network
- Dry-run mode to preview what would be backed up
- Detailed reporting of what was saved

Usage:
  # Preview what would be backed up
  python scripts/backup/incremental_backup.py --dry-run

  # Actually run the backup
  python scripts/backup/incremental_backup.py

  # Specify custom destination
  python scripts/backup/incremental_backup.py --dest ~/my-backups/image-workflow
"""

import argparse
import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, TypedDict


class BackupStats(TypedDict):
    """Statistics for a backup operation."""

    name: str
    source: str
    destination: str
    files_new: int
    files_modified: int
    files_unchanged: int
    files_total: int
    bytes_new: int
    bytes_unchanged: int
    new_files: list[str]
    modified_files: list[str]


def log(message: str, level: str = "INFO") -> None:
    """Log message to both stdout and log file."""
    timestamp = datetime.now().isoformat()
    print(f"[{timestamp}] {level}: {message}")


def find_most_recent_backup(backup_root: Path) -> Path | None:
    """Find the most recent backup directory."""
    if not backup_root.exists():
        return None

    # Find all dated backup directories (YYYY-MM-DD format)
    backup_dirs = [
        d
        for d in backup_root.iterdir()
        if d.is_dir() and len(d.name) == 10 and d.name.count("-") == 2
    ]

    if not backup_dirs:
        return None

    # Sort by name (YYYY-MM-DD sorts chronologically)
    return sorted(backup_dirs)[-1]


def file_changed(src: Path, prev_backup: Path | None) -> bool:
    """Check if file is new or changed compared to previous backup."""
    if prev_backup is None:
        return True  # No previous backup, everything is new

    # Check if file exists in previous backup
    prev_file = prev_backup / src.name
    if not prev_file.exists():
        return True  # New file

    # Compare modification time and size
    src_stat = src.stat()
    prev_stat = prev_file.stat()

    if src_stat.st_size != prev_stat.st_size:
        return True  # Size changed

    # Return True if modified more recently, False otherwise
    return src_stat.st_mtime > prev_stat.st_mtime


def backup_with_dedup(
    src_dir: Path,
    dst_dir: Path,
    prev_backup_dir: Path | None,
    name: str,
    dry_run: bool = False,
) -> BackupStats:
    """
    Backup a directory with smart deduplication.

    - New/changed files: Copy to new backup
    - Unchanged files: Hardlink from previous backup (instant, zero copy)
    """
    stats: BackupStats = {
        "name": name,
        "source": str(src_dir),
        "destination": str(dst_dir),
        "files_new": 0,
        "files_modified": 0,
        "files_unchanged": 0,
        "files_total": 0,
        "bytes_new": 0,
        "bytes_unchanged": 0,
        "new_files": [],
        "modified_files": [],
    }

    if not src_dir.exists():
        log(f"⚠️  Source not found: {src_dir}")
        return stats

    if not dry_run:
        dst_dir.mkdir(parents=True, exist_ok=True)

    # Process all files in source
    for src_file in src_dir.rglob("*"):
        if not src_file.is_file():
            continue

        stats["files_total"] += 1
        file_size = src_file.stat().st_size

        # Calculate relative path
        rel_path = src_file.relative_to(src_dir)
        dst_file = dst_dir / rel_path

        # Check if file exists in previous backup
        prev_file = None
        if prev_backup_dir:
            prev_file = prev_backup_dir / src_dir.name / rel_path

        # Determine if file changed
        if prev_file and prev_file.exists():
            src_stat = src_file.stat()
            prev_stat = prev_file.stat()

            # File unchanged - can hardlink
            if (
                src_stat.st_size == prev_stat.st_size
                and src_stat.st_mtime <= prev_stat.st_mtime
            ):
                stats["files_unchanged"] += 1
                stats["bytes_unchanged"] += file_size

                if not dry_run:
                    dst_file.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        # Create hardlink (instant, no copy)
                        os.link(prev_file, dst_file)
                    except OSError:
                        # Hardlink failed (cross-device?), fall back to copy
                        shutil.copy2(prev_file, dst_file)
                continue
            # File modified
            stats["files_modified"] += 1
            stats["bytes_new"] += file_size
            stats["modified_files"].append(str(rel_path))
        else:
            # New file
            stats["files_new"] += 1
            stats["bytes_new"] += file_size
            stats["new_files"].append(str(rel_path))

        # Copy new/modified file
        if not dry_run:
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst_file)

    return stats


def format_bytes(bytes_val: int | float) -> str:
    """Format bytes as human-readable string."""
    val = float(bytes_val)
    for unit in ["B", "KB", "MB", "GB"]:
        if val < 1024:
            return f"{val:.1f} {unit}"
        val /= 1024
    return f"{val:.1f} TB"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Smart incremental backup - only backs up new/changed files"
    )
    parser.add_argument(
        "--dest",
        default=str(Path.home() / "project-data-archives" / "image-workflow"),
        help="Backup destination root directory",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be backed up without actually copying files",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]
    data_root = project_root / "data"
    backup_root = Path(args.dest).expanduser()

    if args.dry_run:
        log("🔍 DRY RUN MODE - No files will be copied", "INFO")

    log("🚀 Starting Smart Incremental Backup", "START")

    # Find most recent backup
    prev_backup = find_most_recent_backup(backup_root)
    if prev_backup:
        log(f"📂 Previous backup found: {prev_backup.name}")
    else:
        log("📂 No previous backup found - this will be a full backup")

    # Create new backup directory
    today = datetime.now().strftime("%Y-%m-%d")
    backup_dir = backup_root / today

    if backup_dir.exists() and not args.dry_run:
        log(f"⚠️  Backup for {today} already exists, will update it")

    log(f"📂 Backup destination: {backup_dir}")

    # Define what to backup
    backup_sources = [
        (
            data_root / "file_operations_logs",
            "file_operations_logs",
            "File operations logs",
        ),
        (data_root / "snapshot", "snapshot", "Snapshot data"),
        (data_root / "training", "training", "Training data"),
        (data_root / "ai_data", "ai_data", "AI data"),
    ]

    all_stats = []
    total_new_bytes = 0
    total_unchanged_bytes = 0

    # Backup each source
    for src_dir, dst_name, display_name in backup_sources:
        log(f"\n📁 Processing: {display_name}")

        stats = backup_with_dedup(
            src_dir,
            backup_dir / dst_name,
            prev_backup,
            display_name,
            dry_run=args.dry_run,
        )

        all_stats.append(stats)
        total_new_bytes += stats["bytes_new"]
        total_unchanged_bytes += stats["bytes_unchanged"]

        # Report statistics
        log(f"   Total files: {stats['files_total']}")
        log(f"   New files: {stats['files_new']} ({format_bytes(stats['bytes_new'])})")
        log(f"   Modified files: {stats['files_modified']}")
        log(
            f"   Unchanged files: {stats['files_unchanged']} ({format_bytes(stats['bytes_unchanged'])})"
        )

        if stats["new_files"] and len(stats["new_files"]) <= 10:
            log(f"   New: {', '.join(stats['new_files'])}")
        elif stats["new_files"]:
            log(
                f"   New: {stats['new_files'][0]} ... and {len(stats['new_files']) - 1} more"
            )

    # Summary
    log("\n" + "=" * 60)
    log("📊 BACKUP SUMMARY", "SUMMARY")
    log("=" * 60)
    log(f"Total data to transfer: {format_bytes(total_new_bytes)}")
    log(f"Total data deduplicated: {format_bytes(total_unchanged_bytes)}")

    if total_unchanged_bytes > 0:
        saved_pct = (
            total_unchanged_bytes / (total_new_bytes + total_unchanged_bytes)
        ) * 100
        log(f"Bandwidth saved: {saved_pct:.1f}%")

    if args.dry_run:
        log("\n🔍 This was a DRY RUN - no files were copied")
        log("Run without --dry-run to perform the actual backup")
    else:
        # Create manifest
        manifest = {
            "timestamp": datetime.now().isoformat(),
            "backup_date": today,
            "is_incremental": prev_backup is not None,
            "previous_backup": str(prev_backup) if prev_backup else None,
            "total_new_bytes": total_new_bytes,
            "total_unchanged_bytes": total_unchanged_bytes,
            "bandwidth_saved_percent": (
                (
                    total_unchanged_bytes
                    / (total_new_bytes + total_unchanged_bytes)
                    * 100
                )
                if total_unchanged_bytes > 0
                else 0
            ),
            "items": all_stats,
        }

        manifest_file = backup_dir / "manifest.json"
        with open(manifest_file, "w") as f:
            json.dump(manifest, f, indent=2)

        log(f"\n📄 Manifest written to: {manifest_file}")
        log("✅ Backup complete!")


if __name__ == "__main__":
    main()
