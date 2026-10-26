
import json
import os
import sys
import time
import tempfile
import unittest

from pathlib import Path
from unittest.mock import patch

# Import project modules
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "src"))

import pipeline_registry
import data_quality_tools
import run_history_tools

from multi_pipeline_tools import (
    list_available_pipelines,
    inspect_pipeline
)

from pipeline_status import check_pipeline_status


class TestPipelineReliability(unittest.TestCase):

    def setUp(self):
        """
        Create isolated test files before each test.
        Real project data will not be modified.
        """

        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)

        base = Path(temp.name)

        sales_file = base / "sales.csv"
        inventory_file = base / "inventory.csv"
        inventory_output = base / "processed_inventory.csv"
        inventory_log = base / "inventory.log"
        history_file = base / "history.jsonl"

        # Simulated sales dataset with known errors
        sales_file.write_text(
            "order_id,client_id,product_id,quantity,unit_price\n"
            "1001,C001,P101,2,450\n"
            "1002,C002,P102,1,1200\n"
            "1003,C003,P101,3,450\n"
            "1004,C004,P103,1,800\n"
            "1005,C005,P102,2,1200\n"
            "1006,C006,P104,-2,500\n"
            "1007,C007,P105,1,-300\n"
            "1003,C003,P101,3,450\n"
            "1008,,P106,2,600\n",
            encoding="utf-8"
        )

        # Valid inventory dataset
        inventory_file.write_text(
            "product_id,warehouse_id,stock_quantity,reorder_level\n"
            "P101,W01,50,10\n"
            "P102,W01,30,15\n"
            "P103,W01,25,10\n"
            "P104,W02,8,20\n",
            encoding="utf-8"
        )

        inventory_output.write_text(
            "product_id,stock_quantity\n"
            "P103,25\n",
            encoding="utf-8"
        )

        inventory_log.write_text(
            "2026-10-26 18:18:38 | INFO | "
            "Inventory ETL pipeline started\n"
            "2026-10-26 18:18:38 | INFO | "
            "Inventory ETL completed successfully\n",
            encoding="utf-8"
        )

        # Make output newer than input
        now = time.time()

        os.utime(inventory_file, (now - 20, now - 20))
        os.utime(inventory_output, (now - 10, now - 10))

        # Simulated structured run history
        error = (
            'ValueError: Unable to parse string '
            '"unknown" at position 2'
        )

        records = [
            {
                "run_id": "run-001",
                "pipeline": "inventory",
                "status": "FAILED",
                "error_message": error,
                "output_updated_during_run": False
            },
            {
                "run_id": "run-002",
                "pipeline": "inventory",
                "status": "FAILED",
                "error_message": error,
                "output_updated_during_run": False
            },
            {
                "run_id": "run-003",
                "pipeline": "inventory",
                "status": "SUCCESS",
                "error_message": None,
                "output_updated_during_run": True
            }
        ]

        history_file.write_text(
            "".join(json.dumps(r) + "\n" for r in records),
            encoding="utf-8"
        )

        # Temporary pipeline configurations
        configs = {
            "sales": {
                "input_file": sales_file,
                "output_file": base / "processed_sales.csv",
                "log_file": base / "sales.log",
                "expected_columns": [
                    "order_id", "customer_id", "product_id",
                    "quantity", "unit_price"
                ],
                "numeric_columns": [
                    "quantity", "unit_price"
                ],
                "id_column": "order_id"
            },
            "inventory": {
                "input_file": inventory_file,
                "output_file": inventory_output,
                "log_file": inventory_log,
                "expected_columns": [
                    "product_id", "warehouse_id",
                    "stock_quantity", "reorder_level"
                ],
                "numeric_columns": [
                    "stock_quantity", "reorder_level"
                ],
                "id_column": "product_id"
            }
        }

        # Redirect diagnostics to temporary files
        patchers = [
            patch.dict(
                pipeline_registry.PIPELINES,
                configs,
                clear=True
            ),
            patch.object(
                data_quality_tools, "INPUT_FILE", sales_file
            ),
            patch.object(
                run_history_tools, "HISTORY_FILE", history_file
            )
        ]

        for patcher in patchers:
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_pipeline_registry(self):
        result = list_available_pipelines()

        self.assertIn("sales", result["available_pipelines"])
        self.assertIn("inventory", result["available_pipelines"])

    def test_sales_schema(self):
        result = inspect_pipeline("sales")

        self.assertIn("customer_id", result["missing_columns"])
        self.assertIn("client_id", result["unexpected_columns"])

    def test_sales_quality(self):
        result = data_quality_tools.check_data_quality()

        self.assertEqual(result["total_records"], 9)

        affected = result["affected_orders"]

        self.assertIn("1003", affected["duplicate_order_ids"])
        self.assertIn("1006", affected["invalid_quantity"])
        self.assertIn("1007", affected["invalid_price"])
        self.assertIn("1008", affected["missing_customer"])

    def test_inventory_numeric_data(self):
        result = inspect_pipeline("inventory")

        self.assertEqual(
            result["non_numeric_values"]["stock_quantity"],
            []
        )

    def test_inventory_history(self):
        result = run_history_tools.get_pipeline_history(
            "inventory"
        )

        self.assertEqual(result["total_recorded_runs"], 3)

        self.assertEqual(
            result["status_counts"]["FAILED"], 2
        )

        self.assertEqual(
            result["latest_recorded_run"]["status"],
            "SUCCESS"
        )

    def test_inventory_status(self):
        result = check_pipeline_status("inventory")

        self.assertEqual(
            result["last_run_status"], "SUCCESS"
        )

        self.assertFalse(result["output_requires_review"])

    def test_unknown_pipeline(self):
        result = inspect_pipeline("unknown_pipeline")

        self.assertEqual(result["error"], "Unknown pipeline")


if __name__ == "__main__":
    unittest.main()
