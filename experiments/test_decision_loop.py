# Import necessary modules
from pathlib import Path
from dotenv import load_dotenv
import sys
from pprint import pprint

# Load environment variables from the .env file
load_dotenv()

# Add the project root directory to the Python path dynamically
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import application-specific modules and classes
from app.core.nodes.plan_node import plan_node
from app.core.nodes.critique_node import critique_node
from app.core.nodes.revise_node import revise_node
from app.core.nodes.decision_node import decision_node
from langgraph.graph import StateGraph
from app.models.schemas import WorkflowState

# Initialize a state graph with the WorkflowState schema
graph = StateGraph(WorkflowState)

graph.add_node("plan", plan_node())
graph.add_node("revise", revise_node())
graph.add_node("critique", critique_node())
graph.add_node("decision", decision_node())

graph.set_entry_point("plan")

graph.add_edge("plan", "revise")
graph.add_edge("revise", "critique")
graph.add_edge("critique", "decision")

# Decision node: if revise_again, go to plan; else, finish
def route_decision(state):
    val = getattr(state, "revise_again", None)
    iteration = getattr(state, "iteration", 0)
    print(f"[DEBUG] route_decision: state.revise_again = {val!r}, iteration = {iteration}")
    if iteration >= 3:
        return "__end__"
    if val is True:
        return "plan"
    return "__end__"

# Use path_map to explicitly map return values to destinations
# "plan" loops, "__end__" terminates

graph.add_conditional_edges(
    "decision",
    route_decision,
    {
        "plan": "plan",
        "__end__": "__end__"
    }
)

app = graph.compile()

user_draft = (
    "This product is amazing and it will definitely make your life better. "
    "It's affordable, easy to use, and very stylish so you should buy it."
)

input_state = {"current_text": user_draft, "iteration": 0}

print("\n📝✨ INPUT STATE ✨📝\n")
pprint(input_state)

print("\n🗺️  GRAPH STRUCTURE 🗺️\n")
print(app.get_graph().draw_ascii())

print("\n🔄 Streaming graph execution (step-by-step):\n")
final_state = {}
for update in app.stream(input_state, stream_mode="updates"):
    # Get the node name (the first key in the update dict)
    node_name = next(iter(update.keys()))
    print("🟢 Step:", node_name)
    for node_output in update.values():
        if isinstance(node_output, dict):
            final_state.update(node_output)
    # Increment iteration after each decision node
    if "decision" in update:
        final_state["iteration"] = final_state.get("iteration", 0) + 1
    pprint(update)
    print("—" * 40)

result = final_state if final_state else None

print("\n🏁 FINAL RESULT 🏁\n")
pprint(result)

print("\n📄 ORIGINAL DRAFT 📄\n")
print(user_draft)

print("\n🧭 FINAL REVISION PLAN 🧭\n")
for step in result.get("revision_plan", []):
    print(f"  🔹 {step}")

print("\n✍️ FINAL REVISED TEXT ✍️\n")
print(result.get("revised_text", "No revised text available"))

print("\n🧐 FINAL CRITIQUE FEEDBACK 🧐\n")
for point in result.get("critique_feedback", []):
    print(f"  💡 {point}")

print("\n🤔 FINAL DECISION (Should Revise Again?) 🤔\n")
if result.get('revise_again') is True:
    print("  🔁 The workflow decided: Revise again! (Looping back to plan node, unless iteration cap is reached)")
elif result.get('revise_again') is False:
    print("  ✅ The workflow decided: No further revision needed. Workflow complete!")
else:
    print("  ⚠️ Unable to determine decision from workflow output.")
