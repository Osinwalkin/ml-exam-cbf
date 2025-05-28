# app.py
import autogen
from dotenv import load_dotenv
import os
from tools import get_todo_data # Import your tool

# Load environment variables
load_dotenv()
mistral_api_key = os.getenv("MISTRAL_API_KEY")

if not mistral_api_key:
    raise ValueError("MISTRAL_API_KEY not found in .env file or environment variables.")

# 1. Define LLM Configuration
config_list_mistral = [
    {
        "model": "open-mistral-nemo",
        "api_key": mistral_api_key,
        "api_type": "mistral",
        "api_base": "https://api.mistral.ai/v1",
         "api_rate_limit": 0.25, # This might be handled by the custom autogen fork
         "repeat_penalty": 1.1,
         "temperature": 0.0,
         "seed": 42,
         "stream": False,
         "native_tool_calls": False, # Important for how Autogen interprets tool use
         "cache_seed": None,
    }
]

llm_config_assistant_mistral = {
    "temperature": 0.0, # Good for deterministic tasks
    "config_list": config_list_mistral,
    "functions": [ # Define the tool for the LLM to be aware of
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
    # Potentially add other Mistral-specific parameters from your LLM_CONFIG here
    # if they are not part of the config_list items, e.g., if your custom autogen
    # fork expects them at this level. But usually, they go into the config_list items.
}

# 2. Create the AssistantAgent (the LLM-powered agent)
assistant = autogen.AssistantAgent(
    name="TodoAssistant",
    system_message="""You are a helpful AI assistant. Your goal is to fetch and display information about a todo item using its ID.
    1.  The user will provide a todo ID. You need to extract this ID.
    2.  Then, use the 'get_todo_data' tool with the extracted ID to fetch the raw todo data in JSON format.
    3.  After receiving the JSON data string, you MUST write Python code to parse this JSON string and extract the 'title' and 'completed' status of the todo item.
    4.  The Python code you write should print the extracted title and completed status.
    5.  Finally, state the title and completed status clearly and then reply with the word 'TERMINATE' on a new line.
    If the tool returns an error, or if the user provides an invalid ID (e.g., not a number, or a non-positive number), report the error message from the tool and TERMINATE.
    When you need to call the 'get_todo_data' tool, make sure to format your request properly for a function call.
    When you write Python code, ensure it is in a triple backtick code block.
    """,
    llm_config=llm_config_assistant_mistral # Use the Mistral config
)

# 3. Create the UserProxyAgent (executes code, provides user input)
user_proxy = autogen.UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=8,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False,
    },
    function_map={ # Register the Python function
        "get_todo_data": get_todo_data
    }
)

# 4. Start the conversation
print("Starting conversation with Mistral-powered agents...")
user_initial_message = "What about todo number 0?"

user_proxy.initiate_chat(
    assistant,
    message=user_initial_message
)

print("\nConversation ended.")
