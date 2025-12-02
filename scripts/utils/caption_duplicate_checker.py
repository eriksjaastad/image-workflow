#!/usr/bin/env python3
"""
Caption Duplicate Checker
=========================
Analyzes .caption files in a directory to find identical content.
Useful for identifying duplicate prompts or similar descriptions.

USAGE:
------
  # Basic duplicate analysis
  python scripts/utils/caption_duplicate_checker.py mixed-0919/black
  python scripts/utils/caption_duplicate_checker.py sorted/unknown --show-content

  # Move duplicate groups to subdirectories
  python scripts/utils/caption_duplicate_checker.py mixed-0919/black --move-groups
  python scripts/utils/caption_duplicate_checker.py sorted/unknown --move-groups --dry-run

FEATURES:
---------
• Finds all .caption files in directory
• Groups files by identical content
• Shows duplicate groups with file counts
• Optional content preview for each group
• Summary statistics of duplicates vs unique files
• Move duplicate groups to numbered subdirectories
• Moves both .caption and .png files together
• Dry-run mode for safe testing
"""

import argparse
import shutil
import sys
from collections import defaultdict
from pathlib import Path


def analyze_caption_duplicates(directory: str, show_content: bool = False) -> dict:
    """
    Analyze .caption files for duplicate content.

    Args:
        directory: Directory to scan for .caption files
        show_content: Whether to show the actual content of each group

    Returns:
        Dictionary with analysis results
    """
    directory_path = Path(directory).resolve()
    if not directory_path.exists() or not directory_path.is_dir():
        msg = f"Directory not found: {directory_path}"
        raise ValueError(msg)

    # Find all .caption files
    caption_files = list(directory_path.rglob("*.caption"))
    total_files = len(caption_files)


    if total_files == 0:
        return {"total_files": 0, "unique_contents": 0, "duplicate_groups": []}

    # Group files by content
    content_groups = defaultdict(list)
    read_errors = []

    for caption_file in caption_files:
        try:
            with open(caption_file, encoding="utf-8") as f:
                content = f.read().strip()
            content_groups[content].append(caption_file)
        except Exception as e:
            read_errors.append(f"Error reading {caption_file}: {e}")

    if read_errors:
        for _error in read_errors:
            pass

    # Analyze results
    unique_contents = len(content_groups)
    duplicate_groups = []
    total_duplicates = 0


    # Find duplicate groups (content appearing in multiple files)
    for content, files in content_groups.items():
        if len(files) > 1:
            duplicate_groups.append(
                {"content": content, "files": files, "count": len(files)}
            )
            total_duplicates += len(files)

    if duplicate_groups:


        # Sort by count (most duplicates first)
        duplicate_groups.sort(key=lambda x: x["count"], reverse=True)

        for _i, group in enumerate(duplicate_groups, 1):

            if show_content:
                (
                    group["content"][:100] + "..."
                    if len(group["content"]) > 100
                    else group["content"]
                )

            for _file_path in group["files"]:
                pass
    else:
        pass

    return {
        "total_files": total_files,
        "unique_contents": unique_contents,
        "duplicate_groups": duplicate_groups,
        "total_duplicates": total_duplicates,
        "unique_files": total_files - total_duplicates,
        "directory_path": directory_path,
    }


def move_duplicate_groups_to_subdirs(
    analysis_results: dict, dry_run: bool = False
) -> dict:
    """
    Move duplicate groups into numbered subdirectories within the same parent directory.
    Moves both .caption and corresponding .png files together.

    Args:
        analysis_results: Results from analyze_caption_duplicates()
        dry_run: Preview mode - don't actually move files

    Returns:
        Dictionary with move operation results
    """
    duplicate_groups = analysis_results["duplicate_groups"]
    directory_path = analysis_results["directory_path"]

    if not duplicate_groups:
        return {"groups_moved": 0, "files_moved": 0, "errors": []}


    groups_moved = 0
    files_moved = 0
    errors = []

    for i, group in enumerate(duplicate_groups, 1):
        group_dir_name = f"duplicate_group_{i:03d}"
        group_dir_path = directory_path / group_dir_name

        (
            group["content"][:50] + "..."
            if len(group["content"]) > 50
            else group["content"]
        )

        if not dry_run:
            try:
                group_dir_path.mkdir(exist_ok=True)
            except Exception as e:
                error_msg = f"Failed to create directory {group_dir_name}: {e}"
                errors.append(error_msg)
                continue

        group_files_moved = 0

        for caption_file in group["files"]:
            try:
                # Move caption and find corresponding PNG file
                png_file = caption_file.with_suffix(".png")

                if png_file.exists():
                    # Use companion file utilities to move PNG and ALL companions
                    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
                    from scripts.utils.companion_file_utils import (
                        move_file_with_all_companions,
                    )

                    if not dry_run:
                        moved_files = move_file_with_all_companions(
                            png_file, group_dir_path, dry_run=False
                        )
                        for _moved_file in moved_files:
                            group_files_moved += 1
                    else:
                        group_files_moved += 2
                else:
                    # Just move the caption file if no PNG exists
                    caption_dest = group_dir_path / caption_file.name
                    if not dry_run:
                        shutil.move(str(caption_file), str(caption_dest))
                    group_files_moved += 1

            except Exception as e:
                error_msg = f"Failed to move {caption_file.name}: {e}"
                errors.append(error_msg)

        if group_files_moved > 0:
            groups_moved += 1
            files_moved += group_files_moved

    if errors:
        for _error in errors:
            pass

    return {"groups_moved": groups_moved, "files_moved": files_moved, "errors": errors}


def main():
    parser = argparse.ArgumentParser(
        description="Check for identical content in .caption files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic duplicate check
  python scripts/utils/caption_duplicate_checker.py mixed-0919/black
  
  # Show content preview for each duplicate group
  python scripts/utils/caption_duplicate_checker.py sorted/unknown --show-content
  
  # Check multiple directories
  python scripts/utils/caption_duplicate_checker.py character_group_1 --show-content
        """,
    )

    parser.add_argument(
        "directory", type=str, help="Directory to scan for .caption files"
    )
    parser.add_argument(
        "--show-content",
        "-c",
        action="store_true",
        help="Show content preview for each duplicate group",
    )
    parser.add_argument(
        "--move-groups",
        "-m",
        action="store_true",
        help="Move duplicate groups to numbered subdirectories",
    )
    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        help="Preview move operations without actually moving files",
    )

    args = parser.parse_args()

    try:
        results = analyze_caption_duplicates(args.directory, args.show_content)

        # Move duplicate groups if requested
        if args.move_groups:
            if results["duplicate_groups"]:
                move_duplicate_groups_to_subdirs(results, args.dry_run)
            else:
                pass

        # Exit with success
        sys.exit(0)

    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()
