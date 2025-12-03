#!/usr/bin/env python3
"""
Utility: Recursive File Mover
==============================
Recursively move all image/YAML pairs from source to destination directory.
Maintains file pair integrity with comprehensive logging and conflict handling.

VIRTUAL ENVIRONMENT:
--------------------
Activate virtual environment first:
  source .venv311/bin/activate

USAGE:
------
Move files between directories:
  python scripts/utils/recursive_file_mover.py __cropped __selected
  python scripts/utils/recursive_file_mover.py ~/Downloads/output 00_white
  python scripts/utils/recursive_file_mover.py source_dir dest_dir --dry-run
  python scripts/utils/recursive_file_mover.py source_dir dest_dir --yes       # AI/non-interactive

FLAGS:
------
  --dry-run     Preview operations without moving files
  --yes         Skip confirmation (for AI/automated usage)

FEATURES:
---------
• Recursively scans source directory for image/YAML pairs
• Moves files while maintaining pairs integrity
• Validates that both source and destination directories exist
• Provides detailed progress reporting with tqdm
• Uses FileTracker for comprehensive operation logging
• Handles name conflicts with automatic renaming
• Dry-run mode for safe preview of operations
• Non-interactive mode (--yes/--force) for AI/automation
"""

import argparse
import sys
from pathlib import Path

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.file_tracker import FileTracker
from scripts.utils.companion_file_utils import (
    move_multiple_files_with_companions,
)


def find_all_image_files(source_dir: Path) -> list[Path]:
    """Find all image files in source directory recursively."""
    image_files = []

    # Supported image extensions
    image_extensions = {".png", ".jpg", ".jpeg"}

    # Find all image files recursively
    for image_file in source_dir.rglob("*"):
        if image_file.is_file() and image_file.suffix.lower() in image_extensions:
            image_files.append(image_file)

    return image_files


def move_files(source_dir: Path, dest_dir: Path, dry_run: bool = False) -> None:
    """Move all image files and their companions from source to destination."""
    # Initialize FileTracker
    tracker = FileTracker("recursive_file_mover")

    # Find all image files
    image_files = find_all_image_files(source_dir)

    if not image_files:
        return

    # Use shared utility function
    results = move_multiple_files_with_companions(
        image_files, dest_dir, dry_run, tracker
    )

    if results["errors"] > 0:
        pass
    if dry_run:
        pass
    else:
        pass


def main():
    parser = argparse.ArgumentParser(
        description="Recursively move all image/YAML pairs from source to destination directory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/utils/recursive_file_mover.py face_groups 00_white
    python scripts/utils/recursive_file_mover.py ~/Downloads/output 00_white  
    python scripts/utils/recursive_file_mover.py face_groups/person_0001 character_group_1
        """,
    )

    parser.add_argument("source", help="Source directory to move files from")
    parser.add_argument("destination", help="Destination directory to move files to")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be moved without actually moving files",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip confirmation prompt (for AI/automated usage)",
    )

    args = parser.parse_args()

    # Resolve paths
    source_dir = Path(args.source).expanduser().resolve()
    dest_dir = Path(args.destination).expanduser().resolve()

    # Validate source directory
    if not source_dir.exists():
        sys.exit(1)

    if not source_dir.is_dir():
        sys.exit(1)

    # Check if source and destination are the same
    if source_dir == dest_dir:
        sys.exit(1)

    # Validate destination directory
    if not dest_dir.exists():
        sys.exit(1)

    if not dest_dir.is_dir():
        sys.exit(1)

    # Check if destination is inside source (would cause issues)
    try:
        dest_dir.relative_to(source_dir)
        sys.exit(1)
    except ValueError:
        pass  # Good - destination is not inside source

    if args.dry_run:
        pass

    # Confirm operation unless it's a dry run or --yes flag is used
    if not args.dry_run and not args.yes:
        response = input("Continue with file move operation? [y/N]: ").strip().lower()
        if response != "y":
            sys.exit(0)

    move_files(source_dir, dest_dir, args.dry_run)


if __name__ == "__main__":
    main()
