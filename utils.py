# utils.py
import streamlit as st
import streamlit.components.v1 as components


def load_css():
    spotify_green = "#1DB954"
    dark_green = "#0E4723"
    blue = "#104C8C"
    css = f"""
    <style>
        .stApp {{
            /* Hier kannst du eventuell dein Spotify-Grün als Fallback setzen, falls kein Wallpaper geladen wird */
            background-color: {spotify_green};
        }}
        a {{
            color: black !important;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .stTextInput > div > div > input {{
            background-color: rgba(255, 255, 255, 0.9);
            color: blue;
            caret-color: black !important;
        }}
        .stButton button, .stForm button {{
            background-color: {blue} !important;
            color: white !important;
            border: 1px solid white !important;
        }}
        .custom-summary {{
            background-color: {dark_green};
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            font-size: 18px;
            color: white !important;
            margin-top: 20px;
            font-weight: bold;
        }}
        .progress-bar-container {{
            width: 100%;
            height: 10px;
            background-color: white;
            border-radius: 50px;
            margin-top: 20px;
            overflow: hidden;
        }}
        .progress-bar-fill {{
            height: 100%;
            width: 0%;
            background-color: {dark_green};
            border-radius: 50px;
            transition: width 0.2s ease-in-out;
        }}
        .playlist-promo {{
            background-color: rgba(0, 0, 0, 0.8);
            padding: 10px;
            border-radius: 8px;
            text-align: center;
            font-size: 10px;
            margin-top: 15px;
            color: white !important;
        }}
        .playlist-promo a {{
            color: #FFD700 !important;
            font-size: 18px;
            font-weight: bold;
        }}
        h1, h2, h3, h4, h5, h6, p, div {{
            color: white !important;
        }}
    </style>
    <style>
      :root {{
         --h1-font-size: 2em;
      }}
      h1 {{
         font-size: var(--h1-font-size) !important;
      }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

    st.markdown("""
    <style>
        [data-testid="stSidebar"] .stButton button, [data-testid="stSidebar"] .stForm button {
            background-color: #333333 !important;
            color: white !important;
            border: 1px solid white !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
    """
    <style>
      .stTextInput > div > div > input::placeholder {
          color: #555555 !important;
      }
    </style>
    """,
    unsafe_allow_html=True
    )

    st.markdown(
    """
    <style>
      .stApp {
        background: url('https://iili.io/3dchREl.jpg') no-repeat center center fixed;
        background-size: cover;
      }
    </style>
    """,
    unsafe_allow_html=True
    )
