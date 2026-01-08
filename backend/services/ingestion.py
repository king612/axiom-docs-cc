"""
Data ingestion service for processing Excel bid spreadsheets.

Handles:
- Scanning data directories
- Version resolution
- Excel parsing
- Vector store population
"""

import logging
from pathlib import Path
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from backend.config import DATA_DIR
from backend.db.vector_store import VectorStore
from backend.models.project import Project
from backend.services.excel_parser import parse_excel_file
from backend.services.version_resolver import get_all_latest_files, scan_estimates_directory

logger = logging.getLogger(__name__)


class IngestionService:
    """Service for ingesting bid spreadsheets into the vector store."""

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        data_dir: Optional[Path] = None,
    ):
        """
        Initialize the ingestion service.

        Args:
            vector_store: VectorStore instance (creates new one if not provided)
            data_dir: Path to data directory (uses config default if not provided)
        """
        self.vector_store = vector_store or VectorStore()
        self.data_dir = Path(data_dir) if data_dir else DATA_DIR

    def ingest_file(self, filepath: Path) -> Optional[Project]:
        """
        Ingest a single Excel file.

        Args:
            filepath: Path to Excel file

        Returns:
            Parsed Project or None if parsing failed
        """
        project = parse_excel_file(filepath)
        if project:
            self.vector_store.add_project(project)
            logger.debug(f"Ingested: {filepath.name}")
        return project

    def ingest_all(
        self,
        clear_existing: bool = False,
        max_workers: int = 4,
        progress_callback: Optional[callable] = None,
    ) -> dict:
        """
        Ingest all latest-version Excel files from the data directory.

        Args:
            clear_existing: If True, clear the vector store before ingesting
            max_workers: Number of parallel workers for parsing
            progress_callback: Optional callback function(current, total) for progress

        Returns:
            Dictionary with ingestion statistics
        """
        if clear_existing:
            logger.info("Clearing existing vector store")
            self.vector_store.clear()

        # Get all latest-version files
        logger.info(f"Scanning directory: {self.data_dir}")
        files = get_all_latest_files(self.data_dir)
        total_files = len(files)
        logger.info(f"Found {total_files} latest-version files to process")

        if total_files == 0:
            return {
                "total_files": 0,
                "successful": 0,
                "failed": 0,
                "with_training_labels": 0,
            }

        # Parse files (can be parallelized since parsing is independent)
        successful = 0
        failed = 0
        with_training_labels = 0
        projects_batch = []

        # Use ThreadPoolExecutor for parallel parsing
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(parse_excel_file, f): f for f in files
            }

            for i, future in enumerate(as_completed(future_to_file)):
                filepath = future_to_file[future]
                try:
                    project = future.result()
                    if project:
                        projects_batch.append(project)
                        successful += 1
                        if project.has_training_labels:
                            with_training_labels += 1

                        # Batch insert every 100 projects
                        if len(projects_batch) >= 100:
                            self.vector_store.add_projects(projects_batch)
                            projects_batch = []
                    else:
                        failed += 1
                        logger.warning(f"Failed to parse: {filepath.name}")

                except Exception as e:
                    failed += 1
                    logger.error(f"Error processing {filepath.name}: {e}")

                # Progress callback
                if progress_callback:
                    progress_callback(i + 1, total_files)

        # Insert remaining projects
        if projects_batch:
            self.vector_store.add_projects(projects_batch)

        stats = {
            "total_files": total_files,
            "successful": successful,
            "failed": failed,
            "with_training_labels": with_training_labels,
        }

        logger.info(
            f"Ingestion complete: {successful}/{total_files} successful, "
            f"{with_training_labels} with training labels"
        )

        return stats

    def ingest_year(self, year: int, clear_existing: bool = False) -> dict:
        """
        Ingest files from a specific year.

        Args:
            year: Year to ingest (e.g., 2024)
            clear_existing: If True, clear the vector store first

        Returns:
            Dictionary with ingestion statistics
        """
        if clear_existing:
            self.vector_store.clear()

        files_by_year = scan_estimates_directory(self.data_dir)
        files = files_by_year.get(year, [])

        if not files:
            logger.warning(f"No files found for year {year}")
            return {"total_files": 0, "successful": 0, "failed": 0}

        logger.info(f"Ingesting {len(files)} files from year {year}")

        successful = 0
        failed = 0
        projects = []

        for filepath in files:
            project = parse_excel_file(filepath)
            if project:
                projects.append(project)
                successful += 1
            else:
                failed += 1

        if projects:
            self.vector_store.add_projects(projects)

        return {
            "year": year,
            "total_files": len(files),
            "successful": successful,
            "failed": failed,
        }

    def get_stats(self) -> dict:
        """Get current vector store statistics."""
        return self.vector_store.get_stats()


def run_ingestion(
    data_dir: Optional[Path] = None,
    clear_existing: bool = True,
) -> dict:
    """
    Convenience function to run full ingestion.

    Args:
        data_dir: Path to data directory
        clear_existing: If True, clear vector store before ingesting

    Returns:
        Ingestion statistics
    """
    service = IngestionService(data_dir=data_dir)
    return service.ingest_all(clear_existing=clear_existing)
