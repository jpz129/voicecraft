from fastapi import APIRouter
from app.models.schemas import ReviseRequest, ReviseResponse
from app.services.revision_agent import run_revision_workflow
from app.services.streaming import stream_revision_workflow
from pydantic import BaseModel

router = APIRouter()

@router.post("/revise", response_model=ReviseResponse)
def revise(request: ReviseRequest):
    return run_revision_workflow(request)

@router.post("/revise/stream")
def revise_stream(request: ReviseRequest):
    return stream_revision_workflow(request)

class FeedbackRequest(ReviseRequest):
    user_feedback: str

@router.post("/revise/feedback", response_model=ReviseResponse)
def revise_with_feedback(request: FeedbackRequest):
    return run_revision_workflow(request)

@router.post("/revise/feedback/stream")
def revise_with_feedback_stream(request: FeedbackRequest):
    return stream_revision_workflow(request)
