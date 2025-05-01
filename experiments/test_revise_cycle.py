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
from app.core.nodes.plan_node import plan_node  # Node for generating a revision plan
from app.core.nodes.revise_node import revise_node  # Node for revising text based on the plan
from langgraph.graph import StateGraph  # Graph-based workflow manager
from app.models.schemas import ReviseState  # Schema for tracking revision state

# Initialize a state graph with the ReviseState schema
graph = StateGraph(ReviseState)

# Add nodes to the graph
# "plan" node generates a revision plan based on the input text
graph.add_node("plan", plan_node())
# "revise" node revises the text based on the generated plan
graph.add_node("revise", revise_node())

# Set the entry point of the graph to the "plan" node
graph.set_entry_point("plan")

# Define the flow of the graph: output of "plan" feeds into "revise"
graph.add_edge("plan", "revise")

# Compile the graph into an executable application
app = graph.compile()

# Sample input text to test the revise cycle
user_draft = (
    "This product is amazing and it will definitely make your life better. "
    "It's affordable, easy to use, and very stylish so you should buy it."
)

# Create the initial state with the user's draft
input_state = {"current_text": user_draft}

# Print the initial input state
print("\n--- INPUT STATE ---\n")
pprint(input_state)

# Print the graph structure
print("\n--- GRAPH STRUCTURE ---\n")
print(graph)

# Invoke the graph with the input state to process the text
result = app.invoke(input_state)

# Print the result after invoking the graph
print("\n--- RESULT ---\n")
pprint(result)

# Print the original text
print("\n--- ORIGINAL ---\n")
print(user_draft)

# Print the generated revision plan
print("\n--- REVISION PLAN ---\n")
for step in result["revision_plan"]:
    pprint(f"- {step}")

# Print the revised text
print("\n--- REVISED TEXT ---\n")
print(result["revised_text"])