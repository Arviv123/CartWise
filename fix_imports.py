"""
Fix all relative imports to absolute imports in src/ directory.
"""

import re
from pathlib import Path

src_dir = Path("src")

# Mapping of relative to absolute imports
replacements = [
    (r'from \.\.core import', 'from core import'),
    (r'from \.\.hardware', 'from hardware'),
    (r'from \.\.models', 'from models'),
    (r'from \.\.providers', 'from providers'),
    (r'from \.\.utils', 'from utils'),
    (r'from \.\.api', 'from api'),
    (r'from \.core import', 'from core import'),
    (r'from \.hardware', 'from hardware'),
    (r'from \.models', 'from models'),
    (r'from \.providers', 'from providers'),
    (r'from \.utils', 'from utils'),
    (r'from \.api', 'from api'),
    (r'from \.routers', 'from api.routers'),
    (r'from \.dependencies', 'from api.dependencies'),
    (r'from \.sms', 'from providers.sms'),
    (r'from \.base', 'from providers.sms.base'),
]

def fix_file(filepath):
    """Fix imports in a single file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[OK] Fixed: {filepath}")
        return True
    return False

def main():
    """Fix all Python files."""
    fixed_count = 0

    for py_file in src_dir.rglob("*.py"):
        if fix_file(py_file):
            fixed_count += 1

    print(f"\n[DONE] Fixed {fixed_count} files")

if __name__ == "__main__":
    main()
