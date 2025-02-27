"""
playlist scanner
"""
import streamlit as st
import requests, json, time, hashlib
from datetime import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="playlist scanner", layout="wide", initial_sidebar_state="expanded")
from utils import load_css
load_css()

# Prüfe, ob der Benutzer eingeloggt ist – sonst verweise auf die Login-Seite
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("You are not logged in. Please log in via the [Login](./1_login) page.")
    st.stop()  # Stoppt die Ausführung der App, falls nicht eingeloggt

# --- Scanner-Funktionalität ---
st.title("playlist scanner")
st.markdown("<h4 style='text-align: left;'>created by <a href='https://www.instagram.com/capelli.mp3/' target='_blank'>capelli.mp3</a></h4>", unsafe_allow_html=True)

def format_number(n):
    return format(n, ",").replace(",", ".")

def get_spotify_token():
    response = requests.get("https://open.spotify.com/get_access_token?reason=transport&productType=web_player").json()
    return response["accessToken"]

def get_playlist_data(playlist_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    response = requests.get(url, headers=headers)
    return response.json()

def get_deezer_playlist_data(playlist_id):
    url = f"https://api.deezer.com/playlist/{playlist_id}"
    response = requests.get(url)
    return response.json()

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

def get_track_additional_info(track_id, token):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    data = requests.get(url, headers=headers).json()
    playcount = get_spotify_playcount(track_id, token)
    release_date = data.get("album", {}).get("release_date", "N/A")
    cover_url = data.get("album", {}).get("images", [{}])[0].get("url", "")
    return {"playcount": playcount, "release_date": release_date, "cover_url": cover_url}

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
    normalized["streams"] = track.get("rank", 0)
    normalized["popularity"] = 0
    normalized["release_date"] = "N/A"
    normalized["platform"] = "Deezer"
    normalized["id"] = str(track.get("id"))
    return normalized

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

# --- Hauptbereich: Scanner UI ---
with st.form("scanner_form"):
    search_term = st.text_input("Enter artist or song:", value="").strip()
    submit = st.form_submit_button("🔍 Scan playlists")

st.markdown(
    """
    <script>
    document.getElementById("scanner_form").addEventListener("submit", function(e) {
        document.activeElement.blur();
    });
    </script>
    """, unsafe_allow_html=True
)

if submit and search_term:
    status_message = st.empty()
    progress_placeholder = st.empty()
    promo_placeholder = st.empty()
    
    spotify_playlist_ids = [
        "6Di85VhG9vfyswWHBTEoQN", "37i9dQZF1DX4jP4eebSWR9", "37i9dQZF1DX59oR8I71XgB",
        "37i9dQZF1DXbKGrOUA30KN", "37i9dQZF1DWUW2bvSkjcJ6", "531gtG63RwBSjuxb7XDGPL",
        "37i9dQZF1DWSTqUqJcxFk6", "37i9dQZF1DX36edUJpD76c", "37i9dQZF1DWSFDWzEZlALC",
        "37i9dQZF1DWTBz12MDeCuX", "37i9dQZEVXbsQiwUKyCsTG", "37i9dQZF1DXcBWIGoYBM5M",
        "37i9dQZF1DX0XUsuxWHRQd", "37i9dQZF1DX4JAvHpjipBk", "37i9dQZF1DX7i0DhceX5x9",
        "37i9dQZF1DX2Nc3B70tvx0", "5RyrcmTrO52jOnaBkcY9dy", "6JMZfOAvKuNGcGAl6nQ4dt",
        "37i9dQZF1DX1zpUaiwr15A", "37i9dQZEVXbNv6cjoMVCyg", "6oiQozBfDMhbtciv64BDBA"
    ]
    deezer_playlist_ids = [
        "1111143121", "1043463931", "146820791", "1257540851",
        "8668716682", "4524622884", "65490170", "785141981"
    ]
    all_playlists = [(pid, "spotify") for pid in spotify_playlist_ids] + [(pid, "deezer") for pid in deezer_playlist_ids]
    
    # Global declaration for Spotify token/headers
    global SPOTIFY_TOKEN, SPOTIFY_HEADERS
    spotify_token = get_spotify_token()
    SPOTIFY_TOKEN = spotify_token
    SPOTIFY_HEADERS = {"Authorization": f"Bearer {spotify_token}"}
    
    results = {}
    total_listings = 0
    unique_playlists = set()
    total_playlists = len(all_playlists)
    
    for i, (pid, platform) in enumerate(all_playlists, start=1):
        if platform == "spotify":
            playlist = get_playlist_data(pid, spotify_token)
            if not playlist:
                continue
            playlist_name = playlist.get("name", "Unknown Playlist")
            playlist_followers = playlist.get("followers", {}).get("total", "N/A")
            if isinstance(playlist_followers, int):
                playlist_followers = format_number(playlist_followers)
            playlist_owner = playlist.get("owner", {}).get("display_name", "N/A")
            tracks = find_tracks_by_artist(pid, search_term, spotify_token)
            cover = playlist.get("images", [{}])[0].get("url")
            playlist_url = f"https://open.spotify.com/playlist/{pid}"
        else:
            playlist = get_deezer_playlist_data(pid)
            if not playlist:
                continue
            playlist_name = playlist.get("title", "Unknown Playlist")
            playlist_followers = playlist.get("fans", "N/A")
            if isinstance(playlist_followers, int):
                playlist_followers = format_number(playlist_followers)
            playlist_owner = playlist.get("user", {}).get("name", "N/A")
            tracks = find_tracks_by_artist_deezer(pid, search_term)
            cover = playlist.get("picture")
            playlist_url = f"https://www.deezer.com/playlist/{pid}"
        
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
                "owner": playlist_owner
            })
    
    # Anzeige der Ergebnisse
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
        
        # Anzeige der einzelnen Tracks und zugehörigen Playlists...
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
                st.markdown(f"<div style='margin-bottom: 20px;'><a href='{plist['url']}' target='_blank' style='font-size: 16px; font-weight: bold; text-decoration: none; color: black;'>{plist['name']}</a><br><span style='font-size: 12px; color: white;'>{extra_playlist}</span></div>", unsafe_allow_html=True)
    else:
        st.warning(f"I'm sorry, {search_term} couldn't be found. 😔")
