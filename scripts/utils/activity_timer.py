#!/usr/bin/env python3
"""
Universal Activity Timer System for Image Processing Scripts
============================================================

Tracks active work time across all workflow scripts with intelligent idle detection.
Provides cross-script reporting and detailed productivity metrics.

FEATURES:
---------
• 1-minute idle detection (configurable)
• Manual batch markers for accurate productivity metrics
• Cross-script time totals and per-script breakdowns
• Real-time activity monitoring
• Persistent session storage
• Detailed operation tracking (files processed, operations performed)
• Integration with existing FileTracker system

USAGE:
------
In any script:
    from utils.activity_timer import ActivityTimer

    timer = ActivityTimer("script_name")
    timer.start_session()

    # Mark manual batches
    timer.mark_batch("Processing batch 1")

    # Track operations
    timer.log_operation("crop", file_count=3)
    timer.log_operation("delete", file_count=1)

    # End session
    timer.end_session()

REPORTING:
----------
    from utils.activity_timer import TimerReporter

    reporter = TimerReporter()
    reporter.daily_summary()
    reporter.script_breakdown()
    reporter.productivity_metrics()
"""

import json
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


@dataclass
class ActivitySession:
    """Represents a single activity session"""

    script_name: str
    session_id: str
    start_time: float
    end_time: float | None = None
    active_time: float = 0.0
    idle_time: float = 0.0
    last_activity: float = 0.0
    batches: list[dict[str, Any]] = None
    operations: list[dict[str, Any]] = None

    def __post_init__(self):
        if self.batches is None:
            self.batches = []
        if self.operations is None:
            self.operations = []


class ActivityTimer:
    """Activity timer with intelligent idle detection and cross-script reporting"""

    def __init__(self, script_name: str, idle_threshold: int = 60):  # 1 minute default
        self.script_name = script_name
        self.idle_threshold = idle_threshold  # seconds
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Timer state
        self.session_start = None
        self.last_activity = None
        self.active_time = 0.0
        self.idle_time = 0.0
        self.is_active = False
        self.current_batch = None

        # Data storage
        self.data_dir = Path(__file__).parent.parent.parent / "data" / "timer_data"
        self.data_dir.mkdir(exist_ok=True)
        self.session_file = self.data_dir / f"session_{self.session_id}.json"
        self.daily_file = (
            self.data_dir / f"daily_{datetime.now().strftime('%Y%m%d')}.json"
        )

        # Session tracking
        self.current_session = ActivitySession(
            script_name=script_name, session_id=self.session_id, start_time=time.time()
        )

        # Background monitoring
        self._monitor_thread = None
        self._stop_monitoring = False

    def start_session(self):
        """Start a new activity session"""
        self.session_start = time.time()
        self.last_activity = self.session_start
        self.is_active = True


        # Start background monitoring
        self._start_monitoring()

        # Log session start
        self._save_session_data()

    def mark_activity(self):
        """Mark user activity (call this on user interactions)"""
        current_time = time.time()

        if self.last_activity and self.is_active:
            # Add time since last activity to active time
            time_diff = current_time - self.last_activity
            if time_diff <= self.idle_threshold:
                self.active_time += time_diff
            else:
                # Was idle, add idle time
                self.idle_time += time_diff

        self.last_activity = current_time
        self.is_active = True

    def mark_batch(self, batch_name: str, description: str = ""):
        """Mark the start of a manual batch"""
        self.mark_activity()

        batch_data = {
            "name": batch_name,
            "description": description,
            "start_time": time.time(),
            "timestamp": datetime.now().isoformat(),
        }

        self.current_session.batches.append(batch_data)
        self.current_batch = batch_name

        self._save_session_data()

    def end_batch(self, summary: str = ""):
        """End the current batch"""
        if self.current_session.batches and self.current_batch:
            # Update the last batch with end time
            last_batch = self.current_session.batches[-1]
            if last_batch["name"] == self.current_batch:
                last_batch["end_time"] = time.time()
                last_batch["duration"] = (
                    last_batch["end_time"] - last_batch["start_time"]
                )
                last_batch["summary"] = summary


        self.current_batch = None
        self._save_session_data()

    def log_operation(
        self, operation_type: str, file_count: int | None = None, details: str = ""
    ):
        """Log a specific operation (crop, delete, move, etc.)"""
        self.mark_activity()

        operation_data = {
            "type": operation_type,
            "file_count": file_count,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "batch": self.current_batch,
        }

        self.current_session.operations.append(operation_data)
        self._save_session_data()

    def get_current_stats(self) -> dict[str, Any]:
        """Get current session statistics"""
        current_time = time.time()
        total_time = current_time - self.session_start if self.session_start else 0

        # Update active time if currently active
        if self.is_active and self.last_activity:
            time_since_activity = current_time - self.last_activity
            if time_since_activity <= self.idle_threshold:
                self.active_time += time_since_activity
                self.last_activity = current_time
            else:
                self.is_active = False

        # Ensure active time never exceeds total time
        active_time_capped = min(self.active_time, total_time)

        return {
            "script": self.script_name,
            "session_id": self.session_id,
            "total_time": total_time,
            "active_time": active_time_capped,
            "idle_time": self.idle_time,
            "efficiency": (active_time_capped / total_time * 100)
            if total_time > 0
            else 0,
            "batches_completed": len(
                [b for b in self.current_session.batches if "end_time" in b]
            ),
            "total_operations": len(self.current_session.operations),
            "files_processed": sum(
                op.get("file_count", 0)
                for op in self.current_session.operations
                if op.get("file_count")
            ),
            "is_active": self.is_active,
        }

    def print_live_stats(self):
        """Print current session statistics"""
        self.get_current_stats()


    def end_session(self):
        """End the current activity session"""
        if not self.session_start:
            return

        # Stop monitoring
        self._stop_monitoring = True
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1)

        # Final activity update
        current_time = time.time()
        if self.last_activity and self.is_active:
            time_diff = current_time - self.last_activity
            if time_diff <= self.idle_threshold:
                self.active_time += time_diff
            else:
                self.idle_time += time_diff

        # Update session
        self.current_session.end_time = current_time
        self.current_session.active_time = self.active_time
        self.current_session.idle_time = self.idle_time
        self.current_session.last_activity = self.last_activity

        # Save final session data
        self._save_session_data()
        self._save_daily_summary()

        # Print final stats
        self.get_current_stats()

    def _start_monitoring(self):
        """Start background monitoring thread"""

        def monitor():
            while not self._stop_monitoring:
                time.sleep(30)  # Check every 30 seconds
                if self.last_activity and self.is_active:
                    time_since_activity = time.time() - self.last_activity
                    if time_since_activity > self.idle_threshold:
                        self.is_active = False
                        self.idle_time += time_since_activity

        self._monitor_thread = threading.Thread(target=monitor, daemon=True)
        self._monitor_thread.start()

    def _save_session_data(self):
        """Save current session data to file"""
        try:
            with open(self.session_file, "w") as f:
                json.dump(asdict(self.current_session), f, indent=2)
        except Exception:
            pass

    def _save_daily_summary(self):
        """Save session to daily summary file"""
        try:
            daily_data = []
            if self.daily_file.exists():
                with open(self.daily_file) as f:
                    daily_data = json.load(f)

            daily_data.append(asdict(self.current_session))

            with open(self.daily_file, "w") as f:
                json.dump(daily_data, f, indent=2)
        except Exception:
            pass


class TimerReporter:
    """Reporting system for activity timer data"""

    def __init__(self):
        self.data_dir = Path(__file__).parent.parent.parent / "data" / "timer_data"
        self.data_dir.mkdir(exist_ok=True)

    def daily_summary(self, date: str | None = None) -> dict[str, Any]:
        """Get daily summary for specified date (default: today)"""
        if not date:
            date = datetime.now().strftime("%Y%m%d")

        daily_file = self.data_dir / f"daily_{date}.json"

        if not daily_file.exists():
            return {}

        try:
            with open(daily_file) as f:
                sessions = json.load(f)

            # Calculate totals
            total_active = sum(s.get("active_time", 0) for s in sessions)
            total_time = sum(
                (s.get("end_time", time.time()) - s.get("start_time", 0))
                for s in sessions
            )
            total_files = sum(len(s.get("operations", [])) for s in sessions)
            total_operations = sum(
                sum(op.get("file_count", 0) for op in s.get("operations", []))
                for s in sessions
            )

            # Script breakdown
            script_stats = {}
            for session in sessions:
                script = session.get("script_name", "unknown")
                if script not in script_stats:
                    script_stats[script] = {
                        "active_time": 0,
                        "total_time": 0,
                        "sessions": 0,
                        "files_processed": 0,
                        "operations": 0,
                    }

                script_stats[script]["active_time"] += session.get("active_time", 0)
                script_stats[script]["total_time"] += session.get(
                    "end_time", time.time()
                ) - session.get("start_time", 0)
                script_stats[script]["sessions"] += 1
                script_stats[script]["operations"] += len(session.get("operations", []))
                script_stats[script]["files_processed"] += sum(
                    op.get("file_count", 0) for op in session.get("operations", [])
                )

            summary = {
                "date": date,
                "total_active_time": total_active,
                "total_session_time": total_time,
                "efficiency": (total_active / total_time * 100)
                if total_time > 0
                else 0,
                "total_files_processed": total_operations,
                "total_operations": total_files,
                "script_breakdown": script_stats,
                "session_count": len(sessions),
            }

            return summary

        except Exception:
            return {}

    def print_daily_summary(self, date: str | None = None):
        """Print formatted daily summary"""
        summary = self.daily_summary(date)

        if not summary:
            return


        for _script, stats in summary["script_breakdown"].items():
            (
                (stats["active_time"] / stats["total_time"] * 100)
                if stats["total_time"] > 0
                else 0
            )

    def cross_script_totals(self, days: int = 7) -> dict[str, Any]:
        """Get cross-script totals for the last N days"""
        totals = {
            "total_active_time": 0,
            "total_session_time": 0,
            "total_files_processed": 0,
            "total_operations": 0,
            "script_totals": {},
            "daily_breakdown": [],
        }

        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
            daily = self.daily_summary(date)

            if daily:
                totals["total_active_time"] += daily["total_active_time"]
                totals["total_session_time"] += daily["total_session_time"]
                totals["total_files_processed"] += daily["total_files_processed"]
                totals["total_operations"] += daily["total_operations"]
                totals["daily_breakdown"].append(daily)

                # Aggregate script totals
                for script, stats in daily["script_breakdown"].items():
                    if script not in totals["script_totals"]:
                        totals["script_totals"][script] = {
                            "active_time": 0,
                            "total_time": 0,
                            "files_processed": 0,
                            "operations": 0,
                            "sessions": 0,
                        }

                    for key in [
                        "active_time",
                        "total_time",
                        "files_processed",
                        "operations",
                        "sessions",
                    ]:
                        totals["script_totals"][script][key] += stats[key]

        return totals

    def print_cross_script_summary(self, days: int = 7):
        """Print cross-script summary for the last N days"""
        totals = self.cross_script_totals(days)


        if totals["total_session_time"] > 0:
            (
                totals["total_active_time"] / totals["total_session_time"] * 100
            )


        for _script, stats in totals["script_totals"].items():
            (
                (stats["active_time"] / stats["total_time"] * 100)
                if stats["total_time"] > 0
                else 0
            )
            (
                (stats["files_processed"] / (stats["active_time"] / 3600))
                if stats["active_time"] > 0
                else 0
            )



# Convenience functions for quick reporting
def daily_report(date: str | None = None):
    """Quick daily report"""
    reporter = TimerReporter()
    reporter.print_daily_summary(date)


def weekly_report():
    """Quick weekly report"""
    reporter = TimerReporter()
    reporter.print_cross_script_summary(7)


def cleanup_old_data(days_to_keep: int = 30):
    """Clean up old timer data files"""
    data_dir = Path(__file__).parent.parent.parent / "data" / "timer_data"
    if not data_dir.exists():
        return

    cutoff_date = datetime.now() - timedelta(days=days_to_keep)

    for file in data_dir.glob("*.json"):
        if file.stem.startswith(("daily_", "session_")):
            try:
                # Extract date from filename
                date_str = file.stem.split("_")[1][:8]  # YYYYMMDD
                file_date = datetime.strptime(date_str, "%Y%m%d")

                if file_date < cutoff_date:
                    file.unlink()

            except (ValueError, IndexError):
                continue  # Skip files that don't match expected format


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Activity Timer Reporting")
    parser.add_argument("--daily", help="Show daily report for date (YYYYMMDD)")
    parser.add_argument("--weekly", action="store_true", help="Show weekly report")
    parser.add_argument("--cleanup", type=int, help="Clean up data older than N days")

    args = parser.parse_args()

    if args.daily:
        daily_report(args.daily)
    elif args.weekly:
        weekly_report()
    elif args.cleanup:
        cleanup_old_data(args.cleanup)
    else:
        # Default: show today's report
        daily_report()
