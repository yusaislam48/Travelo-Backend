from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from dotenv import load_dotenv
import os
import requests
import base64
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Initialize Flask and OpenAI client
app = Flask(__name__)
CORS(app)
client = OpenAI(api_key=OPENAI_API_KEY)

# ----------------------
# PLAN TRIP (ChatGPT)
# ----------------------
@app.route('/api/plan-trip', methods=['POST'])
def plan_trip():
    data = request.get_json()
    origin = data.get("origin", "Unknown")
    destination = data.get("destination", "")
    date = data.get("date", "")
    language = data.get("language", "bn")  # default to Bangla
    currency = data.get("currency", "BDT")  # default to BDT

    if not destination:
        return jsonify({"error": "Destination is required"}), 400

    # Instruction for OpenAI to respond in selected language and currency
    prompt = (
        f"You are a smart multilingual travel assistant. Respond in '{language}' language.\n\n"
        f"Plan a trip from {origin} to {destination} on {date}. "
        f"Show all costs in {currency}.\n\n"
        f"### Best Time to Visit:\n\n"
        f"### Top 3 Attractions:\n\n"
        f"### Recommended Travel Methods:\n\n"
        f"### Budget Breakdown:\n\n"
        f"### Hotel Zone Suggestions:\n\n"
        f"### Packing Tips:\n"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a smart travel planner who adapts to the user's preferred language and currency."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        message = response.choices[0].message.content
        return jsonify({"result": message})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/config/maps-key', methods=['GET'])
def get_maps_api_key():
    return jsonify({ "key": GOOGLE_MAPS_API_KEY })

@app.route('/api/config/weather-key', methods=['GET'])
def get_weather_api_key():
    return jsonify({ "key": OPENWEATHER_API_KEY })


# ----------------------
# WEATHER API (OpenWeatherMap)
# ----------------------
@app.route('/api/weather', methods=['POST'])
def get_weather():
    city = request.json.get("city")
    if not city:
        return jsonify({"error": "City is required"}), 400

    try:
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
        res = requests.get(url, params=params)
        data = res.json()

        if res.status_code != 200:
            return jsonify({"error": f"OpenWeatherMap error: {data.get('message', 'Unknown error')}"})

        return jsonify({
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"]
        })

    except Exception as e:
        print("⚠️ WEATHER ERROR:", e)
        return jsonify({"error": str(e)}), 500


# ----------------------
# RESTAURANTS NEARBY (Google Places)
# ----------------------
@app.route('/api/restaurants', methods=['POST'])
def get_restaurants():
    location = request.json.get("location")  # Expected format: {"lat": ..., "lng": ...}
    if not location:
        return jsonify({"error": "Location is required"}), 400

    try:
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{location['lat']},{location['lng']}",
            "radius": 3000,
            "type": "restaurant",
            "key": GOOGLE_MAPS_API_KEY
        }
        res = requests.get(url, params=params)
        data = res.json()

        restaurants = [{
            "name": r["name"],
            "rating": r.get("rating", "N/A"),
            "vicinity": r["vicinity"]
        } for r in data.get("results", [])[:5]]

        return jsonify({"restaurants": restaurants})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------
# ITINERARY GENERATOR (ChatGPT)
# ----------------------
@app.route('/api/itinerary', methods=['POST'])
def get_itinerary():
    destination = request.json.get("destination")
    days = request.json.get("days", 3)
    language = request.json.get("language", "bn")
    currency = request.json.get("currency", "BDT")

    if not destination:
        return jsonify({"error": "Destination required"}), 400

    try:
        prompt = (
            f"You are a smart travel planner. Respond in '{language}'. "
            f"Create a {days}-day travel itinerary for {destination}. "
            f"Include day-wise sightseeing, food spots, tips, and mention costs in {currency}."
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        itinerary = response.choices[0].message.content
        return jsonify({"itinerary": itinerary})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ----------------------
# IMAGE ANALYSIS (OpenAI Vision)
# ----------------------
@app.route('/api/analyze-image', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if not file.content_type.startswith('image/'):
        return jsonify({"error": "File must be an image"}), 400

    try:
        # Read and encode the image
        image_data = file.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Create the prompt for image analysis
        prompt = """Analyze this travel destination image and provide the following details:
        1. The name of the place/landmark
        2. The city and country where it's located
        3. A brief description of its historical and cultural significance
        4. The best time to visit
        5. Top things to do in the area
        
        Format the response as a JSON object with the following keys:
        place_name, city, country, description, best_time, things_to_do"""

        # Call OpenAI Vision API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )

        # Parse the response
        result = response.choices[0].message.content
        
        # Clean and validate the response
        try:
            # Try to extract JSON from the response text
            # Look for JSON-like structure in the text
            import json
            import re
            
            # Try to find a JSON object in the text
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                result = json_match.group()
            
            data = json.loads(result)
            required_keys = ['place_name', 'city', 'country', 'description', 'best_time', 'things_to_do']
            
            # Ensure all required keys exist
            for key in required_keys:
                if key not in data:
                    data[key] = "Information not available"
                    
            return jsonify(data)
            
        except (json.JSONDecodeError, AttributeError) as e:
            print("⚠️ JSON PARSING ERROR:", str(e))
            print("Raw response:", result)
            # Fallback if the response is not valid JSON
            return jsonify({
                "place_name": "Could not determine",
                "city": "Unknown",
                "country": "Unknown",
                "description": "Could not parse the response properly. Please try again.",
                "best_time": "Information not available",
                "things_to_do": "Information not available"
            })

    except Exception as e:
        print("⚠️ IMAGE ANALYSIS ERROR:", str(e))
        return jsonify({"error": "Failed to analyze image"}), 500


# ----------------------
# MAIN
# ----------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=True)