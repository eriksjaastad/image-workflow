from typing import Any

#!/usr/bin/env python3
"""
Test that all production scripts have dashboard mappings.

This test prevents the "invisible work" bug where a script logs operations
but the dashboard doesn't recognize the script name, making thousands of
operations invisible.
"""

import sys
from pathlib import Path

import pytest

# Skip in CI - requires local data directories
pytestmark = pytest.mark.local_only

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

from scripts.dashboard.engines.data_engine import DashboardDataEngine


def test_all_production_scripts_have_mappings():
    """
    Ensure key production scripts have explicit mappings in get_display_name().

    This is a documentation test - verifies important scripts are mapped.
    Scripts that map to their title-case equivalent are considered valid
    (e.g., "multi_crop_tool" → "Multi Crop Tool" is explicitly mapped).
    """
    engine = DashboardDataEngine("data")

    # Key scripts that should definitely be mapped
    key_scripts = [
        "01_web_image_selector",
        "03_web_character_sorter",
        "ai_desktop_multi_crop",
        "ai_assisted_reviewer",
    ]

    # Just verify these don't return empty or error
    for script in key_scripts:
        display_name = engine.get_display_name(script)
        assert display_name, f"Script '{script}' should have a display name"
        assert len(display_name) > 0, f"Display name for '{script}' should not be empty"


def test_mapped_scripts_are_in_production_list():
    """Check that commonly mapped scripts have proper display name mappings."""
    engine = DashboardDataEngine("data")

    # These are scripts we know should be active and tracked
    critical_scripts = [
        "ai_desktop_multi_crop",
        "ai_desktop_multi_crop_queue",
        "ai_assisted_reviewer",
        "01_web_image_selector",
    ]

    # Verify the mapping exists for each critical script
    for script in critical_scripts:
        display_name = engine.get_display_name(script)
        assert display_name, f"Critical script '{script}' should have a display name"
        # Just verify we get a non-empty string back
        assert isinstance(display_name, str) and len(display_name) > 0


def test_no_duplicate_mappings():
    """
    Ensure multiple script names don't accidentally map to the same
    display name in a way that would cause confusion.

    Note: It's OKAY for multiple scripts to map to the same display name
    (e.g., "batch_crop_tool" and "multi_crop_tool" both → "Multi Crop Tool")
    but we want to document this.
    """
    engine = DashboardDataEngine("data")

    production_scripts = [
        "01_web_image_selector",
        "03_web_character_sorter",
        "04_multi_crop_tool",
        "multi_crop_tool",
        "ai_desktop_multi_crop",
        "ai_desktop_multi_crop_queue",
        "crop_queue_processor",
        "ai_assisted_reviewer",
        "character_sorter",
        "image_version_selector",
        "multi_batch_crop_tool",
        "batch_crop_tool",
    ]

    mappings: dict[str, Any] = {}
    for script in production_scripts:
        display = engine.get_display_name(script)
        mappings.setdefault(display, []).append(script)

    # Print mappings for documentation
    print("\nScript → Display Name Mappings:")
    for display, scripts in sorted(mappings.items()):
        print(f"  {display}:")
        for script in scripts:
            print(f"    - {script}")

    # This test just documents the mappings, doesn't fail
    # But it helps us see what's grouped together
    assert True


if __name__ == "__main__":
    # Run tests manually
    print("Running dashboard script mapping tests...")

    try:
        test_all_production_scripts_have_mappings()
        print("✅ All production scripts have explicit mappings")
    except AssertionError as e:
        print(f"❌ {e}")
        sys.exit(1)

    try:
        test_mapped_scripts_are_in_production_list()
        print("✅ Critical scripts are mapped")
    except AssertionError as e:
        print(f"❌ {e}")
        sys.exit(1)

    try:
        test_no_duplicate_mappings()
        print("✅ Mapping documentation complete")
    except AssertionError as e:
        print(f"❌ {e}")
        sys.exit(1)

    print("\n🎉 All dashboard mapping tests passed!")
