import subprocess
from pathlib import Path

preview_sessions = {}
BASE_PORT = 3001


def get_next_port():
    return BASE_PORT + len(preview_sessions)


def start_preview(project_id: str, workspace: Path):
    if project_id in preview_sessions:
        return preview_sessions[project_id]

    port = get_next_port()
    process = subprocess.Popen(
        [
            "cmd",
            "/c",
            "npm",
            "run",
            "dev",
            "--",
            "--port",
            str(port)
        ],
        cwd=workspace,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    preview_sessions[project_id] = {
        "port": port,
        "process": process
    }

    return preview_sessions[project_id]


def stop_preview(project_id: str):
    session = preview_sessions.get(project_id)

    if not session:
        return False

    session["process"].terminate()
    del preview_sessions[project_id]

    return True

