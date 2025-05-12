import logging
from fastapi.responses import StreamingResponse
import json
from app.core.graph import build_decision_loop_graph
from app.models.schemas import ReviseRequest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voicecraft.backend")

def stream_revision_workflow(request: ReviseRequest):
    app_graph = build_decision_loop_graph(request.iteration_cap)
    input_state = {"current_text": request.draft, "iteration": 0}
    # If user_feedback is present, add it to the state
    if hasattr(request, "user_feedback") and request.user_feedback:
        input_state["user_feedback"] = request.user_feedback
    # capture request_id for cancellation
    req_id = request.request_id

    def event_stream():
        # Initial typing indicator
        yield json.dumps({"step": "status", "node_output": {"status": "typing"}}) + "\n"
        state_accum = {}
        # initialize history list
        state_accum['history'] = []
        for update in app_graph.stream(input_state, stream_mode="updates"):
            # Move cancellation check inside the loop for responsiveness
            from app.api.routes import cancelled_requests, cancel_lock
            with cancel_lock:
                if cancelled_requests.get(req_id, False):
                    yield json.dumps({"step": "cancelled", "node_output": {"message": "Cancelled by user."}}) + "\n"
                    cancelled_requests.pop(req_id, None)
                    return
            for node_output in update.values():
                if isinstance(node_output, dict):
                    state_accum.update(node_output)
            # record snapshot of current state without history
            snapshot = {k: v for k, v in state_accum.items() if k != 'history'}
            state_accum['history'].append(snapshot.copy())
            # Log the node, node output, and full workflow state for backend inspection
            node = next(iter(update.keys()))
            logger.info(f"[Streamed update] Node: {node}\nNode Output: {json.dumps(update, indent=2)}\nWorkflow State: {json.dumps(state_accum, indent=2)}")
            yield json.dumps({
                "step": node,
                "node_output": update,
                "workflow_state": state_accum
            }, default=str) + "\n"

    return StreamingResponse(event_stream(), media_type="application/json")
