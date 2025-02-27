# utils.py
import streamlit as st
import streamlit.components.v1 as components


def load_css():
    spotify_green = "#1DB954"
    dark_green = "#0E4723"
    css = f"""
    <style>
        .stApp {{
            background-color: {spotify_green};
            color: white !important;
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
            color: black;
            caret-color: black !important;
        }}
        .stButton button, .stForm button {{
            background-color: {dark_green} !important;
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
      /* Verstecke den internen Sidebar-Toggle-Button */
      [data-testid="stSidebarNav"] {
          display: none;
      }
      /* Style für dein eigenes Hamburger-Icon */
      #custom-hamburger {
          position: fixed;
          top: 10px;
          left: 10px;
          z-index: 10000;
          cursor: pointer;
          font-size: 24px;
          background-color: rgba(0, 0, 0, 0.5);
          padding: 5px;
          border-radius: 5px;
          color: #FFF;
      }
    </style>
    """,
    unsafe_allow_html=True,
)
    components.html(
    """
    <div id="custom-hamburger">&#9776;</div>
    <script>
      // Toggle-Funktion: Simuliere einen Klick auf den versteckten Sidebar-Toggle
      document.getElementById("custom-hamburger").onclick = function() {
          // Hier kannst du anpassen, wie die Sidebar ein- oder ausgeblendet werden soll
          var sidebar = document.querySelector('[data-testid="stSidebar"]');
          if (sidebar.style.display === "none") {
              sidebar.style.display = "block";
          } else {
              sidebar.style.display = "none";
          }
      };
    </script>
    """,
    height=0,
)

