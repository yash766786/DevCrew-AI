import subprocess
from pathlib import Path
from app.tools.file_tools import get_workspace

IMAGE_NAME = "ai-nextjs-runner"

def build_project_in_docker(project_id: Path):
    workspace = get_workspace(project_id)
    workspace = workspace.resolve()
    print(f"\n\nworkspce:------\n{workspace}")

    print("Using shared node_modules volume")
    command = [
        "docker",
        "run",
        "--rm",
    
        "-v",
        f"{workspace}:/app",
    
        "-v",
        "nextjs_node_modules:/app/node_modules",
    
        IMAGE_NAME,
    
        "sh",
        "-c",
        "npm run build"
    ]

    process = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    print(f"\n\nRunning Docker Build:----")
    print(" ".join(command))
    print(f"\nprocess:---\n{process.returncode}\n{process.stderr}\n{process.stdout}")

    return {
        "success": process.returncode == 0,
        "install_output": process.stdout,
        "build_output": process.stdout,
        "build_error": process.stderr
    }

