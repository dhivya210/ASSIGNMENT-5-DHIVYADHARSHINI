import openai
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Create a new thread
thread = openai.beta.threads.create()
print(f"Thread ID: {thread.id}")