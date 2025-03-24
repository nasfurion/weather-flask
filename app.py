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
    # You can use a geocoding API (like Nominatim) to get latitude and longitude
    return 44.6464, -63.5729  # Example: Halifax, Nova Scotia

def get_weather(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

if __name__ == "__main__":
    app.run(debug=True)
