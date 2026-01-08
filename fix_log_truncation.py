#!/usr/bin/env python3
"""
Fix log truncation across all projects.
Removes string slicing like [:50], [:100], etc. from log statements
and changes logging.basicConfig to DEBUG level.
"""
import re
from pathlib import Path

# Truncation patterns to remove/increase
TRUNCATION_PATTERNS = [
    (r'\[:15\]', '[:500]'),
    (r'\[:20\]', '[:500]'),
    (r'\[:25\]', '[:500]'),
    (r'\[:30\]', '[:500]'),
    (r'\[:35\]', '[:500]'),
    (r'\[:40\]', '[:500]'),
    (r'\[:45\]', '[:500]'),
    (r'\[:50\]', '[:500]'),
    (r'\[:60\]', '[:500]'),
    (r'\[:70\]', '[:500]'),
    (r'\[:80\]', '[:500]'),
    (r'\[:90\]', '[:500]'),
    (r'\[:100\]', '[:500]'),
    (r'\[:150\]', '[:500]'),
    (r'\[:200\]', '[:500]'),
]

# Logging level pattern
LOGGING_PATTERN = (r'logging\.basicConfig\(level=logging\.INFO\)', 'logging.basicConfig(level=logging.DEBUG)')

def fix_file(filepath):
    """Fix truncations and logging level in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        changes_made = []

        # Fix truncation patterns
        for pattern, replacement in TRUNCATION_PATTERNS:
            count = len(re.findall(pattern, content))
            if count > 0:
                content = re.sub(pattern, replacement, content)
                changes_made.append(f"  - Replaced {count} instances of {pattern}")

        # Fix logging level
        if 'logging.basicConfig(level=logging.INFO)' in content:
            content = content.replace('logging.basicConfig(level=logging.INFO)',
                                    'logging.basicConfig(level=logging.DEBUG)')
            changes_made.append("  - Changed logging level to DEBUG")

        # Write back if changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ {filepath}")
            for change in changes_made:
                print(change)
            return True
        return False

    except Exception as e:
        print(f"✗ Error processing {filepath}: {e}")
        return False

def main():
    """Process all Python files in the projects."""
    base_path = Path(__file__).parent
    projects = ['pantheon-chat', 'pantheon-replit', 'SearchSpaceCollapse']

    total_files = 0
    modified_files = 0

    for project in projects:
        project_path = base_path / project
        if not project_path.exists():
            print(f"Skipping {project} (not found)")
            continue

        print(f"\n{'='*60}")
        print(f"Processing {project}")
        print(f"{'='*60}")

        # Find all Python files
        python_files = list(project_path.rglob('*.py'))

        for py_file in python_files:
            # Skip virtual environments and node_modules
            if '.venv' in str(py_file) or 'node_modules' in str(py_file):
                continue

            total_files += 1
            if fix_file(py_file):
                modified_files += 1

    print(f"\n{'='*60}")
    print(f"Summary: Modified {modified_files}/{total_files} files")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
