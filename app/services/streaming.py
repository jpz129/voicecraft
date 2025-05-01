from fastapi.responses import StreamingResponse
import json
from app.core.graph import build_decision_loop_graph
from app.models.schemas import ReviseRequest

def stream_revision_workflow(request: ReviseRequest):
    app_graph = build_decision_loop_graph(request.iteration_cap)
    input_state = {"current_text": request.draft, "iteration": 0}

    def event_stream():
        for update in app_graph.stream(input_state, stream_mode="updates"):
            yield json.dumps(update, default=str) + "\n"

    return StreamingResponse(event_stream(), media_type="application/json")
