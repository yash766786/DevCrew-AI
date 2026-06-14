# app/models/project.py

from pydantic import BaseModel
from typing import Dict, Any


# class Project(BaseModel):
#     project_id: str
#     prompt: str
#     plan: Dict[str, Any]
#     status: str

#     build_logs: str = ""
#     build_errors: str = ""


class Project(BaseModel):
    project_id: str
    prompt: str

    plan: Dict[str, Any]
    status: str

    build_logs: str = ""
    build_errors: str = ""
    preview_url: str = ""

    retry_count: int = 0