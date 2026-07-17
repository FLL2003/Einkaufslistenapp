import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json

# Firebase Initialisierung
if not firebase_admin._apps:
    # Hier laden wir den Key aus den Streamlit Secrets, die wir gerade konfiguriert haben
    key_dict = json.loads(st.secrets["FIREBASE_SERVICE_ACCOUNT"])
    cred = credentials.Certificate(key_dict)
    firebase_admin.initialize_app(cred)

db = firestore.client()
col = db.collection('einkaufsliste')

st.title("🛒 Einkauf")

# Hol den Namen aus der URL, falls vorhanden
query_params = st.query_params
user_name = query_params.get("name", ["Familie"])[0] # Standard ist "Familie"

# Nutze den Namen direkt bei der Eingabe
st.write(f"Hallo {user_name}, was fügst du hinzu?")

# Beim Speichern in Firebase:
if st.form_submit_button("Hinzufügen"):
    col.add({"text": item, "by": user_name, "bought": False})


# Hinzufügen
with st.form("add", clear_on_submit=True):
    item = st.text_input("", placeholder="Neues Item...")
    person = st.text_input("", placeholder="Wer braucht es?")
    if st.form_submit_button("Hinzufügen"):
        col.add({"text": item, "by": person, "bought": False})
        st.rerun()

# Liste
items = col.where("bought", "==", False).stream()
to_delete = []

st.divider()

for doc in items:
    data = doc.to_dict()
    # Jedes Item als Checkbox
    if st.checkbox(f"{data['text']}  — *{data['by']}*"):
        to_delete.append(doc.id)

# Löschen
if st.button("Gekaufte entfernen"):
    for doc_id in to_delete:
        col.document(doc_id).update({"bought": True})
    st.rerun()
