from pydantic import BaseModel
from typing import List


class ProjectPlan(BaseModel):
    project_name: str
    project_type: str
    theme: str
    sections: List[str]
    summary: str


class PlannerRequest(BaseModel):
    session_id: str
    prompt: str

class HumanFeedback(BaseModel):
    message: str