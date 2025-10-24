"""
Release Package Creator
=======================

Creates a clean, Windows-compatible ZIP release of CartWise Pro.

This script:
1. Validates file names and paths
2. Removes temporary/cache files
3. Creates a clean directory structure
4. Packages everything into a ZIP file

Author: CartWise Team
Version: 1.0.0
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


class ReleasePackager:
    """Handles creation of release packages."""

    # Directories to exclude from release
    EXCLUDE_DIRS = {
        '__pycache__',
        '.pytest_cache',
        '.vscode',
        '.idea',
        '.git',
        'node_modules',
        'venv',
        'env',
        '.env',
        'build',
        'dist',
        '*.egg-info',
        'TRASH_UNUSED_FILES'
    }

    # File patterns to exclude
    EXCLUDE_FILES = {
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.DS_Store',
        'Thumbs.db',
        '*.db-wal',
        '*.db-shm',
        '*.log',
        '.gitignore',
        '.gitattributes'
    }

    # Maximum path length (Windows limitation)
    MAX_PATH_LENGTH = 240

    def __init__(self, source_dir: str, output_name: str = "CartWise-Pro"):
        """
        Initialize packager.

        Args:
            source_dir: Source directory to package
            output_name: Name of output package (without .zip)
        """
        self.source_dir = Path(source_dir).resolve()
        self.output_name = output_name
        self.temp_dir = Path(f"temp_{output_name}")
        self.issues = []

    def validate_filename(self, filename: str) -> bool:
        """
        Check if filename is Windows-compatible.

        Args:
            filename: Filename to check

        Returns:
            True if valid, False otherwise
        """
        # Check for non-ASCII characters
        if not all(ord(c) < 128 for c in filename):
            return False

        # Check for illegal Windows characters
        illegal_chars = '<>:"|?*'
        if any(c in filename for c in illegal_chars):
            return False

        # Check for problematic characters
        problematic = '()[]#&@!%'
        if any(c in filename for c in problematic):
            self.issues.append(f"Warning: '{filename}' contains problematic character")
            return True  # Warning, not error

        return True

    def validate_path_length(self, path: Path) -> bool:
        """
        Check if path length is acceptable.

        Args:
            path: Path to check

        Returns:
            True if valid, False otherwise
        """
        if len(str(path)) > self.MAX_PATH_LENGTH:
            self.issues.append(f"Path too long ({len(str(path))} chars): {path}")
            return False
        return True

    def should_exclude(self, path: Path) -> bool:
        """
        Check if path should be excluded.

        Args:
            path: Path to check

        Returns:
            True if should exclude, False otherwise
        """
        name = path.name

        # Check directory exclusions
        if path.is_dir() and name in self.EXCLUDE_DIRS:
            return True

        # Check file pattern exclusions
        for pattern in self.EXCLUDE_FILES:
            if pattern.startswith('*.'):
                ext = pattern[1:]
                if name.endswith(ext):
                    return True
            elif name == pattern:
                return True

        return False

    def scan_directory(self) -> bool:
        """
        Scan source directory for issues.

        Returns:
            True if no critical issues found, False otherwise
        """
        print("🔍 Scanning directory structure...")

        critical_issues = 0

        for root, dirs, files in os.walk(self.source_dir):
            root_path = Path(root)

            # Remove excluded directories from walk
            dirs[:] = [d for d in dirs if not self.should_exclude(root_path / d)]

            # Check directory name
            if not self.validate_filename(root_path.name):
                self.issues.append(f"Invalid directory name: {root_path.name}")
                critical_issues += 1

            # Check files
            for file in files:
                file_path = root_path / file

                if self.should_exclude(file_path):
                    continue

                if not self.validate_filename(file):
                    self.issues.append(f"Invalid filename: {file}")
                    critical_issues += 1

                if not self.validate_path_length(file_path):
                    critical_issues += 1

        if self.issues:
            print(f"\n⚠️  Found {len(self.issues)} issues:")
            for issue in self.issues[:10]:  # Show first 10
                print(f"   - {issue}")
            if len(self.issues) > 10:
                print(f"   ... and {len(self.issues) - 10} more")

        if critical_issues > 0:
            print(f"\n❌ Found {critical_issues} critical issues that must be fixed!")
            return False

        print("✅ No critical issues found\n")
        return True

    def copy_files(self):
        """Copy files to temporary directory, excluding unwanted ones."""
        print(f"📁 Copying files to {self.temp_dir}...")

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

        self.temp_dir.mkdir()

        copied = 0
        skipped = 0

        for root, dirs, files in os.walk(self.source_dir):
            root_path = Path(root)
            rel_path = root_path.relative_to(self.source_dir)

            # Remove excluded directories
            dirs[:] = [d for d in dirs if not self.should_exclude(root_path / d)]

            # Create directory in temp
            dest_dir = self.temp_dir / rel_path
            if rel_path != Path('.'):
                dest_dir.mkdir(parents=True, exist_ok=True)

            # Copy files
            for file in files:
                file_path = root_path / file

                if self.should_exclude(file_path):
                    skipped += 1
                    continue

                dest_file = dest_dir / file
                shutil.copy2(file_path, dest_file)
                copied += 1

        print(f"   ✅ Copied {copied} files")
        print(f"   ⏭️  Skipped {skipped} files\n")

    def create_readme(self):
        """Create a README file with instructions."""
        readme_content = """# CartWise Pro - Smart Shopping Cart Management System

## Quick Start

### Windows
1. Extract this ZIP to `C:\\CartWise-Pro`
2. Open Command Prompt in that directory
3. Run: `pip install -r requirements.txt`
4. Configure `config/.env` with your settings
5. Run: `python run_server.py`
6. Open browser: http://localhost:8002

### Linux
1. Extract this ZIP
2. See `LINUX_SETUP.md` for detailed instructions
3. Run: `python3 run_server.py`

## Documentation

- `RENTAL_TRACKING_SYSTEM.md` - Rental tracking system guide
- `FIX_RS485_ISSUE.md` - RS485 troubleshooting
- `LINUX_SETUP.md` - Linux installation guide

## Support

For issues, check the logs in `logs/cartwise.log`

## System Requirements

- Python 3.8 or higher
- Windows 10/11 or Linux
- RS485 adapter (for hardware control)
- Internet connection (for SMS)

---
Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        readme_path = self.temp_dir / "README.txt"
        readme_path.write_text(readme_content, encoding='utf-8')
        print("📝 Created README.txt\n")

    def create_zip(self):
        """Create ZIP archive."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_name = f"{self.output_name}_{timestamp}.zip"

        print(f"📦 Creating ZIP archive: {zip_name}...")

        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.temp_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.temp_dir)
                    zipf.write(file_path, arcname)

        # Get ZIP size
        zip_size = os.path.getsize(zip_name)
        size_mb = zip_size / (1024 * 1024)

        print(f"   ✅ Created: {zip_name}")
        print(f"   📊 Size: {size_mb:.2f} MB\n")

        return zip_name

    def cleanup(self):
        """Remove temporary directory."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            print("🧹 Cleaned up temporary files\n")

    def create_release(self) -> str:
        """
        Create a complete release package.

        Returns:
            Path to created ZIP file

        Raises:
            SystemExit: If validation fails
        """
        print("=" * 60)
        print("CartWise Pro - Release Package Creator")
        print("=" * 60)
        print()

        # Step 1: Validate
        if not self.scan_directory():
            print("\n❌ Validation failed! Please fix issues before creating release.")
            sys.exit(1)

        # Step 2: Copy files
        self.copy_files()

        # Step 3: Create README
        self.create_readme()

        # Step 4: Create ZIP
        zip_path = self.create_zip()

        # Step 5: Cleanup
        self.cleanup()

        print("=" * 60)
        print("✅ Release package created successfully!")
        print("=" * 60)
        print(f"\nPackage: {zip_path}")
        print("\nYou can now share this ZIP file.")
        print("It will extract cleanly on any Windows or Linux system.\n")

        return zip_path


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        source_dir = sys.argv[1]
    else:
        source_dir = "."

    if len(sys.argv) > 2:
        output_name = sys.argv[2]
    else:
        output_name = "CartWise-Pro"

    packager = ReleasePackager(source_dir, output_name)

    try:
        packager.create_release()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
        packager.cleanup()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        packager.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()
