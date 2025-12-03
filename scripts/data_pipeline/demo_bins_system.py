from typing import Any

#!/usr/bin/env python3
"""
15-Minute Bins System Demo
==========================
Quick demonstration and validation of the bins system.

This script:
1. Generates bins for last 7 days
2. Validates them against raw logs
3. Shows sample bin output
4. Calculates performance metrics

Run this to verify the system is working correctly.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))


def print_section(title: str):
    """Print a section header."""


def run_command(cmd: list, description: str) -> tuple[bool, str]:
    """Run a command and return success status and output."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=project_root, check=False
        )

        output = result.stdout + result.stderr

        if result.returncode == 0:
            return True, output
        return False, output
    except Exception as e:
        return False, str(e)


def count_bins(data_dir: Path) -> int:
    """Count total bins across all days."""
    bins_dir = data_dir / "aggregates" / "daily"
    if not bins_dir.exists():
        return 0

    total = 0
    for bin_file in bins_dir.rglob("agg_15m.jsonl"):
        try:
            with open(bin_file) as f:
                total += sum(1 for _ in f)
        except Exception:
            continue

    return total


def show_sample_bin(data_dir: Path):
    """Show a sample bin record."""
    bins_dir = data_dir / "aggregates" / "daily"
    if not bins_dir.exists():
        return

    # Find most recent bin file
    bin_files = list(bins_dir.rglob("agg_15m.jsonl"))
    if not bin_files:
        return

    # Sort by modification time (newest first)
    bin_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    # Read first bin from most recent file
    try:
        with open(bin_files[0]) as f:
            first_line = f.readline()
            if first_line:
                json.loads(first_line)
            else:
                pass
    except Exception:
        pass


def check_raw_logs(data_dir: Path) -> tuple[int, str, str]:
    """Check raw logs availability."""
    logs_dir = data_dir / "file_operations_logs"
    archives_dir = data_dir / "log_archives"

    log_count = len(list(logs_dir.glob("*.log"))) if logs_dir.exists() else 0
    archive_count = len(list(archives_dir.glob("*.gz"))) if archives_dir.exists() else 0

    # Find date range
    all_files: list[Any] = []
    if logs_dir.exists():
        all_files.extend(logs_dir.glob("*.log"))
    if archives_dir.exists():
        all_files.extend(archives_dir.glob("*.gz"))

    if not all_files:
        return 0, "N/A", "N/A"

    # Extract dates from filenames
    dates = []
    for f in all_files:
        # Extract YYYYMMDD from filename
        import re

        match = re.search(r"(\d{8})", f.name)
        if match:
            date_str = match.group(1)
            try:
                date = datetime.strptime(date_str, "%Y%m%d")
                dates.append(date)
            except Exception:
                continue

    if dates:
        dates.sort()
        min_date = dates[0].strftime("%Y-%m-%d")
        max_date = dates[-1].strftime("%Y-%m-%d")
    else:
        min_date = "N/A"
        max_date = "N/A"

    return log_count + archive_count, min_date, max_date


def main():
    """Run demo."""
    print_section("15-Minute Bins System Demo")

    data_dir = project_root / "data"

    # Check prerequisites

    log_count, _min_date, _max_date = check_raw_logs(data_dir)

    if log_count == 0:
        sys.exit(1)

    # Step 1: Generate bins
    print_section("Step 1: Generate Bins (Last 7 Days)")

    success, _ = run_command(
        [sys.executable, "scripts/data_pipeline/aggregate_to_15m.py", "--days", "7"],
        "Aggregating last 7 days to 15-minute bins",
    )

    if not success:
        sys.exit(1)

    # Count bins
    count_bins(data_dir)

    # Step 2: Validate bins
    print_section("Step 2: Validate Bins")

    success, _output = run_command(
        [sys.executable, "scripts/data_pipeline/validate_15m_bins.py", "--days", "7"],
        "Validating bins against raw logs",
    )

    if not success:
        pass

    # Step 3: Show sample
    print_section("Step 3: Sample Bin Record")
    show_sample_bin(data_dir)

    # Step 4: Performance metrics
    print_section("Step 4: Performance Metrics")

    # Calculate compression ratio
    bins_dir = data_dir / "aggregates" / "daily"
    if bins_dir.exists():
        bins_size = sum(
            f.stat().st_size for f in bins_dir.rglob("agg_15m.jsonl") if f.is_file()
        )

        logs_dir = data_dir / "file_operations_logs"
        archives_dir = data_dir / "log_archives"

        logs_size = 0
        if logs_dir.exists():
            logs_size += sum(f.stat().st_size for f in logs_dir.glob("*.log"))
        if archives_dir.exists():
            logs_size += sum(f.stat().st_size for f in archives_dir.glob("*.gz"))

        if logs_size > 0:
            (1 - bins_size / logs_size) * 100
        else:
            pass

    # Step 5: Next steps
    print_section("Next Steps")

    print_section("Demo Complete ✅")


if __name__ == "__main__":
    main()
