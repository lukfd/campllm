import argparse
import logging
import os

from src.database.database import Database


def main():
    parser = argparse.ArgumentParser(description="Test the database connection.")
    parser.add_argument(
        "--database-uri",
        type=str,
        help="Database URI",
        default=os.getenv("DATABASE_URI", "http://chroma:8000"),
        required=False,
    )
    parser.add_argument(
        "--query", type=str, help="Query text for testing", required=False
    )
    parser.add_argument(
        "--list", action="store_true", help="List all collections in the database"
    )
    parser.add_argument(
        "--peek", action="store_true", help="Peek at collection in the database"
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info(f"Testing database connection to URI: {args.database_uri}")
    database = Database(args.database_uri)

    if args.list:
        print(database.list_collections())

    if args.query:
        print(database.parks.query(args.query))

    if args.peek:
        print(database.parks.peek())


if __name__ == "__main__":
    main()
