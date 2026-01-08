#!/usr/bin/env python3
"""
Script to ingest bid spreadsheets into the vector store.

Usage:
    python scripts/ingest_data.py [--clear] [--year YEAR]

Options:
    --clear     Clear existing data before ingesting
    --year      Only ingest files from a specific year
"""

import argparse
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.ingestion import IngestionService
from backend.config import DATA_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Ingest bid spreadsheets into the vector store"
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear existing data before ingesting",
    )
    parser.add_argument(
        "--year",
        type=int,
        help="Only ingest files from a specific year",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=str(DATA_DIR),
        help="Path to data directory",
    )

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Axiom Proposal Assistant - Data Ingestion")
    logger.info("=" * 60)

    service = IngestionService(data_dir=Path(args.data_dir))

    # Progress callback
    def progress(current, total):
        if current % 100 == 0 or current == total:
            pct = (current / total) * 100
            logger.info(f"Progress: {current}/{total} ({pct:.1f}%)")

    if args.year:
        logger.info(f"Ingesting year {args.year}...")
        stats = service.ingest_year(args.year, clear_existing=args.clear)
    else:
        logger.info("Ingesting all years...")
        stats = service.ingest_all(
            clear_existing=args.clear,
            progress_callback=progress,
        )

    logger.info("=" * 60)
    logger.info("Ingestion Complete!")
    logger.info(f"  Total files processed: {stats.get('total_files', 0)}")
    logger.info(f"  Successfully ingested: {stats.get('successful', 0)}")
    logger.info(f"  Failed: {stats.get('failed', 0)}")
    logger.info(f"  With training labels: {stats.get('with_training_labels', 0)}")
    logger.info("=" * 60)

    # Print final stats
    final_stats = service.get_stats()
    logger.info("Vector Store Statistics:")
    logger.info(f"  Total documents: {final_stats.get('total_documents', 0)}")
    logger.info(f"  Documents with training data: {final_stats.get('documents_with_training_labels', 0)}")

    if final_stats.get("years"):
        logger.info("  Documents by year:")
        for year, count in sorted(final_stats["years"].items(), reverse=True):
            logger.info(f"    {year}: {count}")


if __name__ == "__main__":
    main()
