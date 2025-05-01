from pydantic import BaseModel
from typing import List, TypedDict, Optional

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
    iteration: int = 0  # Add iteration counter

class ReviseRequest(BaseModel):
    draft: str
    iteration_cap: int = 3

class ReviseResponse(BaseModel):
    result: dict