#!/usr/bin/env python3
"""Project Startup Script.

Creates a new project manifest with all required fields, proper timestamps,
and automatic image counting.

Usage:
    # Interactive mode (prompts for all inputs)
    python scripts/00_start_project.py

    # Recommended: Auto-derive project ID from directory name (for automation/CI/CD)
    python scripts/00_start_project.py sandbox/TEST-mojo1

    # Alternative: Explicit flags for special cases where ID ≠ directory name
    python scripts/00_start_project.py --project-id mojo3 --content-dir ../mojo3

When to use each approach:
    - INTERACTIVE (no args):
      * Manual, one-off project setup
      * When you want to customize the project title
      * First time setting up a project

    - POSITIONAL ARG (recommended):
      * Sandbox testing with TEST- prefixed directories
      * Automation scripts and CI/CD pipelines
      * Batch processing multiple projects
      * Keeps project ID and directory in sync automatically

    - EXPLICIT FLAGS (special cases):
      * Legacy scripts that need specific naming
      * When project ID differs from directory name by design
      * Advanced scenarios with complex directory structures
      * Backward compatibility with existing integrations

Features:
- Automatically generates UTC timestamps with Z suffix
- Counts PNG images in content directory
- Creates manifest with all required fields
- Backs up existing manifests before overwriting
- Validates project directory structure
"""

import argparse
import json
import logging
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

# Ensure project root on import path for shared utilities
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

try:
    from scripts.file_tracker import FileTracker
    from scripts.utils.companion_file_utils import extract_timestamp_from_filename
    from scripts.utils.sandbox_mode import SandboxConfig
except ImportError as e:
    logger.warning("Import failed (some features disabled): %s", e)
    FileTracker = None  # type: ignore
    SandboxConfig = None  # type: ignore

    def extract_timestamp_from_filename(filename: str):  # type: ignore
        import re as _re

        m = _re.match(r"^(\d{8}_\d{6})", filename)
        return m.group(1) if m else None


def count_images(directory: Path) -> int:
    """Count PNG images in a directory (recursive to match actual project structure)."""
    if not directory.exists():
        return 0
    return len(list(directory.rglob("*.png")))


def count_groups_by_timestamp_stem(directory: Path) -> int:
    """Count unique timestamp stems (YYYYMMDD_HHMMSS) across all PNGs in directory tree."""
    if not directory.exists():
        return 0
    stems = set()
    for p in directory.rglob("*.png"):
        ts = extract_timestamp_from_filename(p.name)
        if ts:
            stems.add(ts)
    return len(stems)


def get_utc_timestamp() -> str:
    """Get current UTC timestamp in ISO format with Z suffix."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def validate_project_id(project_id: str) -> bool:
    """Validate project ID format."""
    if not project_id:
        return False
    # Simple validation: alphanumeric, underscore, hyphen
    return all(c.isalnum() or c in "-_" for c in project_id)


def get_project_manifest_template(
    project_id: str,
    title: str,
    content_dir: Path,
    initial_images: int,
    timestamp: str,
    group_count: int,
) -> dict:
    """Generate a project manifest template with all required fields.

    Returns a dictionary matching the schema used by mojo1/mojo2 projects.
    """
    return {
        "schemaVersion": 1,
        "projectId": project_id,
        "title": title,
        "status": "active",
        "createdAt": timestamp,
        "startedAt": timestamp,
        "finishedAt": None,
        "removeFileOnFinish": True,
        "paths": {
            "root": str(content_dir),
            "selectedDir": "../../__selected",
            "cropDir": "../../__crop",
            "characterGroups": [
                "../../__character_group_1",
                "../../__character_group_2",
                "../../__character_group_3",
            ],
        },
        "counts": {
            "initialImages": initial_images,
            "finalImages": None,
            "groupCount": group_count,
        },
        "metrics": {
            "imagesPerHourEndToEnd": None,
            "stepRates": {},
            "stager": {
                "zip": "",
                "eligibleCount": 0,
                "byExtIncluded": {},
                "excludedCounts": {},
                "incomingByExt": {},
            },
        },
        "steps": [
            {
                "name": "select_versions",
                "startedAt": None,
                "finishedAt": None,
                "imagesProcessed": None,
            },
            {
                "name": "character_sort",
                "startedAt": None,
                "finishedAt": None,
                "imagesProcessed": None,
            },
            {
                "name": "crop",
                "startedAt": None,
                "finishedAt": None,
                "imagesProcessed": None,
            },
            {
                "name": "dedupe",
                "startedAt": None,
                "finishedAt": None,
                "imagesProcessed": None,
            },
            {
                "name": "final_review",
                "startedAt": None,
                "finishedAt": None,
                "imagesProcessed": None,
            },
        ],
        "notes": "Project manifest stored outside content to avoid inclusion in deliverables.",
    }


def scan_extensions(content_dir: Path) -> set[str]:
    """Scan a directory and return all unique file extensions found."""
    extensions: set[str] = set()
    if not content_dir.exists():
        logger.warning("Cannot scan extensions: %s does not exist", content_dir)
        return extensions

    skipped_count = 0
    for p in content_dir.rglob("*"):
        try:
            if not p.is_file():
                continue
            ext = p.suffix.lower().lstrip(".")
            if ext:  # Only add if there's actually an extension
                extensions.add(ext)
        except (OSError, PermissionError) as e:
            skipped_count += 1
            logger.debug("Skipped unreadable file %s: %s", p, e)

    if skipped_count > 0:
        logger.warning(
            "Skipped %d unreadable files during extension scan. "
            ".gitignore patterns may be incomplete.",
            skipped_count,
        )

    return extensions


def update_gitignore(
    project_id: str,
    content_dir: Path | None = None,
    content_dir_name: str | None = None,
) -> None:
    """Update .gitignore to exclude project files by extension.

    Scans the content directory for all file extensions and adds per-project
    ignore patterns with section markers for easy removal on project finish.
    """
    gitignore_path = Path(".gitignore")

    # Create .gitignore if it doesn't exist
    if not gitignore_path.exists():
        gitignore_path.write_text("")

    current_content = gitignore_path.read_text()

    # Check if project block already exists
    start_marker = f"# === PROJECT: {project_id}"
    end_marker = f"# === END PROJECT: {project_id} ==="

    if start_marker in current_content:
        print(f"⚠️  Project {project_id} already in .gitignore, skipping")
        return

    # Scan for extensions if content_dir provided
    extensions = set()
    if content_dir and content_dir.exists():
        extensions = scan_extensions(content_dir)

    # Build project block
    timestamp = datetime.now(UTC).strftime("%Y-%m-%d")
    lines_to_add = [
        "",
        f"# === PROJECT: {project_id} (started {timestamp}) ===",
    ]

    # Add extension-based patterns (sorted for consistency)
    if extensions:
        for ext in sorted(extensions):
            lines_to_add.append(f"{project_id}/**/*.{ext}")

        # Also add patterns for content dir if different from project_id
        if content_dir_name and content_dir_name != project_id:
            for ext in sorted(extensions):
                lines_to_add.append(f"{content_dir_name}/**/*.{ext}")
    else:
        # Fallback: just ignore the directories
        lines_to_add.append(f"{project_id}/")
        if content_dir_name and content_dir_name != project_id:
            lines_to_add.append(f"{content_dir_name}/")

    lines_to_add.append(end_marker)

    # Append to gitignore
    if current_content and not current_content.endswith("\n"):
        current_content += "\n"

    current_content += "\n".join(lines_to_add) + "\n"
    gitignore_path.write_text(current_content)

    ext_count = len(extensions) if extensions else 0
    print(f"✅ Added {project_id} to .gitignore ({ext_count} extensions)")


def create_project_manifest(
    project_id: str,
    content_dir: Path,
    title: str | None = None,
    force: bool = False,
    sandbox_config: "SandboxConfig | None" = None,
) -> dict:
    """Create a new project manifest.

    Args:
        project_id: Unique project identifier (e.g., "mojo3")
        content_dir: Path to project content directory
        title: Human-readable project title (defaults to capitalized project_id)
        force: Overwrite existing manifest without prompting
        sandbox_config: Optional sandbox configuration for isolated testing

    Returns:
        Dictionary with status and manifest path
    """
    # Validate inputs
    if not validate_project_id(project_id):
        return {
            "status": "error",
            "message": f"Invalid project ID: {project_id}. Use alphanumeric, underscore, or hyphen only.",
        }

    # Validate project ID against sandbox mode
    if sandbox_config and not sandbox_config.validate_project_id(project_id):
        mode = "sandbox" if sandbox_config.enabled else "production"
        prefix_msg = (
            "must start with TEST-"
            if sandbox_config.enabled
            else "must NOT start with TEST-"
        )
        return {
            "status": "error",
            "message": f"Invalid project ID for {mode} mode: {project_id} {prefix_msg}",
        }

    # Resolve content directory
    content_dir = content_dir.resolve()
    if not content_dir.exists():
        return {
            "status": "error",
            "message": f"Content directory does not exist: {content_dir}",
        }

    if not content_dir.is_dir():
        return {
            "status": "error",
            "message": f"Content path is not a directory: {content_dir}",
        }

    # Count images
    image_count = count_images(content_dir)
    if image_count == 0:
        print(f"⚠️  Warning: No PNG images found in {content_dir}")
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != "y":
            return {
                "status": "cancelled",
                "message": "User cancelled due to no images found",
            }

    # Generate title if not provided
    if not title:
        title = project_id.capitalize()

    # Determine manifest directory (sandbox-aware)
    if sandbox_config:
        manifest_dir = sandbox_config.projects_dir
    else:
        manifest_dir = Path("data/projects")
        manifest_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = manifest_dir / f"{project_id}.project.json"

    if manifest_path.exists() and not force:
        print(f"⚠️  Project manifest already exists: {manifest_path}")
        response = input("Overwrite existing manifest? (y/N): ").strip().lower()
        if response != "y":
            return {
                "status": "cancelled",
                "message": "User cancelled to avoid overwriting",
            }

        # Create backup
        backup_path = manifest_path.with_suffix(".project.json.bak")
        try:
            shutil.copy2(manifest_path, backup_path)
            print(f"✅ Created backup: {backup_path}")
        except Exception as e:
            return {"status": "error", "message": f"Failed to create backup: {e}"}

    # Generate timestamp
    timestamp = get_utc_timestamp()

    # Make content_dir relative to project root (for manifest storage)
    try:
        Path.cwd()
        relative_content = Path("../../" + content_dir.name)
    except Exception:
        relative_content = content_dir

    # Generate manifest
    # Compute group count from content dir (unique stems)
    group_count = count_groups_by_timestamp_stem(content_dir)

    manifest = get_project_manifest_template(
        project_id=project_id,
        title=title,
        content_dir=relative_content,
        initial_images=image_count,
        timestamp=timestamp,
        group_count=group_count,
    )

    # Write manifest
    try:
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        # Verify manifest is readable and valid JSON
        try:
            verification = json.loads(manifest_path.read_text(encoding="utf-8"))
            if verification.get("projectId") != project_id:
                msg = (
                    f"Manifest verification failed: projectId mismatch "
                    f"(expected {project_id}, got {verification.get('projectId')})"
                )
                logger.error(msg)
                return {"status": "error", "message": msg}
            logger.info("Verified manifest: %s", manifest_path)
        except (json.JSONDecodeError, OSError) as e:
            msg = f"Manifest written but verification failed: {e}"
            logger.exception(msg)
            return {"status": "error", "message": msg}

        # Update .gitignore with project-specific extension patterns
        update_gitignore(project_id, content_dir, content_dir.name)

        # Log manifest creation (if tracker available)
        if FileTracker is not None:
            try:
                tracker = FileTracker("00_start_project", sandbox=False)
                tracker.log_operation(
                    "create",
                    source_dir=str(manifest_path.parent),
                    dest_dir=str(manifest_path.parent),
                    file_count=1,
                    files=[manifest_path.name],
                    notes="create project manifest with groupCount",
                )
            except Exception as e:
                logger.exception(
                    "Failed to log manifest creation to FileTracker: %s", e
                )
                logger.warning("Manifest created but NOT logged in audit trail!")
        else:
            logger.warning("FileTracker unavailable - operation not logged")

        # Ensure per-project allowlist exists (used by prezip_stager)
        try:
            allowlist_dir = Path("data/projects")
            allowlist_dir.mkdir(parents=True, exist_ok=True)
            allowlist_path = allowlist_dir / f"{project_id}_allowed_ext.json"
            if not allowlist_path.exists():
                # Build a dynamic allowlist from an inventory of current content extensions
                ext_counts: dict[str, int] = {}
                total_files = 0
                for p in content_dir.rglob("*"):
                    try:
                        if not p.is_file():
                            continue
                        ext = p.suffix.lower().lstrip(".")
                        if not ext:
                            continue
                        total_files += 1
                        ext_counts[ext] = ext_counts.get(ext, 0) + 1
                    except (OSError, PermissionError) as e:
                        logger.debug("Skipping unreadable file %s: %s", p, e)
                        # Continue - some files may be inaccessible, but we can still
                        # build an allowlist from readable ones

                # Write an inventory snapshot for operator visibility
                try:
                    inventory = {
                        "projectId": project_id,
                        "scannedAt": timestamp,
                        "contentDir": str(content_dir),
                        "totalFiles": total_files,
                        "extCounts": dict(
                            sorted(ext_counts.items(), key=lambda kv: (-kv[1], kv[0]))
                        ),
                    }
                    (allowlist_dir / f"{project_id}_inventory.json").write_text(
                        json.dumps(inventory, indent=2, ensure_ascii=False),
                        encoding="utf-8",
                    )
                    logger.info(
                        "Created inventory: %s",
                        allowlist_dir / f"{project_id}_inventory.json",
                    )
                except OSError as e:
                    logger.warning(
                        "Failed to write inventory file (non-critical): %s", e
                    )

                # Derive allowedExtensions from inventory (fallback to sensible defaults)
                allowed_exts = (
                    sorted(ext_counts.keys())
                    if ext_counts
                    else [
                        "png",
                        "yaml",
                        "caption",
                        "txt",
                    ]
                )

                allow_doc = {
                    "allowedExtensions": allowed_exts,
                    "clientWhitelistOverrides": [],
                }
                allowlist_path.write_text(
                    json.dumps(allow_doc, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )
                logger.info("Created allowlist: %s", allowlist_path)
                print(f"✅ Created extension allowlist: {allowlist_path}")
        except OSError as e:
            msg = (
                f"Failed to create allowlist {allowlist_path}: {e}\n"
                f"This will cause prezip_stager to fail later. "
                f"Check directory permissions for data/projects/"
            )
            logger.error(msg)
            # Return error immediately - don't let user think setup succeeded
            return {"status": "error", "message": msg}
    except Exception as e:
        return {"status": "error", "message": f"Failed to write manifest: {e}"}

    return {
        "status": "success",
        "message": "Project manifest created successfully",
        "manifest_path": str(manifest_path),
        "project_id": project_id,
        "initial_images": image_count,
        "started_at": timestamp,
        "group_count": group_count,
    }


def interactive_mode():
    """Run the script in interactive mode, prompting for all inputs."""
    print("=" * 60)
    print("🚀 Project Startup Script")
    print("=" * 60)
    print()

    # Get project ID
    while True:
        project_id = input("Enter project ID (e.g., 'mojo3'): ").strip()
        if validate_project_id(project_id):
            break
        print(
            "❌ Invalid project ID. Use alphanumeric characters, underscores, or hyphens."
        )

    # Get content directory
    while True:
        content_dir_input = input(
            f"Enter content directory path (relative to repo root, e.g., '../{project_id}'): "
        ).strip()
        content_dir = Path(content_dir_input).expanduser()

        if content_dir.exists() and content_dir.is_dir():
            break

        print(f"❌ Directory not found or not a directory: {content_dir}")
        create_new = (
            input("Would you like to create this directory? (y/N): ").strip().lower()
        )
        if create_new == "y":
            try:
                content_dir.mkdir(parents=True, exist_ok=True)
                print(f"✅ Created directory: {content_dir}")
                break
            except Exception as e:
                print(f"❌ Failed to create directory: {e}")

    # Get optional title
    default_title = project_id.capitalize()
    title_input = input(f"Enter project title (default: '{default_title}'): ").strip()
    title = title_input if title_input else default_title

    # Preview
    image_count = count_images(content_dir)
    print()
    print("=" * 60)
    print("📋 Project Summary")
    print("=" * 60)
    print(f"Project ID:       {project_id}")
    print(f"Title:            {title}")
    print(f"Content Dir:      {content_dir}")
    print(f"Initial Images:   {image_count} PNG files")
    print(f"Group Count:      {count_groups_by_timestamp_stem(content_dir)}")
    print(f"Timestamp:        {get_utc_timestamp()}")
    print("=" * 60)
    print()

    # Confirm
    confirm = input("Create project manifest? (Y/n): ").strip().lower()
    if confirm == "n":
        print("❌ Cancelled by user")
        return

    # Create manifest
    result = create_project_manifest(
        project_id=project_id, content_dir=content_dir, title=title, force=False
    )

    # Display result
    if result["status"] == "success":
        print()
        print("=" * 60)
        print("✅ SUCCESS!")
        print("=" * 60)
        print(f"Manifest created: {result['manifest_path']}")
        print(f"Project ID:       {result['project_id']}")
        print(f"Initial Images:   {result['initial_images']}")
        print(f"Started At:       {result['started_at']}")
        print()
        print("🎯 Next steps:")
        print("   1. Run your image processing tools")
        print("   2. When complete, run the prezip_stager to finish the project")
        print("=" * 60)
    else:
        print()
        print(f"❌ {result['status'].upper()}: {result['message']}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create a new project manifest with proper timestamps and image counts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
USAGE PATTERNS:

1. INTERACTIVE MODE (Recommended for manual testing)
   python scripts/00_start_project.py
   → Prompts for project ID, directory, and title

2. POSITIONAL ARGUMENT (Recommended for automation/scripting)
   python scripts/00_start_project.py sandbox/TEST-mojo1
   → Auto-derives "TEST-mojo1" as project ID from directory name
   → Perfect for CI/CD, automation, batch processing
   → Reduces user error by keeping ID and directory in sync

3. EXPLICIT FLAGS (For special cases, scripting with custom paths)
   python scripts/00_start_project.py --project-id mojo3 --content-dir ../mojo3
   → Use when project ID differs from directory name
   → Useful when content is outside repo structure
   → For backward compatibility with existing scripts

WHEN TO USE EACH:

  INTERACTIVE MODE:
  - First time setting up a project
  - Manual, one-off project creation
  - When you need to enter custom title

  POSITIONAL ARGUMENT:
  - Sandbox testing (TEST- prefixed directories)
  - Batch processing multiple projects
  - CI/CD pipelines
  - Automation scripts

  EXPLICIT FLAGS:
  - Advanced scenarios with complex directory structures
  - Legacy scripts that need specific naming
  - When project ID ≠ directory name by design

EXAMPLES:

  # Interactive mode
  python scripts/00_start_project.py

  # Sandbox testing (auto-derives TEST-mojo1)
  python scripts/00_start_project.py sandbox/TEST-mojo1

  # Production project (auto-derives mojo3)
  python scripts/00_start_project.py ../mojo3

  # Custom naming (legacy/special cases)
  python scripts/00_start_project.py --project-id custom-id --content-dir /path/to/images

  # With custom title
  python scripts/00_start_project.py --project-id mojo3 --content-dir ../mojo3 --title "Mojo Project 3"

  # Force overwrite (skip confirmation)
  python scripts/00_start_project.py ../mojo3 --force
        """,
    )

    parser.add_argument(
        "content_dir_positional",
        nargs="?",
        help="(Recommended) Path to project content directory - project ID auto-derived from directory name. "
        "Use this for sandbox testing or automation. Keep ID and directory in sync automatically.",
    )
    parser.add_argument(
        "--project-id",
        help="(Optional) Unique project identifier. Only use with --content-dir. "
        "Not needed with positional argument (auto-derived). Use for special cases where ID differs from directory name.",
    )
    parser.add_argument(
        "--content-dir",
        help="(Optional) Path to project content directory. Only use with --project-id. "
        "Not needed with positional argument. Use for advanced scenarios with complex directory structures.",
    )
    parser.add_argument(
        "--title", help="Human-readable project title (default: capitalized project-id)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing manifest without prompting",
    )
    parser.add_argument(
        "--sandbox",
        action="store_true",
        help="Run in sandbox mode (test data isolated, requires TEST- prefix)",
    )

    args = parser.parse_args()

    # Initialize sandbox configuration
    sandbox = SandboxConfig(enabled=args.sandbox) if SandboxConfig else None
    if sandbox and sandbox.enabled:
        sandbox.print_banner()

    # Handle positional argument: derive project ID from directory name
    project_id = args.project_id
    content_dir = args.content_dir

    if args.content_dir_positional:
        # Positional argument provided: derive project ID from directory name
        content_dir = args.content_dir_positional
        dir_path = Path(content_dir)
        project_id = dir_path.name  # Use directory name as project ID

        if args.project_id or args.content_dir:
            print(
                "❌ Error: Use either positional directory OR --project-id/--content-dir, not both"
            )
            sys.exit(1)

    # If no arguments provided, run in interactive mode
    if not project_id or not content_dir:
        if project_id or content_dir:
            print(
                "❌ Error: Both --project-id and --content-dir are required when using arguments"
            )
            print("Run without arguments for interactive mode.")
            sys.exit(1)

        interactive_mode()
        return

    # Command-line mode
    content_dir_path = Path(content_dir).expanduser()

    result = create_project_manifest(
        project_id=project_id,
        content_dir=content_dir_path,
        title=args.title,
        force=args.force,
        sandbox_config=sandbox,
    )

    # Print result as JSON for scripting
    print(json.dumps(result, indent=2))

    # Exit with appropriate code
    sys.exit(0 if result["status"] == "success" else 1)


if __name__ == "__main__":
    main()
