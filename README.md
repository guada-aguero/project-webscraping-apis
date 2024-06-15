# Route and Music Recommender

## Introduction

Welcome to the Route and Music Recommender app! This application is designed to enhance your travel experience by providing you with a customized travel route, weather information, historical facts about your destination, and a tailored music playlist to enjoy during your journey. The app leverages multiple APIs to gather and present this information seamlessly.

## How It Works

The app integrates several APIs to provide a comprehensive travel experience:

1. **Spotify API**: Used for authenticating users and generating personalized music recommendations based on user preferences (artists or genres).
2. **Google Maps API**: Fetches the travel route between the origin and destination, including step-by-step directions and estimated travel time.
3. **OpenWeatherMap API**: Provides current weather information for the destination.
4. **Wikipedia API**: Retrieves historical and summary information about the destination.
5. **Unsplash API**: Fetches a relevant image of the destination to give a visual appeal.

### Pipeline Overview

1. **User Authentication**: Users authenticate via Spotify to enable music recommendation and playback features.
2. **Input Form**: Users enter their travel details, including the origin, destination, and music preferences.
3. **API Requests**: The app makes requests to various APIs to gather travel routes, weather data, historical facts, and destination images.
4. **Data Processing**: The gathered data is processed to create a comprehensive travel and music recommendation package.
5. **Display Results**: The results, including the travel route, weather, historical information, and music playlist, are displayed on a web page.

## External Data Sources

- [Spotify API](https://developer.spotify.com/documentation/web-api/)
- [Google Maps API](https://developers.google.com/maps/documentation/directions/start)
- [OpenWeatherMap API](https://openweathermap.org/api)
- [Wikipedia API](https://wikipedia.readthedocs.io/en/latest/code.html)
- [Unsplash API](https://unsplash.com/documentation)

## Conclusions

This project demonstrates how multiple APIs can be integrated to create a rich user experience. By combining travel route information, real-time weather updates, historical data, and personalized music playlists, users receive a tailored travel companion that enhances their journey.

## Further Questions

If you have any questions or need further assistance, feel free to reach out to the project maintainers.

---

### How to Run the Project

#### Prerequisites

- Python 3.7 or higher
- Flask
- Spotipy
- Requests
- Wikipedia-API
- dotenv

#### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/route-music-recommender.git
   cd route-music-recommender

2. **Install dependencies**:

	pip install -r requirements.txt

3. **Setup environment variables**:

 - Create a .env file in the project directory.
 - Add your API keys and secrets to the .env file:
	SPOTIPY_CLIENT_ID=your_spotify_client_id
	SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
	SPOTIPY_REDIRECT_URI=your_spotify_redirect_uri
	GOOGLE_MAPS_API_KEY=your_google_maps_api_key
	OPENWEATHERMAP_API_KEY=your_openweathermap_api_key
	UNSPLASH_ACCESS_KEY=your_unsplash_access_key

4. **Run the application**:
	python app.py

5. **Access the app**:
	Open your web browser and go to http://127.0.0.1:5000/.

Enjoy your enhanced travel experience with Route and Music Recommender!
