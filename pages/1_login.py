# pages/login.py
import streamlit as st
import streamlit.components.v1 as components
import requests, json, hashlib
from datetime import datetime
from utils import load_css

st.set_page_config(page_title="Login", layout="wide", initial_sidebar_state="expanded")
load_css()

# Helper-Funktionen
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_data(email):
    NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
    DATABASE_ID = st.secrets["DATABASE_ID"]
    NOTION_VERSION = "2022-06-28"
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
    stored_hash = user_page.get("properties", {})\
        .get("Password", {})\
        .get("rich_text", [{}])[0]\
        .get("text", {})\
        .get("content", "")
    return stored_hash == hash_password(password)

# Initialisiere Login-Status
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Login-Verarbeitung über Query-Parameter
params = st.query_params
if "email" in params and "password" in params:
    email_param = params["email"][0]
    password_param = params["password"][0]
    if check_user_login(email_param, password_param):
         st.session_state.logged_in = True
         st.session_state.user_email = email_param
         st.set_query_params(logged_in="1", user_email=email_param)
         st.success("Logged in successfully!")
         # Redirect zur Haupt-App, sodass das Login-Fenster nicht mehr sichtbar ist
         st.markdown('<meta http-equiv="refresh" content="0; url=/playlist_scanner">', unsafe_allow_html=True)
    else:
         st.error("Login failed. Check your details.")

# Sidebar: Custom Login Form mit Autofill
if not st.session_state.logged_in:
    with st.sidebar:
        st.markdown("## Login")
        login_html = """
        <div style="max-width: 300px; margin: auto; font-family: sans-serif;">
          <form id="loginForm">
            <label for="email" style="color: white;">Email:</label><br>
            <input type="email" id="email" name="email" autocomplete="username" required 
                   style="width: 100%; padding: 8px; margin-bottom: 10px; color: white; background-color: transparent; border: 1px solid white;"><br>
            <label for="password" style="color: white;">Password:</label><br>
            <input type="password" id="password" name="password" autocomplete="current-password" required 
                   style="width: 100%; padding: 8px; margin-bottom: 10px; color: white; background-color: transparent; border: 1px solid white;"><br>
            <button type="submit" style="width: 100%; padding: 10px; background-color: #0E4723; color: white; border: none;">Login</button>
          </form>
        </div>
        <script>
          document.getElementById("loginForm").onsubmit = function(e) {
            e.preventDefault();
            var email = document.getElementById("email").value;
            var password = document.getElementById("password").value;
            // Weiterleitung zur Hauptseite mit Query-Parametern
            window.location.href = "/playlist_scanner?email=" + encodeURIComponent(email) + "&password=" + encodeURIComponent(password);
          }
        </script>
        """
        components.html(login_html, height=300)
else:
    with st.sidebar:
        st.markdown("### Logged in as " + st.session_state.user_email)
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.set_query_params()
            st.sidebar.info("Logged out.")

# Hauptbereich der Login-Seite (optional)
if st.session_state.logged_in:
    st.title("Welcome to playlist scanner")
    st.markdown("<h4 style='text-align: left;'>created by <a href='https://www.instagram.com/capelli.mp3/' target='_blank'>capelli.mp3</a></h4>", unsafe_allow_html=True)
    st.write("You are now logged in. Redirecting to the main app...")
