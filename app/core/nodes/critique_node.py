from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import PydanticOutputParser
from huggingface_hub import InferenceClient
from pathlib import Path
import os

from app.models.schemas import CritiqueFeedback, WorkflowState

# Load and prepare the critique prompt
critique_template = Path(__file__).parent.parent / "prompts" / "critique.txt"
prompt_text = critique_template.read_text() if critique_template.exists() else (
    "You are an expert writing assistant. Given the following text and its revision plan, provide a list of constructive critiques or suggestions for improvement."
)
parser = PydanticOutputParser(pydantic_object=CritiqueFeedback)
escaped_format_instructions = parser.get_format_instructions().replace("{", "{{").replace("}", "}}")
full_prompt = prompt_text + "\n\n" + escaped_format_instructions
prompt = PromptTemplate(template=full_prompt, input_variables=["revised_text", "revision_plan", "user_feedback"])

# Define the critique node
def critique_node():
    endpoint_url = os.getenv("HF_ENDPOINT_URL")
    api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    client = InferenceClient(model=endpoint_url, token=api_token)

    def generate(state: WorkflowState):
        formatted_prompt = prompt.format(
            revised_text=state.revised_text,
            revision_plan="\n".join(state.revision_plan or []),
            user_feedback=state.user_feedback or ""
        )
        # Call LLM with error handling to avoid crashing on network issues
        try:
            response = client.text_generation(
                prompt=formatted_prompt,
                max_new_tokens=500,
                temperature=0.3,
            )
        except requests.exceptions.RequestException as e:
            return {"critique_feedback": [f"Error: Could not connect to Hugging Face endpoint. {str(e)}"]}
        # Defensive: handle empty/null response
        if not response or response.strip().lower() in ("null", "none"):
            return {"critique_feedback": ["No critique feedback was generated."]}
        try:
            return {"critique_feedback": parser.invoke(response).feedback}
        except Exception as e:
            return {"critique_feedback": [f"Failed to parse critique feedback: {e}"]}

    return RunnableLambda(generate)
