import subprocess
from pathlib import Path


IMAGE_NAME = "ai-nextjs-runner"


def build_project_in_docker(project_path: Path):
    project_path = project_path.resolve()

    command = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{project_path}:/app",
        IMAGE_NAME,
        "sh",
        "-c",
        "npm install && npm run build"
    ]

    print("Running Docker Build:")
    print(" ".join(command))

    process = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    print(process)

    return {
        "success": process.returncode == 0,
        "install_output": process.stdout,
        "build_output": process.stdout,
        "build_error": process.stderr
    }