import streamlit as st
import json
import requests
import asyncio
import shutil
import subprocess
from playwright.async_api import async_playwright

def ensure_playwright_installed():
    if not shutil.which("playwright"):
        st.error("Playwright ist nicht installiert.")
        return
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True)
    except Exception as e:
        st.error(f"Fehler bei playwright install: {e}")

ensure_playwright_installed()

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
        st.warning(f"Spotify API Fehler ({r.status_code}) für Playlist ID {playlist_id}")
        st.text("Token geladen.")  # Token-Details für Debugging ausgeblendet
        st.text(f"Response: {r.text}")
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

from pathlib import Path

def load_token():
    token_path = Path(".secrets") / ".token.txt"
    token_path.parent.mkdir(parents=True, exist_ok=True)
    return token_path.read_text(encoding="utf-8").strip() if token_path.exists() else None

def save_token(token):
    token_path = Path(".secrets") / ".token.txt"
    token_path.write_text(token, encoding="utf-8")

def is_token_valid(token):
    url = "https://api.spotify.com/v1/playlists/37i9dQZF1DX4JAvHpjipBk"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        return requests.get(url, headers=headers).status_code == 200
    except:
        return False

async def get_new_token():
    token = None
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        async def handle_request(request):
            nonlocal token
            auth = request.headers.get("authorization")
            if auth and auth.startswith("Bearer "):
                token = auth.split(" ")[1]

        context.on("request", handle_request)
        page = await context.new_page()
        await page.goto("https://open.spotify.com/")
        st.warning("Bitte logge dich im Spotify-Fenster ein und kehre danach zurück.")
        while not token:
            await asyncio.sleep(1)
        await browser.close()

    if token:
        save_token(token)
        st.success("Spotify-Token erfolgreich gespeichert.")
        return token
    else:
        st.error("Kein Token gefunden.")
        return None

def ensure_token():
    token = load_token()
    if not token or not is_token_valid(token):
        token = asyncio.run(get_new_token())
        st.info("⚠️ Token wurde geladen und wird zwischengespeichert in '.secrets/.token.txt'")
    return token

st.set_page_config(page_title="Getrackte Playlists", layout="wide")
st.title("📋 Übersicht aller getrackten Playlists")
st.markdown("Diese Seite zeigt alle Playlists aus der `playlists.json`, geordnet nach Spotify und Deezer.")

token = ensure_token()
if not token:
    st.warning("Kein gültiger Spotify Token vorhanden – Zugriff wird nicht funktionieren.")
else:
    st.info("Spotify-Token wurde geladen, versuche Playlists zu laden...")

playlists = load_playlists()

col1, col2 = st.columns(2)

with col1:
    st.header("Spotify")
    for pid, name in playlists.get("spotify", {}).items():
        data = get_spotify_playlist_data(pid, token) if token else None
        if not data:
            st.write(f"{name} (ID: {pid}) – [Details nicht ladbar, evtl. Token ungültig oder API-Fehler]")
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
