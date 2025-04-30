from pathlib import Path
from dotenv import load_dotenv
import sys


# Load env vars from .env
load_dotenv()

# Add project root to PYTHONPATH at runtime
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
    
# This script is used to test the revise cycle of the app.
from app.core.nodes.plan_node import plan_node
from app.core.nodes.revise_node import revise_node
from langgraph.graph import StateGraph
from app.models.schemas import ReviseState


graph = StateGraph(ReviseState)
graph.add_node("plan", plan_node())
graph.add_node("revise", revise_node())
graph.set_entry_point("plan")
graph.add_edge("plan", "revise")

app = graph.compile()

# Sample input
user_draft = (
    "This product is amazing and it will definitely make your life better. "
    "It's affordable, easy to use, and very stylish so you should buy it."
)

input_state = {"current_text": user_draft}

result = app.invoke(input_state)

print("\n--- ORIGINAL ---\n")
print(user_draft)
print("\n--- REVISION PLAN ---\n")
for step in result["revision_plan"]:
    print(f"- {step}")
print("\n--- REVISED TEXT ---\n")
print(result["revised_text"])