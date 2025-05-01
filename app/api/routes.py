from fastapi import APIRouter
from app.models.schemas import ReviseRequest, ReviseResponse
from app.services.revision_agent import run_revision_workflow
from app.services.streaming import stream_revision_workflow

router = APIRouter()

@router.post("/revise", response_model=ReviseResponse)
def revise(request: ReviseRequest):
    return run_revision_workflow(request)

@router.post("/revise/stream")
def revise_stream(request: ReviseRequest):
    return stream_revision_workflow(request)
