import requests
import json

def get_bitcoin_price_data() -> str:
    """
    Fetches the current Bitcoin price data from the CoinDesk API.
    Returns the full JSON response as a string to allow the LLM to parse it.
    Includes basic error handling.
    """
    print("----- EXECUTING TOOL: get_bitcoin_price_data -----")
    try:
        url = "https://api.coindesk.com/v1/bpi/currentprice.json"
        response = requests.get(url)
        response.raise_for_status() # Raises an HTTPError for bad responses (4XX or 5XX)
        print(f"----- TOOL: API Call Successful. Response: {response.text[:100]}... -----")
        return response.text # Return the raw JSON string
    except requests.exceptions.HTTPError as http_err:
        error_message = f"HTTP error occurred: {http_err} - Status Code: {response.status_code}"
        print(f"----- TOOL ERROR: {error_message} -----")
        return json.dumps({"error": "HTTPError", "message": error_message})
    except requests.exceptions.ConnectionError as conn_err:
        error_message = f"Error Connecting: {conn_err}"
        print(f"----- TOOL ERROR: {error_message} -----")
        return json.dumps({"error": "ConnectionError", "message": error_message})
    except requests.exceptions.Timeout as timeout_err:
        error_message = f"Timeout Error: {timeout_err}"
        print(f"----- TOOL ERROR: {error_message} -----")
        return json.dumps({"error": "Timeout", "message": error_message})
    except requests.exceptions.RequestException as req_err:
        error_message = f"An unexpected error occurred with the API request: {req_err}"
        print(f"----- TOOL ERROR: {error_message} -----")
        return json.dumps({"error": "RequestException", "message": error_message})

if __name__ == "__main__":
    # Test the tool directly
    data = get_bitcoin_price_data()
    print("\nRaw data from tool:")
    print(data)
    # Basic manual parsing test
    try:
        parsed_data = json.loads(data)
        if "error" not in parsed_data:
            usd_rate = parsed_data['bpi']['USD']['rate_float']
            print(f"\nManually extracted USD rate: {usd_rate}")
        else:
            print(f"\nError in fetched data: {parsed_data['error']} - {parsed_data.get('message')}")
    except json.JSONDecodeError:
        print("\nFailed to parse JSON from tool output.")
    except KeyError:
        print("\nFailed to extract USD rate, unexpected JSON structure.")