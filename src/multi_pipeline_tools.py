
import json
import pandas as pd

from pipeline_registry import PIPELINES


# TOOL 1: List registered pipelines
def list_available_pipelines():

    return {
        "available_pipelines": list(PIPELINES.keys())
    }


# TOOL 2: Inspect a selected pipeline
def inspect_pipeline(pipeline_name: str):

    """Inspect schema and numeric data types for a registered pipeline."""

    pipeline_name = pipeline_name.strip().lower()

    if pipeline_name not in PIPELINES:
        return {
            "error": "Unknown pipeline",
            "available_pipelines": list(PIPELINES.keys())
        }

    config = PIPELINES[pipeline_name]
    input_file = config["input_file"]

    if not input_file.is_file():
        return {
            "pipeline": pipeline_name,
            "error": "Input file does not exist"
        }

    df = pd.read_csv(input_file)

    expected = config["expected_columns"]
    actual = df.columns.tolist()

    missing = [c for c in expected if c not in actual]
    unexpected = [c for c in actual if c not in expected]

    # Detect values that cannot be converted to numbers
    invalid_numeric = {}

    for column in config["numeric_columns"]:

        if column not in df.columns:
            continue

        converted = pd.to_numeric(
            df[column], errors="coerce"
        )

        invalid_rows = []

        for index in df.index[converted.isna()]:

            value = df.at[index, column]

            invalid_rows.append({
                "csv_line": int(index) + 2,
                "record_id": str(
                    df.at[index, config["id_column"]]
                ),
                "invalid_value": (
                    None if pd.isna(value) else str(value)
                )
            })

        invalid_numeric[column] = invalid_rows

    return {
        "pipeline": pipeline_name,
        "total_records": len(df),
        "expected_columns": expected,
        "actual_columns": actual,
        "missing_columns": missing,
        "unexpected_columns": unexpected,
        "non_numeric_values": invalid_numeric
    }


# TOOL 3: Read logs for a selected pipeline
def read_registered_pipeline_logs(pipeline_name: str):

    """Read recent logs for a registered pipeline."""

    pipeline_name = pipeline_name.strip().lower()

    if pipeline_name not in PIPELINES:
        return {"error": "Unknown pipeline"}

    log_file = PIPELINES[pipeline_name]["log_file"]

    if not log_file.is_file():
        return {"error": "Log file does not exist"}

    with open(log_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    return {
        "pipeline": pipeline_name,
        "recent_logs": "".join(lines[-30:])
    }


# Test our general diagnostic tool
if __name__ == "__main__":

    print("\nREGISTERED PIPELINES:")
    print(json.dumps(list_available_pipelines(), indent=4))

    for name in PIPELINES:

        print(f"\n===== {name.upper()} =====")

        result = inspect_pipeline(name)

        print(json.dumps(result, indent=4))
