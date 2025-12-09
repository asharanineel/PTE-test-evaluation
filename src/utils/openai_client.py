#--- START OF FILE utils/openai_client.py ---

import openai
from config import settings

def get_openai_client():
    """
    Initializes and returns a configured OpenAI client instance based on
    the settings provided in the environment.
    """
    client = openai.OpenAI(
        api_key=settings.OPENAI_API_KEY
    )
    return client