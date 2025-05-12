from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import PydanticOutputParser
from huggingface_hub import InferenceClient
from pathlib import Path
import os
import json
import logging

from app.models.schemas import RevisionPlan, WorkflowState

logger = logging.getLogger("voicecraft.backend.plan")

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
        # Format and log the prompt for debugging
        formatted_prompt = prompt.format(
            input=state.current_text,
            user_feedback=state.user_feedback or ""
        )
        logger.info(f"[Plan Prompt]\n{formatted_prompt}")
        response = client.text_generation(
            prompt=formatted_prompt,
            max_new_tokens=500,
            temperature=0.3,
        )
        # Defensive: handle empty/null/invalid response
        if not response or response.strip().lower() in ("null", "none", ""):
            logger.error("[Plan Node] LLM returned empty or null response.")
            return {"revision_plan": ["No revision plan could be generated. Please try again or check the LLM endpoint."]}
        try:
            parsed = parser.invoke(response)
            return {"revision_plan": parsed.revision_plan}
        except Exception as e:
            logger.error(f"[Plan Node] Failed to parse revision plan: {e}\nRaw response: {response}")
            return {"revision_plan": [f"Failed to parse revision plan: {e}"]}

    return RunnableLambda(generate)
