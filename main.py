from workflows.job_monitor_graph import build_graph
from agents.servicenow_agent import get_all_incidents, get_incident_details
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)

def main():
    # logs = "ERROR: NullPointerException in DataIngestJob during GCS bucket read"
    # dag_id = "DataIngestJob"

    logging.info("-------> AI Ops Agentic Workflow STARTING.......")

    graph = build_graph()
    print(graph.get_graph().draw_ascii())

    incident_list=get_all_incidents()
    logging.info("List of Open incidents are : %s", incident_list if incident_list else "[]")

    for incident in incident_list:
        details = get_incident_details(incident)
        dag_id = details['short_description']
        logs = details['description']
        logging.info(f"Composer DAG-id : {details['short_description']}")
        logging.info(f"Logs from SNOW incident : {details['description']}")
        result = graph.invoke({"logs": logs, "dag_id": dag_id})
        logging.info(f"The result after invoking graph for incident number [{incident}] is {result}")

if __name__ == "__main__":
    main()
