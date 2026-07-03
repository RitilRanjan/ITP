import streamlit as st
from st_keyup import st_keyup

st.write("Test st_keyup")

if "current_cmd" not in st.session_state:
    st.session_state.current_cmd = ""
if "keyup_key" not in st.session_state:
    st.session_state.keyup_key = 0

st.write(f"current_cmd state: '{st.session_state.current_cmd}'")

partial_command = st_keyup("Type something:", value=st.session_state.current_cmd, key=f"input_{st.session_state.keyup_key}")

if partial_command is not None:
    st.session_state.current_cmd = partial_command

st.write(f"partial: '{partial_command}'")

if st.button("Update to foo"):
    st.session_state.current_cmd = "foo"
    st.session_state.keyup_key += 1
    st.rerun()

st.write("Done")
