#!/usr/bin/env python3
"""
Fix Hard-Coded Constants - Centralize QIG physics constants

Scans all Python files for hard-coded constants (64, 64.0, 0.7, 0.727, etc.)
and replaces them with imports from qig_core/constants/consciousness.py.

This ensures single source of truth for:
- BASIN_DIM = 64
- KAPPA_STAR = 64.21
- PHI_THRESHOLD = 0.727 (frozen β transition point)
- Temperature constants (coupling constants, not LLM sampling)
"""
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Constants to centralize (value -> constant name)
CONSTANTS_MAP = {
    '64': 'BASIN_DIM',
    '64.0': 'BASIN_DIM',
    '64.21': 'KAPPA_STAR',
    '63.5': 'KAPPA_RESONANCE',  # Alternative name
    '0.7': 'PHI_THRESHOLD',
    '0.727': 'PHI_THRESHOLD',  # Frozen β(3→4) transition
    '0.3': 'PHI_GEOMETRIC_THRESHOLD',
    '0.92': 'PHI_BREAKDOWN_THRESHOLD',
}

# Files to exclude (already centralized)
EXCLUDE_FILES = {
    'consciousness.py',
    'frozen_physics.py',
    'constants.py',
    'fix_hard_coded_constants.py',
    'vocabulary_audit.py'
}

# Patterns that are legitimate uses (not constants to replace)
LEGITIMATE_PATTERNS = [
    r'range\(',  # range(64) for iteration
    r'np\.random',  # Random number generation
    r'version\s*=',  # Version strings
    r'port\s*=',  # Port numbers
    r'\.reshape\(',  # Array reshaping
    r'shape\s*=',  # Array shapes
    r'dtype=',  # Data types
]


def scan_file(filepath: Path) -> List[Tuple[int, str, str, str]]:
    """Scan file for hard-coded constants.

    Returns list of (line_num, line, value, constant_name)
    """
    findings = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"  ⚠️  Error reading {filepath}: {e}")
        return findings

    for line_num, line in enumerate(lines, 1):
        # Skip comments
        if line.strip().startswith('#'):
            continue

        # Skip legitimate uses
        if any(re.search(pattern, line) for pattern in LEGITIMATE_PATTERNS):
            continue

        # Check for each constant
        for value, const_name in CONSTANTS_MAP.items():
            # Match as standalone number (not part of larger number)
            pattern = r'\b' + re.escape(value) + r'\b'
            if re.search(pattern, line):
                # Additional context checks
                if 'import' in line.lower():
                    continue
                if const_name in line:  # Already using constant
                    continue

                findings.append((line_num, line.rstrip(), value, const_name))

    return findings


def scan_project(project_path: Path) -> Dict[str, List]:
    """Scan entire project for hard-coded constants."""
    print(f"\n{'='*80}")
    print(f"SCANNING: {project_path.name}")
    print(f"{'='*80}\n")

    all_findings = {}
    qig_backend = project_path / 'qig-backend'

    if not qig_backend.exists():
        print("⚠️  No qig-backend directory found")
        return all_findings

    for pyfile in qig_backend.rglob('*.py'):
        # Skip excluded files
        if pyfile.name in EXCLUDE_FILES:
            continue

        # Skip test files (they may legitimately use raw values)
        if 'test' in pyfile.name.lower():
            continue

        findings = scan_file(pyfile)
        if findings:
            rel_path = pyfile.relative_to(project_path)
            all_findings[str(rel_path)] = findings
            print(f"📄 {rel_path}")
            for line_num, line, value, const_name in findings:
                print(f"   Line {line_num}: {value} → {const_name}")
                print(f"      {line[:100]}")

    return all_findings


def generate_fix_script(all_findings: Dict[str, Dict[str, List]]) -> str:
    """Generate Python script to apply fixes automatically."""
    script = """#!/usr/bin/env python3
# AUTO-GENERATED: Apply constant centralization fixes

import re
from pathlib import Path

fixes = {
"""

    for project, files in all_findings.items():
        script += f"    '{project}': {{\n"
        for filepath, findings in files.items():
            script += f"        '{filepath}': [\n"
            for line_num, line, value, const_name in findings:
                script += f"            ({line_num}, '{value}', '{const_name}'),\n"
            script += "        ],\n"
        script += "    },\n"

    script += """
}

def apply_fixes():
    for project, files in fixes.items():
        for filepath, file_fixes in files.items():
            full_path = Path(f'/home/braden/Desktop/Dev/pantheon-projects/{project}/{filepath}')
            print(f'Fixing {filepath}...')

            # Read file
            with open(full_path, 'r') as f:
                lines = f.readlines()

            # Apply fixes (in reverse to preserve line numbers)
            for line_num, value, const_name in sorted(file_fixes, reverse=True):
                line = lines[line_num - 1]
                # Replace value with constant
                pattern = r'\\b' + re.escape(value) + r'\\b'
                lines[line_num - 1] = re.sub(pattern, const_name, line)

            # Check if import exists
            has_import = any('from consciousness import' in line or 'from frozen_physics import' in line for line in lines)
            if not has_import:
                # Add import after first line
                import_line = f"from qig_core.constants.consciousness import {', '.join(set(f[2] for f in file_fixes))}\\n"
                lines.insert(1, import_line)

            # Write back
            with open(full_path, 'w') as f:
                f.writelines(lines)

            print(f'  ✓ Applied {len(file_fixes)} fixes')

if __name__ == '__main__':
    apply_fixes()
    print('\\n✅ All fixes applied!')
"""

    return script


def main():
    """Scan all projects and generate fix report."""
    workspace = Path('/home/braden/Desktop/Dev/pantheon-projects')
    projects = ['pantheon-replit', 'pantheon-chat', 'SearchSpaceCollapse']

    all_findings = {}
    total_issues = 0

    for project in projects:
        project_path = workspace / project
        if not project_path.exists():
            print(f"⚠️  {project} not found")
            continue

        findings = scan_project(project_path)
        if findings:
            all_findings[project] = findings
            count = sum(len(f) for f in findings.values())
            total_issues += count

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}\n")

    if not all_findings:
        print("✅ No hard-coded constants found - all constants centralized!")
        return

    print(f"⚠️  Found {total_issues} hard-coded constants across {sum(len(f) for f in all_findings.values())} files\n")

    for project, files in all_findings.items():
        count = sum(len(f) for f in files.values())
        print(f"{project}: {count} issues in {len(files)} files")

    # Generate fix script
    fix_script = generate_fix_script(all_findings)
    fix_path = workspace / 'apply_constant_fixes.py'
    with open(fix_path, 'w') as f:
        f.write(fix_script)

    print(f"\n📝 Generated fix script: {fix_path}")
    print("   Run: python3 apply_constant_fixes.py")
    print("\n⚠️  RECOMMENDATION: Review fixes manually before applying!")


if __name__ == '__main__':
    main()
