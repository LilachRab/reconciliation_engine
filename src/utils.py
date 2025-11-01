import os


def get_project_root() -> str:
    src_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(src_dir)
    return project_root


def ensure_directory_exists(file_path: str) -> None:
    directory = os.path.dirname(file_path)
    os.makedirs(directory, exist_ok=True)
