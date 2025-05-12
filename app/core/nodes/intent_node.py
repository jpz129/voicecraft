from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from huggingface_hub import InferenceClient
from pathlib import Path
import os
import re
import json
from app.models.schemas import WorkflowState, IntentOutput

def intent_node():
    # Prompt for intent classification
    prompt_text = (
        "You are an intent classifier for a writing assistant. "
        "Classify the user's message as one of: 'question', 'feedback', or 'other'. "
        "If the message is a question about the draft or revision, use 'question'. "
        "If the message is feedback, suggestions, or requests for changes, use 'feedback'. "
        "If the message is not a question or feedback about the draft, classify as 'other'. "
        "Respond ONLY with a JSON object: {{\"intent\": \"question|feedback|other\"}}.\n"
        "User message: {user_message}\n"
    )
    prompt = PromptTemplate(template=prompt_text, input_variables=["user_message"])
    parser = PydanticOutputParser(pydantic_object=IntentOutput)
    endpoint_url = os.getenv("HF_ENDPOINT_URL")
    api_token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    client = InferenceClient(model=endpoint_url, token=api_token)

    def generate(state: WorkflowState):
        text = (state.user_feedback or state.current_text or "").strip()
        # Stop keywords
        if any(keyword in text.lower() for keyword in ["stop", "exit", "cancel"]):
            return {"intent": "stop"}
        # LLM-based intent detection
        formatted_prompt = prompt.format(user_message=text)
        try:
            response = client.text_generation(
                prompt=formatted_prompt,
                max_new_tokens=30,
                temperature=0.01
            )
        except Exception as e:
            # Log the error and return fallback intent
            import logging
            logging.error(f"Intent node failed to call Hugging Face endpoint: {e}")
            return {"intent": "other", "error": f"Intent detection failed: {e}"}
        # Extract JSON from the response
        match = re.search(r'\{.*?\}', response, re.DOTALL)
        intent = "other"
        if match:
            json_str = match.group(0)
            try:
                parsed = parser.invoke(json_str)
                if hasattr(parsed, 'intent'):
                    intent = parsed.intent
                elif isinstance(parsed, dict):
                    intent = parsed.get("intent", "other")
            except Exception:
                try:
                    loaded = json.loads(json_str)
                    if isinstance(loaded, dict):
                        intent = loaded.get("intent", "other")
                except Exception:
                    intent = "other"
        # Only allow QA if a revised draft exists
        if intent == "question" and getattr(state, "revised_text", None):
            return {"intent": "qa"}
        elif intent == "stop":
            return {"intent": "stop"}
        elif intent == "feedback":
            return {"intent": "plan"}
        else:
            return {"intent": intent}
    return RunnableLambda(generate)