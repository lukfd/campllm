import argparse
import logging
import subprocess
from pathlib import Path

from src.util.clean import Cleaner
from src.database.database import Database
from src.util.index import Indexer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATABASE_URI = "http://localhost:8000"


def collect_data(park_file: Path, chrome_path: str | None = None):
    project_root = Path(__file__).resolve().parents[2]
    crawler_script = project_root / "src" / "script" / "collect.js"
    command = ["node", str(crawler_script), "--collect", "-o", str(park_file)]

    if chrome_path:
        command.extend(["--chrome-path", chrome_path])

    subprocess.run(command, cwd=project_root, check=True)


def main():
    parser = argparse.ArgumentParser(description="Clean and index the park file.")
    parser.add_argument(
        "--park-file", type=Path, help="Path to the park file", required=True
    )
    parser.add_argument(
        "--database-uri",
        type=str,
        help="Database URI",
        default=DATABASE_URI,
        required=False,
    )
    parser.add_argument(
        "--chrome-path",
        type=str,
        help="Path to the Chrome executable used by the crawler",
        required=False,
    )
    parser.add_argument(
        "--collect", action="store_true", help="Collect raw data before cleaning"
    )
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)

    if args.collect:
        logger.info("Collecting raw data with the Node crawler.")
        collect_data(args.park_file, args.chrome_path)
        logger.info("Collection completed.")

    logger.info(f"Cleaning park file: {args.park_file}")
    cleaned_file = Cleaner(args.park_file).clean()
    logger.info("Cleaning completed. Cleaned file: {cleaned_file}")

    logger.info("Indexing cleaned data into the database.")
    database = Database(args.database_uri)
    Indexer(file=cleaned_file, park_collection=database.parks).index()


if __name__ == "__main__":
    main()
