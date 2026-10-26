
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

PIPELINES = {

    "sales": {
        "input_file": BASE_DIR / "data/raw/sales.csv",
        "log_file": BASE_DIR / "logs/sales_etl.log",
        "output_file": BASE_DIR / "data/processed/processed_sales.csv",

        "expected_columns": [
            "order_id",
            "customer_id",
            "product_id",
            "quantity",
            "unit_price"
        ],

        "numeric_columns": [
            "quantity",
            "unit_price"
        ],

        "id_column": "order_id"
    },

    "inventory": {
        "input_file": BASE_DIR / "data/raw/inventory.csv",
        "log_file": BASE_DIR / "logs/inventory_etl.log",
        "output_file": BASE_DIR / "data/processed/processed_inventory.csv",

        "expected_columns": [
            "product_id",
            "warehouse_id",
            "stock_quantity",
            "reorder_level"
        ],

        "numeric_columns": [
            "stock_quantity",
            "reorder_level"
        ],

        "id_column": "product_id"
    }
}
