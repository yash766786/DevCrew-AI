from pydantic import BaseModel
from typing import List


# class Page(BaseModel):
#     name: str
#     sections: List[str]


class ProjectPlan(BaseModel):
    project_name: str
    project_type: str
    theme: str
    sections: List[str]
    summary: str


class PlannerRequest(BaseModel):
    prompt: str