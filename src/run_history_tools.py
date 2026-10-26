
import json
from collections import Counter

from pipeline_registry import PIPELINES, BASE_DIR


HISTORY_FILE = BASE_DIR / "logs/run_history.jsonl"


# Extract the most useful error message
def extract_error(error_message):

    if not error_message:
        return None

    lines = error_message.splitlines()

    errors = [
        line.strip()
        for line in lines
        if line.strip().startswith(
            ("ValueError:", "TypeError:", "KeyError:")
        )
    ]

    if errors:
        return errors[-1]

    return "Unclassified error"


# Return only important fields from a run
def summarize_run(record):

    return {
        "run_id": record.get("run_id"),
        "started_at": record.get("started_at"),
        "finished_at": record.get("finished_at"),
        "status": record.get("status"),
        "error": extract_error(
            record.get("error_message")
        ),
        "output_updated": record.get(
            "output_updated_during_run"
        )
    }


# Main historical investigation function
def get_pipeline_history(pipeline_name: str):

    name = pipeline_name.strip().lower()

    if name not in PIPELINES:
        return {
            "error": "Unknown pipeline",
            "available_pipelines": list(PIPELINES.keys())
        }

    if not HISTORY_FILE.is_file():
        return {
            "pipeline": name,
            "total_recorded_runs": 0,
            "message": "No structured history exists yet"
        }

    records = []

    with open(HISTORY_FILE, "r", encoding="utf-8") as file:

        for line in file:

            if not line.strip():
                continue

            try:
                record = json.loads(line)

                if record.get("pipeline") == name:
                    records.append(record)

            except json.JSONDecodeError:
                continue

    # Count execution statuses
    status_counts = Counter(
        record.get("status", "UNKNOWN")
        for record in records
    )

    # Find the most recent recorded success
    last_success = next(
        (
            record for record in reversed(records)
            if record.get("status") == "SUCCESS"
        ),
        None
    )

    # Identify repeated errors
    errors = Counter(
        extract_error(record.get("error_message"))
        for record in records
        if record.get("status") == "FAILED"
    )

    repeated_errors = [
        {
            "error": error,
            "occurrences": count
        }
        for error, count in errors.items()
        if error and count > 1
    ]

    return {
        "pipeline": name,
        "total_recorded_runs": len(records),
        "status_counts": dict(status_counts),
        "latest_recorded_run": (
            summarize_run(records[-1])
            if records else None
        ),
        "last_successful_recorded_run": (
            summarize_run(last_success)
            if last_success else None
        ),
        "repeated_errors": repeated_errors,
        "recent_runs": [
            summarize_run(record)
            for record in reversed(records[-5:])
        ]
    }


# Test the historical analysis
if __name__ == "__main__":

    result = get_pipeline_history("inventory")

    print(json.dumps(result, indent=4))
