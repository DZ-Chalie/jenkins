import requests
import json

api_key = 'f2d4edf96a127c40d4c152319c9fc2bc'
cities = ['Seoul', 'Busan', 'Suwon']

print("--- Testing OpenWeatherMap API ---")

for city in cities:
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city},KR&appid={api_key}&units=metric&lang=kr'
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {city}: {data['weather'][0]['main']} ({data['weather'][0]['description']}), Temp: {data['main']['temp']}")
        else:
            print(f"❌ {city}: Error {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ {city}: Exception {e}")
