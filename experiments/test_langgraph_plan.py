# Import necessary modules
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from pprint import pprint

# Load environment variables from the .env file
load_dotenv()

# Add the project root directory to the Python path dynamically
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import application-specific modules and classes
from app.core.nodes.plan_node import plan_node  # Node for generating a revision plan
from langgraph.graph import StateGraph  # Graph-based workflow manager
from typing import TypedDict  # For defining structured input/output types

# Define a schema for the writing state
class WritingState(TypedDict):
    current_text: str  # The user's draft text
    revision_plan: str  # The generated revision plan

# Initialize a state graph with the WritingState schema
graph = StateGraph(WritingState)

# Add the "plan" node to the graph
# This node generates a revision plan based on the input text
graph.add_node("plan", plan_node())

# Set the entry point of the graph to the "plan" node
graph.set_entry_point("plan")

# Compile the graph into an executable application
app = graph.compile()

# Sample input text to test the plan generation
user_draft = (
    "This product is amazing and it will definitely make your life better. "
    "It's affordable, easy to use, and very stylish so you should buy it."
)

# Create the initial state with the user's draft
input_state = {"current_text": user_draft}

# Print the initial input state
print("\n--- INPUT STATE ---\n")
pprint(input_state)

# Invoke the graph with the input state to generate a revision plan
result = app.invoke(input_state)

# Print the graph structure
print("\n--- GRAPH STRUCTURE ---\n")
print(graph)

# Print the result after invoking the graph
print("\n--- RESULT ---\n")
pprint(result)

# Print the generated revision plan
print("\n--- REVISION PLAN ---\n")
pprint(result["revision_plan"])
