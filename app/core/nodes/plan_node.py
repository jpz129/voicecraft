from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_huggingface import HuggingFaceEndpoint
from pathlib import Path
import os

# Load the prompt template
plan_template = Path(__file__).parent.parent / "prompts" / "plan.txt"
prompt_text = plan_template.read_text()

prompt = PromptTemplate.from_template(prompt_text)

# Define the planning node
def plan_node():
    endpoint_url = os.getenv("HF_ENDPOINT_URL")
    api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

    llm = HuggingFaceEndpoint(
        endpoint_url=endpoint_url,
        huggingfacehub_api_token=api_token,
        temperature=0.3,
        max_new_tokens=300
    )

    chain = prompt | llm
    return RunnableLambda(lambda state: {
        "revision_plan": chain.invoke({"input": state["current_text"]})
    })
