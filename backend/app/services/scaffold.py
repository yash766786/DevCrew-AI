from pathlib import Path
import shutil

from app.services.workspace import get_workspace

BASE_DIR = Path(__file__).resolve().parents[3]

TEMPLATE_DIR = BASE_DIR / "templates" / "nextjs"


def scaffold_project(project_id: str):
    workspace = get_workspace(project_id)

    print("Template Path:", TEMPLATE_DIR)
    print("Exists:", TEMPLATE_DIR.exists())

    shutil.copytree(
        TEMPLATE_DIR,
        workspace,
        dirs_exist_ok=True
    )