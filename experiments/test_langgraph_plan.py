import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load env vars from .env
load_dotenv()

# Add project root to PYTHONPATH at runtime
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# ✅ Now safe to import
from app.core.nodes.plan_node import plan_node
from langgraph.graph import StateGraph

from typing import TypedDict

class WritingState(TypedDict):
    current_text: str
    revision_plan: str

graph = StateGraph(WritingState)

graph.add_node("plan", plan_node())
graph.set_entry_point("plan")

app = graph.compile()

# Sample input
user_draft = (
    "This product is amazing and it will definitely make your life better. "
    "It's affordable, easy to use, and very stylish so you should buy it."
)

input_state = {"current_text": user_draft}

result = app.invoke(input_state)
print("\n--- REVISION PLAN ---\n")
print(result["revision_plan"])
