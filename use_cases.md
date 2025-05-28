# Use Cases til WeatherAgent

## Use Case 1: Godkendt weather fetch

**Input/Prompt:**
user_initial_message = "What is the current weather in Copenhagen?"
**Forventet Output og Rigtig output:**
The current weather in Copenhagen, DK is as follows:
Temperature: 15.3°C
Description: Broken clouds
TERMINATE

## Use Case 2: By ikke fundet

**Input/Prompt:**
user_initial_message = "How's the weather in NonExistentCityName123?"
**Forventet Output:**
?
**Rigtigt Output:**
   * UserProxy (to WeatherAssistant):
   * exitcode: 0 (execution succeeded)
   * Code output:
   * Error: API-kald for vejrdata fejlede. Status 404. Detaljer: city not found
   * WeatherAssistant (to UserProxy):
   * I'm sorry, but I couldn't find weather information for NonExistentCityName123. Please check the city name and try again. TERMINATE
   * Samtale afsluttet.

## Use Case 3: Uklart bruger input

**Input/Prompt:**
user_initial_message = "Weather for."
**Forventet Output:**
?
**Rigtig Output:**
The current weather in Copenhagen, DK is 15.3°C with broken clouds. TERMINATE

