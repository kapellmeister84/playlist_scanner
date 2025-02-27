# pages/2_About.py
import streamlit as st
from utils import load_css
load_css()

st.title("About")
st.markdown("""
I’m a music producer, so I get it—every Thursday night turns into a hunt through playlists, hoping to spot your new release. This app takes that hassle away by automatically checking the most important Spotify and Deezer playlists, saving you the late-night scrolling. Got suggestions or missing playlists you’d like to see? Drop me a line at t.schroth@echolux.de—I’d love to hear from you!

**Disclaimer:** By signing up, you agree to the collection, storage, and processing of your data for the purpose of providing this service. The app owner is not liable for any damages, losses, or issues that may arise from using this application. Use it at your own discretion.
""")

# Social Media Icons einfügen
st.markdown("""
<div style="text-align: center; margin-top: 20px;">
  <a href="https://www.instagram.com/capelli.mp3/" target="_blank" title="Instagram">
    <img src="https://upload.wikimedia.org/wikipedia/commons/a/a5/Instagram_icon.png" alt="Instagram" style="width:40px; margin: 0 10px;">
  </a>
  <a href="https://www.tiktok.com/@capelli.mp3" target="_blank" title="TikTok">
    <img src="https://upload.wikimedia.org/wikipedia/en/thumb/a/a9/TikTok_logo.svg/1024px-TikTok_logo.svg.png" alt="TikTok" style="width:40px; margin: 0 10px;">
  </a>
  <a href="https://open.spotify.com/intl-de/artist/039VhVUEhmLgBiLkJog0Td" target="_blank" title="Spotify">
    <img src="https://upload.wikimedia.org/wikipedia/commons/1/19/Spotify_logo_without_text.svg" alt="Spotify" style="width:40px; margin: 0 10px;">
  </a>
</div>
""", unsafe_allow_html=True)
