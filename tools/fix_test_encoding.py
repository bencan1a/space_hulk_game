#!/usr/bin/env python3
"""
Fix encoding issues in test files by adding encoding='utf-8' to all open() calls.
This prevents Windows cp1252 codec errors when reading files with UTF-8 characters.
"""

import re
from pathlib import Path


def fix_file_encoding(file_path: Path) -> tuple[bool, int]:
    """
    Fix encoding in a single file.

    Returns:
        Tuple of (was_modified, num_changes)
    """
    content = file_path.read_text(encoding="utf-8")
    original = content

    # Pattern 1: with open(path) as f:
    content = re.sub(r"with open\(([^,)]+)\) as", r"with open(\1, encoding='utf-8') as", content)

    # Pattern 2: open(path, 'r') - replace 'r' with encoding
    content = re.sub(r"open\(([^,)]+), ['\"]r['\"]", r"open(\1, encoding='utf-8'", content)

    changes = len(re.findall(r"encoding='utf-8'", content)) - len(
        re.findall(r"encoding='utf-8'", original)
    )

    if content != original:
        file_path.write_text(content, encoding="utf-8")
        return True, changes

    return False, 0


def main():
    """Fix encoding in all test files."""
    tests_dir = Path(__file__).parent.parent / "tests"

    total_files = 0
    total_changes = 0

    for test_file in tests_dir.glob("**/*.py"):
        modified, changes = fix_file_encoding(test_file)
        if modified:
            total_files += 1
            total_changes += changes
            print(f"✓ {test_file.name}: {changes} changes")

    print(f"\nFixed {total_changes} open() calls in {total_files} files")


if __name__ == "__main__":
    main()
