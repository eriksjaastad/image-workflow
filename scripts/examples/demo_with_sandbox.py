#!/usr/bin/env python3
"""Demo: Using Sandbox Mode for Safe Testing

This example demonstrates how to use SandboxConfig to safely test
workflow operations without polluting production data.

Key Features Demonstrated:
- Creating a SandboxConfig instance
- Validating and formatting project IDs
- Using sandbox paths for file operations
- Integrating with FileTracker
- Cleaning up test data

Usage:
    python scripts/examples/demo_with_sandbox.py
"""

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.file_tracker import FileTracker
from scripts.utils.sandbox_mode import SandboxConfig


def demo_sandbox_basics():
    """Demonstrate basic SandboxConfig usage."""
    # Create sandbox configuration
    sandbox = SandboxConfig(enabled=True)
    sandbox.print_banner()

    # Show configured paths

    # Demonstrate project ID validation
    test_ids = ["TEST-demo", "production-project", "test-lowercase"]
    for pid in test_ids:
        sandbox.validate_project_id(pid)

    # Demonstrate project ID formatting


def demo_file_operations():
    """Demonstrate file operations in sandbox mode."""
    sandbox = SandboxConfig(enabled=True)

    # Example: Create a test project manifest
    project_id = "TEST-demo-example"
    manifest_path = sandbox.projects_dir / f"{project_id}.project.json"

    # Write a simple test manifest
    test_manifest = {
        "projectId": project_id,
        "status": "test",
        "note": "This is sandbox test data - safe to delete",
    }

    import json

    manifest_path.write_text(json.dumps(test_manifest, indent=2), encoding="utf-8")

    # Verify marker file exists
    marker_exists = SandboxConfig.has_marker_file(sandbox.projects_dir)
    if marker_exists:
        sandbox.projects_dir / ".sandbox_marker"


def demo_filetracker_integration():
    """Demonstrate FileTracker integration with sandbox."""
    sandbox = SandboxConfig(enabled=True)

    # Create FileTracker with sandbox configuration
    tracker = FileTracker(script_name="demo_sandbox", sandbox_config=sandbox)

    # Log a test operation
    tracker.log_operation(
        operation="test",
        source_dir="demo_source",
        dest_dir="demo_dest",
        file_count=5,
        notes="This is a sandbox test operation",
    )


def demo_cleanup():
    """Demonstrate cleanup process."""


def main():
    """Run all demos."""
    try:
        demo_sandbox_basics()
        demo_file_operations()
        demo_filetracker_integration()
        demo_cleanup()

    except Exception:
        import traceback

        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
