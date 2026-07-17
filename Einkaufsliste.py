import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

# --- 1. Firebase Initialisierung ---
if not firebase_admin._apps:
    key_dict = json.loads(st.secrets["FIREBASE_SERVICE_ACCOUNT"])
    cred = credentials.Certificate(key_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()
col = db.collection('einkaufsliste')

# --- 2. Benutzeroberfläche ---
st.title("🛒 Einkaufsliste")

# Namen aus der URL holen (Standard: "Familie")
query_params = st.query_params
user_name = query_params.get("name", ["Familie"])[0]

st.write(f"Hallo **{user_name}**, was fügst du heute hinzu?")

# --- 3. Formular zum Hinzufügen ---
with st.form("add_form", clear_on_submit=True):
    item = st.text_input("Neues Produkt:")
    # Wir nutzen hier direkt 'user_name' aus der URL, damit man es nicht eingeben muss
    submitted = st.form_submit_button("Hinzufügen")
    
    if submitted and item:
        col.add({"text": item, "by": user_name, "bought": False})
        st.success(f"{item} wurde hinzugefügt!")
        st.rerun()

st.divider()

# --- 4. Liste anzeigen & Löschen ---
items = col.where("bought", "==", False).stream()
to_delete = []

for doc in items:
    data = doc.to_dict()
    # Checkbox zum Auswählen der erledigten Dinge
    if st.checkbox(f"{data['text']} — von {data['by']}"):
        to_delete.append(doc.id)

if st.button("Gekaufte entfernen"):
    for doc_id in to_delete:
        col.document(doc_id).update({"bought": True})
    st.rerun()
