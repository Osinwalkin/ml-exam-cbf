# app.py
import autogen
from dotenv import load_dotenv
import os
from tools import get_todo_data # Import your tool

# Load environment variables (for OPENAI_API_KEY)
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file or environment variables.")

# 1. Define LLM Configuration
# Using gpt-3.5-turbo as it's faster and cheaper for development.
# You can switch to gpt-4o or gpt-4-turbo later if needed for better reasoning.
config_list_gpt35 = [
    {
        "model": "gpt-3.5-turbo-0125", # Or another suitable model like gpt-4o-mini
        "api_key": api_key,
    }
]

llm_config_assistant = {
    "temperature": 0,
    "config_list": config_list_gpt35,
    "functions": [
        {
            "name": "get_todo_data",
            "description": "Fetches data for a specific todo item by its ID from JSONPlaceholder. Returns raw JSON string.",
            "parameters": {
                "type": "object",
                "properties": {
                    "todo_id": {
                        "type": "integer",
                        "description": "The ID of the todo item to fetch (e.g., 1, 2, 3)."
                    }
                },
                "required": ["todo_id"]
            }
        }
    ]
}

# 2. Create the AssistantAgent (the LLM-powered agent)
assistant = autogen.AssistantAgent(
    name="TodoAssistant",
    system_message="""You are a helpful AI assistant. Your goal is to fetch and display information about a todo item using its ID.
    1.  The user will provide a todo ID.
    2.  Use the 'get_todo_data' tool with the provided ID to fetch the raw todo data in JSON format.
    3.  After receiving the JSON data string, you MUST write Python code to parse this JSON string and extract the 'title' and 'completed' status of the todo item.
    4.  Print the extracted title and completed status.
    5.  Finally, state the title and completed status clearly and then reply with the word 'TERMINATE' on a new line.
    If the tool returns an error, or if the user provides an invalid ID (e.g. not a number), report the error message and TERMINATE.
    """,
    llm_config=llm_config_assistant
)

# 3. Create the UserProxyAgent (executes code, provides user input)
user_proxy = autogen.UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER", # No human intervention during the agent conversation
    max_consecutive_auto_reply=8, # Max replies for the conversation
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "coding", # Directory to store and execute generated code
        "use_docker": False,  # Set to True if you have Docker and want to use it
    },
    # Register the Python function with the UserProxyAgent so it can execute it when the LLM calls it
    function_map={
        "get_todo_data": get_todo_data
    }
)

# 4. Start the conversation
print("Starting conversation with agents...")
user_initial_message = "Can you get me the details for todo item number 5?"

user_proxy.initiate_chat(
    assistant,
    message=user_initial_message
)

print("\nConversation ended.")
