
import pandas as pd
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data/raw/inventory.csv"
OUTPUT_FILE = BASE_DIR / "data/processed/processed_inventory.csv"
LOG_FILE = BASE_DIR / "logs/inventory_etl.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def run_etl():
    logging.info("Inventory ETL pipeline started")

    # Extract
    df = pd.read_csv(INPUT_FILE)
    logging.info(f"Loaded {len(df)} inventory records")

    # Validate schema
    required_columns = [
        "product_id",
        "warehouse_id",
        "stock_quantity",
        "reorder_level"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    # Validate numeric data types
    df["stock_quantity"] = pd.to_numeric(
        df["stock_quantity"], errors="raise"
    )

    df["reorder_level"] = pd.to_numeric(
        df["reorder_level"], errors="raise"
    )

    # Transform
    df["needs_restock"] = (
        df["stock_quantity"] <= df["reorder_level"]
    )

    # Load
    df.to_csv(OUTPUT_FILE, index=False)

    logging.info("Inventory ETL completed successfully")
    print("Inventory ETL completed successfully!")


if __name__ == "__main__":
    try:
        run_etl()

    except Exception:
        logging.exception("Inventory ETL pipeline failed")
        print("Inventory ETL failed! Check logs/inventory_etl.log")
        raise
