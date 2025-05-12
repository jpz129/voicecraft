from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse, JSONResponse
from app.models.schemas import ReviseRequest, ReviseResponse
from app.services.revision_agent import run_revision_workflow
from app.services.streaming import stream_revision_workflow
from pydantic import BaseModel
import uuid
from typing import Dict
from threading import Lock
import json

router = APIRouter()

# Shared cancellation state (in-memory, thread-safe)
cancelled_requests: Dict[str, bool] = {}
cancel_lock = Lock()

@router.post("/cancel")
async def cancel_request(data: dict):
    request_id = data.get("request_id")
    if not request_id:
        return JSONResponse({"error": "Missing request_id"}, status_code=400)
    with cancel_lock:
        cancelled_requests[request_id] = True
    return {"status": "cancelled"}

@router.post("/revise", response_model=ReviseResponse)
def revise(request: ReviseRequest):
    return run_revision_workflow(request)

@router.post("/revise/stream")
async def revise_stream(request: Request):
    body = await request.json()
    req = ReviseRequest(**body)
    return stream_revision_workflow(req)

class FeedbackRequest(ReviseRequest):
    user_feedback: str

@router.post("/revise/feedback", response_model=ReviseResponse)
def revise_with_feedback(request: FeedbackRequest):
    return run_revision_workflow(request)

@router.post("/revise/feedback/stream")
def revise_with_feedback_stream(request: FeedbackRequest):
    return stream_revision_workflow(request)
