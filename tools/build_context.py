#!/usr/bin/env python3
"""
Generate comprehensive documentation context for AI agents.

This script:
1. Generates API documentation from src/ using pdoc3
2. Collects active project plans from agent-projects/
3. Assembles unified CONTEXT.md for AI consumption
4. Updates SUMMARY.md with project status
5. Cleans old temporary files from agent-tmp/

Environment Variables:
    CONTEXT_MAX_CHARS: Maximum context file size (default: 150000)
    PLANS_MAX_AGE_DAYS: Maximum age for active plans (default: 21)
    CLEAN_TMP_AGE_DAYS: Age threshold for temp file cleanup (default: 7)
"""

import os
import subprocess  # nosec B404
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# Configuration from environment or defaults
CONTEXT_MAX_CHARS = int(os.getenv("CONTEXT_MAX_CHARS", "150000"))
PLANS_MAX_AGE_DAYS = int(os.getenv("PLANS_MAX_AGE_DAYS", "21"))
CLEAN_TMP_AGE_DAYS = int(os.getenv("CLEAN_TMP_AGE_DAYS", "7"))

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
AGENT_PROJECTS_DIR = PROJECT_ROOT / "agent-projects"
AGENT_TMP_DIR = PROJECT_ROOT / "agent-tmp"
SRC_DIR = PROJECT_ROOT / "src"


def generate_api_docs() -> None:
    """Generate API documentation using pdoc3."""
    print("Generating API documentation...")

    api_docs_dir = DOCS_DIR / "_generated" / "api"
    api_docs_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Generate HTML documentation
        subprocess.run(  # nosec B603, B607
            [
                "pdoc",
                "--html",
                "--output-dir",
                str(api_docs_dir),
                "--force",
                "space_hulk_game",
            ],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        print(f"✅ API docs generated in {api_docs_dir}")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Warning: API doc generation failed: {e}")
        print(f"   stderr: {e.stderr}")
    except FileNotFoundError:
        print("⚠️  Warning: pdoc3 not found. Install with: pip install pdoc3")


def parse_plan_metadata(plan_path: Path) -> dict[str, str] | None:
    """
    Parse YAML frontmatter from plan.md file.

    Returns dict with status, owner, created, updated, priority.
    """
    try:
        content = plan_path.read_text()

        # Extract YAML frontmatter between --- markers
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter = parts[1].strip()
                metadata = {}
                for line in frontmatter.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        metadata[key.strip()] = value.strip()
                return metadata
    except Exception as e:
        print(f"⚠️  Warning: Could not parse {plan_path}: {e}")

    return None


def collect_active_plans() -> list[dict[str, Any]]:
    """Collect active project plans from agent-projects/."""
    print("Collecting active project plans...")

    if not AGENT_PROJECTS_DIR.exists():
        print("i  No agent-projects/ directory found")
        return []

    plans = []
    cutoff_date = datetime.now() - timedelta(days=PLANS_MAX_AGE_DAYS)

    for plan_dir in AGENT_PROJECTS_DIR.iterdir():
        if not plan_dir.is_dir():
            continue

        plan_file = plan_dir / "plan.md"
        if not plan_file.exists():
            continue

        # Parse metadata
        metadata = parse_plan_metadata(plan_file)
        if not metadata:
            continue

        # Check if active and recent
        status = metadata.get("status", "").lower()
        created_str = metadata.get("created", "")

        try:
            created_date = datetime.strptime(created_str, "%Y-%m-%d")
            if created_date < cutoff_date:
                continue  # Too old
        except (ValueError, TypeError):
            print(f"⚠️  Warning: Invalid date in {plan_file}")
            continue

        if status in ["active", "in_progress", "ongoing"]:
            plans.append(
                {
                    "name": plan_dir.name,
                    "path": plan_file,
                    "metadata": metadata,
                    "created": created_date,
                }
            )

    print(f"✅ Found {len(plans)} active plans")
    return plans


def build_context_file() -> None:
    """Assemble unified CONTEXT.md for AI agents."""
    print("Building CONTEXT.md...")

    context_parts = []

    # Header
    context_parts.append("# Space Hulk Game - AI Agent Context\n\n")
    context_parts.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    context_parts.append("---\n\n")

    # Project Overview
    context_parts.append("## Project Overview\n\n")
    readme_path = PROJECT_ROOT / "README.md"
    if readme_path.exists():
        readme_content = readme_path.read_text()
        # Extract first section (before first ## heading)
        lines = readme_content.split("\n")
        overview = []
        for line in lines[1:]:  # Skip title
            if line.startswith("##"):
                break
            overview.append(line)
        context_parts.append("\n".join(overview).strip())
        context_parts.append("\n\n")

    # Active Projects
    plans = collect_active_plans()
    if plans:
        context_parts.append("## Active Projects\n\n")
        for plan in sorted(plans, key=lambda p: p["created"], reverse=True):
            meta = plan["metadata"]
            context_parts.append(f"### {plan['name']}\n\n")
            context_parts.append(f"- **Status:** {meta.get('status', 'unknown')}\n")
            context_parts.append(f"- **Owner:** {meta.get('owner', 'unknown')}\n")
            context_parts.append(f"- **Created:** {meta.get('created', 'unknown')}\n")
            context_parts.append(f"- **Priority:** {meta.get('priority', 'unknown')}\n")
            context_parts.append(f"- **Location:** `{plan['path'].relative_to(PROJECT_ROOT)}`\n\n")
        context_parts.append("\n")

    # API Documentation Reference
    context_parts.append("## API Documentation\n\n")
    api_docs_dir = DOCS_DIR / "_generated" / "api"
    if api_docs_dir.exists():
        context_parts.append(
            f"Detailed API documentation available in `{api_docs_dir.relative_to(PROJECT_ROOT)}/`\n\n"
        )
        context_parts.append("Key modules:\n")
        context_parts.append("- `space_hulk_game.crew` - Main CrewAI implementation\n")
        context_parts.append("- `space_hulk_game.engine` - Game engine components\n")
        context_parts.append("- `space_hulk_game.quality` - Quality evaluation system\n\n")
    else:
        context_parts.append(
            "API documentation not yet generated. Run: `pdoc --html src/space_hulk_game`\n\n"
        )

    # Project Structure
    context_parts.append("## Project Structure\n\n")
    context_parts.append("```\n")
    context_parts.append("space_hulk_game/\n")
    context_parts.append("├── src/space_hulk_game/  # Source code\n")
    context_parts.append("│   ├── config/           # Agent/task YAML configs\n")
    context_parts.append("│   ├── engine/           # Game engine\n")
    context_parts.append("│   ├── quality/          # Quality evaluators\n")
    context_parts.append("│   └── crew.py           # Main CrewAI crew\n")
    context_parts.append("├── tests/                # Test suite\n")
    context_parts.append("├── tools/                # Utility scripts\n")
    context_parts.append("├── docs/                 # Documentation\n")
    context_parts.append("├── game-config/          # Game templates\n")
    context_parts.append("├── agent-projects/       # Active projects\n")
    context_parts.append("└── agent-tmp/            # Temporary files\n")
    context_parts.append("```\n\n")

    # Key Documentation
    context_parts.append("## Key Documentation\n\n")
    context_parts.append("- **AGENTS.md** - AI agent guidance (start here!)\n")
    context_parts.append("- **CLAUDE.md** - Comprehensive project documentation\n")
    context_parts.append("- **README.md** - Project overview and setup\n")
    context_parts.append("- **docs/SETUP.md** - Detailed installation guide\n")
    context_parts.append("- **docs/QUICKSTART.md** - Quick reference\n\n")

    # Assemble and truncate
    full_context = "".join(context_parts)

    if len(full_context) > CONTEXT_MAX_CHARS:
        full_context = full_context[:CONTEXT_MAX_CHARS]
        full_context += "\n\n---\n\n**[Context truncated to fit size limit]**\n"

    # Write to file
    context_path = PROJECT_ROOT / "CONTEXT.md"
    context_path.write_text(full_context)
    print(f"✅ CONTEXT.md generated ({len(full_context):,} chars)")


def clean_temp_files() -> None:
    """Clean old files from agent-tmp/."""
    print("Cleaning old temporary files...")

    if not AGENT_TMP_DIR.exists():
        print("i  No agent-tmp/ directory found")
        return

    cutoff_date = datetime.now() - timedelta(days=CLEAN_TMP_AGE_DAYS)
    removed_count = 0

    for item in AGENT_TMP_DIR.rglob("*"):
        if item.is_file():
            try:
                mtime = datetime.fromtimestamp(item.stat().st_mtime)
                if mtime < cutoff_date:
                    item.unlink()
                    removed_count += 1
            except Exception as e:
                print(f"⚠️  Warning: Could not remove {item}: {e}")

    print(f"✅ Removed {removed_count} old temporary files")


def update_summary() -> None:
    """Update SUMMARY.md with current project status."""
    print("Updating SUMMARY.md...")

    summary_parts = []

    # Header
    summary_parts.append("# Space Hulk Game - Project Summary\n\n")
    summary_parts.append(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

    # Quick Stats
    src_files = len(list(SRC_DIR.rglob("*.py")))
    test_files = len(list((PROJECT_ROOT / "tests").rglob("*.py")))

    summary_parts.append("## Quick Stats\n\n")
    summary_parts.append(f"- **Source Files:** {src_files}\n")
    summary_parts.append(f"- **Test Files:** {test_files}\n")

    # Active Projects
    plans = collect_active_plans()
    summary_parts.append(f"- **Active Projects:** {len(plans)}\n\n")

    if plans:
        summary_parts.append("## Active Projects\n\n")
        for plan in plans:
            meta = plan["metadata"]
            summary_parts.append(f"- **{plan['name']}** ({meta.get('status', 'unknown')})\n")

    # Write
    summary_path = PROJECT_ROOT / "SUMMARY.md"
    summary_path.write_text("".join(summary_parts))
    print("✅ SUMMARY.md updated")


def main() -> None:
    """Main execution."""
    print("=" * 60)
    print("Space Hulk Game - Documentation Generation")
    print("=" * 60)
    print()

    try:
        # Step 1: Generate API docs
        generate_api_docs()
        print()

        # Step 2: Build context file
        build_context_file()
        print()

        # Step 3: Update summary
        update_summary()
        print()

        # Step 4: Clean old temp files
        clean_temp_files()
        print()

        print("=" * 60)
        print("✅ Documentation generation complete!")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
