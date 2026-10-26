
import sys
import json
import uuid
import subprocess

from datetime import datetime
from pathlib import Path

from pipeline_registry import PIPELINES, BASE_DIR


# Only these existing scripts can be executed
PIPELINE_SCRIPTS = {
    "sales": BASE_DIR / "src/sales_etl.py",
    "inventory": BASE_DIR / "src/inventory_etl.py"
}

HISTORY_FILE = BASE_DIR / "logs/run_history.jsonl"


def current_time():
    return datetime.now().astimezone().isoformat(
        timespec="seconds"
    )


def modified_at(path):
    if not path.is_file():
        return None

    return datetime.fromtimestamp(
        path.stat().st_mtime
    ).astimezone().isoformat(timespec="seconds")


def run_pipeline(name):

    if name not in PIPELINES or name not in PIPELINE_SCRIPTS:
        print(f"Unknown pipeline: {name}")
        return 1

    config = PIPELINES[name]

    input_file = config["input_file"]
    output_file = config["output_file"]

    # Generate a unique identifier for this execution
    run_id = str(uuid.uuid4())

    previous_output_time = (
        output_file.stat().st_mtime_ns
        if output_file.is_file() else None
    )

    record = {
        "run_id": run_id,
        "pipeline": name,
        "started_at": current_time(),
        "input_modified_at_start": modified_at(input_file),
        "output_modified_before": modified_at(output_file)
    }

    print(f"\nStarting pipeline: {name}")
    print(f"Run ID: {run_id}")

    status = "UNKNOWN"
    exit_code = None
    error_message = None

    try:
        result = subprocess.run(
            [sys.executable, str(PIPELINE_SCRIPTS[name])],
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            timeout=60
        )

        exit_code = result.returncode

        status = (
            "SUCCESS" if exit_code == 0 else "FAILED"
        )

        if result.stdout:
            print(result.stdout)

        if result.stderr:
            error_message = result.stderr[-1200:]
            print(error_message)

    except subprocess.TimeoutExpired:
        status = "TIMEOUT"
        error_message = "Pipeline exceeded 60 seconds"
        print(error_message)

    finally:
        current_output_time = (
            output_file.stat().st_mtime_ns
            if output_file.is_file() else None
        )

        record.update({
            "finished_at": current_time(),
            "status": status,
            "exit_code": exit_code,
            "error_message": error_message,
            "output_modified_after": modified_at(output_file),
            "output_updated_during_run": (
                current_output_time is not None
                and current_output_time != previous_output_time
            )
        })

        HISTORY_FILE.parent.mkdir(
            parents=True, exist_ok=True
        )

        with open(
            HISTORY_FILE, "a", encoding="utf-8"
        ) as file:
            file.write(json.dumps(record) + "\n")

        print(f"\nRecorded run status: {status}")
        print(f"History saved to: {HISTORY_FILE}")

    return exit_code if exit_code is not None else 1


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python src/pipeline_runner.py <pipeline>")
        print("Available: sales, inventory")
        sys.exit(1)

    pipeline_name = sys.argv[1].strip().lower()

    sys.exit(run_pipeline(pipeline_name))
