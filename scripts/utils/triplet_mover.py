#!/usr/bin/env python3
"""
Utility: Triplet Mover
=======================
Find and move complete triplets (stage1/stage1.5/stage2) to destination directory.
Maintains file integrity by moving complete sets with their companion files (same-stem metadata, e.g., .yaml/.caption).

VIRTUAL ENVIRONMENT:
--------------------
Activate virtual environment first:
  source .venv311/bin/activate

USAGE:
------
Move complete triplets to new directory:
  python scripts/utils/triplet_mover.py source_dir destination_dir
  python scripts/utils/triplet_mover.py ~/Downloads/raw_images triplets/

FEATURES:
---------
• Detects complete triplet sequences (stage1→stage1.5→stage2)
• Moves PNG files with corresponding companion metadata
• Creates destination directory if needed
• Reports incomplete triplets for manual review
• Safe file operations with progress tracking
• Preserves timestamp and metadata information
"""

import argparse
import shutil
import sys
from pathlib import Path

# Import standardized companion file utilities
sys.path.append(str(Path(__file__).parent))
from companion_file_utils import detect_stage, move_file_with_all_companions


def scan_images_recursive(folder: Path) -> list[Path]:
    """Scan for PNG files recursively in folder and subdirectories."""
    files = []
    for png_file in folder.rglob("*.png"):
        files.append(png_file)
    return sorted(files)


def find_triplets(files: list[Path]) -> list[tuple[Path, Path, Path]]:
    """Find complete triplets in the sorted file list, following the logic from triplet_culler_v9."""
    triplets = []
    i = 0
    while i < len(files) - 2:  # Need at least 3 files remaining
        # Get stages for the next 3 files
        stages = [detect_stage(files[j].name) for j in range(i, i + 3)]

        # Check if we have stage1, stage1.5, stage2 in sequence (like triplet_culler_v9)
        if (
            stages[0] == "stage1_generated"
            and stages[1] == "stage1.5_face_swapped"
            and stages[2] == "stage2_upscaled"
        ):
            # Found a triplet - timestamps don't need to match exactly
            triplets.append((files[i], files[i + 1], files[i + 2]))
            i += 3  # Skip past this triplet
        else:
            i += 1  # Move to next file

    return triplets


def check_conflicts(triplet: tuple[Path, Path, Path], dest_dir: Path) -> list[str]:
    """Check for conflicting files that would be overwritten."""
    conflicts = []

    for png_path in triplet:
        # Check PNG conflict
        dest_png = dest_dir / png_path.name
        if dest_png.exists():
            conflicts.append(png_path.name)

        # Check YAML conflict
        yaml_path = png_path.parent / f"{png_path.stem}.yaml"
        if yaml_path.exists():
            dest_yaml = dest_dir / yaml_path.name
            if dest_yaml.exists():
                conflicts.append(yaml_path.name)

    return conflicts


def move_triplet_with_yamls(triplet: tuple[Path, Path, Path], dest_dir: Path) -> bool:
    """Move a triplet of PNG files and ALL their corresponding companion files."""
    # First check for conflicts
    conflicts = check_conflicts(triplet, dest_dir)
    if conflicts:
        for _conflict in conflicts:
            pass
        return False

    moved_files = []
    try:
        for png_path in triplet:
            # Use wildcard logic to move PNG and ALL companion files
            files_moved = move_file_with_all_companions(
                png_path, dest_dir, dry_run=False
            )
            moved_files.extend(files_moved)

        return True

    except Exception:
        # Try to move back any files we already moved
        for moved_file in moved_files:
            try:
                original_dir = triplet[0].parent  # Assume all from same dir
                shutil.move(str(dest_dir / moved_file), str(original_dir / moved_file))
            except Exception:
                pass
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Find and move complete triplets to destination directory"
    )
    parser.add_argument(
        "source_dir", type=str, help="Source directory to search for triplets"
    )
    parser.add_argument("dest_dir", type=str, help="Destination directory for triplets")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be moved without actually moving",
    )
    args = parser.parse_args()

    source_dir = Path(args.source_dir).expanduser().resolve()
    dest_dir = Path(args.dest_dir).expanduser().resolve()

    if not source_dir.exists() or not source_dir.is_dir():
        sys.exit(1)

    if not dest_dir.exists():
        sys.exit(1)

    files = scan_images_recursive(source_dir)

    triplets = find_triplets(files)

    if not triplets:
        return

    if args.dry_run:
        for _i, triplet in enumerate(triplets, 1):
            for png_path in triplet:
                yaml_path = png_path.parent / f"{png_path.stem}.yaml"
                if yaml_path.exists():
                    pass
        return

    # Confirm before moving
    response = input(f"\nMove {len(triplets)} triplets to {dest_dir}? (y/n): ").lower()
    if response != "y":
        return

    moved_count = 0

    for _i, triplet in enumerate(triplets, 1):
        if move_triplet_with_yamls(triplet, dest_dir):
            moved_count += 1
        else:
            break

    if moved_count == len(triplets):
        pass
    else:
        pass

    # Clean up empty directories
    for root, _dirs, files in source_dir.walk(top_down=False):
        if root != source_dir:  # Don't remove the source directory itself
            try:
                if not any(root.iterdir()):  # Directory is empty
                    root.rmdir()
            except Exception:
                pass  # Directory not empty or permission error


if __name__ == "__main__":
    main()
