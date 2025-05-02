from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from huggingface_hub import InferenceClient
from pathlib import Path
import os
import requests
from app.models.schemas import WorkflowState

# Load the prompt template
prompt_path = Path(__file__).parent.parent / "prompts" / "revise.txt"
prompt_text = prompt_path.read_text()
prompt = PromptTemplate(
    template=prompt_text,
    input_variables=["revision_plan", "current_text", "user_feedback"]
)

def revise_node():
    endpoint_url = os.getenv("HF_ENDPOINT_URL")
    api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    client = InferenceClient(model=endpoint_url, token=api_token)

    def generate(state: WorkflowState):
        try:
            formatted_prompt = prompt.format(
                current_text=state.current_text,
                revision_plan="\n".join(state.revision_plan or []),
                user_feedback=state.user_feedback or ""
            )
            revised = client.text_generation(
                prompt=formatted_prompt,
                max_new_tokens=600,
                temperature=0.3
            )
            return {"revised_text": revised}
        except requests.exceptions.RequestException as e:
            return {"revised_text": f"Error: Could not connect to Hugging Face endpoint. {str(e)}"}

    return RunnableLambda(generate)