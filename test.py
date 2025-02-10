import requests
import json

# Fetch data from the API
url = r"https://www.yr.no/api/v0/locations/1-255674/forecast"
url = r"https://www.yr.no/api/v0/locations/1-255674/auroraforecast?language=nb"
response = requests.get(url)

if response.status_code == 200:
    # Parse the JSON response
    data = response.json()

    # Save the JSON data to a file
    with open("forecast.json", "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    print("Data saved to 'forecast.json'")
else:
    print(f"Failed to fetch data. Status code: {response.status_code}")
