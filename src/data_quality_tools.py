
import pandas as pd
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data/raw/sales.csv"


def check_data_quality():
    """Inspect sales data and identify exact faulty orders."""

    df = pd.read_csv(INPUT_FILE)

    # 1. Basic information
    total_records = len(df)

    null_counts = {
        col: int(count)
        for col, count in df.isna().sum().items()
    }

    # 2. Detect duplicate order IDs
    duplicate_mask = df["order_id"].duplicated(keep=False)

    duplicate_ids = (
        df.loc[duplicate_mask, "order_id"]
        .drop_duplicates()
        .astype(str)
        .tolist()
    )

    duplicate_count = int(
        df["order_id"].duplicated().sum()
    )

    # 3. Detect invalid quantities
    quantity = pd.to_numeric(
        df["quantity"], errors="coerce"
    )

    invalid_quantity_mask = (
        quantity.isna() | (quantity <= 0)
    )

    invalid_quantity_ids = (
        df.loc[invalid_quantity_mask, "order_id"]
        .astype(str)
        .tolist()
    )

    # 4. Detect invalid prices
    price = pd.to_numeric(
        df["unit_price"], errors="coerce"
    )

    invalid_price_mask = (
        price.isna() | (price < 0)
    )

    invalid_price_ids = (
        df.loc[invalid_price_mask, "order_id"]
        .astype(str)
        .tolist()
    )

    # 5. Detect missing customer identifiers
    customer_col = (
        "customer_id"
        if "customer_id" in df.columns
        else "client_id"
    )

    missing_customer_mask = df[customer_col].isna()

    missing_customer_ids = (
        df.loc[missing_customer_mask, "order_id"]
        .astype(str)
        .tolist()
    )

    # 6. Return evidence for the AI agent
    return {
        "total_records": total_records,
        "null_counts": null_counts,
        "duplicate_order_ids": duplicate_count,
        "invalid_quantity_rows": len(invalid_quantity_ids),
        "invalid_unit_price_rows": len(invalid_price_ids),
        "affected_orders": {
            "duplicate_order_ids": duplicate_ids,
            "invalid_quantity": invalid_quantity_ids,
            "invalid_price": invalid_price_ids,
            "missing_customer": missing_customer_ids
        },
        "validation_rules": {
            "quantity": "Must be numeric and greater than zero",
            "unit_price": "Must be numeric and non-negative",
            "order_id": "Must be unique",
            "customer_id": "Must not be missing"
        }
    }


if __name__ == "__main__":
    result = check_data_quality()
    print(json.dumps(result, indent=4))
