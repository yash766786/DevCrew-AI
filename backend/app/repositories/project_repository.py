import json
from app.db.models import Project

def create_project_db(db, project_id: str, state: dict):
    project = Project(
        id=project_id,
        state_json=json.dumps(state)
    )

    db.add(project)
    db.commit()

    return project


def get_project_db(db, project_id: str):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        return None

    return json.loads(project.state_json)


def save_project_db(db, project_id: str, state: dict):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    project.state_json = json.dumps(state)
    db.commit()