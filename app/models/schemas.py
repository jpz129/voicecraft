from pydantic import BaseModel
from typing import List

class RevisionPlan(BaseModel):
    revision_plan: List[str]
