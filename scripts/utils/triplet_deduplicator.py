#!/usr/bin/env python3
"""
Triplet Deduplication Utility - Remove triplets if any stage matches completed work

This utility prevents duplicates by checking incoming images against files already
in Kiara_Average_Completed. If ANY stage of a triplet matches an existing file,
the ENTIRE triplet is removed from the new batch.

Usage:
    python scripts/utils/triplet_deduplicator.py <new_images_directory>

Example:
    python scripts/utils/triplet_deduplicator.py "Raw_Images_New"
"""

import argparse
from pathlib import Path

from utils.companion_file_utils import (
    extract_base_timestamp,
    find_all_companion_files,
    safe_delete_paths,
)


def build_completed_database(completed_dir):
    """Build a set of all base timestamps from completed work."""
    completed_path = Path(completed_dir)
    completed_timestamps = set()

    if not completed_path.exists():
        return completed_timestamps

    # Find all PNG files in completed directory
    png_files = list(completed_path.rglob("*.png"))

    for png_file in png_files:
        base_timestamp = extract_base_timestamp(png_file.name)
        if base_timestamp:
            completed_timestamps.add(base_timestamp)

    return completed_timestamps


def find_triplets_in_directory(directory):
    """Find all triplets in the given directory."""
    dir_path = Path(directory)
    triplets = {}

    # Find all PNG files and group by base timestamp
    png_files = list(dir_path.glob("*.png"))

    for png_file in png_files:
        base_timestamp = extract_base_timestamp(png_file.name)
        if not base_timestamp:
            continue

        if base_timestamp not in triplets:
            triplets[base_timestamp] = {}

        # Determine stage type
        if "_stage1_generated.png" in png_file.name:
            triplets[base_timestamp]["stage1"] = png_file
        elif "_stage1.5_face_swapped.png" in png_file.name:
            triplets[base_timestamp]["stage1_5"] = png_file
        elif "_stage2_upscaled.png" in png_file.name:
            triplets[base_timestamp]["stage2"] = png_file

    return triplets


def remove_triplet_files(triplet_files):
    """Remove all files in a triplet (PNG + ALL companion files)."""
    removed_files = []

    for _stage, png_file in triplet_files.items():
        if png_file and png_file.exists():
            # Find ALL companion files (YAML, caption, etc.)
            all_companions = find_all_companion_files(png_file)
            all_files = [png_file, *all_companions]

            # Remove PNG + all companions using centralized utility
            try:
                deleted_paths = safe_delete_paths(
                    all_files, hard_delete=False, tracker=None
                )
                for deleted_path in deleted_paths:
                    removed_files.append(deleted_path.name)
            except Exception:
                pass

    return removed_files


def main():
    parser = argparse.ArgumentParser(
        description="Remove duplicate triplets based on completed work"
    )
    parser.add_argument(
        "new_images_dir", help="Directory containing new images to deduplicate"
    )
    parser.add_argument(
        "--completed-dir",
        default="Kiara_Average_Completed",
        help="Directory containing completed work (default: Kiara_Average_Completed)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without actually removing files",
    )

    args = parser.parse_args()

    new_images_path = Path(args.new_images_dir)
    if not new_images_path.exists():
        return


    # Build database of completed work
    completed_timestamps = build_completed_database(args.completed_dir)

    if not completed_timestamps:
        return

    # Find triplets in new images
    new_triplets = find_triplets_in_directory(args.new_images_dir)

    if not new_triplets:
        return


    # Check for duplicates
    duplicates_found = []

    for base_timestamp, triplet_files in new_triplets.items():
        if base_timestamp in completed_timestamps:
            duplicates_found.append((base_timestamp, triplet_files))

    if not duplicates_found:
        return


    total_removed = 0

    for base_timestamp, triplet_files in duplicates_found:

        if args.dry_run:
            for _stage, png_file in triplet_files.items():
                if png_file and png_file.exists():
                    # Show PNG + ALL companion files
                    all_companions = find_all_companion_files(png_file)
                    all_files = [png_file, *all_companions]
                    for _file_to_remove in all_files:
                        pass
        else:
            removed_files = remove_triplet_files(triplet_files)
            total_removed += len(removed_files)

    if args.dry_run:
        pass
    else:
        pass


if __name__ == "__main__":
    main()
