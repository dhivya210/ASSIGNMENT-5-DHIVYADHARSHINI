#ASSIGNMENT 5
#NAME : DHIVYADHARSHINI KATHIRAVAN SATHYABAMA


import time
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os
import json

app = FastAPI()

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city_name": {
                        "type": "string",
                        "description": "The name of the city, e.g., Liepaja",
                    },
                },
                "required": ["city_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_news",
            "description": "Get the latest news headlines about a topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "The topic to search for, e.g., technology",
                    },
                },
                "required": ["topic"],
            },
        },
    },
]

# Create an assistant
assistant = openai.beta.assistants.create(
    name="Web Service Assistant",
    instructions="You are an assistant that provides weather and news information.",
    model="gpt-3.5-turbo",
    tools=tools,
)

# Create a thread
thread = openai.beta.threads.create()

# Function to get weather data
def get_weather(city_name):
    # Simulate weather data (replace with actual API call)
    return f"The weather in {city_name} is sunny with a temperature of 25°C."

# Function to get news headlines
def get_news(topic):
    # Simulate news data (replace with actual API call)
    return f"Here are the latest news headlines about {topic}: 1. AI Breakthrough, 2. Quantum Computing Advances."

# Handle assistant responses
def handle_assistant_response(run):
    while run.status != "completed":
        run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run.status == "requires_action":
            for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                if tool_call.function.name == "get_weather":
                    arguments = json.loads(tool_call.function.arguments)
                    city_name = arguments["city_name"]
                    output = get_weather(city_name)
                elif tool_call.function.name == "get_news":
                    arguments = json.loads(tool_call.function.arguments)
                    topic = arguments["topic"]
                    output = get_news(topic)
                else:
                    output = "Unknown tool call."

                # Submit the tool output
                openai.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=[{
                        "tool_call_id": tool_call.id,
                        "output": output,
                    }],
                )
        time.sleep(1)

    # Retrieve the final response
    messages = openai.beta.threads.messages.list(thread_id=thread.id)
    return messages.data[0].content[0].text.value

# Model for a single message
class Message(BaseModel):
    role: str
    content: str

# Receive a message and return a response from the virtual assistant
@app.post("/send-message/")
async def process_message_and_respond(thread_id: str, message: str):
    """
    Receive a message from the user and return a response from the virtual assistant.

    Args:
        thread_id (str): The ID of the conversation thread.
        message (str): The message sent by the user.

    Returns:
        dict: A dictionary containing the thread ID and the assistant's response.
    """
    try:
        # Add user input to the thread
        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=message,
        )

        # Run the assistant
        run = openai.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )

        # Handle the assistant's response
        response = handle_assistant_response(run)
        return {
            "thread_id": thread_id,
            "response": response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Retrieve conversation history
@app.get("/conversation-history/")
async def conversation_history(thread_id: str):
    """
    Retrieve the conversation history for a specific thread.

    Args:
        thread_id (str): The ID of the conversation thread.

    Returns:
        dict: A dictionary containing the thread ID and a list of conversation messages.
    """
    try:
        messages = openai.beta.threads.messages.list(thread_id=thread.id)
        conversation_history = []
        for message in messages.data:
            conversation_history.append({
                "sender": message.role,
                "content": message.content[0].text.value
            })
        return {
            "thread_id": thread_id,
            "conversation_history": conversation_history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the web service
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)