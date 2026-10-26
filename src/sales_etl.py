import pandas as pd
import logging
from pathlib import Path

# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data/raw/sales.csv"
OUTPUT_FILE = BASE_DIR / "data/processed/processed_sales.csv"
LOG_FILE = BASE_DIR / "logs/sales_etl.log"

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def run_etl():
    logging.info("Sales ETL pipeline started")

    # Step 1: Extract
    df = pd.read_csv(INPUT_FILE)
    logging.info(f"Loaded {len(df)} records")

    # Step 2: Validate schema
    required_columns = [
        "order_id",
        "customer_id",
        "product_id",
        "quantity",
        "unit_price"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(f"Missing columns: {missing}")

    # Step 3: Transform
    df["total_amount"] = df["quantity"] * df["unit_price"]

    # Step 4: Load
    df.to_csv(OUTPUT_FILE, index=False)

    logging.info("Sales ETL pipeline completed successfully")
    print("ETL completed successfully!")


if __name__ == "__main__":
    try:
        run_etl()
    except Exception:
        logging.exception("Sales ETL pipeline failed")
        print("ETL failed! Check logs/sales_etl.log")
        raise
