import subprocess
from pathlib import Path

IMAGE_NAME = "ai-nextjs-runner"
preview_sessions = {}
BASE_PORT = 3001


def get_next_port():
    return BASE_PORT + len(preview_sessions)


def start_preview(project_id: str, workspace: Path): 

    if project_id in preview_sessions:
        return preview_sessions[project_id]

    workspace = workspace.resolve()

    port = get_next_port()

    container_name = f"preview-{project_id[:8]}"

    command = [
        "docker",
        "run",
        "-d",
        "--rm",
        "--name",
        container_name,
        "-p",
        f"{port}:3000",
        "-v",
        f"{workspace}:/app",
        IMAGE_NAME,
        "sh",
        "-c",
        "npm install && npm run dev -- --hostname 0.0.0.0"
    ]

    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(result.stderr)

    preview_sessions[project_id] = {
        "container_name": container_name,
        "port": port
    }

    print(f"preview session:-----------------------\n{preview_sessions}\n\n\n")

    return preview_sessions[project_id]


def stop_preview(project_id: str):

    session = preview_sessions.get(project_id)

    if not session:
        return False

    subprocess.run(
        [
            "docker",
            "stop",
            session["container_name"]
        ],
        capture_output=True
    )

    del preview_sessions[project_id]

    return True


def get_preview_status(project_id: str):

    session = preview_sessions.get(project_id)

    if not session:
        return None

    return {
        "container_name": session["container_name"],
        "port": session["port"]
    }

