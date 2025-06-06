from pydantic import BaseModel
from typing import List, TypedDict, Optional, Literal

class RevisionPlan(BaseModel):
    revision_plan: List[str]

class CritiqueFeedback(BaseModel):
    feedback: List[str]  # List of critique points or suggestions

class DecisionOutput(BaseModel):
    revise_again: bool  # Whether to loop for another revision

class ReviseState(TypedDict):
    current_text: str
    revision_plan: list[str]
    critique_feedback: list[str]  # Added critique feedback
    revised_text: str

class WorkflowState(BaseModel):
    current_text: str
    revision_plan: Optional[List[str]] = None
    revised_text: Optional[str] = None
    critique_feedback: Optional[List[str]] = None
    revise_again: Optional[bool] = None
    iteration: int = 0
    user_feedback: Optional[str] = None
    history: Optional[List[dict]] = []  # Memory of past state snapshots
    intent: Optional[str] = None
    answer: Optional[str] = None

class ReviseRequest(BaseModel):
    draft: str
    iteration_cap: int = 3
    request_id: str  # unique identifier for this request, used for cancellation

class ReviseResponse(BaseModel):
    result: dict

class IntentOutput(BaseModel):
    intent: Literal["feedback", "question", "other"]