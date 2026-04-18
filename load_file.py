import os

def load_file(filename):
    """
    Load and return the contents of a file as a string.
    Args:
        filename (str): Relative path to file from this script.
    Returns:
        str or None: File contents or None if not found.
    """
    try:
        script_directory = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_directory, filename)
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        return None