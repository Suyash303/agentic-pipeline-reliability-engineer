
from google import genai
from google.genai import types
from pipeline_status import check_pipeline_status
from run_history_tools import get_pipeline_history
# Import our multi-pipeline diagnostic functions
from multi_pipeline_tools import (
    list_available_pipelines,
    inspect_pipeline,
    read_registered_pipeline_logs
)

# Existing sales-specific data quality checker
from data_quality_tools import check_data_quality


# TOOL 1: Discover available pipelines
def list_pipelines() -> dict:
    """List all registered pipelines that can be investigated."""

    print("\n[TOOL CALLED] list_pipelines", flush=True)
    return list_available_pipelines()


# TOOL 2: Inspect a selected pipeline
def inspect_registered_pipeline(pipeline_name: str) -> dict:
    """Inspect source schema and numeric conversion errors.

    Args:
        pipeline_name: Registered pipeline name, such as sales or inventory.
    """

    print(
        f"\n[TOOL CALLED] inspect_pipeline: {pipeline_name}",
        flush=True
    )

    return inspect_pipeline(pipeline_name)


# TOOL 3: Read a selected pipeline's logs
def get_pipeline_logs(pipeline_name: str) -> dict:
    """Read recent execution logs of a registered pipeline.

    Args:
        pipeline_name: Registered pipeline name, such as sales or inventory.
    """

    print(
        f"\n[TOOL CALLED] read_pipeline_logs: {pipeline_name}",
        flush=True
    )

    return read_registered_pipeline_logs(pipeline_name)


# TOOL 4: Sales-specific business validation
def check_sales_quality() -> dict:
    """Check sales records for duplicates, missing identifiers,
    invalid quantities, and negative unit prices.
    This tool applies only to the sales pipeline.
    """

    print("\n[TOOL CALLED] check_sales_quality", flush=True)
    return check_data_quality()

# TOOL 5: Pipeline execution status and freshness
def investigate_pipeline_status(pipeline_name: str) -> dict:
    """
    Check the latest logged execution status and output
    freshness indicators for a registered pipeline.

    Args:
        pipeline_name: Registered pipeline name,
                       such as sales or inventory.
    """

    print(
        f"\n[TOOL CALLED] check_pipeline_status: {pipeline_name}",
        flush=True
    )

    return check_pipeline_status(pipeline_name)


# TOOL 6: Analyze historical pipeline runs
def investigate_run_history(pipeline_name: str) -> dict:
    """
    Analyze recorded execution history for a registered pipeline.

    Returns total runs, success and failure counts,
    latest execution, last recorded success,
    and repeated errors.

    Args:
        pipeline_name: Registered pipeline name,
                       such as sales or inventory.
    """

    print(
        f"\n[TOOL CALLED] get_pipeline_history: {pipeline_name}",
        flush=True
    )

    return get_pipeline_history(pipeline_name)


# Connect to Gemini
client = genai.Client(
    http_options=types.HttpOptions(
        timeout=90000,
        retry_options=types.HttpRetryOptions(attempts=1)
    )
)


# Create our interactive agent
chat = client.chats.create(
    model="gemini-3.5-flash-lite",
    config=types.GenerateContentConfig(
        tools=[
                list_pipelines,
    inspect_registered_pipeline,
    get_pipeline_logs,
    check_sales_quality,
    investigate_pipeline_status,
    investigate_run_history
        ],

        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            maximum_remote_calls=10
        ),

        system_instruction=(
            "You are an Agentic Data Pipeline Reliability Engineer. "
            "Your job is to investigate existing data pipelines. "
            "Use the registered diagnostic tools to gather evidence. "
            "When a pipeline is named, investigate that pipeline. "
            "Use the sales-specific quality tool only for sales. "
            "Explain confirmed failures, root causes, affected records, "
            "business impact, and recommended actions. "
            "Distinguish schema errors, numeric conversion errors, "
            "and business-rule data quality issues. "
            "Numeric conversion success does not guarantee valid data. "
            "Do not assume old logs describe the current dataset. "
            "Do not invent evidence. "
            "Do not modify files or automatically fix pipelines."
            "Use investigate_pipeline_status when asked about "
"pipeline health, execution status, or output freshness. "
"Always distinguish a historical failed execution "
"from problems found in the current input dataset. "
"Treat file modification times as freshness indicators, "
"not proof of data correctness. "
"Do not claim that an old output is current simply "
"because the output file exists. "
"Use investigate_run_history when users ask about "
"execution history, failure frequency, recurring errors, "
"or previous successful runs. "
"Historical analysis must rely on recorded executions. "
"If no successful run is recorded, explain that no success "
"exists in the available structured history, not that the "
"pipeline has never succeeded. "
"Never invent run IDs, timestamps, or failure counts. "
        )
    )
)


print("\n========================================")
print(" AGENTIC PIPELINE RELIABILITY ENGINEER")
print("========================================")
print("Registered pipelines: sales, inventory")
print("Type 'exit' to quit.\n")


while True:

    question = input("\nYou: ").strip()

    if question.lower() in ["exit", "quit"]:
        print("\nAgent stopped.")
        break

    if not question:
        continue

    try:
        response = chat.send_message(question)

        print("\n========== AGENT REPORT ==========\n")
        print(response.text or "No response received.")

    except Exception as e:
        print("\nAgent Error:", type(e).__name__)
        print("Details:", str(e))
