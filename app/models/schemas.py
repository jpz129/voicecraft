from pydantic import BaseModel
from typing import List, TypedDict

class RevisionPlan(BaseModel):
    revision_plan: List[str]

class ReviseState(TypedDict):
    current_text: str
    revision_plan: list[str]
    revised_text: str