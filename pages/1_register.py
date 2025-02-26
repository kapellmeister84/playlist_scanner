# pages/3_register.py
import streamlit as st
import hashlib, requests, json
from datetime import datetime

NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
DATABASE_ID = st.secrets["DATABASE_ID"]
NOTION_VERSION = "2022-06-28"

st.set_page_config(page_title="Registrierung", layout="wide")
st.title("Registrierung")

from utils import load_css

load_css()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def email_exists(email):
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json"
    }
    payload = {"filter": {"property": "Email", "title": {"equals": email}}}
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    data = response.json()
    return len(data.get("results", [])) > 0

def add_user_to_notion(email, first_name, last_name, password_hash):
    if email_exists(email):
        st.error("Diese E-Mail ist bereits registriert.")
        return False
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json"
    }
    data = {
        "parent": {"database_id": DATABASE_ID},
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

with st.form("registration_form"):
    st.subheader("Neues Konto erstellen")
    email = st.text_input("E-Mail", placeholder="user@example.com")
    first_name = st.text_input("Vorname")
    last_name = st.text_input("Nachname")
    password = st.text_input("Passwort", type="password")
    password_confirm = st.text_input("Passwort bestätigen", type="password")
    reg_submit = st.form_submit_button("Registrieren")
    
if reg_submit:
    if not email or "@" not in email or not first_name or not last_name or not password:
        st.error("Bitte alle Felder korrekt ausfüllen.")
    elif password != password_confirm:
        st.error("Passwörter stimmen nicht überein!")
    else:
        password_hash = hash_password(password)
        if add_user_to_notion(email, first_name, last_name, password_hash):
            st.success("Registrierung erfolgreich! Du kannst dich jetzt über die Login-Leiste anmelden.")
