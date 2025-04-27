import os
from dotenv import load_dotenv

load_dotenv()

config = {
    "api_key": {
        "key": os.getenv("OPENAI_API_KEY")
    },
    "model": {
        "name": os.getenv("MODEL_NAME", "gpt-4")
    }
}