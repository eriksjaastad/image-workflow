#!/usr/bin/env python3
"""
Convert to Parquet v1
=====================
Converts JSONL snapshots to Parquet format with compression.

This is an optional upgrade that provides:
- Faster query performance (especially for large datasets)
- Better compression (typically 5-10x smaller than JSONL)
- Column-based analytics optimization

Requirements:
    pip install pyarrow pandas

Usage:
    # Convert all datasets
    python scripts/convert_to_parquet_v1.py --all

    # Convert specific dataset
    python scripts/convert_to_parquet_v1.py --dataset operation_events

    # Specify compression
    python scripts/convert_to_parquet_v1.py --all --compression snappy
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, cast

try:
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
except ImportError:
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = PROJECT_ROOT / "snapshot"

DATASETS = {
    "operation_events": {
        "jsonl_pattern": "operation_events_v1/day=*/events.jsonl",
        "parquet_dir": "operation_events_v1_parquet",
        "partition_cols": ["day"],
    },
    "derived_sessions": {
        "jsonl_pattern": "derived_sessions_v1/day=*/sessions.jsonl",
        "parquet_dir": "derived_sessions_v1_parquet",
        "partition_cols": ["day"],
    },
    "timer_sessions": {
        "jsonl_pattern": "timer_sessions_v1/day=*/sessions.jsonl",
        "parquet_dir": "timer_sessions_v1_parquet",
        "partition_cols": ["day"],
    },
    "progress_snapshots": {
        "jsonl_pattern": "progress_snapshots_v1/day=*/snapshots.jsonl",
        "parquet_dir": "progress_snapshots_v1_parquet",
        "partition_cols": ["day"],
    },
    "daily_aggregates": {
        "jsonl_pattern": "daily_aggregates_v1/day=*/aggregate.json",
        "parquet_dir": "daily_aggregates_v1_parquet",
        "partition_cols": ["day"],
    },
    "projects": {
        "jsonl_pattern": "projects_v1/projects.jsonl",
        "parquet_dir": "projects_v1_parquet",
        "partition_cols": [],
    },
}


def read_jsonl(file_path: Path) -> list[dict[str, Any]]:
    """Read JSONL file into list of dicts."""
    records = []
    with open(file_path) as f:
        for line in f:
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records


def read_json(file_path: Path) -> dict[str, Any]:
    """Read single JSON file."""
    with open(file_path) as f:
        return json.load(f)


def convert_dataset(
    dataset_name: str, compression: str = "snappy", row_group_size: int = 100000
) -> bool:
    """
    Convert a dataset from JSONL to Parquet.

    Args:
        dataset_name: Name of dataset to convert
        compression: Compression codec (snappy, gzip, zstd, none)
        row_group_size: Number of rows per row group

    Returns:
        True if successful
    """
    if dataset_name not in DATASETS:
        return False

    config = DATASETS[dataset_name]

    # Find all JSONL/JSON files
    pattern = cast(str, config["jsonl_pattern"])
    jsonl_files = list(SNAPSHOT_DIR.glob(pattern))

    if not jsonl_files:
        return False

    # Read all records
    all_records = []
    for jsonl_file in jsonl_files:
        try:
            if jsonl_file.suffix == ".jsonl":
                records = read_jsonl(jsonl_file)
            else:
                # Single JSON file (aggregates)
                record = read_json(jsonl_file)
                # Extract day from path
                day = jsonl_file.parent.name.split("=")[1]
                record["day"] = day
                records = [record]

            all_records.extend(records)
        except Exception:
            continue

    if not all_records:
        return False

    # Convert to DataFrame
    try:
        df = pd.DataFrame(all_records)
    except Exception:
        return False

    # Output directory
    output_dir = SNAPSHOT_DIR / cast(str, config["parquet_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write Parquet
    partition_cols = config.get("partition_cols", [])

    try:
        if partition_cols:
            # Write partitioned
            table = pa.Table.from_pandas(df)
            pq.write_to_dataset(
                table,
                root_path=str(output_dir),
                partition_cols=partition_cols,
                compression=compression,
                use_dictionary=True,  # Dictionary encoding for string columns
                row_group_size=row_group_size,
            )
        else:
            # Write single file
            output_file = output_dir / f"{dataset_name}.parquet"
            df.to_parquet(
                output_file, compression=compression, index=False, engine="pyarrow"
            )

        # Show size comparison
        jsonl_size = sum(f.stat().st_size for f in jsonl_files)
        parquet_files = list(output_dir.rglob("*.parquet"))
        parquet_size = sum(f.stat().st_size for f in parquet_files)

        jsonl_size / parquet_size if parquet_size > 0 else 0

        return True

    except Exception:
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Convert JSONL snapshots to Parquet format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Datasets:
  - operation_events: File operation events
  - derived_sessions: Derived sessions
  - timer_sessions: Legacy timer sessions
  - progress_snapshots: Progress snapshots
  - daily_aggregates: Pre-aggregated daily stats
  - projects: Project manifests

Compression options:
  - snappy: Fast compression/decompression (default)
  - gzip: Better compression ratio, slower
  - zstd: Best of both worlds (modern)
  - none: No compression

Examples:
  # Convert all datasets with snappy compression
  python scripts/convert_to_parquet_v1.py --all
  
  # Convert specific dataset with zstd compression
  python scripts/convert_to_parquet_v1.py --dataset operation_events --compression zstd
  
  # Convert multiple datasets
  python scripts/convert_to_parquet_v1.py --dataset operation_events --dataset derived_sessions
        """,
    )

    parser.add_argument("--all", action="store_true", help="Convert all datasets")
    parser.add_argument(
        "--dataset",
        action="append",
        choices=list(DATASETS.keys()),
        help="Dataset to convert (can be specified multiple times)",
    )
    parser.add_argument(
        "--compression",
        default="snappy",
        choices=["snappy", "gzip", "zstd", "none"],
        help="Compression codec (default: snappy)",
    )
    parser.add_argument(
        "--row-group-size",
        type=int,
        default=100000,
        help="Rows per row group (default: 100000)",
    )

    args = parser.parse_args()

    if not args.all and not args.dataset:
        sys.exit(1)

    # Determine datasets to convert
    if args.all:
        datasets_to_convert = list(DATASETS.keys())
    else:
        datasets_to_convert = args.dataset

    # Convert datasets
    failed = []
    for dataset_name in datasets_to_convert:
        success = convert_dataset(
            dataset_name,
            compression=args.compression,
            row_group_size=args.row_group_size,
        )
        if not success:
            failed.append(dataset_name)

    # Summary

    if failed:
        for dataset_name in failed:
            pass
    else:
        pass

    sys.exit(0 if not failed else 1)


if __name__ == "__main__":
    main()
