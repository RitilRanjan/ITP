import streamlit as st

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "interactive_cmd" not in st.session_state:
    st.session_state.interactive_cmd = None

st.write("Chat History:")
for msg in st.session_state.chat_history:
    st.write(msg)

payload = st.text_input("Payload")
if payload and payload != st.session_state.get("last_payload"):
    st.session_state.last_payload = payload
    st.session_state.interactive_cmd = payload
    st.rerun()

command = None
interactive_submit = False
if st.session_state.get("interactive_cmd"):
    command = st.session_state.interactive_cmd
    st.session_state.interactive_cmd = None
    interactive_submit = True

if command:
    st.session_state.chat_history.append(f"Exec: {command}")
    st.rerun()
