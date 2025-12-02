#!/usr/bin/env python3
"""
Query Snapshots with DuckDB
============================
Provides a SQL interface to query snapshot data using DuckDB.

DuckDB can query JSONL files directly without importing to a database.

Usage:
    # Interactive mode
    python scripts/query_snapshots_duckdb.py

    # Execute query
    python scripts/query_snapshots_duckdb.py --query "SELECT script_id, COUNT(*) FROM events GROUP BY script_id"

    # Export to CSV
    python scripts/query_snapshots_duckdb.py --query "..." --output results.csv

Requirements:
    pip install duckdb

Note: This script requires duckdb to be installed. Install with:
    pip install duckdb
"""

import argparse
import sys
from pathlib import Path

try:
    import duckdb
except ImportError:
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = PROJECT_ROOT / "snapshot"


def create_views(con: duckdb.DuckDBPyConnection) -> None:
    """Create views for all snapshot datasets."""
    # Operation events view
    events_pattern = str(
        SNAPSHOT_DIR / "operation_events_v1" / "day=*" / "events.jsonl"
    )
    con.execute(f"""
        CREATE OR REPLACE VIEW events AS
        SELECT * FROM read_json_auto('{events_pattern}', union_by_name=true)
    """)

    # Derived sessions view
    derived_sessions_pattern = str(
        SNAPSHOT_DIR / "derived_sessions_v1" / "day=*" / "sessions.jsonl"
    )
    con.execute(f"""
        CREATE OR REPLACE VIEW derived_sessions AS
        SELECT * FROM read_json_auto('{derived_sessions_pattern}', union_by_name=true)
    """)

    # Legacy timer sessions view
    timer_sessions_pattern = str(
        SNAPSHOT_DIR / "timer_sessions_v1" / "day=*" / "sessions.jsonl"
    )
    con.execute(f"""
        CREATE OR REPLACE VIEW timer_sessions AS
        SELECT * FROM read_json_auto('{timer_sessions_pattern}', union_by_name=true)
    """)

    # Progress snapshots view
    progress_pattern = str(
        SNAPSHOT_DIR / "progress_snapshots_v1" / "day=*" / "snapshots.jsonl"
    )
    con.execute(f"""
        CREATE OR REPLACE VIEW progress_snapshots AS
        SELECT * FROM read_json_auto('{progress_pattern}', union_by_name=true)
    """)

    # Projects view
    projects_file = str(SNAPSHOT_DIR / "projects_v1" / "projects.jsonl")
    con.execute(f"""
        CREATE OR REPLACE VIEW projects AS
        SELECT * FROM read_json_auto('{projects_file}', union_by_name=true)
    """)

    # Daily aggregates view
    aggregates_pattern = str(
        SNAPSHOT_DIR / "daily_aggregates_v1" / "day=*" / "aggregate.json"
    )
    con.execute(f"""
        CREATE OR REPLACE VIEW daily_aggregates AS
        SELECT * FROM read_json_auto('{aggregates_pattern}', union_by_name=true)
    """)


def show_schema(con: duckdb.DuckDBPyConnection) -> None:
    """Show available views and their schemas."""
    views = [
        "events",
        "derived_sessions",
        "timer_sessions",
        "progress_snapshots",
        "projects",
        "daily_aggregates",
    ]

    for view in views:
        try:
            result = con.execute(f"DESCRIBE {view}").fetchall()
            for _col_name, _col_type, _null, _key, _default, _extra in result:
                pass
        except Exception:
            pass


def execute_query(
    con: duckdb.DuckDBPyConnection, query: str, output_file: str | None = None
) -> None:
    """Execute a SQL query and display/save results."""
    try:
        result = con.execute(query)

        if output_file:
            # Export to CSV
            con.execute(f"COPY ({query}) TO '{output_file}' (HEADER, DELIMITER ',')")
        else:
            # Display results
            rows = result.fetchall()
            [desc[0] for desc in result.description]


            for _row in rows:
                pass


    except Exception:
        pass


def interactive_mode(con: duckdb.DuckDBPyConnection) -> None:
    """Run in interactive SQL mode."""
    while True:
        try:
            query = input("duckdb> ").strip()

            if not query:
                continue

            if query.lower() in [".quit", "exit", "quit"]:
                break

            if query.lower() == ".tables":
                result = con.execute("SHOW TABLES").fetchall()
                for _row in result:
                    pass
                continue

            if query.lower().startswith(".schema"):
                parts = query.split()
                view_name = parts[1] if len(parts) > 1 else None

                if view_name:
                    result = con.execute(f"DESCRIBE {view_name}").fetchall()
                    for _col_name, _col_type, _null, _key, _default, _extra in result:
                        pass
                else:
                    show_schema(con)
                continue

            # Execute query
            result = con.execute(query)
            rows = result.fetchall()
            [desc[0] for desc in result.description]


            for _row in rows[:100]:  # Limit to first 100 rows
                pass

            if len(rows) > 100:
                pass


        except KeyboardInterrupt:
            break
        except Exception:
            pass


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Query snapshot data using DuckDB SQL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python scripts/query_snapshots_duckdb.py
  
  # Execute query
  python scripts/query_snapshots_duckdb.py --query "SELECT script_id, COUNT(*) FROM events GROUP BY script_id ORDER BY COUNT(*) DESC"
  
  # Export to CSV
  python scripts/query_snapshots_duckdb.py --query "SELECT * FROM projects" --output projects.csv
  
  # Show schema
  python scripts/query_snapshots_duckdb.py --show-schema

Sample Queries:
  # Top scripts by event count
  SELECT script_id, COUNT(*) as count FROM events GROUP BY script_id ORDER BY count DESC LIMIT 10
  
  # Daily file processing totals
  SELECT day, SUM(files_processed) as total_files FROM derived_sessions GROUP BY day ORDER BY day
  
  # Active projects
  SELECT project_id, title, status, initial_images FROM projects WHERE status = 'active'
  
  # Operations by type
  SELECT operation, COUNT(*) as count FROM events WHERE operation IS NOT NULL GROUP BY operation ORDER BY count DESC
        """,
    )

    parser.add_argument("--query", help="SQL query to execute")
    parser.add_argument("--output", help="Output CSV file")
    parser.add_argument(
        "--show-schema", action="store_true", help="Show schema for all views"
    )

    args = parser.parse_args()

    # Initialize DuckDB
    con = duckdb.connect(database=":memory:")

    # Create views
    try:
        create_views(con)
    except Exception:
        sys.exit(1)

    # Execute based on arguments
    if args.show_schema:
        show_schema(con)
    elif args.query:
        execute_query(con, args.query, args.output)
    else:
        interactive_mode(con)


if __name__ == "__main__":
    main()
