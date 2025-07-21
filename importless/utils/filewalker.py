import os
from typing import List

def find_python_files(root_dir: str) -> List[str]:
    """
    Recursively search root_dir for all Python files (.py) and return their paths.
    """
    python_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".py"):
                full_path = os.path.join(dirpath, filename)
                python_files.append(full_path)
    return python_files
