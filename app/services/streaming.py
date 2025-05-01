import logging
from fastapi.responses import StreamingResponse
import json
from app.core.graph import build_decision_loop_graph
from app.models.schemas import ReviseRequest

def stream_revision_workflow(request: ReviseRequest):
    app_graph = build_decision_loop_graph(request.iteration_cap)
    input_state = {"current_text": request.draft, "iteration": 0}
    # If user_feedback is present, add it to the state
    if hasattr(request, "user_feedback") and request.user_feedback:
        input_state["user_feedback"] = request.user_feedback

    logger = logging.getLogger("voicecraft.workflow")

    def event_stream():
        state_accum = {}
        for update in app_graph.stream(input_state, stream_mode="updates"):
            for node_output in update.values():
                if isinstance(node_output, dict):
                    state_accum.update(node_output)
            logger.info(f"[Workflow State after step] {update.keys()}\n{json.dumps(state_accum, indent=2)}")
            yield json.dumps(update, default=str) + "\n"

    return StreamingResponse(event_stream(), media_type="application/json")
