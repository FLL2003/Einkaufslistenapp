import streamlit as st
from firebase_admin import credentials, firestore, initialize_app

# Initialisierung (nur einmal ausführen)
if not st.session_state.get('initialized'):
    cred = credentials.Certificate("firebase-key.json")
    initialize_app(cred)
    st.session_state.initialized = True

db = firestore.client()
col = db.collection('einkaufsliste')

st.title("🛒 Einkauf")

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
