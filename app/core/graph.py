from langgraph.graph import StateGraph
from app.models.schemas import WorkflowState
from app.core.nodes.plan_node import plan_node
from app.core.nodes.revise_node import revise_node
from app.core.nodes.critique_node import critique_node
from app.core.nodes.decision_node import decision_node

def build_decision_loop_graph(iteration_cap: int = 3):
    graph = StateGraph(WorkflowState)
    graph.add_node("plan", plan_node())
    graph.add_node("revise", revise_node())
    graph.add_node("critique", critique_node())
    graph.add_node("decision", decision_node())
    graph.set_entry_point("plan")
    graph.add_edge("plan", "revise")
    graph.add_edge("revise", "critique")
    graph.add_edge("critique", "decision")

    def route_decision(state):
        val = getattr(state, "revise_again", None)
        iteration = getattr(state, "iteration", 0)
        if iteration >= iteration_cap:
            return "__end__"
        if val is True:
            return "plan"
        return "__end__"

    graph.add_conditional_edges(
        "decision",
        route_decision,
        {
            "plan": "plan",
            "__end__": "__end__"
        }
    )
    return graph.compile()
