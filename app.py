from flask import Flask, request, render_template
import requests
import os
import json
from datetime import datetime

app = Flask(__name__)
latitude = None
longitude = None

weather_data = None

@app.route("/", methods=["GET", "POST"])
def index():
    global weather_data
    graph_data = None
    background_image = "static/Background_Images/default.png"
    weather_icons = ["default.png"] * 7  # Default icon for 7-day forecast if no data

    if request.method == "POST":
        global city_name 
        city_name = request.form["city"]
        city = request.form["city"]
        lat, lon = get_coordinates(city)
        if lat and lon:
            weather_data = get_weather(lat, lon)
            
            # Check if weather_data is valid
            if weather_data:
                weather_code = weather_data["current"]["weather_code"]
                background_image = get_background_image(weather_code)
                graph_data = {
                    "time": weather_data["daily"]["time"],
                    "temperature_2m_max": weather_data["daily"]["temperature_2m_max"],
                    "temperature_2m_min": weather_data["daily"]["temperature_2m_min"],
                } 

                # Map weather codes to icon filenames
                icon_mapping = {
                    0: "clear-sky.png",
                    1: "partly-cloudy.png", 2: "partly-cloudy.png", 3: "partly-cloudy.png",
                    45: "fog.png", 48: "fog.png",
                    51: "drizzle.png", 53: "drizzle.png", 55: "drizzle.png",
                    56: "freezing-drizzle.png", 57: "freezing-drizzle.png",
                    61: "rain.png", 63: "rain.png", 65: "rain.png",
                    66: "freezing-rain.png", 67: "freezing-rain.png",
                    71: "snow.png", 73: "snow.png", 75: "snow.png", 77: "snow.png",
                    85: "snow-grains.png", 86: "snow-grains.png",
                    95: "thunderstorm.png", 96: "thunderstorm.png", 99: "thunderstorm.png"
                }

                # Map the 7-day forecast weather codes to their respective icons
                weather_icons = []
                for code in weather_data["daily"]["weather_code"]:
                    icon = icon_mapping.get(code, "default.png")  # Default icon if no match
                    weather_icons.append(icon)

            else:
                # If weather_data is None, set a default image or show an error
                background_image = "static/Background_Images/error.png"
                weather_icons = ["error.png"] * 7  # Placeholder error icon

        else:
            # Handle the case where coordinates are not found
            background_image = "static/Background_Images/error.png"
            weather_icons = ["error.png"] * 7  # Placeholder error icon

    city_name = weather_data['timezone'].split('/')[-1] if weather_data else "Unknown City"

    return render_template("index.html", weather=weather_data , city_name=city_name, background_image=background_image, graph=json.dumps(graph_data), weather_icons=weather_icons)

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

        latitude = data["lat"]
        longitude = data["lon"]

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

# Function to determine background image based on weather code
def get_background_image(weather_code):
    """Returns the appropriate background image based on the weather code."""
    image_folder = "/static/Background_Images"  # Ensure the path starts with a slash

    print(f"Weather code: {weather_code}")  # Debugging line

    background_mapping = {
        "clear_sky.png": [0],
        "partly_cloudy.png": [1, 2, 3],
        "fog.png": [45, 48],
        "drizzle.png": [51, 53, 55],
        "freezing_drizzle.png": [56, 57],
        "rain.png": [61, 63, 65],
        "freezing_rain.png": [66, 67],
        "snow.png": [71, 73, 75, 77],
        "snow_grains.png": [85, 86],
        "thunderstorm.png": [95, 96, 99]
    }

    # Check for the correct image
    for image, codes in background_mapping.items():
        if weather_code in codes:
            image_path = f"{image_folder}/{image}"
            return image_path if os.path.exists(image_path.lstrip('/')) else f"{image_folder}/default.png"
    
    print(f"{image_folder}/default.png")
    return f"{image_folder}/default.png"

@app.route('/day-details/<int:day_index>')
def day_details(day_index):
    # Fetch weather details for the selected day
    background_image = get_background_image(weather_data["daily"]["weather_code"][day_index])
    return render_template('day_details.html', weather=weather_data, day_index=day_index, city_name=city_name, background_image=background_image)