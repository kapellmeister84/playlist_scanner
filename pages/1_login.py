# pages/login.py
import streamlit as st
import streamlit.components.v1 as components
import requests, json, hashlib
from datetime import datetime

# Seitenkonfiguration
st.set_page_config(page_title="Login", layout="wide", initial_sidebar_state="expanded")
from utils import load_css
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

# Initialisiere den Login-Status
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Login-Verarbeitung über Query-Parameter (falls über das HTML-Formular gesendet)
params = st.experimental_get_query_params()
if "email" in params and "password" in params:
    email_param = params["email"][0]
    password_param = params["password"][0]
    if check_user_login(email_param, password_param):
         st.session_state.logged_in = True
         st.session_state.user_email = email_param
         st.experimental_set_query_params(logged_in="1", user_email=email_param)
         st.success("Logged in successfully!")
    else:
         st.error("Login failed. Check your details.")

# Sidebar: Custom Login Form mit Autofill
if not st.session_state.logged_in:
    with st.sidebar:
        st.markdown("## Login")
        login_html = """
        <div style="max-width: 300px; margin: auto; font-family: sans-serif;">
          <form id="loginForm">
            <label for="email">Email:</label><br>
            <input type="email" id="email" name="email" autocomplete="username" required 
                   style="width: 100%; padding: 8px; margin-bottom: 10px;"><br>
            <label for="password">Password:</label><br>
            <input type="password" id="password" name="password" autocomplete="current-password" required 
                   style="width: 100%; padding: 8px; margin-bottom: 10px;"><br>
            <button type="submit" style="width: 100%; padding: 10px; background-color: #0E4723; color: white; border: none;">Login</button>
          </form>
        </div>
        <script>
          document.getElementById("loginForm").onsubmit = function(e) {
            e.preventDefault();
            var email = document.getElementById("email").value;
            var password = document.getElementById("password").value;
            // Sende die Daten per Query-Parameter, damit sie im Python-Code verarbeitet werden können
            window.location.href = "/login?email=" + encodeURIComponent(email) + "&password=" + encodeURIComponent(password);
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
            st.experimental_set_query_params()
            st.sidebar.info("Logged out.")

# Hauptbereich der Login-Seite (optional kannst du hier weitere Infos anzeigen)
if st.session_state.logged_in:
    st.title("Welcome to playlist scanner")
    st.markdown("<h4 style='text-align: left;'>created by <a href='https://www.instagram.com/capelli.mp3/' target='_blank'>capelli.mp3</a></h4>", unsafe_allow_html=True)
    st.write("You are now logged in. Use the app navigation to access different features.")
