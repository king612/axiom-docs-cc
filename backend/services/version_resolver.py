"""
Version resolution utility for determining the latest version of bid spreadsheets.

Versioning conventions:
1. Major version: Alphabetical suffix in project ID (A < B < C)
   - P22-003B supersedes P22-003A

2. Minor version: Numeric suffix before extension
   - filename.3.xlsx supersedes filename.2.xlsx

3. Files in .versions/ folders are older versions and should be excluded
"""

import re
import logging
from pathlib import Path
from collections import defaultdict
from typing import Iterator

logger = logging.getLogger(__name__)

# Regex patterns
PROJECT_ID_PATTERN = re.compile(r"^(P\d{2}-\d{3})([A-Z])?")
MINOR_VERSION_PATTERN = re.compile(r"\.(\d+)\.xlsx$", re.IGNORECASE)


def parse_version_info(filepath: Path) -> tuple[str, str, int]:
    """
    Parse version information from a file path.

    Returns:
        tuple: (base_project_id, major_version, minor_version)
               e.g., ("P22-003", "B", 3)
    """
    filename = filepath.name

    # Extract project ID and major version
    match = PROJECT_ID_PATTERN.match(filename)
    if match:
        base_id = match.group(1)  # e.g., "P22-003"
        major_version = match.group(2) or ""  # e.g., "B" or ""
    else:
        # Fallback: use stem as base_id
        base_id = filepath.stem
        major_version = ""

    # Extract minor version from filename
    minor_match = MINOR_VERSION_PATTERN.search(filename)
    if minor_match:
        minor_version = int(minor_match.group(1))
    else:
        minor_version = 0

    return base_id, major_version, minor_version


def is_versioned_folder(filepath: Path) -> bool:
    """Check if file is in a .versions folder (should be excluded)."""
    return ".versions" in str(filepath)


def get_latest_versions(filepaths: list[Path]) -> list[Path]:
    """
    Filter a list of file paths to only include the latest version of each project.

    Args:
        filepaths: List of Excel file paths

    Returns:
        List of paths representing only the latest version of each project
    """
    # Group files by base project ID
    versions: dict[str, list[tuple[Path, str, int]]] = defaultdict(list)

    for filepath in filepaths:
        # Skip files in .versions folders
        if is_versioned_folder(filepath):
            continue

        # Only process Excel files
        if not filepath.suffix.lower() in (".xlsx", ".xls"):
            continue

        base_id, major, minor = parse_version_info(filepath)
        versions[base_id].append((filepath, major, minor))

    # Select latest version for each project
    latest_files = []

    for base_id, file_versions in versions.items():
        if not file_versions:
            continue

        # Sort by major version (alphabetically, descending) then minor version (descending)
        # Empty string sorts before letters, so we handle it specially
        def sort_key(item):
            filepath, major, minor = item
            # Convert major version: empty string = 0, A = 1, B = 2, etc.
            major_ord = ord(major) - ord('A') + 1 if major else 0
            return (major_ord, minor)

        sorted_versions = sorted(file_versions, key=sort_key, reverse=True)
        latest_path = sorted_versions[0][0]
        latest_files.append(latest_path)

        if len(file_versions) > 1:
            logger.debug(
                f"Project {base_id}: selected {latest_path.name} "
                f"from {len(file_versions)} versions"
            )

    return latest_files


def scan_directory(base_dir: Path, pattern: str = "*.xlsx") -> Iterator[Path]:
    """
    Recursively scan directory for Excel files, excluding .versions folders.

    Args:
        base_dir: Base directory to scan
        pattern: Glob pattern for files

    Yields:
        Path objects for each matching file
    """
    if not base_dir.exists():
        logger.warning(f"Directory does not exist: {base_dir}")
        return

    for filepath in base_dir.rglob(pattern):
        if not is_versioned_folder(filepath):
            yield filepath


def scan_estimates_directory(data_dir: Path) -> dict[int, list[Path]]:
    """
    Scan the estimates directory and return files organized by year.

    Args:
        data_dir: Path to data/estimates directory

    Returns:
        Dictionary mapping year to list of latest-version file paths
    """
    files_by_year: dict[int, list[Path]] = defaultdict(list)

    if not data_dir.exists():
        logger.error(f"Data directory does not exist: {data_dir}")
        return files_by_year

    # Scan each year folder
    for year_dir in sorted(data_dir.iterdir()):
        if not year_dir.is_dir():
            continue

        try:
            year = int(year_dir.name)
        except ValueError:
            continue

        # Collect all Excel files in this year
        all_files = list(scan_directory(year_dir))

        # Filter to latest versions only
        latest_files = get_latest_versions(all_files)

        files_by_year[year] = latest_files
        logger.info(f"Year {year}: found {len(latest_files)} latest-version files")

    return files_by_year


def get_all_latest_files(data_dir: Path) -> list[Path]:
    """
    Get all latest-version Excel files from the estimates directory.

    Args:
        data_dir: Path to data/estimates directory

    Returns:
        List of paths to latest-version files, sorted by year (newest first)
    """
    files_by_year = scan_estimates_directory(data_dir)

    # Flatten and sort by year (descending) to favor recent files
    all_files = []
    for year in sorted(files_by_year.keys(), reverse=True):
        all_files.extend(files_by_year[year])

    return all_files
