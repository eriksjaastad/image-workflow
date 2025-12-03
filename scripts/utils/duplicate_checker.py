#!/usr/bin/env python3
"""
Utility: Duplicate File Checker
================================
Find exact duplicate files by comparing filenames (not file content).
Useful for verifying file integrity after operations like selection/sorting.

VIRTUAL ENVIRONMENT:
--------------------
Activate virtual environment first:
  source .venv311/bin/activate

USAGE:
------
Single-directory scan (recursive):
  python scripts/utils/duplicate_checker.py /path/to/root

Two-directory comparison (recursive; show filenames that exist in BOTH):
  python scripts/utils/duplicate_checker.py /path/dirA /path/dirB

Options:
  --extensions png            # default: png (comma-separated if you need more)

FEATURES:
---------
• Scans subdirectories recursively
• Finds duplicate filenames across a tree, or intersection between two trees
• Defaults to PNG files (companions can be added via --extensions)
• Clear summary with example paths
"""

import argparse
import sys
from collections import defaultdict
from pathlib import Path


def find_all_files(
    root_dir: Path, extensions: list[str] | None = None
) -> dict[str, list[Path]]:
    """Find all files and group them by filename."""
    if extensions is None:
        extensions = [".png"]

    file_map = defaultdict(list)

    for ext in extensions:
        pattern = f"**/*{ext}"
        for file_path in root_dir.rglob(pattern):
            if file_path.is_file():
                filename = file_path.name
                file_map[filename].append(file_path)

    return file_map


def find_duplicates(file_map: dict[str, list[Path]]) -> dict[str, list[Path]]:
    """Find files that appear in multiple locations."""
    duplicates = {}

    for filename, paths in file_map.items():
        if len(paths) > 1:
            duplicates[filename] = paths

    return duplicates


def analyze_directories(root_dir: Path, extensions: list[str]) -> None:
    """Analyze all directories for duplicate files."""
    # Find all files
    file_map = find_all_files(root_dir, extensions)

    sum(len(paths) for paths in file_map.values())
    len(file_map)

    # Find duplicates
    duplicates = find_duplicates(file_map)

    if not duplicates:
        return

    # Group duplicates by directory pairs
    duplicate_pairs = defaultdict(list)

    for filename, paths in duplicates.items():
        # Sort paths to get consistent grouping
        sorted_paths = sorted(paths)
        for i in range(len(sorted_paths)):
            for j in range(i + 1, len(sorted_paths)):
                dir1 = sorted_paths[i].parent
                dir2 = sorted_paths[j].parent
                key = f"{dir1} ↔ {dir2}"
                duplicate_pairs[key].append(
                    (filename, sorted_paths[i], sorted_paths[j])
                )

    # Report duplicates by directory pairs
    for _dir_pair, files in duplicate_pairs.items():
        for filename, _path1, _path2 in sorted(files)[:10]:  # Show first 10
            pass

        if len(files) > 10:
            pass

    # Summary by directory
    dir_counts: dict[str, int] = defaultdict(int)

    for filename, paths in duplicates.items():
        for path in paths:
            dir_counts[path.parent] += 1

    for _directory, _count in sorted(dir_counts.items()):
        pass


def analyze_two_directories(dir_a: Path, dir_b: Path, extensions: list[str]) -> None:
    """Compare two roots and report filenames present in both (recursive)."""
    map_a = find_all_files(dir_a, extensions)
    map_b = find_all_files(dir_b, extensions)

    sum(len(paths) for paths in map_a.values())
    sum(len(paths) for paths in map_b.values())

    common_names = set(map_a.keys()) & set(map_b.keys())
    if not common_names:
        return

    shown = 0
    for name in sorted(common_names):
        paths_a = sorted(map_a[name])
        paths_b = sorted(map_b[name])
        for _p in paths_a[:5]:
            pass
        if len(paths_a) > 5:
            pass
        for _p in paths_b[:5]:
            pass
        if len(paths_b) > 5:
            pass
        shown += 1
        if shown >= 50:
            break


def main():
    parser = argparse.ArgumentParser(
        description="Find duplicate filenames (single dir) or intersections (two dirs)"
    )
    parser.add_argument(
        "root_dir",
        nargs="?",
        default=".",
        help="Root directory to scan (single-directory mode)",
    )
    parser.add_argument(
        "second_dir",
        nargs="?",
        default=None,
        help="Optional: second directory for two-directory comparison",
    )
    parser.add_argument(
        "--extensions",
        default="png",
        help="Comma-separated file extensions to check (default: png)",
    )
    args = parser.parse_args()

    root_dir = Path(args.root_dir).expanduser().resolve()
    if not root_dir.exists() or not root_dir.is_dir():
        sys.exit(1)

    extensions = [
        f".{ext.strip()}" for ext in args.extensions.split(",") if ext.strip()
    ]
    if not extensions:
        extensions = [".png"]

    if args.second_dir:
        dir_b = Path(args.second_dir).expanduser().resolve()
        if not dir_b.exists() or not dir_b.is_dir():
            sys.exit(1)
        analyze_two_directories(root_dir, dir_b, extensions)
        return

    analyze_directories(root_dir, extensions)


if __name__ == "__main__":
    main()
