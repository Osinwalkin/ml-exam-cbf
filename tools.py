# tools.py
import requests
import json

# Konstanter for API URL og standard timeout
JSONPLACEHOLDER_BASE_URL = "https://jsonplaceholder.typicode.com"
DEFAULT_REQUEST_TIMEOUT = 10

# Fetcher data til en specifik todo fra JSONPlaceholder API.
# Returnerer raw JSON-respons som en string, hvis det lykkes.
# Hvis der opstår problemer, returneres en JSON-streng med en 'error'-nøgle.
def get_todo_data(todo_id: int) -> str:
    # Log start
    print(f"----- EXECUTING TOOL: get_todo_data (ID: {todo_id}) -----")

    # 1. Input Validation
    if not isinstance(todo_id, int) or todo_id <= 0:
        error_message = "Invalid todo_id. Must be a positive integer."
        print(f"----- TOOL ERROR (Input Validation): {error_message} -----")
        return json.dumps({"error": "InvalidInput", "message": error_message})

    # Sammensæt URL til API-kald
    url = f"{JSONPLACEHOLDER_BASE_URL}/todos/{todo_id}"

    try:
        # 2. API Call
        response = requests.get(url, timeout=DEFAULT_REQUEST_TIMEOUT)
        response.raise_for_status()  # Raises HTTPError for 4xx/5xx responses

        # API-kald var succesfuldt (status 2xx)
        print(f"----- TOOL: API Call Successful (Status: {response.status_code}). Validating response... -----")
        
        # 3. Response Validation (skal være gyldigt JSON og et dictionary)
        try:
            parsed_response = json.loads(response.text)
            if not isinstance(parsed_response, dict):
                error_message = "API response was not a JSON object as expected."
                print(f"----- TOOL ERROR (Invalid Response Format): {error_message} Raw text: {response.text[:100]}... -----")
                return json.dumps({"error": "InvalidResponseFormat", "message": error_message})
            
            # Svar valideret, returner raw JSON-string
            print(f"----- TOOL: Response validated. Content: {response.text[:100]}... -----")
            return response.text

        except json.JSONDecodeError:
            # Fejl hvis API-svar ikke er gyldigt JSON
            error_message = "Failed to parse API response as JSON. The response was not valid JSON."
            print(f"----- TOOL ERROR (JSON Decode Error): {error_message} Raw text: {response.text[:200]}... -----")
            return json.dumps({"error": "JSONDecodeError", "message": error_message})

    # Håndtering af HTTP fejl (f.eks. 404 Not Found, 500 Server Error)
    except requests.exceptions.HTTPError as http_err:
        status_code = "Unknown"
        api_response_text_snippet = "[no response content]"

        if http_err.response is not None:
            status_code = http_err.response.status_code
            try:
                api_response_text_snippet = http_err.response.text[:200] if http_err.response.text else "[empty response body]"
            except Exception:
                api_response_text_snippet = "[could not retrieve error response text]"
        
        llm_friendly_message = f"API request failed with HTTP status {status_code}."
        
        print(f"----- TOOL ERROR (HTTPError): Status {status_code}. URL: {url}. Response: {api_response_text_snippet} -----")
        return json.dumps({
            "error": "APIHttpError",
            "message": llm_friendly_message,
            "status_code": status_code,
        })

    except requests.exceptions.Timeout:
        error_message = f"API request timed out after {DEFAULT_REQUEST_TIMEOUT} seconds."
        print(f"----- TOOL ERROR (Timeout): {error_message} URL: {url} -----")
        return json.dumps({"error": "APITimeoutError", "message": error_message})

    except requests.exceptions.ConnectionError:
        error_message = "Failed to connect to the API. Check network or API server."
        print(f"----- TOOL ERROR (ConnectionError): {error_message} URL: {url} -----")
        return json.dumps({"error": "APIConnectionError", "message": error_message})

    except requests.exceptions.RequestException as req_err: # Catch other requests-related errors
        error_message = f"An unexpected API request error occurred: {str(req_err)}"
        print(f"----- TOOL ERROR (RequestException): {error_message} URL: {url} -----")
        return json.dumps({"error": "APIRequestError", "message": error_message})

    except Exception as e: # Catch any other unexpected errors within the tool
        error_message = f"An unexpected internal error occurred in the tool: {str(e)}"
        print(f"----- TOOL ERROR (InternalToolError): {error_message} -----")
        return json.dumps({"error": "InternalToolError", "message": error_message})

# Test script til direkte kørsel af tools.py
def _test_and_print_todo_data(todo_id, description):
    print(f"--- Test Case: {description} (Todo ID: {todo_id}) ---")
    data_string = get_todo_data(todo_id)
    print(f"Raw output from tool: {data_string}")
    try:
        parsed_data = json.loads(data_string)
        if "error" in parsed_data:
            print(f"Tool returned error: {parsed_data.get('message')} (Type: {parsed_data.get('error')}, Status: {parsed_data.get('status_code')})")
        else:
            title = parsed_data.get('title', 'N/A')
            completed = parsed_data.get('completed', 'N/A')
            print(f"Successfully fetched: Title='{title}', Completed={completed}")
    except json.JSONDecodeError:
        print("Critical Error: Output from tool was not valid JSON, even for an error message.")
    print("-" * 40 + "\n")


if __name__ == "__main__":
    print("Starting direct test of get_todo_data tool...\n")

    test_cases = [
        {"id": 1, "desc": "Successful Call (Existing Todo)"},
        {"id": 5, "desc": "Successful Call (Another Existing Todo)"},
        {"id": 99999, "desc": "Non-existent Todo ID (Expect APIHttpError 404)"},
        {"id": 0, "desc": "Invalid Input (ID 0 - Expect InvalidInput Error)"},
        {"id": -5, "desc": "Invalid Input (Negative ID - Expect InvalidInput Error)"},
        # {"id": "abc", "desc": "Invalid Input (String ID)"}
    ]

    for case in test_cases:
        _test_and_print_todo_data(case["id"], case["desc"])

    # Test nogle andre ugyldige input
    print("--- Test Case: Invalid Input Type (String 'abc') ---")
    data_string_abc = get_todo_data("abc") # type: ignore # Suppress type checker warning for this test
    print(f"Raw output from tool for 'abc': {data_string_abc}")