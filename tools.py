# tools.py
import requests
import json

def get_todo_data(todo_id: int) -> str:
    """
    Fetches data for a specific todo item from JSONPlaceholder.
    Returns the full JSON response as a string.
    Includes basic error handling.

    Args:
        todo_id: The ID of the todo item to fetch (e.g., 1, 2, 3).
    """
    print(f"----- EXECUTING TOOL: get_todo_data (ID: {todo_id}) -----")
    if not isinstance(todo_id, int) or todo_id <= 0:
        error_message = "Invalid todo_id. Must be a positive integer."
        print(f"----- TOOL ERROR: {error_message} -----")
        return json.dumps({"error": "InvalidInput", "message": error_message})

    url = f"https://jsonplaceholder.typicode.com/todos/{todo_id}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # Raises an HTTPError for bad responses (4XX or 5XX)
        print(f"----- TOOL: API Call Successful. Response: {response.text[:100]}... -----")
        return response.text # Return the raw JSON string

    except requests.exceptions.HTTPError as http_err:
        status_code_info = ""
        response_text_info = "No response body available."
        if http_err.response is not None:
            status_code_info = f" Status Code: {http_err.response.status_code}."
            try:
                response_text_info = f" Response: {http_err.response.text[:200] if http_err.response.text else '[empty response body]'}..."
            except Exception:
                response_text_info = " Could not retrieve or display error response text."
        error_message = f"HTTP error: {http_err}{status_code_info}{response_text_info}"
        print(f"----- TOOL ERROR: {error_message} -----")
        return json.dumps({
            "error": "HTTPError",
            "message": str(http_err),
            "status_code": http_err.response.status_code if http_err.response is not None else None,
            "response_text": http_err.response.text[:500] if http_err.response is not None and http_err.response.text else None
        })
    except requests.exceptions.ConnectionError as conn_err:
        error_message = f"Error Connecting: {conn_err}"
        print(f"----- TOOL ERROR: {error_message} -----")
        return json.dumps({"error": "ConnectionError", "message": error_message})
    except requests.exceptions.Timeout as timeout_err:
        error_message = f"Timeout Error: {timeout_err}"
        print(f"----- TOOL ERROR: {error_message} -----")
        return json.dumps({"error": "Timeout", "message": error_message})
    except requests.exceptions.RequestException as req_err:
        error_message = f"An unexpected API request error occurred: {req_err}"
        print(f"----- TOOL ERROR: {error_message} -----")
        return json.dumps({"error": "RequestException", "message": error_message})
    except Exception as e:
        error_message = f"An unexpected internal error occurred in the tool: {str(e)}"
        print(f"----- TOOL ERROR: {error_message} -----")
        return json.dumps({"error": "ToolInternalError", "message": error_message})

if __name__ == "__main__":
    print("--- Test Case 1: Successful Call (Todo ID 1) ---")
    todo_id_success = 1
    data_success = get_todo_data(todo_id_success)
    print(f"\nRaw data for Todo ID {todo_id_success}:")
    print(data_success)
    try:
        parsed_data = json.loads(data_success)
        if "error" not in parsed_data:
            title = parsed_data.get('title')
            completed_status = parsed_data.get('completed')
            print(f"\nManually extracted title: {title}")
            print(f"Completed status: {completed_status}")
        else:
            print(f"\nError in fetched data: {parsed_data.get('error')} - {parsed_data.get('message')}")
    except json.JSONDecodeError:
        print("\nFailed to parse JSON from successful tool output.")
    except KeyError:
        print("\nFailed to extract data, unexpected JSON structure.")
    print("-" * 40)

    print("--- Test Case 2: Non-existent Todo ID (e.g., 99999) ---")
    todo_id_fail = 99999 # This will likely give a 404 HTTPError
    data_fail = get_todo_data(todo_id_fail)
    print(f"\nRaw data for Todo ID {todo_id_fail}:")
    print(data_fail)
    try:
        parsed_error_data = json.loads(data_fail)
        if "error" in parsed_error_data:
            print(f"\nError from tool: {parsed_error_data['error']} - {parsed_error_data['message']}")
            if "status_code" in parsed_error_data:
                print(f"Status Code: {parsed_error_data['status_code']}")
        else:
            # JSONPlaceholder for a non-existent ID returns {} and a 404.
            # The response.raise_for_status() should catch the 404.
            print("\nTool did not return an error structure as expected for non-existent ID.")
    except json.JSONDecodeError:
        print("\nFailed to parse JSON from tool error output.")
    print("-" * 40)

    print("--- Test Case 3: Invalid Input (Todo ID 0) ---")
    todo_id_invalid = 0
    data_invalid = get_todo_data(todo_id_invalid)
    print(f"\nRaw data for Todo ID {todo_id_invalid}:")
    print(data_invalid)
    try:
        parsed_invalid_data = json.loads(data_invalid)
        if "error" in parsed_invalid_data:
            print(f"\nError from tool: {parsed_invalid_data['error']} - {parsed_invalid_data['message']}")
        else:
            print("\nExpected error for invalid input, but 'error' key not found.")
    except json.JSONDecodeError:
        print("\nFailed to parse JSON from tool invalid input output.")
    print("-" * 40)