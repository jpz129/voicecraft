from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from huggingface_hub import InferenceClient
from pathlib import Path
import os

from app.models.schemas import WorkflowState

# Load prompt template for QA
qa_template_path = Path(__file__).parent.parent / "prompts" / "retrieval.txt"
qa_prompt_text = qa_template_path.read_text() if qa_template_path.exists() else (
    "You are an expert writing assistant. Given the draft and a question, provide a concise answer."
)
qa_prompt = PromptTemplate(
    template=qa_prompt_text,
    input_variables=["current_text", "user_feedback"]
)

# Define the QA node
def qa_node():
    endpoint_url = os.getenv("HF_ENDPOINT_URL")
    api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    client = InferenceClient(model=endpoint_url, token=api_token)

    def generate(state: WorkflowState):
        # Format the QA prompt
        formatted = qa_prompt.format(
            current_text=state.current_text,
            user_feedback=state.user_feedback or ""
        )
        # Call LLM to answer question
        try:
            answer = client.text_generation(
                prompt=formatted,
                max_new_tokens=200,
                temperature=0.3
            )
        except Exception as e:
            answer = f"Error: Failed to generate answer. {e}"
        return {"answer": answer.strip()}

    return RunnableLambda(generate)