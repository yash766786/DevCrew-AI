# import socket
import subprocess
from app.tools.file_tools import get_workspace

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


def start_preview(project_id: str): 
    if project_id in preview_sessions:
        return preview_sessions[project_id]

    workspace = get_workspace(project_id)
    workspace = workspace.resolve()

    port = get_free_port()
    container_name = f"preview-{project_id[:8]}"

    # command = [
    #     "docker",
    #     "run",
    #     "-d",
    #     "--rm",
    #     "--name",
    #     container_name,
    #     "-p",
    #     f"{port}:3000",
    #     "-v",
    #     f"{workspace}:/app",
    #     IMAGE_NAME,
    #     "sh",
    #     "-c",
    #     "npm run dev -- --hostname 0.0.0.0"
    # ]
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
       "npm run dev -- --hostname 0.0.0.0"
    ]
    
    print(f"\nSelected Port: {port}")
    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise Exception(result.stderr)

    preview_sessions[project_id] = {
        "container_name": container_name,
        "port": port,
        "preview_url": f"http://localhost:{port}"
    }

    print(f"\n\npreview session:-----------------------\n{preview_sessions}")
    print("Docker stdout:", result.stdout)
    print("Docker stderr:", result.stderr)

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

