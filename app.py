from flask import Flask, request, render_template
import requests
from datetime import datetime

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    if request.method == "POST":
        city = request.form["city"]
        lat, lon = get_coordinates(city)
        if lat and lon:
            weather_data = get_weather(lat, lon)
    return render_template("index.html", weather=weather_data)

def get_coordinates(city):
    url = f"https://nominatim.openstreetmap.org/search"
    params = {
        "city": city,
        "format": "json",
        "limit": 1
    }

    user_agent = "FlaskApp/1.0 w0491179@nscc.ca"
    
    response = requests.get(url, params=params, headers={"User-Agent": user_agent})
    
    if response.status_code == 200 and response.json():
        data = response.json()[0] 
        return float(data["lat"]), float(data["lon"])
    return None, None

def get_weather(lat, lon):
    """Fetch weather data for the given latitude and longitude."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=weather_code,temperature_2m_max,temperature_2m_min,sunrise,sunset,rain_sum,showers_sum,snowfall_sum,precipitation_sum,precipitation_hours&current=precipitation,weather_code,temperature_2m&timezone=auto"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        # Parse the time from ISO 8601 format and convert to a readable format
        weather_time = datetime.fromisoformat(data['current']['time'])
        # Format the time as YYYY-MM-DD HH:MM:SS
        formatted_time = weather_time.strftime('%Y-%m-%d %H:%M:%S')
        data['current']['formatted_time'] = formatted_time
        return data
    return None

if __name__ == "__main__":
    app.run(debug=True)
