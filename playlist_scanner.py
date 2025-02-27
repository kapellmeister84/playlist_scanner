"""
playlist scanner
"""
import streamlit as st
import requests, json, time, hashlib
from datetime import datetime
import streamlit.components.v1 as components

# Initialisiere den Registrierungs-Status, falls noch nicht vorhanden
if "registered" not in st.session_state:
    st.session_state.registered = False

st.set_page_config(page_title="playlist scanner", layout="wide", initial_sidebar_state="expanded")

from utils import load_css
load_css()

# --- Query-Parameter auswerten und Login verarbeiten ---
params = st.experimental_get_query_params()
if "logged_in" in params and params["logged_in"] == ["1"] and "user_email" in params:
    st.session_state.logged_in = True
    st.session_state.user_email = params["user_email"][0]
# Wenn die Login-Daten über das benutzerdefinierte Formular übergeben wurden:
elif "email" in params and "password" in params:
    email_param = params["email"][0]
    password_param = params["password"][0]
    if check_user_login(email_param, password_param):
         st.session_state.logged_in = True
         st.session_state.user_email = email_param
         # Setze Query-Parameter, damit der Login-Zustand erhalten bleibt
         st.experimental_set_query_params(logged_in="1", user_email=email_param)
    else:
         st.session_state.logged_in = False
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- Helper-Funktionen ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_data(email):
    url = f"https://api.notion.com/v1/databases/{st.secrets['DATABASE_ID']}/query"
    headers = {
        "Authorization": f"Bearer {st.secrets['NOTION_TOKEN']}",
        "Notion-Version": "2022-06-28",
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
    stored_hash = user_page.get("properties", {}).get("Password", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "")
    return stored_hash == hash_password(password)

def email_exists(email):
    return get_user_data(email) is not None

def add_user_to_notion(email, first_name, last_name, password_hash):
    if email_exists(email):
        st.error("This email is already registered.")
        return False
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {st.secrets['NOTION_TOKEN']}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    data = {
        "parent": {"database_id": st.secrets["DATABASE_ID"]},
        "properties": {
            "Email": {"title": [{"text": {"content": email}}]},
            "First Name": {"rich_text": [{"text": {"content": first_name}}]},
            "Last Name": {"rich_text": [{"text": {"content": last_name}}]},
            "Password": {"rich_text": [{"text": {"content": password_hash}}]},
            "Date created": {"date": {"start": datetime.utcnow().isoformat()}}
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.status_code == 200

# --- Registrierungsbereich ---
if not st.session_state.registered:
    st.title("Registration")
    with st.form("registration_form"):
        email = st.text_input("Email", placeholder="user@example.com")
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        password = st.text_input("Password", type="password")
        password_confirm = st.text_input("Confirm Password", type="password")
        reg_submit = st.form_submit_button("Register")
    
    if reg_submit:
        if not email or "@" not in email or not first_name or not last_name or not password:
            st.error("Please fill in all fields correctly.")
        elif password != password_confirm:
            st.error("Passwords do not match!")
        else:
            password_hash = hash_password(password)
            if add_user_to_notion(email, first_name, last_name, password_hash):
                st.success("Registration successful! You can now log in via the login bar.")
                st.session_state.registered = True
                # Neuladen der Seite, sodass der Login (in der Sidebar) sichtbar wird
                st.experimental_set_query_params()
                st.markdown('<meta http-equiv="refresh" content="0">', unsafe_allow_html=True)

# --- Sidebar: Custom Login Form mit Autofill ---
if not st.session_state.logged_in:
    with st.sidebar:
        st.markdown("## Login")
        login_html = """
        <div style="max-width: 300px; margin: auto; font-family: sans-serif;">
          <form id="loginForm">
            <label for="email">Email:</label><br>
            <input type="email" id="email" name="email" autocomplete="username" required style="width: 100%; padding: 8px; margin-bottom: 10px;"><br>
            <label for="password">Password:</label><br>
            <input type="password" id="password" name="password" autocomplete="current-password" required style="width: 100%; padding: 8px; margin-bottom: 10px;"><br>
            <button type="submit" style="width: 100%; padding: 10px; background-color: #0E4723; color: white; border: none;">Login</button>
          </form>
        </div>
        <script>
          document.getElementById("loginForm").onsubmit = function(e) {
            e.preventDefault();
            var email = document.getElementById("email").value;
            var password = document.getElementById("password").value;
            // Redirect mit Query-Parametern zur Login-Verarbeitung
            window.location.href = "/?email=" + encodeURIComponent(email) + "&password=" + encodeURIComponent(password);
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

# --- Restlicher Code (z. B. Scanner functionality) ---
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

st.title("playlist scanner")
st.markdown("<h4 style='text-align: left;'>created by <a href='https://www.instagram.com/capelli.mp3/' target='_blank'>capelli.mp3</a></h4>", unsafe_allow_html=True)

# Hier folgt der Rest deiner Scanner-Funktionalität...
def format_number(n):
    return format(n, ",").replace(",", ".")

# ... (alle weiteren Funktionen und der Code zur Verarbeitung der Playlists)
