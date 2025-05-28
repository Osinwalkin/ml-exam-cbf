# Autogen AI Agent: Aktuel Vejrudsigt Henter

Dette projekt implementerer et AI-agent system ved hjælp af AutoGen frameworket og Mistral's `open-mistral-nemo` Large Language Model (LLM). Agenten er designet til at hente den aktuelle vejrudsigt (temperatur og beskrivelse) for en specificeret by ved hjælp af OpenWeatherMap API'en.

Dette projekt er blevet udviklet som en del af eksamensprojektet i Machine Learning (Forår 2025).

## Funktionaliteter

*   **Ekstern API Integration:** Agenten anvender et brugerdefineret Python-værktøj (`get_current_weather`) til at hente data fra OpenWeatherMap API'en.
*   **Brug af Værktøjer:** Demonstrerer definition og brug af et brugerdefineret værktøj inden for Autogen-frameworket.
*   **Kodegenerering & Eksekvering:** LLM'en (via `WeatherAssistant`-agenten) genererer Python-kode til at parse JSON-svaret fra API'en. Denne kode eksekveres derefter af `UserProxyAgent`.
*   **Multi-Agent Interaktion:** Implementerer et setup med to agenter (`UserProxyAgent` og `WeatherAssistant`), der samarbejder om at opfylde brugerens anmodning.
*   **Fejlhåndtering:** Værktøjet og agentsystemet inkluderer logik til at håndtere ugyldige brugerinput, API-fejl (f.eks. by ikke fundet, ugyldig API-nøgle) og parsing-problemer.
*   **Håndtering af Environment Variabler:** Sikker håndtering af API-nøgler ved hjælp af en `.env`-fil.

## Projektstruktur

*   app.py            # til at køre Autogen-agenterne
*   tools.py          # Indeholder API tool
*   requirements.txt
*   .env              # environment variabler
*   README.md         
*   use_cases.md      # Få use cases af hvad man kan forvente af agenten

## Afhængigheder

*   Python 3.10
*   AutoGen Framework
*   Mistral AI Client `mistralai`
*   python-dotenv
*   requests
Resten ligger i requirements.txt 

## Opsætningsinstruktioner

1.  **Klon Repository'et:**

    git clone URL
    cd REPOSITORY


2.  **Opret og Aktivér et Python Virtuelt Miljø:**

    ```bash
    python -m venv venv
    # Windows
    # venv\Scripts\activate
    ```

3.  **Installér Afhængigheder:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Opsæt Environment Variabler:**
    *   Lav en .env fil
    *   Man skal tilmelde sig og få fat i en nøgle fra mistral og OpenWeatherMap
        MISTRAL_API_KEY=""
        OPENWEATHERMAP_API_KEY=""

## Sådan Kører Du Koden

1.  Sørg for, at dit virtuelle miljø er aktiveret, og alle afhængigheder er installeret.
2.  Verificér, at dine `MISTRAL_API_KEY` og `OPENWEATHERMAP_API_KEY` er korrekt sat i `.env`-filen.

3.  Kør
    ```bash
    python app.py
    ```

4.  
    * Scriptet vil starte en samtale mellem agenterne. I bunden af app.py kan du se de forskellige scenarier, kør kun en af gangen da den kan starte med at hallucinere.

## Agent Design Overblik

Systemet består af to primære Autogen-agenter:

1.  **`UserProxyAgent`
    *   Starter chatten med brugerens anmodning (f.eks. at spørge om vejret i en by).
    *   Executer `get_current_weather`-værktøjet, når anmodet af `WeatherAssistant`
    *   Executer Python-kode genereret af `WeatherAssistant` til opgaver som f.eks. parsing af JSON-vejrdata.
    *   Opererer uden direkte input under kørslen (`human_input_mode="NEVER"`).

2.  **`AssistantAgent` ("WeatherAssistant"):**
    *   Drevet af Mistral `open-mistral-nemo` LLM.
    *   Modtager brugeranmodninger og værktøjsoutput.
    *   Fortolker brugerens anmodning for at identificere bynavnet.
    *   Beslutter, hvornår `get_current_weather_for_agent`-værktøjet skal bruges (dette er navnet defineret i det tool schema, der gives til LLM'en).
    *   Genererer Python-kode til at parse JSON-data returneret af OpenWeatherMap API'en, specifikt for at udtrække temperatur og vejrbeskrivelse.
    *   Formulerer det endelige svar til brugeren, hvor vejrinformationen eller eventuelle fejl præsenteres.
    *   Har en system_message/prompt den følger