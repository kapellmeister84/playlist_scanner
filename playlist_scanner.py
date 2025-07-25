"""
playlist scanner
"""

import streamlit as st
import requests, json, time, hashlib
from datetime import datetime
import base64
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright
from fpdf import FPDF
from PIL import Image
from io import BytesIO
from collections import defaultdict
import os
import shutil
import subprocess

def ensure_playwright_installed():
    if not shutil.which("playwright"):
        st.error("Playwright ist nicht installiert.")
        return
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True)
    except Exception as e:
        st.error(f"Fehler bei playwright install: {e}")

ensure_playwright_installed()


# Accessing secrets (Notion token, Database ID, etc.)
NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
DATABASE_ID = st.secrets["DATABASE_ID"]
NOTION_VERSION = st.secrets["NOTION_VERSION"] if "NOTION_VERSION" in st.secrets else "2022-06-28"
CLIENT_ID = st.secrets["CLIENT_ID"]
CLIENT_SECRET = st.secrets["CLIENT_SECRET"]


# --- Token handling ---
TOKEN_FILE = "token.txt"
TOKEN_PATH = Path(TOKEN_FILE)

def load_token():
    if TOKEN_PATH.exists():
        return TOKEN_PATH.read_text().strip()
    return None

def save_token(token):
    TOKEN_PATH.write_text(token)

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
        st.info("⚠️ Token wurde geladen und wird zwischengespeichert in 'token.txt'")
    return token



st.set_page_config(page_title="playlist scanner", layout="wide", initial_sidebar_state="expanded")

from utils import load_css
load_css()

# --- Funktionen ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_data(email):
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json"
    }
    payload = {"filter": {"property": "Email", "title": {"equals": email}}}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    data = response.json()
    results = data.get("results", [])
    return results[0] if results else None

def check_user_login(email, password):
    user_page = get_user_data(email)
    if not user_page:
        return False
    rich_text = user_page.get("properties", {}).get("Password", {}).get("rich_text", [])
    stored_hash = rich_text[0].get("text", {}).get("content", "") if rich_text else ""
    return stored_hash == hash_password(password)

def load_css():
    # Beispiel: CSS aus einer lokalen Datei laden (anpassen, wie benötigt)
    css = """
    <style>
    .progress-bar-container {width: 100%; background-color: #e0e0e0; border-radius: 5px; margin-bottom: 10px;}
    .progress-bar-fill {height: 10px; background-color: #76c7c0; border-radius: 5px;}
    .playlist-promo {margin: 10px 0; font-size: 14px;}
    .custom-summary {font-size: 16px; margin-top: 20px;}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# CSS laden
load_css()

# On load: Check query parameters (new API style)
params = st.query_params
if params.get("logged_in") == ["1"] and params.get("user_email"):
    st.session_state.logged_in = True
    st.session_state.user_email = params.get("user_email")[0]
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- Sidebar: Login ---
st.sidebar.title("Login")
with st.sidebar.form("login_form"):
    email = st.text_input("Email", placeholder="user@example.com", value=st.session_state.get("user_email", ""))
    password = st.text_input("Password", type="password")
    remember = st.checkbox("Keep me logged in")
    login_submit = st.form_submit_button("Login")
if login_submit:
    if not email or "@" not in email or not password:
        st.sidebar.error("Please fill in all fields correctly.")
    else:
        if check_user_login(email, password):
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.sidebar.success("Logged in successfully!")
            if remember:
                st.query_params = {"logged_in": "1", "user_email": email}
        else:
            st.sidebar.error("Login failed. Check your details.")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.query_params = {}
    st.sidebar.info("Logged out.")

st.markdown(
    """
    <script>
      // Set autocomplete for password fields
      document.addEventListener('DOMContentLoaded', function(){
        var pwdInputs = document.querySelectorAll('input[type="password"]');
        for (var i = 0; i < pwdInputs.length; i++){
            pwdInputs[i].setAttribute('autocomplete', 'current-password');
        }
        const input = document.querySelector('input[type="text"]');
        const btn = document.querySelector('button[type="submit"]');
        if(input && btn) {
          input.addEventListener('keydown', function(e){
            if(e.key === 'Enter'){
              e.preventDefault();
              btn.click();
            }
          });
        }
      });
    </script>
    """, unsafe_allow_html=True
)

st.title("playlist scanner")
st.markdown("<h4 style='text-align: left;'>created by <a href='https://www.instagram.com/capelli.mp3/' target='_blank'>capelli.mp3</a></h4>", unsafe_allow_html=True)
st.markdown(
    """
    <script>
      document.addEventListener('DOMContentLoaded', function(){
        const input = document.querySelector('input[type="text"]');
        const btn = document.querySelector('button[type="submit"]');
        if(input && btn) {
          input.addEventListener('keydown', function(e){
            if(e.key === 'Enter'){
              e.preventDefault();
              btn.click();
            }
          });
        }
      });
    </script>
    """, unsafe_allow_html=True
)

# --- Scanner functionality ---
def format_number(n):
    return format(n, ",").replace(",", ".")

def get_spotify_token():
    return ensure_token()

@st.cache_data
def get_playlist_data(playlist_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    response = requests.get(url, headers=headers)
    return response.json()

@st.cache_data
def get_deezer_playlist_data(playlist_id):
    url = f"https://api.deezer.com/playlist/{playlist_id}"
    response = requests.get(url)
    return response.json()

@st.cache_data
def get_spotify_playcount(track_id, token):
    variables = json.dumps({"uri": f"spotify:track:{track_id}"})
    extensions = json.dumps({
        "persistedQuery": {
            "version": 1,
            "sha256Hash": "26cd58ab86ebba80196c41c3d48a4324c619e9a9d7df26ecca22417e0c50c6a4"
        }
    })
    params = {"operationName": "getTrack", "variables": variables, "extensions": extensions}
    response = requests.get("https://api-partner.spotify.com/pathfinder/v1/query",
                            headers={"Authorization": f"Bearer {SPOTIFY_HEADERS['Authorization'].split()[1]}"}, params=params)
    response.raise_for_status()
    return int(response.json()["data"]["trackUnion"].get("playcount", 0))

@st.cache_data
def get_track_additional_info(track_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    data = requests.get(url, headers=headers).json()
    playcount = get_spotify_playcount(track_id, token)
    release_date = data.get("album", {}).get("release_date", "N/A")
    images = data.get("album", {}).get("images", [])
    cover_url = images[0].get("url", "") if images else ""
    return {"playcount": playcount, "release_date": release_date, "cover_url": cover_url}

@st.cache_data
def find_tracks_by_artist(playlist_id, query, token):
    query = query.strip()
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    params = {"limit": 100}
    tracks_data = requests.get(url, headers=headers, params=params).json()
    matches = []
    for index, item in enumerate(tracks_data.get("items", []), start=1):
        track = item.get("track")
        if track and (query.lower() in track['name'].lower() or any(query.lower() in artist['name'].lower() for artist in track['artists'])):
            extra = get_track_additional_info(track.get("id"), token)
            track["streams"] = extra.get("playcount")
            track["release_date"] = extra.get("release_date")
            track["cover_url"] = extra.get("cover_url")
            matches.append({"track": track, "position": index})
    return matches

def normalize_deezer_track(track):
    normalized = {}
    normalized["name"] = track.get("title", "Unknown Title")
    artist_obj = track.get("artist", {})
    normalized["artists"] = [{
        "name": artist_obj.get("name", "Unknown Artist"),
        "id": str(artist_obj.get("id", ""))
    }]
    cover_url = track.get("album", {}).get("cover")
    normalized["album"] = {"images": [{"url": cover_url}]} if cover_url else {"images": []}
    # Add cover_url directly
    normalized["cover_url"] = cover_url
    normalized["streams"] = track.get("rank", 0)
    normalized["popularity"] = 0
    normalized["release_date"] = "N/A"
    normalized["platform"] = "Deezer"
    normalized["id"] = str(track.get("id"))
    # Fallback: try to get cover from Spotify if cover_url is empty
    if not normalized["cover_url"]:
        try:
            # versuche das Cover via Spotify zu holen
            search_query = f"{normalized['name']} {normalized['artists'][0]['name']}"
            headers = {"Authorization": f"Bearer {SPOTIFY_TOKEN}"}
            search_url = "https://api.spotify.com/v1/search"
            params = {"q": search_query, "type": "track", "limit": 1}
            r = requests.get(search_url, headers=headers, params=params)
            item = r.json().get("tracks", {}).get("items", [])[0]
            normalized["cover_url"] = item.get("album", {}).get("images", [{}])[0].get("url", "")
        except Exception:
            pass
    return normalized

@st.cache_data
def find_tracks_by_artist_deezer(playlist_id, query):
    url = f"https://api.deezer.com/playlist/{playlist_id}/tracks"
    params = {"limit": 100}
    data = requests.get(url, params=params).json()
    matches = []
    for index, track in enumerate(data.get("data", []), start=1):
        if track and 'artist' in track and (query.lower() in track.get("title", "").lower() or query.lower() in track['artist']['name'].lower()):
            normalized_track = normalize_deezer_track(track)
            matches.append({"track": normalized_track, "position": index})
    return matches

def generate_track_key(track):
    track_name = track.get("name", "").strip().lower()
    artists = sorted([artist.get("name", "").strip().lower() for artist in track.get("artists", [])])
    return f"{track_name} - {'/'.join(artists)}"


# --- PDF Generation Function ---
def generate_pdf_streamlit(results, query, token, show_download_button=True):
    import hashlib
    import re
    from urllib.request import urlopen
    def safe_text(text):
        # Remove HTML tags, especially <a ...>@diffusmagazin</a> etc.
        if not text:
            return ""
        # Remove all HTML tags
        text = re.sub(r"<[^>]+>", "", text)
        return text.encode("latin-1", "ignore").decode("latin-1")

    # --- PDF setup ---
    pdf = FPDF()
    pdf.set_auto_page_break(auto=False, margin=15)  # We'll manage page breaks
    SPOTIFY_GREEN = (29, 185, 84)
    BG_IMG_URL = "https://iili.io/3dchREl.jpg"

    # Download background image once
    try:
        response = urlopen(BG_IMG_URL)
        bg_img = Image.open(BytesIO(response.read())).convert("RGB")
        bg_img_path = "background_temp.jpg"
        bg_img.save(bg_img_path, quality=100)
    except Exception as e:
        print(f"Background image error: {e}")
        bg_img_path = None

    def add_page_with_bg():
        pdf.add_page()
        if bg_img_path:
            pdf.image(bg_img_path, x=0, y=0, w=210, h=297)

    # For each unique track, add a section with its own page(s)
    for key, data in results.items():
        track = data["track"]
        playlists = data["playlists"]

        add_page_with_bg()

        # Header: Track name by artist
        track_name = track.get("name", "Unbekannt")
        artist_names = ", ".join([a.get("name", "Unbekannt") for a in track.get("artists", [])])
        pdf.set_font("Arial", "B", 22)
        pdf.set_text_color(*SPOTIFY_GREEN)
        pdf.multi_cell(0, 15, safe_text(f"{track_name} by {artist_names}"), align="C")
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "", 14)
        pdf.cell(0, 10, safe_text(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y – %H:%M:%S')}"), ln=True, align="C")
        # Track-Metadaten
        pdf.set_font("Arial", "", 12)
        details = []
        if track.get("release_date"):
            details.append(f"Released: {track['release_date']}")
        if track.get("popularity") is not None:
            details.append(f"Popularity: {track['popularity']}")
        if track.get("streams") is not None:
            details.append(f"Streams: {format_number(track['streams'])}")
        if details:
            pdf.ln(5)
            pdf.multi_cell(0, 8, " | ".join(details), align="C")
        pdf.ln(10)

        # Cover image (centered)
        cover_url = track.get("cover_url")
        if cover_url:
            try:
                response = requests.get(cover_url)
                img = Image.open(BytesIO(response.content)).convert("RGB")
                img.thumbnail((200, 200), Image.LANCZOS)
                img_io = BytesIO()
                img.save(img_io, format="JPEG", quality=100)
                img_io.seek(0)
                img_path = f"tmp_cover_{hashlib.md5(cover_url.encode()).hexdigest()}.jpg"
                with open(img_path, "wb") as f:
                    f.write(img_io.read())
                pdf.ln(5)
                # Center the image horizontally, width 60mm
                pdf.image(img_path, x=(210-60)//2, y=pdf.get_y(), w=60)
                os.remove(img_path)
                pdf.ln(65)
            except Exception:
                pass
        else:
            pdf.ln(10)

        # Playlists summary for this track
        playlist_names = set()
        for plist in playlists:
            playlist_names.add(plist["name"])
        summary = f"Der Track wurde in {len(playlist_names)} Playlist(s) gefunden. Insgesamt {len(playlists)} Platzierungen."
        pdf.set_font("Arial", "", 13)
        pdf.set_text_color(255, 255, 255)
        pdf.multi_cell(0, 8, safe_text(summary))
        pdf.ln(5)

        # --- Playlists Section (for this track only) ---
        playlist_entries = []
        seen_playlists = set()
        for plist in playlists:
            pl_key = (plist.get("name", ""), plist.get("url", ""))
            if pl_key not in seen_playlists:
                playlist_entries.append(plist)
                seen_playlists.add(pl_key)

        ENTRIES_PER_PAGE = 3
        for idx, plist in enumerate(playlist_entries):
            # Add new page (with bg) every ENTRIES_PER_PAGE (except first page)
            if idx > 0 and idx % ENTRIES_PER_PAGE == 0:
                add_page_with_bg()
            # Section heading
            name = plist.get("name", "Unknown Playlist")
            owner = plist.get("owner", "N/A")
            followers = plist.get("followers", "N/A")
            position = plist.get("position", "-")
            url = plist.get("url", "")
            desc = plist.get("description", "")
            cover = plist.get("cover")

            pdf.set_fill_color(*SPOTIFY_GREEN)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", "B", 13)
            pdf.cell(0, 10, safe_text(f"Playlist: {name}"), ln=True, fill=True)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 8, safe_text(f"Kurator: {owner} – Follower: {followers} – Position: {position}"), ln=True)
            if desc:
                pdf.set_font("Arial", "", 11)
                pdf.multi_cell(0, 7, safe_text(desc))
            if url:
                pdf.set_text_color(29, 185, 84)
                pdf.cell(0, 8, safe_text(url), ln=True, link=url)
                pdf.set_text_color(255, 255, 255)

            # Playlist cover image
            if cover:
                try:
                    response = requests.get(cover)
                    img = Image.open(BytesIO(response.content)).convert("RGB")
                    img.thumbnail((200, 200), Image.LANCZOS)
                    img_io = BytesIO()
                    img.save(img_io, format="JPEG", quality=100)
                    img_io.seek(0)
                    img_path = f"tmp_{hashlib.md5(cover.encode()).hexdigest()}.jpg"
                    with open(img_path, "wb") as f:
                        f.write(img_io.read())
                    y = pdf.get_y()
                    pdf.image(img_path, x=170, y=y - 25, w=30)
                    os.remove(img_path)
                except Exception:
                    pass

            # Layout improvements: add spacing and section divider
            pdf.ln(6)
            pdf.set_draw_color(*SPOTIFY_GREEN)
            pdf.set_line_width(0.8)
            pdf.line(pdf.l_margin, pdf.get_y(), 210 - pdf.r_margin, pdf.get_y())
            pdf.ln(4)

    # Clean up temp bg image
    if bg_img_path and os.path.exists(bg_img_path):
        os.remove(bg_img_path)

    # --- PDF Output ---
    output_filename = f"playlist_scan_{query.replace(' ', '_')}.pdf"
    pdf.output(output_filename)
    # Only show download button if requested
    if show_download_button:
        with open(output_filename, "rb") as f:
            st.download_button(
                label="⬇️ PDF herunterladen",
                data=f,
                file_name=output_filename,
                mime="application/pdf",
                key=f"download_button_{output_filename}_{datetime.now().timestamp()}"
            )

PLAYLISTS_FILE = "playlists.json"

def load_playlists():
    try:
        with open(PLAYLISTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [(pid, "spotify") for pid in data.get("spotify", {})] + [(pid, "deezer") for pid in data.get("deezer", {})]
    except Exception as e:
        st.error(f"Fehler beim Laden der Playlisten: {e}")
        return []

all_playlists = load_playlists()

def update_progress_bar(current, total):
    percentage = int((current / total) * 100)
    progress_html = f"""
        <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: {percentage}%"></div>
        </div>
    """
    progress_placeholder.markdown(progress_html, unsafe_allow_html=True)

def show_playlist_promo():
    promo_html = (
        "<div class='playlist-promo'>🎧 While you wait, check out capelli on spotify: "
        "<a href='https://open.spotify.com/intl-de/artist/039VhVUEhmLgBiLkJog0Td' target='_blank'>Listen here</a></div>"
    )
    promo_placeholder.markdown(promo_html, unsafe_allow_html=True)

if st.session_state.logged_in:
    st.markdown('<div id="search_form">', unsafe_allow_html=True)
    with st.form("scanner_form"):
        search_term = st.text_input("enter artist or song:", value="").strip()
        submit = st.form_submit_button("🔍 scan playlists")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        """
        <script>
        document.getElementById("search_form").addEventListener("submit", function(e) {
            document.activeElement.blur();
        });
        </script>
        """, unsafe_allow_html=True
    )

    status_message = st.empty()
    progress_placeholder = st.empty()
    promo_placeholder = st.empty()

    # Get Spotify token and headers
    global SPOTIFY_TOKEN, SPOTIFY_HEADERS
    spotify_token = get_spotify_token()
    SPOTIFY_TOKEN = spotify_token
    SPOTIFY_HEADERS = {"Authorization": f"Bearer {spotify_token}"}

    import concurrent.futures

    # Only scan if submit is clicked and results are not in session_state
    if submit and "scan_results" not in st.session_state:
        results = {}
        total_listings = 0
        unique_playlists = set()
        total_playlists = len(all_playlists)

        def scan_playlist_wrapper(args):
            pid, platform, token, search_term = args
            if platform == "spotify":
                playlist = get_playlist_data(pid, token)
                if not playlist:
                    return None
                playlist_name = playlist.get("name", "Unknown Playlist")
                playlist_followers = playlist.get("followers", {}).get("total", "N/A")
                if isinstance(playlist_followers, int):
                    playlist_followers = format_number(playlist_followers)
                playlist_owner = playlist.get("owner", {}).get("display_name", "N/A")
                playlist_description = playlist.get("description", "")
                tracks = find_tracks_by_artist(pid, search_term, token)
                cover = playlist.get("images", [{}])[0].get("url")
                playlist_url = f"https://open.spotify.com/playlist/{pid}"
            else:
                playlist = get_deezer_playlist_data(pid)
                if not playlist:
                    return None
                playlist_name = playlist.get("title", "Unknown Playlist")
                playlist_followers = playlist.get("fans", "N/A")
                if isinstance(playlist_followers, int):
                    playlist_followers = format_number(playlist_followers)
                playlist_owner = playlist.get("user", {}).get("name", "N/A")
                playlist_description = playlist.get("description", "")
                tracks = find_tracks_by_artist_deezer(pid, search_term)
                cover = playlist.get("picture")
                playlist_url = f"https://www.deezer.com/playlist/{pid}"
            return {
                "platform": platform,
                "playlist_name": playlist_name,
                "playlist_owner": playlist_owner,
                "playlist_followers": playlist_followers,
                "playlist_description": playlist_description,
                "tracks": tracks,
                "cover": cover,
                "url": playlist_url
            }

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            tasks = [(pid, platform, spotify_token, search_term) for pid, platform in all_playlists]
            future_results = list(executor.map(scan_playlist_wrapper, tasks))

        for i, result in enumerate(future_results, start=1):
            if not result:
                update_progress_bar(i, len(all_playlists))
                continue
            playlist_name = result["playlist_name"]
            playlist_followers = result["playlist_followers"]
            playlist_owner = result["playlist_owner"]
            playlist_description = result["playlist_description"]
            tracks = result["tracks"]
            cover = result["cover"]
            playlist_url = result["url"]
            platform = result["platform"]

            for match in tracks:
                track = match['track']
                position = match['position']
                total_listings += 1
                unique_playlists.add(playlist_name)
                key = generate_track_key(track)
                if key not in results:
                    results[key] = {"track": track, "playlists": []}
                results[key]["playlists"].append({
                    "name": playlist_name,
                    "cover": cover,
                    "url": playlist_url,
                    "position": position,
                    "platform": platform,
                    "followers": playlist_followers,
                    "owner": playlist_owner,
                    "description": playlist_description
                })

            update_progress_bar(i, len(all_playlists))
            time.sleep(0.1)

        status_message.empty()
        progress_placeholder.empty()
        promo_placeholder.empty()

        # Save results to session state
        st.session_state.scan_results = {
            "results": results,
            "search_term": search_term,
            "spotify_token": spotify_token,
            "total_listings": total_listings,
            "unique_playlists": list(unique_playlists)
        }

        # Remove: Call PDF generation automatically if results exist
        # PDF generation will be done after rendering results

    # Display results and PDF only if scan_results exist in session_state
    if "scan_results" in st.session_state:
        data = st.session_state.scan_results
        results = data["results"]
        search_term = data["search_term"]
        spotify_token = data["spotify_token"]
        total_listings = data.get("total_listings", 0)
        unique_playlists = set(data.get("unique_playlists", []))
        if results:
            song_count = len(results)
            playlist_count = len(unique_playlists)
            artist_name = None
            for res in results.values():
                for artist in res.get("track", {}).get("artists", []):
                    if search_term.lower() in artist.get("name", "").lower():
                        artist_name = artist.get("name")
                        break
                if artist_name:
                    break
            if artist_name:
                summary_text = f"{artist_name} is placed in {playlist_count} playlists, with {song_count} distinct song(s). They have been listed a total of {total_listings} times."
            else:
                sample_song = list(results.values())[0]["track"]
                song_title = sample_song.get("name", "").strip()
                summary_text = f"{song_title} is placed in {playlist_count} playlists."
            st.markdown(f"<div class='custom-summary'>{summary_text}</div>", unsafe_allow_html=True)

            # Generate PDF after rendering results, no download button here
            generate_pdf_streamlit(results, search_term, spotify_token, show_download_button=False)
            # Set session_state flag to indicate PDF is ready
            st.session_state.pdf_ready = True

            for res in results.values():
                track = res["track"]
                track_name = track['name']
                clickable_artists = []
                for artist_obj in track['artists']:
                    a_name = artist_obj.get("name", "Unknown")
                    if track.get("platform", "spotify") == "Deezer" and artist_obj.get("id"):
                        clickable_artists.append(f"[{a_name}](https://www.deezer.com/artist/{artist_obj['id']})")
                    elif artist_obj.get("id"):
                        clickable_artists.append(f"[{a_name}](https://open.spotify.com/artist/{artist_obj['id']})")
                    else:
                        clickable_artists.append(a_name)
                artists_md = ", ".join(clickable_artists)
                album_release_date = track.get("release_date", "")
                album_cover = track.get("cover_url") or (track.get("album", {}).get("images", [{}])[0].get("url") if track.get("album", {}).get("images") else None)
                extra_info = ""
                if album_release_date:
                    extra_info += f"Released: {album_release_date}  \n"
                if track.get("popularity") is not None:
                    extra_info += f"Popularity: {track['popularity']}  \n"
                if track.get("streams") is not None:
                    extra_info += f"Streams: {format_number(track['streams'])}  \n"
                st.markdown(f"### 📀 {track_name} – {artists_md}")
                if extra_info:
                    st.markdown(extra_info)
                if album_cover:
                    song_url = ""
                    if track.get("id"):
                        if track.get("platform", "spotify") == "Deezer":
                            song_url = f"https://www.deezer.com/track/{track['id']}"
                        else:
                            song_url = f"https://open.spotify.com/track/{track['id']}"
                    if song_url:
                        st.markdown(f'<a href="{song_url}" target="_blank"><img src="{album_cover}" width="250" style="border-radius: 10px;"></a>', unsafe_allow_html=True)
                st.markdown("#### 📄 Playlists:")
                for plist in res["playlists"]:
                    position = plist.get("position", "-")
                    extra_playlist = f"Followers: {plist.get('followers', 'N/A')} | Owner: {plist.get('owner', 'N/A')}"
                    if plist.get("description"):
                        extra_playlist += f" | {plist.get('description')}"
                    playlist_html = f"""
                        <div style="margin-bottom: 20px;">
                            <a href="{plist['url']}" target="_blank" style="display: block; font-size: 16px; font-weight: bold; text-decoration: none; color: black; margin-bottom: 5px;">
                                {plist['name']}
                            </a>
                            <div style="display: flex; align-items: center;">
                                <a href="{plist['url']}" target="_blank">
                                    <div style="width: 80px; height: 80px; margin-right: 15px;">
                                      <img src="{plist['cover']}" alt="cover" style="width: 100%; height: 100%; object-fit: cover; border-radius: 10px;">
                                    </div>
                                </a>
                                <div>
                                    <span style="font-size: 14px; color: white;">Track #: <strong>{position}</strong> ({plist['platform'].capitalize()})</span><br>
                                    <span style="font-size: 12px; color: white;">{extra_playlist}</span>
                                </div>
                            </div>
                        </div>
                    """
                    st.markdown(playlist_html, unsafe_allow_html=True)
        else:
            st.warning(f"I'm sorry, {search_term} couldn't be found. 😔")
            st.session_state.pdf_ready = False



    # --- Sidebar PDF Download Button or Preparation Notice ---
    if "scan_results" in st.session_state:
        search_term = st.session_state.scan_results.get("search_term", "")
        if "pdf_ready" in st.session_state and st.session_state.pdf_ready:
            output_filename = f"playlist_scan_{search_term.replace(' ', '_')}.pdf"
            try:
                with open(output_filename, "rb") as f:
                    st.sidebar.download_button(
                        label="⬇️ PDF herunterladen",
                        data=f,
                        file_name=output_filename,
                        mime="application/pdf",
                        key="sidebar_pdf_download"
                    )
            except Exception:
                st.sidebar.markdown("⬇️ PDF wird vorbereitet...")
        else:
            st.sidebar.markdown("⬇️ PDF wird vorbereitet...")
