import os
from dotenv import load_dotenv

def get_api_key():
    """
    Read API key from environment variable to avoid embedding secrets in code.
    Returns:
        str: The API key from the environment variable.
    """

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable not set")
    return api_key