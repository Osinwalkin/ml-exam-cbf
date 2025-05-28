# tools.py
import requests
import json
import os

# Konstanter for API URL og standard timeout
OPENWEATHERMAP_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
DEFAULT_REQUEST_TIMEOUT = 10


# Fetcher data til en specifik todo fra JSONPlaceholder API.
# Returnerer raw JSON-respons som en string, hvis det lykkes.
# Hvis der opstår problemer, returneres en JSON-streng med en 'error'-nøgle.
def get_current_weather(city_name: str, api_key: str) -> str:
    """
    Fetches current weather data for a specified city using OpenWeatherMap API.
    Returns the raw JSON response as a string if successful.
    Returns a JSON string with an 'error' key if any issue occurs.

    Args:
        city_name: The name of the city (e.g., "London", "Copenhagen,DK").
        api_key: Your OpenWeatherMap API key.
    """
    # Log start
    print(f"----- VÆRKTØJ KØRER: get_current_weather (By: {city_name}) -----")

    if not api_key:
        error_message = "OpenWeatherMap API key mangler."
        print(f"----- VÆRKTØJSFEJL (Konfiguration): {error_message} -----")
        return json.dumps({"error": "ConfigError", "message": error_message})

    if not city_name or not isinstance(city_name, str):
        error_message = "Ugyldigt bynavn. Skal være en streng og ikke tom."
        print(f"----- VÆRKTØJSFEJL (Input Validering): {error_message} -----")
        return json.dumps({"error": "InvalidInput", "message": error_message})

    # Sammensæt URL til API-kald
    # units=metric for Celsius, units=imperial for Fahrenheit
    params = {
        "q": city_name,
        "appid": api_key,
        "units": "metric" # Eller 'imperial' for Fahrenheit
    }

    try:
        # Udfør API-kald
        response = requests.get(OPENWEATHERMAP_BASE_URL, params=params, timeout=DEFAULT_REQUEST_TIMEOUT)
        response.raise_for_status()  # Kaster HTTPError for 4xx/5xx statuskoder

        # API-kald var succesfuldt
        print(f"----- VÆRKTØJ: Vejrdata API-kald succesfuldt (Status: {response.status_code}). -----")
        
        # OpenWeatherMap returnerer altid JSON, så vi kan direkte returnere teksten
        # Yderligere validering af JSON-struktur kan tilføjes hvis nødvendigt
        return response.text # Returner rå JSON-streng

    except requests.exceptions.HTTPError as http_err:
        # Håndtering af HTTP fejl
        status_code = "Ukendt"
        error_details_from_api = ""
        if http_err.response is not None:
            status_code = http_err.response.status_code
            try:
                # OpenWeatherMap returnerer ofte en JSON fejlbesked
                error_data = http_err.response.json()
                error_details_from_api = error_data.get("message", http_err.response.text[:200])
            except json.JSONDecodeError:
                error_details_from_api = http_err.response.text[:200] if http_err.response.text else "[tomt svar]"
        
        llm_venlig_besked = f"API-kald for vejrdata fejlede. Status {status_code}. Detaljer: {error_details_from_api}"
        
        print(f"----- VÆRKTØJSFEJL (HTTPError): Status {status_code}. Detaljer: {error_details_from_api} -----")
        return json.dumps({
            "error": "APIHttpError",
            "message": llm_venlig_besked,
            "status_code": status_code,
        })

    except requests.exceptions.Timeout:
        error_message = f"API-kald for vejrdata timede ud efter {DEFAULT_REQUEST_TIMEOUT} sekunder."
        print(f"----- VÆRKTØJSFEJL (Timeout): {error_message} -----")
        return json.dumps({"error": "APITimeoutError", "message": error_message})

    except requests.exceptions.ConnectionError:
        error_message = "Kunne ikke forbinde til OpenWeatherMap API'et."
        print(f"----- VÆRKTØJSFEJL (ConnectionError): {error_message} -----")
        return json.dumps({"error": "APIConnectionError", "message": error_message})

    except requests.exceptions.RequestException as req_err:
        error_message = f"En uventet API-forespørgselsfejl opstod: {str(req_err)}"
        print(f"----- VÆRKTØJSFEJL (RequestException): {error_message} -----")
        return json.dumps({"error": "APIRequestError", "message": error_message})

    except Exception as e:
        error_message = f"En uventet intern fejl opstod i værktøjet: {str(e)}"
        print(f"----- VÆRKTØJSFEJL (InternalToolError): {error_message} -----")
        return json.dumps({"error": "InternalToolError", "message": error_message})

# --- Test script til direkte kørsel af tools.py ---
def _test_and_print_weather_data(city: str, api_key_for_test: str, description: str):
    """Hjælpefunktion til at køre en test case for vejrdata og printe resultatet."""
    print(f"--- Test Case: {description} (By: {city}) ---")
    data_string = get_current_weather(city, api_key_for_test)
    print(f"Rå output fra vejr-værktøj: {data_string[:500]}...") # Print kun starten af outputtet
    
    try:
        parsed_data = json.loads(data_string)
        if "error" in parsed_data: # Værktøjet returnerede en struktureret fejl
            print(f"Værktøj returnerede fejl: {parsed_data.get('message')} (Type: {parsed_data.get('error')})")
        elif "cod" in parsed_data and str(parsed_data.get("cod")) != "200": # API'en selv returnerede en fejl (f.eks. by ikke fundet)
            print(f"API fejl: {parsed_data.get('message')} (Kode: {parsed_data.get('cod')})")
        else: # Forventet succes
            temp = parsed_data.get("main", {}).get("temp")
            desc = parsed_data.get("weather", [{}])[0].get("description")
            print(f"Succesfuldt hentet: Temperatur={temp}°C, Beskrivelse='{desc}'")
    except json.JSONDecodeError:
        print("KRITISK FEJL: Output fra værktøj var ikke gyldig JSON.")
    print("-" * 40 + "\n")


if __name__ == "__main__":
    # Importer load_dotenv specifikt til direkte testkørsel
    from dotenv import load_dotenv
    load_dotenv() 
    
    # Hent API-nøglen fra .env
    test_api_key_from_env = os.getenv("OPENWEATHERMAP_API_KEY")

    if not test_api_key_from_env:
        print("ADVARSEL: OPENWEATHERMAP_API_KEY ikke fundet i .env filen.")
        print("Sørg for, at .env filen eksisterer i samme mappe som tools.py (eller projektets rodmappe)")
        print("og indeholder linjen: OPENWEATHERMAP_API_KEY='din_api_nøgle_her'")
        print("Kan ikke køre tests for get_current_weather uden API-nøgle.")
    else:
        print("Starter direkte test af get_current_weather værktøjet...\n")
        test_cities = [
            {"city": "London", "desc": "Succesfuldt kald (London)"},
            {"city": "Copenhagen,DK", "desc": "Succesfuldt kald (København med landekode)"},
            {"city": "NonExistentCityName123", "desc": "By ikke fundet (Forventer API-fejl 404 'city not found')"},
            {"city": "", "desc": "Tomt bynavn (Forventer værktøjsfejl 'InvalidInput')"},
        ]

        for test_case in test_cities:
            # Send den hentede API-nøgle med til testfunktionen
            _test_and_print_weather_data(test_case["city"], test_api_key_from_env, test_case["desc"])

        # Test med en tom streng som API-nøgle for at tjekke validering i selve get_current_weather
        _test_and_print_weather_data("Paris", "", "Manglende API-nøgle i kald (tom streng)")
