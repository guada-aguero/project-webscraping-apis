import os
import logging
import wikipediaapi
from flask import Flask, request, redirect, session, jsonify, render_template, render_template_string
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path="C:/Users/guada/OneDrive/Documents/Ironhack/week09/day01/PROJECT-Data-thieves/project-webscraping-apis/secrets.env")

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'

SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')
UNSPLASH_ACCESS_KEY = os.getenv('UNSPLASH_ACCESS_KEY')

sp_oauth = SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope="user-read-playback-state user-modify-playback-state user-library-read"
)

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Wikipedia API with user agent
USER_AGENT = "MyApp/1.0 (https://example.com; myemail@example.com)"
wiki_wiki = wikipediaapi.Wikipedia('en', headers={'User-Agent': USER_AGENT})

# HTML template for input form
input_form = """
<!DOCTYPE html>
<html>
<head>
    <title>Route and Music Recommender</title>
</head>
<body>
    <h1>Enter your travel details</h1>
    <form action="/recommender" method="get">
        <label for="origin">Origin:</label>
        <input type="text" id="origin" name="origin" required>
        <br>
        <label for="destination">Destination:</label>
        <input type="text" id="destination" name="destination" required>
        <br>
        <label for="preferences">Genres or Artists (comma separated):</label>
        <input type="text" id="preferences" name="preferences" required>
        <br>
        <label for="type">Type:</label>
        <select id="type" name="type" required>
            <option value="genre">Genre</option>
            <option value="artist">Artist</option>
        </select>
        <br>
        <button type="submit">Get Route and Music</button>
    </form>
</body>
</html>
"""

@app.route('/')
def login():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect('/input')

@app.route('/input')
def input_page():
    return render_template_string(input_form)

@app.route('/recommender')
def recommender():
    token_info = session.get('token_info', None)
    if not token_info:
        return redirect('/')

    sp = Spotify(auth=token_info['access_token'])

    origin = request.args.get('origin')
    destination = request.args.get('destination')
    preferences = request.args.get('preferences')
    pref_type = request.args.get('type')

    user_preferences = [pref.strip() for pref in preferences.split(',')]

    route_data = get_route(origin, destination)
    if route_data and 'routes' in route_data and len(route_data['routes']) > 0 and 'legs' in route_data['routes'][0] and len(route_data['routes'][0]['legs']) > 0:
        legs = route_data['routes'][0]['legs'][0]
        travel_time = legs['duration']['value']
        formatted_time = f"{travel_time // 3600} hours {travel_time % 3600 // 60} minutes"
        
        origin_coords = legs['start_location']
        destination_coords = legs['end_location']

        recommendations = get_recommendations(sp, travel_time, user_preferences, pref_type)
        destination_history = get_wikipedia_summary(destination)
        weather_info = get_weather(destination)
        destination_image = get_destination_image(destination)

        response = {
            "travel_time": formatted_time,
            "weather_info": weather_info,
            "route_steps": [clean_html(step['html_instructions']) for step in legs['steps']],
            "recommendations": [{"artist": track['artists'][0]['name'], "track": track['name']} for track in recommendations],
            "destination_history": destination_history,
            "destination_image": destination_image,
            "destination": destination,
            "api_key": GOOGLE_MAPS_API_KEY,
            "origin_lat": origin_coords['lat'],
            "origin_lng": origin_coords['lng'],
            "destination_lat": destination_coords['lat'],
            "destination_lng": destination_coords['lng']
        }
        
        # Attempt to play the recommended tracks on the user's active device
        if not play_music_on_spotify(sp, [track['uri'] for track in recommendations]):
            response["warning"] = "No active Spotify device found or unable to start playback."

        return render_template('map_template.html', **response)
    else:
        logging.error("Error fetching route data")
        return jsonify({"error": "Error fetching route data"})

def get_route(origin, destination):
    endpoint = 'https://maps.googleapis.com/maps/api/directions/json'
    params = {
        'origin': origin,
        'destination': destination,
        'key': GOOGLE_MAPS_API_KEY
    }
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Google Maps API error: {response.status_code}, {response.text}")
        return None

def get_recommendations(sp, travel_time, user_preferences, pref_type):
    # Average song length in seconds
    avg_song_length = 180
    # Estimate the number of songs needed based on travel time
    num_songs = min(travel_time // avg_song_length, 100)

    print(f"Travel time: {travel_time}, Number of songs: {num_songs}")
    print(f"User preferences: {user_preferences}, Preference type: {pref_type}")

    if pref_type == "artist":
        user_preferences = get_artist_ids(sp, user_preferences)
        tracks = []
        for artist_id in user_preferences:
            top_tracks = sp.artist_top_tracks(artist_id)['tracks']
            tracks.extend(top_tracks)
        # Limit the tracks to the estimated number of songs
        tracks = tracks[:num_songs]
    else:
        try:
            # Ensure that the genres are valid and not empty
            if user_preferences:
                recommendations = sp.recommendations(seed_genres=user_preferences, limit=100)['tracks']
                print(f"Recommendations fetched: {len(recommendations)} tracks")
                # Limit the tracks to the estimated number of songs
                tracks = recommendations[:num_songs]
            else:
                print("No valid genres provided")
                tracks = []
        except Exception as e:
            print(f"Error fetching recommendations: {e}")
            tracks = []

    return tracks

def get_artist_ids(sp, artist_names):
    artist_ids = []
    for name in artist_names:
        results = sp.search(q='artist:' + name, type='artist')
        if results['artists']['items']:
            artist_ids.append(results['artists']['items'][0]['id'])
    return artist_ids

def get_wikipedia_summary(query):
    page = wiki_wiki.page(query)
    if page.exists():
        return page.summary  # Get the full summary
    else:
        return "Historical information not available"

def get_weather(location):
    endpoint = 'https://api.openweathermap.org/data/2.5/weather'
    params = {
        'q': location,
        'appid': OPENWEATHERMAP_API_KEY,
        'units': 'metric'
    }
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        data = response.json()
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        return f"{weather_description.capitalize()}, {temperature}°C"
    else:
        logging.error(f"OpenWeatherMap API error: {response.status_code}, {response.text}")
        return "Weather data not available"

def get_destination_image(query):
    endpoint = 'https://api.unsplash.com/search/photos'
    params = {
        'query': query,
        'client_id': UNSPLASH_ACCESS_KEY,
        'per_page': 1
    }
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['results']:
            return data['results'][0]['urls']['regular']
        else:
            return None
    else:
        logging.error(f"Unsplash API error: {response.status_code}, {response.text}")
        return None

def clean_html(raw_html):
    import re
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

def play_music_on_spotify(sp, track_uris):
    devices = sp.devices()
    logging.debug(f"Devices: {devices}")
    if devices['devices']:
        active_device_id = devices['devices'][0]['id']
        logging.debug(f"Active device ID: {active_device_id}")
        try:
            sp.start_playback(device_id=active_device_id, uris=track_uris)
            return True
        except Exception as e:
            logging.error(f"Spotify playback error: {e}")
            return False
    else:
        logging.error("No active devices found")
        return False

if __name__ == "__main__":
    app.run(debug=True)











