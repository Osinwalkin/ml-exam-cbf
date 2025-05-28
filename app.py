# app.py
import warnings

warnings.filterwarnings("ignore", message="flaml.automl is not available.")
warnings.filterwarnings("ignore", message="Cost calculation is not implemented for model open-mistral-nemo")

import os
import autogen
from dotenv import load_dotenv
from tools import get_current_weather
import json

# Load environment variabler
load_dotenv()
mistral_api_key = os.getenv("MISTRAL_API_KEY")
openweathermap_api_key = os.getenv("OPENWEATHERMAP_API_KEY")

if not mistral_api_key:
    raise ValueError("MISTRAL_API_KEY not found in .env file or environment variables.")
if not openweathermap_api_key:
    raise ValueError("OPENWEATHERMAP_API_KEY not found in .env file. Please add it to use the weather tool.")

# Define LLM Configuration
BASE_LLM_CONFIG_MISTRAL = { 
    "config_list": [
        {
            "model": "open-mistral-nemo",
            "api_key": mistral_api_key,
            "api_type": "mistral",
            "api_base": "https://api.mistral.ai/v1",
            "temperature": 0.3,
            "native_tool_calls": False, 
            "seed": 42,
            "api_rate_limit": 0.25
        }
    ],
    "cache_seed": None,
}

# Tool schema til vejrdata
get_weather_tool_schema = {
    "type": "function",
    "function": {
        "name": "get_current_weather",
        "description": "Fetches the current weather for a specified city. Requires the city name.",
        "parameters": {
            "type": "object",
            "properties": {
                "city_name": {
                    "type": "string",
                    "description": "The name of the city, e.g., 'London' or 'Copenhagen,DK'. For cities with common names, adding a comma and two-letter country code can improve accuracy (e.g., 'Paris,FR')."
                }
            },
            "required": ["city_name"]
        }
    }
}

llm_config_for_assistant_with_weather_tool = {
    **BASE_LLM_CONFIG_MISTRAL,
    "tools": [get_weather_tool_schema], 
}

# En wrapper til at kalde værktøjet fra Autogen
def get_current_weather_for_autogen(city_name: str) -> str:
    if not openweathermap_api_key:
        return json.dumps({"error": "ConfigError", "message": "OpenWeatherMap API key is not configured in the system."})
    return get_current_weather(city_name=city_name, api_key=openweathermap_api_key)

WEATHER_ASSISTANT_SYSTEM_MESSAGE = """You are a helpful AI assistant that provides current weather information for a city.

Your task:
1.  The user will ask for the weather in a specific city.
2.  Use the `get_current_weather_for_agent` tool with the city name.
3.  The tool will return a JSON string.
    *   If the JSON string indicates an error from the tool or the API (e.g., contains an "error" key, or an API "cod" that isn't 200 like "404" for city not found), report this error clearly.
    *   If the JSON string is successful weather data (API "cod" is 200):
        *   Write a Python code block to parse this JSON string.
        *   Extract the temperature (from `data['main']['temp']`) and the weather description (from `data['weather'][0]['description']`).
        *   Print the temperature (in Celsius) and the description.
4.  Summarize the findings from the Python code or report any errors.
5.  End your response with TERMINATE.

Example of Python code for successful data:
```python
import json
# weather_json_string will be the string from the tool
# weather_json_string = '{"main":{"temp":10.5},"weather":[{"description":"cloudy"}],"cod":200}' # Simplified example
data = json.loads(weather_json_string)
temp = data.get('main', {}).get('temp')
desc = data.get('weather', [{}])[0].get('description')
if temp is not None and desc is not None:
    print(f"Temperature: {temp}°C")
    print(f"Description: {desc}")
else:
    print("Error: Could not extract weather details.")"""

# Lav en AssistantAgent (vejr-assistenten) med systembesked og LLM-konfiguration
weather_assistant = autogen.AssistantAgent(
    name="WeatherAssistant",
    system_message=WEATHER_ASSISTANT_SYSTEM_MESSAGE,
    llm_config=llm_config_for_assistant_with_weather_tool,
    function_map={
        get_weather_tool_schema["function"]["name"]: get_current_weather_for_autogen
    }
)

# Lav en UserProxyAgent, der vil interagere med vejr-assistenten
user_proxy = autogen.UserProxyAgent(
    name="UserProxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("content", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "work_dir": "coding", 
        "use_docker": False, 
    },
    function_map={
        get_weather_tool_schema["function"]["name"]: get_current_weather_for_autogen
    }
)

print("Starter samtale med vejr-assistenten...")

# Test Scenarier (vælg én ad gangen)
#user_initial_message = "What is the current weather in Copenhagen?"
user_initial_message = "What is the weather in New York City?"
#user_initial_message = "How's the weather in NonExistentCityName123?" # Forventer fejl fra API'en
#user_initial_message = "Weather for." # Forventer at LLM'en spørger om en by, eller at input validering fejler

user_proxy.initiate_chat(
    weather_assistant,
    message=user_initial_message
)

print("\nSamtale afsluttet.")