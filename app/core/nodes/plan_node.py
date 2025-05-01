from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import PydanticOutputParser
from huggingface_hub import InferenceClient
from pathlib import Path
import os
import json

from app.models.schemas import RevisionPlan, WorkflowState

# Load and prepare prompt
plan_template = Path(__file__).parent.parent / "prompts" / "plan.txt"
prompt_text = plan_template.read_text()
parser = PydanticOutputParser(pydantic_object=RevisionPlan)
escaped_format_instructions = parser.get_format_instructions().replace("{", "{{").replace("}", "}}")
full_prompt = prompt_text + "\n\n" + escaped_format_instructions
prompt = PromptTemplate(template=full_prompt, input_variables=["input", "user_feedback"])

# Define the planning node
def plan_node():
    endpoint_url = os.getenv("HF_ENDPOINT_URL")
    api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    client = InferenceClient(model=endpoint_url, token=api_token)

    def generate(state: WorkflowState):
        formatted_prompt = prompt.format(
            input=state.current_text,
            user_feedback=state.user_feedback or ""
        )
        response = client.text_generation(
            prompt=formatted_prompt,
            max_new_tokens=500,
            temperature=0.3,
        )
        return {"revision_plan": parser.invoke(response).revision_plan}

    return RunnableLambda(generate)
