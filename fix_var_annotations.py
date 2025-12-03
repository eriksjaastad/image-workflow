#!/usr/bin/env python3
"""
Script to automatically fix [var-annotated] mypy errors by adding type annotations.
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import Any


def run_mypy_get_var_annotated_errors() -> list[str]:
    """Get all [var-annotated] errors from mypy."""
    try:
        result = subprocess.run(
            ["mypy", "scripts/", "--show-error-codes"],
            capture_output=True,
            text=True,
            cwd="/Users/eriksjaastad/projects/image-workflow",
            check=False,
        )
        lines = result.stdout.split("\n") + result.stderr.split("\n")
        var_annotated_lines = [line for line in lines if "[var-annotated]" in line]
        return var_annotated_lines
    except Exception as e:
        print(f"Error running mypy: {e}")
        return []


def parse_var_annotated_error(line: str) -> tuple[str, int, str]:
    """Parse a [var-annotated] error line to extract file, line number, and variable name."""
    # Format: scripts/file.py:123: error: Need type annotation for "variable_name" [var-annotated]
    match = re.match(r'([^:]+):(\d+): error: Need type annotation for "([^"]+)"', line)
    if match:
        file_path, line_num, var_name = match.groups()
        return file_path, int(line_num), var_name
    return "", 0, ""


def analyze_variable_usage(file_path: str, line_num: int, var_name: str) -> str:
    """Analyze how a variable is used to determine its type annotation."""
    try:
        with open(file_path) as f:
            lines = f.readlines()

        if line_num - 1 >= len(lines):
            return "list[Any]"  # fallback

        # Get the line with the variable declaration
        line = lines[line_num - 1].strip()

        # Common patterns
        if "defaultdict(int)" in line:
            return "dict[str, int]"
        if "defaultdict(list)" in line:
            return "dict[str, list[Any]]"
        if "defaultdict(set)" in line:
            return "dict[str, set[Any]]"
        if "defaultdict(dict)" in line:
            return "dict[str, dict[str, Any]]"
        if "= {}" in line:
            return "dict[str, Any]"
        if "= []" in line:
            return "list[Any]"
        if "= set()" in line:
            return "set[Any]"

        # Look at usage patterns in nearby lines
        start_line = max(0, line_num - 10)
        end_line = min(len(lines), line_num + 20)

        nearby_lines = lines[start_line:end_line]

        # Check for append operations (suggests list)
        append_pattern = re.compile(rf"{re.escape(var_name)}\.append\(")
        if any(append_pattern.search(l) for l in nearby_lines):
            return "list[Any]"

        # Check for dict access patterns
        dict_access_pattern = re.compile(rf"{re.escape(var_name)}\[[^\]]+\]")
        dict_assign_pattern = re.compile(rf"{re.escape(var_name)}\[[^\]]+\]\s*=")
        if any(dict_assign_pattern.search(l) for l in nearby_lines):
            return "dict[str, Any]"

        # Check for increment operations (suggests dict with int values)
        increment_pattern = re.compile(rf"{re.escape(var_name)}\[[^\]]+\]\s*\+=")
        if any(increment_pattern.search(l) for l in nearby_lines):
            return "dict[str, int]"

        # Default fallback
        return "dict[str, Any]"

    except Exception as e:
        print(f"Error analyzing {file_path}:{line_num}: {e}")
        return "dict[str, Any]"  # fallback


def fix_variable_annotation(
    file_path: str, line_num: int, var_name: str, annotation: str
):
    """Fix a variable annotation in the file."""
    try:
        with open(file_path) as f:
            lines = f.readlines()

        if line_num - 1 >= len(lines):
            return False

        line = lines[line_num - 1]
        # Look for pattern: variable_name = value
        pattern = rf"(\s*)({re.escape(var_name)}\s*=\s*.+)"
        match = re.search(pattern, line)

        if match:
            indent, assignment = match.groups()
            new_line = f"{indent}{var_name}: {annotation} = {assignment.split('=', 1)[1].strip()}\n"

            lines[line_num - 1] = new_line

            with open(file_path, "w") as f:
                f.writelines(lines)

            print(
                f"Fixed {file_path}:{line_num} - added {annotation} annotation to {var_name}"
            )
            return True
        print(f"Could not find variable assignment pattern in {file_path}:{line_num}")
        return False

    except Exception as e:
        print(f"Error fixing {file_path}:{line_num}: {e}")
        return False


def main():
    """Main function to fix all [var-annotated] errors."""
    print("Getting current [var-annotated] errors...")

    error_lines = run_mypy_get_var_annotated_errors()
    print(f"Found {len(error_lines)} [var-annotated] errors")

    fixed_count = 0

    for line in error_lines:
        file_path, line_num, var_name = parse_var_annotated_error(line)
        if not file_path:
            continue

        print(f"\nProcessing {file_path}:{line_num} - variable '{var_name}'")

        # Analyze the variable usage to determine type
        annotation = analyze_variable_usage(file_path, line_num, var_name)
        print(f"  Suggested annotation: {annotation}")

        # Fix the annotation
        if fix_variable_annotation(file_path, line_num, var_name, annotation):
            fixed_count += 1

    print(f"\nFixed {fixed_count} out of {len(error_lines)} [var-annotated] errors")

    # Run mypy again to verify
    print("\nRunning mypy again to check remaining errors...")
    result = subprocess.run(
        ["mypy", "scripts/", "--show-error-codes"],
        capture_output=True,
        text=True,
        cwd="/Users/eriksjaastad/projects/image-workflow",
        check=False,
    )

    remaining_var_annotated = len(
        [line for line in result.stdout.split("\n") if "[var-annotated]" in line]
    )
    print(f"Remaining [var-annotated] errors: {remaining_var_annotated}")


if __name__ == "__main__":
    main()
