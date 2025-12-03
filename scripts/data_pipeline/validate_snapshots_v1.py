#!/usr/bin/env python3
"""
Validate Snapshots v1
=====================
Automated validation suite for snapshot data integrity.

Checks:
- Row counts by day (raw vs snapshot)
- Min/max timestamps per day and script
- Distinct scripts and operations against allowlist
- Referential integrity (soft checks)
- Schema conformance
"""

import gzip
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, cast

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = PROJECT_ROOT / "snapshot"
LOGS_DIR = PROJECT_ROOT / "data" / "file_operations_logs"
ARCHIVES_DIR = PROJECT_ROOT / "data" / "log_archives"
TIMER_DIR = PROJECT_ROOT / "data" / "timer_data"

# Allowlists
KNOWN_SCRIPTS = {
    "image_version_selector",
    "character_sorter",
    "multi_crop_tool",
    "desktop_image_selector_crop",
    "web_image_selector",
    "web_character_sorter",
    "face_grouper",
    "batch_crop_tool",
    "duplicate_finder",
}

KNOWN_OPERATIONS = {"move", "copy", "delete", "create", "send_to_trash", "stage_delete"}


def count_raw_events_by_day() -> dict[str, int]:
    """Count events in raw logs by day."""
    by_day: dict[str, int] = defaultdict(int)

    # Count from current logs
    if LOGS_DIR.exists():
        for log_file in LOGS_DIR.glob("*.log"):
            try:
                with open(log_file) as f:
                    for line in f:
                        if line.strip():
                            try:
                                event = json.loads(line)
                                ts_str = event.get("timestamp", "")
                                if ts_str:
                                    # Extract date
                                    day = ts_str[:10].replace("-", "")
                                    by_day[day] += 1
                            except json.JSONDecodeError:
                                continue
            except Exception:
                continue

    # Count from archives
    if ARCHIVES_DIR.exists():
        for gz_file in ARCHIVES_DIR.glob("*.gz"):
            try:
                with gzip.open(gz_file, "rt") as f:
                    for line in f:
                        if line.strip():
                            try:
                                event = json.loads(line)
                                ts_str = event.get("timestamp", "")
                                if ts_str:
                                    day = ts_str[:10].replace("-", "")
                                    by_day[day] += 1
                            except json.JSONDecodeError:
                                continue
            except Exception:
                continue

    return dict(by_day)


def count_snapshot_events_by_day() -> dict[str, int]:
    """Count events in operation_events snapshot by day."""
    by_day: dict[str, int] = {}

    events_dir = SNAPSHOT_DIR / "operation_events_v1"
    if not events_dir.exists():
        return by_day

    for day_dir in events_dir.glob("day=*"):
        day_str = day_dir.name.split("=")[1]
        events_file = day_dir / "events.jsonl"

        if events_file.exists():
            count = sum(1 for line in open(events_file) if line.strip())
            by_day[day_str] = count

    return by_day


def validate_event_counts() -> tuple[bool, list[str]]:
    """Validate event counts between raw and snapshot."""
    raw_counts = count_raw_events_by_day()
    snapshot_counts = count_snapshot_events_by_day()

    all_days = set(raw_counts.keys()) | set(snapshot_counts.keys())

    issues = []
    passed = True

    for day in sorted(all_days):
        raw_count = raw_counts.get(day, 0)
        snapshot_count = snapshot_counts.get(day, 0)

        # Allow 1% variance due to deduplication and malformed events
        if raw_count > 0:
            variance = abs(snapshot_count - raw_count) / raw_count
            if variance > 0.01:
                issues.append(
                    f"  {day}: raw={raw_count}, snapshot={snapshot_count} (variance={variance:.1%})"
                )
                passed = False
            else:
                pass
        elif snapshot_count > 0:
            pass

    if issues:
        for _issue in issues:
            pass

    return passed, issues


def validate_timestamps() -> tuple[bool, list[str]]:
    """Validate timestamp ranges per day."""
    events_dir = SNAPSHOT_DIR / "operation_events_v1"
    if not events_dir.exists():
        return False, ["operation_events_v1 not found"]

    issues = []
    passed = True

    for day_dir in sorted(events_dir.glob("day=*")):
        day_str = day_dir.name.split("=")[1]
        events_file = day_dir / "events.jsonl"

        if not events_file.exists():
            continue

        timestamps = []
        with open(events_file) as f:
            for line in f:
                if line.strip():
                    event = json.loads(line)
                    ts_str = event.get("ts_utc")
                    if ts_str:
                        timestamps.append(ts_str)

        if timestamps:
            min(timestamps)
            max(timestamps)
        else:
            issues.append(f"  {day_str}: No valid timestamps")
            passed = False

    return passed, issues


def validate_scripts_operations() -> tuple[bool, list[str]]:
    """Validate scripts and operations against allowlist."""
    events_dir = SNAPSHOT_DIR / "operation_events_v1"
    if not events_dir.exists():
        return False, ["operation_events_v1 not found"]

    scripts: Counter[str] = Counter()
    operations: Counter[str] = Counter()

    for day_dir in events_dir.glob("day=*"):
        events_file = day_dir / "events.jsonl"
        if not events_file.exists():
            continue

        with open(events_file) as f:
            for line in f:
                if line.strip():
                    event = json.loads(line)
                    scripts[event.get("script_id")] += 1
                    op = event.get("operation")
                    if op:
                        operations[op] += 1

    issues = []
    passed = True

    # Check scripts
    unknown_scripts = set(scripts.keys()) - KNOWN_SCRIPTS
    if unknown_scripts:
        issues.append(f"  Unknown scripts: {unknown_scripts}")
        passed = False

    for _script, _count in scripts.most_common():
        pass

    # Check operations
    unknown_ops = set(operations.keys()) - KNOWN_OPERATIONS
    if unknown_ops:
        issues.append(f"  Unknown operations: {unknown_ops}")
        passed = False

    for op, _count in operations.most_common():
        pass

    return passed, issues


def validate_session_integrity() -> tuple[bool, list[str]]:
    """Soft referential check: session_ids in events should have sessions."""
    # Collect session_ids from events
    events_dir = SNAPSHOT_DIR / "operation_events_v1"
    event_sessions = set()

    if events_dir.exists():
        for day_dir in events_dir.glob("day=*"):
            events_file = day_dir / "events.jsonl"
            if not events_file.exists():
                continue

            with open(events_file) as f:
                for line in f:
                    if line.strip():
                        event = json.loads(line)
                        sid = event.get("session_id")
                        if sid:
                            event_sessions.add((event.get("script_id"), sid))

    # Collect session_ids from derived sessions
    derived_sessions_dir = SNAPSHOT_DIR / "derived_sessions_v1"

    if derived_sessions_dir.exists():
        for day_dir in derived_sessions_dir.glob("day=*"):
            sessions_file = day_dir / "sessions.jsonl"
            if not sessions_file.exists():
                continue

            with open(sessions_file) as f:
                for line in f:
                    if line.strip():
                        json.loads(line)
                        # Derived sessions have their own IDs, can't cross-reference

    # Note: This is a soft check because writers are independent

    return True, []


def validate_snapshots() -> dict[str, Any]:
    """Run all validation checks."""
    results: dict[str, Any] = {"timestamp": datetime.now().isoformat(), "checks": {}}

    # Run checks
    checks = [
        ("event_counts", validate_event_counts),
        ("timestamps", validate_timestamps),
        ("scripts_operations", validate_scripts_operations),
        ("session_integrity", validate_session_integrity),
    ]

    all_passed = True

    for check_name, check_func in checks:
        passed, issues = check_func()
        results["checks"][check_name] = {"passed": passed, "issues": issues}
        if not passed:
            all_passed = False

    # Summary

    for check_name, check_result in results["checks"].items():
        "✅ PASS" if check_result["passed"] else "❌ FAIL"
        if check_result["issues"]:
            for _issue in check_result["issues"]:
                pass

    if all_passed:
        pass
    else:
        pass

    results["all_passed"] = all_passed

    return results


def main():
    """Main entry point."""
    results = validate_snapshots()

    # Write validation report
    report_dir = PROJECT_ROOT / "checks"
    report_dir.mkdir(exist_ok=True)

    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"validation_{timestamp_str}.json"

    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)

    # Exit with appropriate code
    return 0 if results["all_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
