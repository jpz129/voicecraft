from app.core.graph import build_decision_loop_graph
from app.models.schemas import ReviseRequest

def run_revision_workflow(request: ReviseRequest):
    app_graph = build_decision_loop_graph(request.iteration_cap)
    input_state = {"current_text": request.draft, "iteration": 0}
    final_state = {}
    for update in app_graph.stream(input_state, stream_mode="updates"):
        for node_output in update.values():
            if isinstance(node_output, dict):
                final_state.update(node_output)
    return {"result": final_state}
