# pages/2_About.py
import streamlit as st
from utils import load_css

load_css()

st.title("About")
st.markdown("""
I am a music producer and I know the struggle: many artists spend the night from Thursday to release Friday manually searching every playlist to check if their new song got placed. This app makes that process much easier. If you have any suggestions or if you'd like additional playlists to be added, feel free to email me at t.schroth@echolux.de.
""")
