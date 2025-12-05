"""
Pytest configuration for the image-workflow-scripts test suite.

Defines markers and auto-skip logic for environment-specific tests.
"""

import os

import pytest

# Detect CI environment (GitHub Actions sets CI=true)
IN_CI = os.environ.get("CI", "").lower() == "true"


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "local_only: Tests that require local data/environment (skip in CI)",
    )
    config.addinivalue_line(
        "markers",
        "selenium: Tests that require a browser/Selenium WebDriver (skip in CI)",
    )


def pytest_collection_modifyitems(config, items):
    """Auto-skip tests based on markers when running in CI."""
    if not IN_CI:
        return

    skip_local = pytest.mark.skip(reason="Skipped in CI: requires local data/environment")
    skip_selenium = pytest.mark.skip(reason="Skipped in CI: requires browser/Selenium")

    for item in items:
        if "local_only" in item.keywords:
            item.add_marker(skip_local)
        if "selenium" in item.keywords:
            item.add_marker(skip_selenium)
