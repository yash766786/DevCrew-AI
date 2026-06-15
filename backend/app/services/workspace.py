from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]

PROJECTS_ROOT = BASE_DIR / "projects"


def create_workspace(project_id: str) -> Path:
    """
    Create workspace for a project.

    Example:
    projects/<project_id>
    """

    project_path = PROJECTS_ROOT / project_id
    print("\n\nProjects Root:", PROJECTS_ROOT)

    project_path.mkdir(
        parents=True,
        exist_ok=True
    )

    return project_path


def get_workspace(project_id: str) -> Path:
    return PROJECTS_ROOT / project_id

