from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import PydanticOutputParser
from huggingface_hub import InferenceClient
from pathlib import Path
import os
import re
from app.models.schemas import DecisionOutput, WorkflowState

# Decision node: determines if another revision cycle is needed
decision_prompt_path = Path(__file__).parent.parent / "prompts" / "decision.txt"
decision_prompt_text = decision_prompt_path.read_text()
decision_prompt = PromptTemplate(
    template=decision_prompt_text,
    input_variables=["revised_text", "revision_plan", "critique_feedback"]
)
parser = PydanticOutputParser(pydantic_object=DecisionOutput)
escaped_format_instructions = parser.get_format_instructions().replace("{", "{{").replace("}", "}}")
full_prompt = decision_prompt_text + "\n\n" + escaped_format_instructions
decision_prompt = PromptTemplate(
    template=full_prompt,
    input_variables=["revised_text", "revision_plan", "critique_feedback"]
)

def decision_node():
    endpoint_url = os.getenv("HF_ENDPOINT_URL")
    api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    client = InferenceClient(model=endpoint_url, token=api_token)

    def generate(state: WorkflowState):
        formatted_prompt = decision_prompt.format(
            revised_text=state.revised_text,
            revision_plan="\n".join(state.revision_plan or []),
            critique_feedback="\n".join(state.critique_feedback or []),
        )
        response = client.text_generation(
            prompt=formatted_prompt,
            max_new_tokens=10,
            temperature=0.01,  # must be strictly positive
        )
        # Extract JSON from the response, even if extra text is present
        match = re.search(r'\{.*?\}', response, re.DOTALL)
        if match:
            json_str = match.group(0)
            result = parser.invoke(json_str).dict()
            # Increment iteration if looping
            if hasattr(state, 'iteration') and state.iteration is not None:
                result['iteration'] = state.iteration + 1 if result.get('revise_again') else state.iteration
            else:
                result['iteration'] = 1 if result.get('revise_again') else 0
            return result
        else:
            # Fallback: if no JSON found, default to revise_again=False and keep iteration
            return {"revise_again": False, "iteration": getattr(state, 'iteration', 0)}

    return RunnableLambda(generate)
