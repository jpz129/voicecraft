from langgraph.graph import StateGraph
from app.models.schemas import WorkflowState
from app.core.nodes.plan_node import plan_node
from app.core.nodes.revise_node import revise_node
from app.core.nodes.critique_node import critique_node
from app.core.nodes.decision_node import decision_node
from app.core.nodes.intent_node import intent_node
from app.core.nodes.qa_node import qa_node

def build_decision_loop_graph(iteration_cap: int = 3):
    graph = StateGraph(WorkflowState)
    # entry: classify intent (plan, qa, stop)
    graph.add_node("detect_intent", intent_node())
    graph.add_node("plan", plan_node())
    graph.add_node("revise", revise_node())
    graph.add_node("critique", critique_node())
    graph.add_node("decision", decision_node())
    graph.add_node("qa", qa_node())
    graph.set_entry_point("detect_intent")
    # routes from detect_intent are handled by conditional edges
    # plan revision loop
    graph.add_edge("plan", "revise")
    graph.add_edge("revise", "critique")
    graph.add_edge("critique", "decision")
    # qa is terminal
    graph.add_edge("qa", "__end__")

    # decision loop for revision cycles
    def route_decision(state):
        val = getattr(state, "revise_again", None)
        iteration = getattr(state, "iteration", 0)
        if iteration >= iteration_cap:
            return "__end__"
        if val is True:
            return "plan"
        return "__end__"

    graph.add_conditional_edges("decision", route_decision, {"plan": "plan", "__end__": "__end__"})
    # intent routing: use state.intent
    def route_intent(state):
        return getattr(state, "intent", "plan")
    graph.add_conditional_edges("detect_intent", route_intent, {"plan": "plan", "qa": "qa", "question": "qa", "stop": "__end__", "other": "plan"})
    return graph.compile()
