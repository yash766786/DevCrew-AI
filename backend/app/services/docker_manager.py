import subprocess
from pathlib import Path


def build_project(project_path: Path):

    install = subprocess.run(
        ["npm", "install"],
        cwd=project_path,
        capture_output=True,
        text=True
    )

    build = subprocess.run(
        ["npm", "run", "build"],
        cwd=project_path,
        capture_output=True,
        text=True
    )

    return {
        "install_output": install.stdout,
        "build_output": build.stdout,
        "build_error": build.stderr,
        "success": build.returncode == 0
    }