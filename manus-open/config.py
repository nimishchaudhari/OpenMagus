import os

# Load environment variables
LLM_API_KEY = os.getenv('LLM_API_KEY')
LLM_MODEL = os.getenv('LLM_MODEL')

# Configuration for LiteLLM
config = {
    'api_key': LLM_API_KEY,
    'model': LLM_MODEL
}
