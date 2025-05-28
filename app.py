# app.py
import warnings

warnings.filterwarnings("ignore", message="flaml.automl is not available.")
warnings.filterwarnings("ignore", message="Cost calculation is not implemented for model open-mistral-nemo")

import os
import autogen
from dotenv import load_dotenv
from tools import get_todo_data
import json

# Load environment variables
load_dotenv()
mistral_api_key = os.getenv("MISTRAL_API_KEY")

if not mistral_api_key:
    raise ValueError("MISTRAL_API_KEY not found in .env file or environment variables.")

# Define LLM Configuration
BASE_LLM_CONFIG_MISTRAL = { 
    "config_list": [
        {
            "model": "open-mistral-nemo",
            "api_key": mistral_api_key,
            "api_type": "mistral",
            "api_base": "https://api.mistral.ai/v1",
            "api_rate_limit": 0.1,
            "repeat_penalty": 1.1,
            "temperature": 0.0,
            "seed": 42,
            "stream": False,
            "native_tool_calls": False, 
            "cache_seed": None,
        }
    ],
}

get_todo_data_tool_schema = {
    "type": "function", 
    "function": { 
        "name": "get_todo_data",
        "description": "Fetches data for a specific todo item by its ID from the JSONPlaceholder API. Returns the raw JSON response as a string. Handles API errors by returning a JSON string with an 'error' key.",
        "parameters": {
            "type": "object",
            "properties": {
                "todo_id": {
                    "type": "integer",
                    "description": "The ID of the todo item to fetch (e.g., 1, 2, 3). Must be a positive integer."
                }
            },
            "required": ["todo_id"]
        }
    }
}

llm_config_for_assistant_with_tool = {
    **BASE_LLM_CONFIG_MISTRAL,
    "tools": [get_todo_data_tool_schema], 
}

# Create the AssistantAgent and system message (the LLM-powered agent)
assistant = autogen.AssistantAgent(
    name="TodoAssistant",
    system_message="""You are an AI assistant that fetches and displays todo item details (title, completion status) using its ID.

**Workflow:**
1.  **Get Todo ID:** User provides a todo ID. Extract it. If the ID is invalid (not a positive integer, e.g., 0 or "abc"), inform the user and TERMINATE. Do not call the tool.
2.  **Use Tool:** If ID is valid, call `get_todo_data` tool with the `todo_id`. The tool returns a JSON STRING.
3.  **Process Tool Output (JSON STRING):**
    *   **Success (No "error" key in JSON string):**
        *   Generate a Python code block (```python ... ```).
        *   The Python code MUST:
            1.  `import json`
            2.  Parse the received JSON STRING using `json.loads()`.
            3.  Extract 'title' and 'completed' from the parsed dictionary.
            4.  `print()` the title and completed status.
        *   After the code block, summarize the findings from the code's output.
    *   **Error (JSON string has an "error" key):**
        *   Report the error message from the tool directly. Do NOT generate parsing code.
4.  **End:** Conclude your response with 'TERMINATE' on a new line.

**Example Python Code for Successful Tool Output (e.g., tool returns '{"id":1, "title":"Task A", "completed":false}'):**
```python
import json
tool_response_str = '{"id":1, "title":"Task A", "completed":false}' # This will be the actual string from the tool
data = json.loads(tool_response_str)
title = data.get('title')
completed = data.get('completed')
print(f"Title: {title}")
print(f"Completed: {completed}")

Key Rules:
Python for parsing is ONLY for successful tool outputs.
Always json.loads() the raw JSON string from the tool.
TERMINATE is your final word, on its own line.""",
    llm_config=llm_config_for_assistant_with_tool,
    function_map={
        get_todo_data_tool_schema["function"]["name"]: get_todo_data
    }
)

# Create the UserProxyAgent (executes code, provides user input)
user_proxy = autogen.UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=8,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "coding",
        "use_docker": False,
    },
    function_map={
        get_todo_data_tool_schema["function"]["name"]: get_todo_data
    }
)

# Start the conversation
# Test Scenarios
# One at a time would be optimal to avoid hallucinations
user_initial_message = "Can you get me the details for todo item number 5?"
#user_initial_message = "Get info for todo 1."
#user_initial_message = "What about todo number 201?"
# user_initial_message = "Fetch details for todo 0"
# user_initial_message = "I need info for todo item 'abc'."

user_proxy.initiate_chat(
    assistant,
    message=user_initial_message
)

print("\nConversation ended.")
