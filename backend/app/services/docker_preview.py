# import socket
import subprocess
from app.tools.file_tools import get_workspace

import time
import requests

IMAGE_NAME = "ai-nextjs-runner"
preview_sessions = {}
BASE_PORT = 3001


# def get_free_port(start=3008):
#     port = start

#     while True:
#         with socket.socket() as s:
#             try:
#                 s.bind(("localhost", port))
#                 return port
#             except OSError:
#                 port += 1


def get_free_port(start=3004):
    used_ports = set()

    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Ports}}"],
        capture_output=True,
        text=True
    )

    for line in result.stdout.splitlines():
        if "->" in line:
            host_port = line.split("->")[0].split(":")[-1]
            try:
                used_ports.add(int(host_port))
            except:
                pass

    port = start

    while port in used_ports:
        port += 1

    return port


def start_preview(project_id: str, port: int | None = None): 
    if project_id in preview_sessions:
        return preview_sessions[project_id]

    workspace = get_workspace(project_id)
    workspace = workspace.resolve()

    if port is None:
        port = get_free_port()
    
    container_name = f"preview-{project_id[:8]}"

    print("Using shared node_modules volume")
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

       "-v",
       "nextjs_node_modules:/app/node_modules",

       IMAGE_NAME,

       "sh",
       "-c",
       "npm run start -- --hostname 0.0.0.0"
    ]
    
    print(f"\nSelected Port: {port}")
    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(result.stderr)

    # Wait until Next.js is ready
    preview_url = f"http://localhost:{port}"

    print("Waiting for preview server...")
    for _ in range(30):
        try:
            response = requests.get(preview_url, timeout=2)
            if response.status_code == 200:
                print("Preview ready!")
                break

        except Exception:
            pass

        time.sleep(1)

    preview_sessions[project_id] = {
        "container_name": container_name,
        "port": port,
        "preview_url": f"http://localhost:{port}"
    }

    print(f"\n\npreview session:-----------------------\n{preview_sessions}")
    print("Docker stdout:", result.stdout)
    print("Docker stderr:", result.stderr)

    return preview_sessions[project_id]


def restart_preview(project_id: str):
    old_session = preview_sessions.get(project_id)
    old_port = None

    if old_session:
        old_port = old_session["port"]
        stop_preview(project_id)

    return start_preview(project_id, port=old_port)


def stop_preview(project_id: str):
    session = preview_sessions.get(project_id)

    if not session:
        return

    container_name = session["container_name"]
    print(f"\nStopping Preview: {container_name}")

    subprocess.run(
        [
            "docker",
            "stop",
            container_name
        ],
        capture_output=True,
        text=True
    )
    preview_sessions.pop(project_id, None)


def get_preview_status(project_id: str):

    session = preview_sessions.get(project_id)

    if not session:
        return None

    return {
        "container_name": session["container_name"],
        "port": session["port"]
    }

