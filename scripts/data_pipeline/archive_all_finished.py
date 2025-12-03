#!/usr/bin/env python3
"""
Archive All Finished Projects
==============================
Convenience script to archive all finished projects at once.

This converts raw logs for finished projects into pre-aggregated bins,
dramatically speeding up dashboard load times.
"""

import json
import subprocess
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))


def main():
    # Find all project manifests
    projects_dir = project_root / "data" / "projects"
    if not projects_dir.exists():
        sys.exit(1)

    manifests = list(projects_dir.glob("*.project.json"))
    if not manifests:
        sys.exit(1)

    # First: Generate bins for all historical data
    result = subprocess.run(
        [sys.executable, "scripts/data_pipeline/aggregate_to_15m.py", "--days", "180"],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        sys.exit(1)

    # Find finished projects
    finished_projects = []
    active_projects = []

    for manifest_path in manifests:
        try:
            with open(manifest_path) as f:
                manifest = json.load(f)

            project_id = manifest.get("projectId")
            status = manifest.get("status")
            title = manifest.get("title", project_id)

            if not project_id:
                continue

            if status in {"finished", "archived"}:
                finished_projects.append((project_id, title, manifest))
            else:
                active_projects.append((project_id, title, status))
        except Exception:
            continue

    if not finished_projects:
        sys.exit(0)

    # Step 2: Archive each finished project

    archived_count = 0
    failed = []

    for project_id, title, manifest in finished_projects:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/data_pipeline/archive_project_bins.py",
                project_id,
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            archived_count += 1
            # Show key stats from output
            if "bins" in result.stdout:
                for line in result.stdout.split("\n"):
                    if (
                        "bins" in line.lower()
                        or "files" in line.lower()
                        or "hours" in line.lower()
                    ):
                        pass
        else:
            failed.append(project_id)
            if result.stderr:
                pass

    # Summary
    if failed:
        for _pid in failed:
            pass

    # Next steps


if __name__ == "__main__":
    main()
