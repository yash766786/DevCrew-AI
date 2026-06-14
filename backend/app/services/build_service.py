import subprocess
from pathlib import Path


def build_project(project_path: Path):

    print(project_path)
    print(project_path.exists())

    install_process = subprocess.run(
        ["cmd", "/c", "npm", "install"],
        cwd=project_path,
        capture_output=True,
        text=True
    )

    build_process = subprocess.run(
        ["cmd", "/c", "npm", "run", "build"],
        cwd=project_path,
        capture_output=True,
        text=True
    )

    return {
        "success": build_process.returncode == 0,
        "install_output": install_process.stdout,
        "build_output": build_process.stdout,
        "build_error": build_process.stderr
    }