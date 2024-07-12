
from typing import List

FILE_TYPES = [".md", ".markdown"]
FIGURE_FOLDER = "figures"

def is_file_type(file_name: str, file_types: List[str] = FILE_TYPES) -> bool:
    """
    Check if the file is of the given type

    Args:
        file_name (str): Name of the file
        file_types (list[str]): List of file types

    Returns:
        bool: True if the file is of the given type
    """
    for file_type in file_types:
        if file_name.endswith(file_type):
            return True
    return False