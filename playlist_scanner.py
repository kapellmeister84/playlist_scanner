import streamlit as st
import requests
import json
import base64
import time
from datetime import datetime, timedelta
from pathlib import Path

# --- Secrets ---
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
TOKEN_FILE = Path("spotify_token.json")

# --- Token Management ---
def get_stored_token():
    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "r") as f:
            data = json.load(f)
        return data
    return None

def save_token(data):
    with open(TOKEN_FILE, "w") as f:
        json.dump(data, f)

def is_token_valid(data):
    expiry = datetime.strptime(data["expires_at"], "%Y-%m-%dT%H:%M:%S")
    return datetime.utcnow() < expiry

def get_new_token():
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_string.encode()).decode()
    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    response.raise_for_status()
    token_data = response.json()
    token_data["expires_at"] = (datetime.utcnow() + timedelta(seconds=token_data["expires_in"]) - timedelta(seconds=10)).strftime("%Y-%m-%dT%H:%M:%S")
    save_token(token_data)
    return token_data

def get_valid_token():
    stored = get_stored_token()
    if stored and is_token_valid(stored):
        return stored["access_token"]
    return get_new_token()["access_token"]

# --- App UI ---
st.set_page_config("Spotify Token Test", layout="centered")
st.title("Spotify Scanner – Robust Version")

search = st.text_input("🔍 Gib ein Stichwort ein (Song oder Artist)", "nina chuba")

if search:
    token = get_valid_token()
    headers = {"Authorization": f"Bearer {token}"}

    st.markdown(f"Suche in Playlist-Daten für: **{search}**")

    # Beispiel: Eine bekannte Playlist zum Test
    playlist_id = "37i9dQZF1DX4jP4eebSWR9"
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    params = {"limit": 100}
    r = requests.get(url, headers=headers, params=params)

    if r.status_code == 200:
        data = r.json()
        found = []
        for item in data.get("items", []):
            track = item.get("track")
            if not track:
                continue
            name = track.get("name", "").lower()
            artists = [a.get("name", "").lower() for a in track.get("artists", [])]
            if search.lower() in name or any(search.lower() in a for a in artists):
                found.append(track)

        if found:
            st.success(f"Gefunden: {len(found)} Track(s)")
            for t in found:
                st.markdown(f"- [{t['name']}]({t['external_urls']['spotify']}) – {', '.join([a['name'] for a in t['artists']])}")
        else:
            st.warning("Kein Treffer gefunden.")
    else:
        st.error(f"Fehler: {r.status_code} – {r.text}")
