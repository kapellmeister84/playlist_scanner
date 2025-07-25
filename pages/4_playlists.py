

import streamlit as st
import json
import requests

PLAYLISTS_FILE = "playlists.json"

def load_playlists():
    try:
        with open(PLAYLISTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Fehler beim Laden der Playlisten: {e}")
        return {"spotify": {}, "deezer": {}}

def get_spotify_playlist_data(playlist_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return None
    data = r.json()
    return {
        "name": data.get("name"),
        "owner": data.get("owner", {}).get("display_name", "Unbekannt"),
        "followers": data.get("followers", {}).get("total", 0),
        "image": data.get("images", [{}])[0].get("url", ""),
        "url": data.get("external_urls", {}).get("spotify", "")
    }

def get_deezer_playlist_data(playlist_id):
    url = f"https://api.deezer.com/playlist/{playlist_id}"
    r = requests.get(url)
    if r.status_code != 200:
        return None
    data = r.json()
    return {
        "name": data.get("title"),
        "owner": data.get("creator", {}).get("name", "Unbekannt"),
        "followers": data.get("fans", 0),
        "image": data.get("picture_medium"),
        "url": f"https://www.deezer.com/playlist/{playlist_id}"
    }

# Optional: Token-Ladefunktion (aus anderer Datei importieren, falls modular)
from pathlib import Path
def load_token():
    token_file = Path("token.txt")
    return token_file.read_text().strip() if token_file.exists() else None

# Page setup
st.set_page_config(page_title="Getrackte Playlists", layout="wide")
st.title("📋 Übersicht aller getrackten Playlists")
st.markdown("Diese Seite zeigt alle Playlists aus der `playlists.json`, geordnet nach Spotify und Deezer.")

token = load_token()
if not token:
    st.warning("Kein Spotify Token gefunden. Bitte im Hauptbereich einloggen, um Spotify-Daten zu laden.")

playlists = load_playlists()

col1, col2 = st.columns(2)

with col1:
    st.header("Spotify")
    for pid, name in playlists.get("spotify", {}).items():
        data = get_spotify_playlist_data(pid, token) if token else None
        if not data:
            st.write(f"{name} (ID: {pid}) – [Details nicht ladbar]")
            continue
        st.markdown(f"""
            <div style="margin-bottom: 20px; padding: 10px; border-radius: 10px; background-color: #1DB95410;">
                <a href="{data['url']}" target="_blank" style="text-decoration: none; color: white;">
                    <img src="{data['image']}" width="100" style="float: left; margin-right: 10px; border-radius: 5px;">
                    <strong>{data['name']}</strong><br>
                    <span>👤 {data['owner']} – 👥 {data['followers']:,} Follower</span>
                </a>
                <div style="clear: both;"></div>
            </div>
        """, unsafe_allow_html=True)

with col2:
    st.header("Deezer")
    for pid, name in playlists.get("deezer", {}).items():
        data = get_deezer_playlist_data(pid)
        if not data:
            st.write(f"{name} (ID: {pid}) – [Details nicht ladbar]")
            continue
        st.markdown(f"""
            <div style="margin-bottom: 20px; padding: 10px; border-radius: 10px; background-color: #ef546f10;">
                <a href="{data['url']}" target="_blank" style="text-decoration: none; color: white;">
                    <img src="{data['image']}" width="100" style="float: left; margin-right: 10px; border-radius: 5px;">
                    <strong>{data['name']}</strong><br>
                    <span>👤 {data['owner']} – 👥 {data['followers']:,} Follower</span>
                </a>
                <div style="clear: both;"></div>
            </div>
        """, unsafe_allow_html=True)
