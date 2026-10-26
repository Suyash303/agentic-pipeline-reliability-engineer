
import json
from datetime import datetime, timezone

from pipeline_registry import PIPELINES, BASE_DIR
from pipeline_status import check_pipeline_status


STATE_FILE = BASE_DIR / "logs/monitor_state.json"
ALERT_FILE = BASE_DIR / "logs/alerts.jsonl"
HISTORY_FILE = BASE_DIR / "logs/run_history.jsonl"


def load_previous_state():
    if not STATE_FILE.exists():
        return {}

    with open(STATE_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_state(state):
    temp_file = STATE_FILE.with_suffix(".tmp")

    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(state, file, indent=4)

    temp_file.replace(STATE_FILE)


# NEW: Find the latest recorded run for each pipeline
def get_latest_runs():
    latest = {}

    if not HISTORY_FILE.is_file():
        return latest

    with open(HISTORY_FILE, "r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                print("Warning: Skipping invalid history record")
                continue

            name = record.get("pipeline")

            if name in PIPELINES and record.get("run_id"):
                latest[name] = record

    return latest


def create_alert(pipeline_name, alert_type, report, run_id=None):
    alert = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(timespec="seconds"),
        "pipeline": pipeline_name,
        "alert_type": alert_type,
        "run_id": run_id,
        "last_run_status": report["last_run_status"],
        "output_requires_review": report["output_requires_review"]
    }

    with open(ALERT_FILE, "a", encoding="utf-8") as file:
        file.write(json.dumps(alert) + "\n")

    print(f"  ALERT: {alert_type}")


def monitor_pipelines():
    previous_state = load_previous_state()
    latest_runs = get_latest_runs()

    current_state = {}

    for name in PIPELINES:
        report = check_pipeline_status(name)

        unhealthy = (
            report["last_run_status"] != "SUCCESS"
            or report["output_requires_review"]
        )

        health = "UNHEALTHY" if unhealthy else "HEALTHY"

        previous = previous_state.get(name)
        latest_run = latest_runs.get(name)

        run_id = (
            latest_run.get("run_id")
            if latest_run else None
        )

        print(f"\nPipeline: {name}")
        print(f"Status: {health}")
        print(f"Last run: {report['last_run_status']}")

        if previous is None:
            # First monitoring observation
            if unhealthy:
                create_alert(
                    name, "UNHEALTHY_DETECTED",
                    report, run_id
                )

        elif previous["health"] != health:
            # Health changed
            alert_type = (
                "PIPELINE_RECOVERED"
                if health == "HEALTHY"
                else "PIPELINE_UNHEALTHY"
            )

            create_alert(name, alert_type, report, run_id)

        elif (
            latest_run is not None
            and run_id != previous.get("last_seen_run_id")
            and latest_run.get("status") in ("FAILED", "TIMEOUT")
        ):
            # New failure even if pipeline was already unhealthy
            create_alert(
                name, "NEW_FAILED_RUN",
                report, run_id
            )

        else:
            print("  No new alert required")

        current_state[name] = {
            "health": health,
            "last_run_status": report["last_run_status"],
            "last_seen_run_id": run_id
        }

    save_state(current_state)


if __name__ == "__main__":
    monitor_pipelines()
