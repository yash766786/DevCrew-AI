import re
from pathlib import Path
from app.services.workspace import get_workspace


def write_file(project_id: str, file_path: str, content: str):
    workspace = get_workspace(project_id)

    target_file = workspace / file_path
    target_file.parent.mkdir(parents=True, exist_ok=True)
    target_file.write_text(content, encoding="utf-8")



def read_file(project_id: str, file_path: str):
    workspace = get_workspace(project_id)
    target_file = workspace / file_path

    return target_file.read_text(
        encoding="utf-8"
    )



def list_files(project_id: str):
    workspace = get_workspace(project_id)
    files = []

    for file in workspace.rglob("*"):
        if file.is_file():
            files.append(str(file.relative_to(workspace)))

    return files


def clean_code(content: str):
    content = re.sub(r"```tsx", "", content)
    content = re.sub(r"```ts", "", content)
    content = re.sub(r"```", "", content)

    return content.strip()

