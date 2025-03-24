from flask import Flask, request, render_template
import requests

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
    
    response = requests.get(url, params=params, headers={"User-Agent": "FlaskApp/1.0"})
    
    if response.status_code == 200 and response.json():
        data = response.json()[0] 
        return float(data["lat"]), float(data["lon"])
    return None, None

def get_weather(lat, lon):
    """Fetch weather data for the given latitude and longitude."""
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

if __name__ == "__main__":
    app.run(debug=True)
