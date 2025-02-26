# pages/2_About.py
import streamlit as st
from utils import load_css

load_css()

st.title("About")
st.markdown("""
I’m a music producer, so I get it—every Thursday night turns into a hunt through playlists, hoping to spot your new release. This app takes that hassle away by automatically checking the most important Spotify and Deezer playlists, saving you the late-night scrolling. Got suggestions or missing playlists you’d like to see? Drop me a line at t.schroth@echolux.de—I’d love to hear from you!

**Disclaimer:** By signing up, you agree to the collection, storage, and processing of your data for the purpose of providing this service. The app owner is not liable for any damages, losses, or issues that may arise from using this application. Use it at your own discretion.
""")
