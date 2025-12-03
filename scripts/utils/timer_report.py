#!/usr/bin/env python3
"""
Activity Timer Reporting Tool
=============================

Standalone reporting tool for activity timer data with comprehensive analytics.
Provides daily summaries, cross-script analysis, and productivity metrics.

USAGE:
------
Daily report:
  python scripts/utils/timer_report.py --daily
  python scripts/utils/timer_report.py --daily 20250924

Weekly report:
  python scripts/utils/timer_report.py --weekly

Cross-script analysis:
  python scripts/utils/timer_report.py --cross-script --days 30

Productivity metrics:
  python scripts/utils/timer_report.py --productivity

Clean old data:
  python scripts/utils/timer_report.py --cleanup 30

Live monitoring:
  python scripts/utils/timer_report.py --live

FEATURES:
---------
• Daily and weekly summaries
• Cross-script performance analysis
• Productivity metrics and trends
• Files per hour calculations
• Efficiency breakdowns
• Data cleanup utilities
• Live session monitoring
"""

import argparse
import json
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

from activity_timer import TimerReporter, cleanup_old_data


class AdvancedTimerReporter(TimerReporter):
    """Extended reporter with additional analytics"""

    def productivity_metrics(self, days: int = 7):
        """Calculate detailed productivity metrics"""
        totals = self.cross_script_totals(days)

        if not totals["script_totals"]:
            return

        # Overall metrics
        total_hours = totals["total_active_time"] / 3600
        if total_hours > 0:
            files_per_hour = totals["total_files_processed"] / total_hours
            totals["total_operations"] / total_hours

        # Script-specific metrics
        script_metrics = []

        for script, stats in totals["script_totals"].items():
            if stats["active_time"] > 0:
                files_per_hour = stats["files_processed"] / (
                    stats["active_time"] / 3600
                )
                efficiency = stats["active_time"] / stats["total_time"] * 100

                script_metrics.append(
                    {
                        "script": script,
                        "files_per_hour": files_per_hour,
                        "efficiency": efficiency,
                        "total_files": stats["files_processed"],
                        "active_hours": stats["active_time"] / 3600,
                    }
                )

        # Sort by files per hour
        script_metrics.sort(key=lambda x: x["files_per_hour"], reverse=True)

        for _i, _metrics in enumerate(script_metrics, 1):
            pass

    def trend_analysis(self, days: int = 14):
        """Analyze productivity trends over time"""
        daily_data = []

        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
            summary = self.daily_summary(date)
            if summary:
                daily_data.append(
                    {
                        "date": date,
                        "active_time": summary["total_active_time"],
                        "efficiency": summary["efficiency"],
                        "files_processed": summary["total_files_processed"],
                    }
                )

        if not daily_data:
            return

        # Calculate averages
        sum(d["active_time"] for d in daily_data) / len(daily_data) / 3600
        sum(d["efficiency"] for d in daily_data) / len(daily_data)
        sum(d["files_processed"] for d in daily_data) / len(daily_data)

        # Show recent days
        for data in daily_data[:7]:  # Last 7 days
            datetime.strptime(data["date"], "%Y%m%d").strftime("%m/%d")
            data["active_time"] / 3600

    def live_monitoring(self):
        """Live monitoring of current sessions"""
        try:
            while True:
                # Look for active session files
                session_files = list(self.data_dir.glob("session_*.json"))
                active_sessions = []

                current_time = time.time()

                for session_file in session_files:
                    try:
                        with open(session_file) as f:
                            session_data = json.load(f)

                        # Check if session is recent (within last 30 minutes)
                        if session_data.get("start_time", 0) > current_time - 1800:
                            active_sessions.append(session_data)
                    except (json.JSONDecodeError, KeyError):
                        continue

                # Clear screen and show active sessions

                if active_sessions:
                    for session in active_sessions:
                        session.get("script_name", "unknown")
                        start_time = session.get("start_time", 0)
                        current_time - start_time

                else:
                    pass

                time.sleep(5)  # Update every 5 seconds

        except KeyboardInterrupt:
            pass

    def export_data(self, days: int = 30, format: str = "json"):
        """Export timer data for external analysis"""
        export_data = {
            "export_date": datetime.now().isoformat(),
            "days_included": days,
            "daily_summaries": [],
            "cross_script_totals": self.cross_script_totals(days),
        }

        # Collect daily summaries
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
            summary = self.daily_summary(date)
            if summary:
                export_data["daily_summaries"].append(summary)

        # Export to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = Path(f"timer_export_{timestamp}.{format}")

        if format == "json":
            with open(export_file, "w") as f:
                json.dump(export_data, f, indent=2)
        else:
            return


def main():
    parser = argparse.ArgumentParser(description="Activity Timer Reporting Tool")

    # Report types
    parser.add_argument(
        "--daily", nargs="?", const=None, help="Show daily report (optional: YYYYMMDD)"
    )
    parser.add_argument("--weekly", action="store_true", help="Show weekly report")
    parser.add_argument(
        "--cross-script", action="store_true", help="Show cross-script analysis"
    )
    parser.add_argument(
        "--productivity", action="store_true", help="Show productivity metrics"
    )
    parser.add_argument(
        "--trends", action="store_true", help="Show productivity trends"
    )
    parser.add_argument("--live", action="store_true", help="Live session monitoring")

    # Options
    parser.add_argument(
        "--days", type=int, default=7, help="Number of days for analysis (default: 7)"
    )
    parser.add_argument("--cleanup", type=int, help="Clean up data older than N days")
    parser.add_argument("--export", choices=["json"], help="Export data format")

    args = parser.parse_args()

    # Create reporter
    reporter = AdvancedTimerReporter()

    # Handle cleanup first
    if args.cleanup:
        cleanup_old_data(args.cleanup)
        return

    # Handle export
    if args.export:
        reporter.export_data(args.days, args.export)
        return

    # Handle live monitoring
    if args.live:
        reporter.live_monitoring()
        return

    # Handle reports
    if args.daily is not None:
        reporter.print_daily_summary(args.daily)
    elif args.weekly:
        reporter.print_cross_script_summary(7)
    elif args.cross_script:
        reporter.print_cross_script_summary(args.days)
    elif args.productivity:
        reporter.productivity_metrics(args.days)
    elif args.trends:
        reporter.trend_analysis(args.days)
    else:
        # Default: show today's summary
        reporter.print_daily_summary()

        # Also show quick productivity summary
        reporter.productivity_metrics(7)


if __name__ == "__main__":
    main()
