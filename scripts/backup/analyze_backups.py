#!/usr/bin/env python3
"""
Backup Cleanup Utility
======================
Analyzes backup history and identifies redundant backups that can be safely deleted.

Shows which backups are identical (no changes between them) so you can reclaim disk space.

Usage:
  # Just analyze - don't delete anything
  python scripts/backup/analyze_backups.py

  # Show detailed file-level differences
  python scripts/backup/analyze_backups.py --verbose

  # Clean up redundant backups (keeps most recent of each group)
  python scripts/backup/analyze_backups.py --cleanup
"""

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, cast


def get_dir_fingerprint(directory: Path) -> tuple[int, int, str]:
    """
    Get a fingerprint of directory contents.
    Returns: (file_count, total_bytes, hash_of_hashes)
    """
    if not directory.exists():
        return (0, 0, "")

    files_info = []
    total_bytes = 0

    for file_path in sorted(directory.rglob("*")):
        if file_path.is_file():
            stat = file_path.stat()
            rel_path = file_path.relative_to(directory)
            files_info.append(f"{rel_path}:{stat.st_size}:{stat.st_mtime}")
            total_bytes += stat.st_size

    # Create hash of all file info
    combined = "\n".join(files_info)
    fingerprint = hashlib.sha256(combined.encode()).hexdigest()[:16]

    return (len(files_info), total_bytes, fingerprint)


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
        description="Analyze and optionally clean up redundant backups"
    )
    parser.add_argument(
        "--dest",
        default=str(Path.home() / "project-data-archives" / "image-workflow"),
        help="Backup root directory to analyze",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed information about each backup",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Actually delete redundant backups (keeps most recent of each group)",
    )
    args = parser.parse_args()

    backup_root = Path(args.dest).expanduser()

    if not backup_root.exists():
        print(f"❌ Backup directory not found: {backup_root}")
        return

    print("=" * 70)
    print("📊 Backup Analysis")
    print("=" * 70)
    print(f"Analyzing: {backup_root}\n")

    # Find all backup directories
    backup_dirs = sorted(
        [
            d
            for d in backup_root.iterdir()
            if d.is_dir() and len(d.name) == 10 and d.name.count("-") == 2
        ]
    )

    if not backup_dirs:
        print("⚠️  No backup directories found")
        return

    print(f"Found {len(backup_dirs)} backups\n")

    # Analyze each backup
    backup_info = []
    for backup_dir in backup_dirs:
        print(f"📁 Analyzing {backup_dir.name}...", end=" ")

        file_count, total_bytes, fingerprint = get_dir_fingerprint(backup_dir)

        info = {
            "date": backup_dir.name,
            "path": backup_dir,
            "file_count": file_count,
            "total_bytes": total_bytes,
            "fingerprint": fingerprint,
            "size_str": format_bytes(total_bytes),
        }
        backup_info.append(info)

        print(f"{file_count} files, {info['size_str']}")

    # Group by fingerprint (identical backups)
    fingerprint_groups: dict[str, list[dict[str, Any]]] = {}
    for info in backup_info:
        fp = str(info["fingerprint"])
        if fp not in fingerprint_groups:
            fingerprint_groups[fp] = []
        fingerprint_groups[fp].append(info)

    # Analyze redundancy
    print("\n" + "=" * 70)
    print("🔍 Redundancy Analysis")
    print("=" * 70)

    unique_count = len(fingerprint_groups)
    redundant_count = len(backup_dirs) - unique_count

    print(f"\nUnique backups: {unique_count}")
    print(f"Redundant backups: {redundant_count}")

    if redundant_count == 0:
        print("\n✅ All backups are unique - nothing to clean up!")
        return

    # Calculate space that could be saved
    total_space_used: int = sum(cast(int, info["total_bytes"]) for info in backup_info)
    space_for_unique: int = sum(
        cast(int, groups[0]["total_bytes"]) for groups in fingerprint_groups.values()
    )
    space_wasted = total_space_used - space_for_unique

    print(f"\nTotal space used: {format_bytes(total_space_used)}")
    print(f"Space for unique backups: {format_bytes(space_for_unique)}")
    print(f"Wasted space: {format_bytes(space_wasted)}")
    print(f"Potential savings: {(space_wasted / total_space_used * 100):.1f}%")

    # Show redundant groups
    print("\n" + "=" * 70)
    print("📋 Redundant Backup Groups")
    print("=" * 70)

    redundant_to_delete = []

    for fp, group in fingerprint_groups.items():
        if len(group) > 1:
            print(
                f"\n🔄 Identical backups ({len(group)} copies, {group[0]['size_str']} each):"
            )

            # Sort by date
            group_sorted = sorted(group, key=lambda x: x["date"])

            for i, backup in enumerate(group_sorted):
                status = (
                    "KEEP (newest)"
                    if i == len(group_sorted) - 1
                    else "DELETE (redundant)"
                )
                marker = "  ✅" if i == len(group_sorted) - 1 else "  ❌"
                print(f"{marker} {backup['date']} - {status}")

                if i < len(group_sorted) - 1:  # Not the newest
                    redundant_to_delete.append(backup)

    # Cleanup if requested
    if args.cleanup:
        print("\n" + "=" * 70)
        print("🗑️  CLEANUP MODE")
        print("=" * 70)

        if not redundant_to_delete:
            print("\n✅ Nothing to delete")
            return

        print(f"\nWill delete {len(redundant_to_delete)} redundant backups:")
        for backup in redundant_to_delete:
            print(f"  - {backup['date']} ({backup['size_str']})")

        print(
            f"\nSpace to be freed: {format_bytes(sum(b['total_bytes'] for b in redundant_to_delete))}"
        )

        response = input(
            "\n⚠️  Are you sure? This cannot be undone! (type 'yes' to confirm): "
        )

        if response.lower() == "yes":
            import shutil

            for backup in redundant_to_delete:
                print(f"🗑️  Deleting {backup['date']}...", end=" ")
                shutil.rmtree(backup["path"])
                print("✅")

            print(f"\n✅ Cleaned up {len(redundant_to_delete)} redundant backups!")
            print(
                f"💾 Freed {format_bytes(sum(b['total_bytes'] for b in redundant_to_delete))}"
            )
        else:
            print("\n❌ Cleanup cancelled")
    else:
        print("\n💡 To clean up redundant backups, run with --cleanup flag")
        print("   python scripts/backup/analyze_backups.py --cleanup")


if __name__ == "__main__":
    main()
