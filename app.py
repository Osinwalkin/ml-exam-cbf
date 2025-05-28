# app.py
import warnings

warnings.filterwarnings("ignore", message="flaml.automl is not available.")
warnings.filterwarnings("ignore", message="Cost calculation is not implemented for model open-mistral-nemo")

import autogen
from dotenv import load_dotenv
import os
from tools import get_todo_data # Import your tool
import json

# Load environment variables
load_dotenv()
mistral_api_key = os.getenv("MISTRAL_API_KEY")

if not mistral_api_key:
    raise ValueError("MISTRAL_API_KEY not found in .env file or environment variables.")

# 1. Define LLM Configuration
BASE_LLM_CONFIG_MISTRAL = { # Renamed to avoid clash if you were to import
    "config_list": [
        {
            "model": "open-mistral-nemo",
            "api_key": mistral_api_key,
            "api_type": "mistral",
            "api_base": "https://api.mistral.ai/v1", # Often needed
            # Copied from your successful config.py:
            "api_rate_limit": 0.1,
            "repeat_penalty": 1.1,
            "temperature": 0.0,
            "seed": 42,
            "stream": False,
            "native_tool_calls": False, # Crucial
            "cache_seed": None,
        }
    ],
}

get_todo_data_tool_schema = {
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

llm_config_for_assistant_with_tool = {
    **BASE_LLM_CONFIG_MISTRAL, # Spread the base config
    "tools": [
        {
            "type": "function", # Use "type": "function" as in your successful example
            "function": get_todo_data_tool_schema, # Pass the schema dictionary
        }
    ],
}

# 2. Create the AssistantAgent (the LLM-powered agent)
assistant = autogen.AssistantAgent(
    name="TodoAssistant",
    system_message="""You are a helpful AI assistant. Your goal is to fetch and display information about a todo item using its ID.

    **Workflow:**
    1.  **Understand User Request:** The user will provide a todo ID. You need to extract this ID.
    2.  **Call the Tool:** Use the 'get_todo_data' tool with the extracted ID.
    3.  **Receive Tool Output:** You will receive the tool's output. This output will be a JSON STRING.
    4.  **Parse and Present (If Successful Tool Call):**
        *   If the tool call was successful and you received a JSON STRING with todo data, you MUST then write a Python code block (e.g., ```python ... ```).
        *   Inside this Python code, you must first use `json.loads()` to parse the JSON STRING you received from the tool into a Python dictionary.
        *   Then, extract the 'title' and 'completed' status from this Python dictionary.
        *   The Python code block you write should print the extracted title and completed status.
        *   After the Python code block, in your text response, clearly state the title and completed status (this will be your final summary).
    5.  **Handle Tool Errors (If Tool Call Failed):**
        *   If the JSON STRING from the tool indicates an error (e.g., it's a JSON object containing an "error" key), report this error message clearly in your text response. Do NOT try to write parsing code in this case.
    6.  **Terminate:** After providing the information or reporting an error, end your response with the word 'TERMINATE' on a new line. Do NOT include 'TERMINATE' inside any code blocks.

    **Example of generated Python code (after receiving a JSON string from the tool):**
    ```python
    import json
    # Assume 'tool_output_json_string' is the variable holding the string you received from the tool
    # For example: tool_output_json_string = '{"userId": 1, "id": 5, "title": "some title", "completed": false}'
    
    # You need to actually get this string from the previous turn's tool output.
    # For the sake of this example, let's imagine it's passed to you.
    # In a real flow, you'd refer to the actual tool output you received.
    
    # Correct approach:
    # json_data_from_tool = <the actual JSON string you received from the tool>
    # data = json.loads(json_data_from_tool)
    # title = data.get('title')
    # completed = data.get('completed')
    # print(f"Title: {title}")
    # print(f"Completed: {completed}")
    ```

    **Important:**
    - Your Python code for parsing MUST operate on the JSON STRING received from the tool by using `json.loads()`.
    - When you decide to use the 'get_todo_data' tool, your response should trigger its use.
    - When writing Python code for parsing, ensure it is in a triple backtick code block (e.g., ```python ... ```).
    """,
    llm_config=llm_config_for_assistant_with_tool,
    # Add function_map to AssistantAgent as in your successful example
    function_map={
        get_todo_data_tool_schema["name"]: get_todo_data
    }
)

# 3. Create the UserProxyAgent (executes code, provides user input)
user_proxy = autogen.UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=8, # Increased slightly for more attempts if needed
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={ # Enable code execution for parsing
        "work_dir": "coding",
        "use_docker": False,
    },
    # Crucially, UserProxyAgent also needs the function_map for execution
    function_map={
        get_todo_data_tool_schema["name"]: get_todo_data
    }
)

# 4. Start the conversation
print("Starting conversation with Mistral-powered agents (Attempt 3)...")
user_initial_message = "Can you get me the details for todo item number 5?"
#user_initial_message = "What about todo number 0?" # To test the error handling flow

user_proxy.initiate_chat(
    assistant,
    message=user_initial_message
)

print("\nConversation ended.")
