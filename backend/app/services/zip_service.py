from pathlib import Path
import zipfile


IGNORE_DIRS = {
    "node_modules",
    ".next"
}


def create_project_zip(project_path: Path, zip_path: Path):

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in project_path.rglob("*"):

            if not file.is_file():
                continue

            if any(
                part in IGNORE_DIRS
                for part in file.parts
            ):
                continue

            arcname = file.relative_to(project_path)
            zipf.write(file, arcname)

    return zip_path

