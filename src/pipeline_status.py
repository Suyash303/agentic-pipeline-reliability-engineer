
import json
from datetime import datetime

from pipeline_registry import PIPELINES


def check_pipeline_status(pipeline_name: str):
    """Check recent execution status and possible output staleness."""

    name = pipeline_name.strip().lower()

    if name not in PIPELINES:
        return {
            "error": "Unknown pipeline",
            "available_pipelines": list(PIPELINES.keys())
        }

    config = PIPELINES[name]

    input_file = config["input_file"]
    output_file = config["output_file"]
    log_file = config["log_file"]

    # 1. Determine latest execution status from logs
    status = "UNKNOWN"
    last_event_time = None

    if log_file.is_file():

        with open(log_file, "r", encoding="utf-8") as file:

            for line in file:

                if " | INFO | " in line and "pipeline started" in line:
                    status = "INCOMPLETE"
                    last_event_time = line.split(" | ")[0]

                elif " | INFO | " in line and "completed successfully" in line:
                    status = "SUCCESS"
                    last_event_time = line.split(" | ")[0]

                elif " | ERROR | " in line and "pipeline failed" in line:
                    status = "FAILED"
                    last_event_time = line.split(" | ")[0]

    # 2. Check whether files exist
    input_exists = input_file.is_file()
    output_exists = output_file.is_file()

    # 3. Compare file modification times
    input_newer_than_output = None

    if input_exists and output_exists:
        input_newer_than_output = (
            input_file.stat().st_mtime >
            output_file.stat().st_mtime
        )

    # 4. Identify possible stale output
    output_requires_review = (
        status != "SUCCESS"
        or not output_exists
        or input_newer_than_output is True
    )

    def modified_at(path):
        if not path.is_file():
            return None

        return datetime.fromtimestamp(
            path.stat().st_mtime
        ).isoformat(timespec="seconds")

    return {
        "pipeline": name,
        "last_run_status": status,
        "last_log_event_time": last_event_time,
        "input_exists": input_exists,
        "output_exists": output_exists,
        "input_last_modified": modified_at(input_file),
        "output_last_modified": modified_at(output_file),
        "input_newer_than_output": input_newer_than_output,
        "output_requires_review": output_requires_review
    }


if __name__ == "__main__":

    for name in PIPELINES:

        print(f"\n===== {name.upper()} STATUS =====")

        result = check_pipeline_status(name)

        print(json.dumps(result, indent=4))
