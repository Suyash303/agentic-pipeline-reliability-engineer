
# Agentic Data Pipeline Reliability Engineer

An AI-powered Data Engineering reliability system that investigates ETL pipeline failures, identifies root causes, detects data quality problems, monitors pipeline health, and verifies recovery using execution history.

Built with Python, Pandas, Google Gemini API, and automated diagnostic tools.

## 1. Business Problem

Organizations rely on ETL pipelines to process operational and analytical data.

These pipelines may fail because of:

- Unexpected schema changes
- Invalid data types
- Missing or duplicate records
- Data quality violations
- Pipeline execution errors
- Stale output datasets

Traditional troubleshooting often requires engineers to manually inspect logs, source datasets, and execution history.

This project demonstrates how an AI agent can assist Data Engineers with evidence-based failure investigation.

## 2. Solution

The Agentic Data Pipeline Reliability Engineer combines deterministic Python diagnostics with Gemini function calling.

Users can ask natural-language questions such as:

- Why did my Sales pipeline fail?
- Which Inventory records contain invalid values?
- Which pipelines are unhealthy?
- Has my Inventory pipeline recovered?
- Are the same failures happening repeatedly?

The agent chooses diagnostic tools, examines their results, and generates a troubleshooting report with supporting evidence and recommended actions.

The agent is read-only. It does not automatically modify production data or apply fixes.

## 3. System Architecture

```text
                  USER
                   |
         Natural Language Query
                   |
                   v
             GEMINI AI AGENT
                   |
          Function Calling
                   |
       +-----------+-----------+
       |           |           |
       v           v           v
   Log Analysis  Schema     Data Quality
                 Analysis    Validation
       |           |           |
       +-----------+-----------+
                   |
          Pipeline Registry
                   |
          +--------+--------+
          |                 |
          v                 v
      Sales ETL       Inventory ETL
          |                 |
          +--------+--------+
                   |
          Execution Tracking
                   |
             Run History
                   |
          Status & Freshness
                   |
           Health Monitoring
                   |
            Alert History
```

Gemini handles interactive investigation and explanation.

Deterministic Python programs handle validation, execution tracking, monitoring, and alert generation.

## 4. Core Features

### Agentic Root Cause Analysis
- Natural-language troubleshooting
- Gemini function calling
- Evidence-based investigation reports
- Recommended corrective actions

### Multi-Pipeline Diagnostics
- Registry-based pipeline selection
- Sales and Inventory demonstration pipelines
- Schema mismatch identification
- Non-numeric data detection

### Data Quality Investigation
- Duplicate order identification
- Missing customer identifiers
- Invalid quantities
- Negative unit prices
- Identification of affected order IDs

Sales-specific business validation rules are implemented for the demonstration dataset.

### Pipeline Reliability Monitoring
- Latest logged execution status
- Input and output modification timestamps
- Potential stale-output detection
- Health transition monitoring

### Structured Execution History
- Unique run IDs
- Execution status and timestamps
- Captured failure messages
- Repeated-error detection
- Latest recorded successful execution

### Automated Alert Generation
- Initial unhealthy pipeline alerts
- Recovery alerts
- New failed-run alerts
- Basic alert deduplication
- Ubuntu cron-based scheduled checks

Alerts are currently stored locally in JSONL files.

## 5. Technology Stack

| Component | Technology |
|-----------|------------|
| Programming | Python 3.10 |
| AI Model Integration | Google Gemini API |
| AI SDK | google-genai |
| Data Processing | Pandas |
| Source Data | CSV |
| Execution History | JSONL |
| Scheduling | Ubuntu cron |
| Testing | unittest |
| Operating System | Ubuntu Linux |

## 6. Getting Started

### Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd pipeline-reliability-agent
```

Replace `YOUR_REPOSITORY_URL` with the actual GitHub URL after publication.

### Create a virtual environment

```bash
python3.10 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Configure Gemini API access

Create a Gemini API key using Google AI Studio.

```bash
read -rsp "Gemini API key: " GEMINI_API_KEY
echo
export GEMINI_API_KEY
```

Never commit API keys to GitHub.

### Start the AI agent

```bash
python -u src/reliability_agent.py
```

## 7. Demonstration Pipelines

The repository includes two sample ETL pipelines.

### Sales ETL

Processes sales transactions and calculates total order amounts.

The demonstration input intentionally contains a schema mismatch and several data quality violations.

Example issues:

- Expected `customer_id`, found `client_id`
- Duplicate order 1003
- Invalid quantity in order 1006
- Negative price in order 1007
- Missing customer identifier in order 1008

### Inventory ETL

Processes warehouse stock quantities and calculates restocking indicators.

A numeric conversion failure can be demonstrated by replacing product P103's stock quantity with `unknown`.

The original valid sample quantity is 25.

## 8. Pipeline Execution Tracking

Run a registered pipeline using:

```bash
python src/pipeline_runner.py inventory
```

Or:

```bash
python src/pipeline_runner.py sales
```

Each execution generates a unique run ID and appends its result to:

```text
logs/run_history.jsonl
```

The Sales demonstration dataset initially contains intentional errors, so its pipeline is expected to fail.

Inspect Inventory execution history:

```bash
python src/run_history_tools.py
```

## 9. Health Monitoring

Check all registered pipelines:

```bash
python src/pipeline_status.py
```

Run the alert monitor:

```bash
python src/pipeline_monitor.py
```

New alerts are stored in:

```text
logs/alerts.jsonl
```

For periodic monitoring on Ubuntu, configure cron to execute `src/pipeline_monitor.py` using the virtual environment's Python interpreter.

The scheduler runs only while the host environment is active.

## 10. Automated Testing

Run the test suite:

```bash
python -m unittest discover -s tests -v
```

The tests use isolated temporary datasets and simulated execution history.

The test suite checks:

- Pipeline registration
- Schema mismatch detection
- Sales data quality rules
- Inventory numeric validation
- Structured history analysis
- Pipeline status checking
- Unknown pipeline handling

These tests validate deterministic diagnostic components, not LLM reasoning quality.

## 11. Example Agent Interaction

**User:**

Investigate why my Inventory pipeline failed.

**Agent workflow:**

1. Select the Inventory pipeline.
2. Read execution logs.
3. Inspect source data.
4. Identify invalid numeric values.
5. Explain the root cause.
6. Recommend corrective action.

**Example finding:**

```text
Pipeline: Inventory
Status: FAILED

Root Cause:
Invalid value "unknown" in stock_quantity.

Affected Product:
P103

Recommended Action:
Verify and correct the source stock quantity,
then rerun the pipeline and check its output.
```

This illustrates a test scenario rather than a live production failure.

## 12. Safety and Limitations

- AI tools use registered, read-only diagnostic functions.
- The agent recommends fixes but does not apply them.
- File timestamps are freshness indicators, not proof of correctness.
- Monitoring uses local logs and files.
- JSONL run history records executions launched through the project runner.
- Business-specific quality rules are not yet fully generalized.
- The system is a portfolio prototype, not a production deployment.

## 13. Future Improvements

- Apache Airflow integration
- PySpark pipeline monitoring
- Kafka-based monitoring events
- Database-backed execution history
- Advanced data quality rules
- Email or Slack notifications
- SLA-aware incident prioritization
- Interactive monitoring dashboard

## 14. Project Goal

Demonstrate the combination of Data Engineering, observability, deterministic validation, and Agentic AI to investigate pipeline reliability problems and support evidence-based operational decisions.
