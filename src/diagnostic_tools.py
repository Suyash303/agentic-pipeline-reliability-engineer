
import csv
import json
from pathlib import Path

# Locate the project directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Files that our diagnostic tools can inspect
INPUT_FILE = BASE_DIR / "data/raw/sales.csv"
LOG_FILE = BASE_DIR / "logs/sales_etl.log"

# Schema expected by our ETL pipeline
EXPECTED_COLUMNS = [
    "order_id",
    "customer_id",
    "product_id",
    "quantity",
    "unit_price"
]


# TOOL 1: Inspect the source CSV schema
def inspect_csv_schema():

    with open(INPUT_FILE, "r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        actual_columns = next(reader, [])

    missing_columns = [
        col for col in EXPECTED_COLUMNS
        if col not in actual_columns
    ]

    unexpected_columns = [
        col for col in actual_columns
        if col not in EXPECTED_COLUMNS
    ]

    return {
        "expected_columns": EXPECTED_COLUMNS,
        "actual_columns": actual_columns,
        "missing_columns": missing_columns,
        "unexpected_columns": unexpected_columns
    }


# TOOL 2: Read recent pipeline logs
def read_pipeline_logs():

    with open(LOG_FILE, "r", encoding="utf-8") as file:
        log_lines = file.readlines()

    return {
        "recent_logs": "".join(log_lines[-15:])
    }


# Test both tools
if __name__ == "__main__":

    result = {
        "schema_analysis": inspect_csv_schema(),
        "log_analysis": read_pipeline_logs()
    }

    print(json.dumps(result, indent=4))
