
from langchain.schema import HumanMessage,SystemMessage,AIMessage
from config.settings import LLM_API_TOKEN,VEC_DB_API_TOKEN
#from utils.api_utils import make_api_request
#from utils.extract_fx import extract_msg
import logging
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from langchain_community.chat_models import ChatOpenAI

from agents.composer_status_agent import check_job_status
from agents.composer_trigger_agent import trigger_job
from agents.jira_agent import create_jira
from agents.email_agent import send_email
from langchain.agents import initialize_agent, AgentType


tools = [ check_job_status,trigger_job , send_email,create_jira]

index_name = "job-runbook-index"
embedder = SentenceTransformer("all-MiniLM-L6-v2")

pc = Pinecone(api_key=VEC_DB_API_TOKEN)

index = pc.Index(index_name)

def generate_llm_response(stacktrace: str, top_k: int = 3):
    query_embedding = embedder.encode(stacktrace).tolist()

    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)

    matched_chunks = [match.metadata["text"] for match in results.matches]

    prompt = (
        #f"You are a cloud operations assistant."
        f"Given the following stacktrace:\n\n{stacktrace}\n\n"
        f"And the following job runbook entries:\n\n"
        + "".join(matched_chunks) +
       # "\n\nSuggest the most appropriate remediation action"
       "\n\nSuggest the most appropriate remediation action and execute it along with creating a Jira ticket"
       # "\n\nExecute only the tool required to remediate the issue as per remediation action of the specific Error and Job Name mentioned"
    )

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3,openai_api_key = LLM_API_TOKEN)

    messages = [
    SystemMessage(content="You are a cloud operations SRE Agent."),
    HumanMessage(content=prompt)
    ]


    agent = initialize_agent(
    tools, 
    llm, 
    agent=AgentType.OPENAI_FUNCTIONS, 
    verbose=True
    )
   
    response=agent.invoke(messages)
    return response



def analyze_logs(log_text: str) -> str:
    response = generate_llm_response(log_text)

    logging.info({
        "input": response["input"],
        "output": response["output"]
    })
    return AIMessage(content=response["output"])


