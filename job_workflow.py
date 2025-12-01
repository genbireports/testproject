from agents.log_parser_agent import analyze_logs
from agents.composer_status_agent import check_job_status
from agents.composer_trigger_agent import trigger_job
from agents.confluent_reader_agent import fetch_runbook
from agents.jira_agent import create_jira
from agents.email_agent import send_email
from agents.activity_tracker import activity_logger
import logging
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing import TypedDict
from typing import Annotated
from agents.servicenow_agent import get_incident_details


class MonitorState(TypedDict):
    logs: str
    dag_id: str
    issue: str
    status: str
    triggered: str
    index: str
    messages: Annotated[list, add_messages]


tools = [ check_job_status,trigger_job , send_email,create_jira]

def load_runbook(state: MonitorState) -> MonitorState:
    idx = fetch_runbook("98309")
    return {**state, "index": idx}

def parse_logs(state: MonitorState) -> MonitorState:
    response = analyze_logs(state["logs"])
    return {**state, "messages": [response]}


# def check_status(state: MonitorState) -> MonitorState:
#     status = check_job_status(state["dag_id"])
#     return {**state, "status": status}

def log_activity(state: MonitorState) -> MonitorState:
    activity_logger(state)
    return {**state, "triggered": "activity_logged"}


def debug_node(state: MonitorState) -> MonitorState:
    logging.info(f"DEBUG STATE: {state}")
    return state  



# def load_dag_id_logs(state: MonitorState) -> MonitorState:
#     details = get_incident_details("INC0010005")
#     return {
#         **state,
#         "dag_id": details["short_description"],
#         "logs": details["description"]
#     }

def build_graph():

    graph = StateGraph(MonitorState)

    # graph.add_node("load_dag_id_logs", load_dag_id_logs)
    graph.add_node("load_run_book", load_runbook)
    graph.add_node("parse_logs", parse_logs)
    #graph.add_node("tools", ToolNode(tools))
    graph.add_node("debug_node", debug_node)
    graph.add_node("log_activity", log_activity)

    # graph.set_entry_point("load_dag_id_logs")
    graph.set_entry_point("load_run_book")

    # graph.add_edge("load_dag_id_logs", "load_run_book")
    graph.add_edge("load_run_book", "parse_logs")
    graph.add_edge("parse_logs", "debug_node")
   # graph.add_edge("debug_node", "tools")
    #graph.add_edge("tools", "debug_node")
    graph.add_edge("debug_node","log_activity")
    graph.set_finish_point("log_activity")

    return graph.compile()
