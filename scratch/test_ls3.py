import streamlit as st
from streamlit_local_storage import LocalStorage

local_storage = LocalStorage()

if local_storage.getItem("test_key"):
    st.write("Value from LS:", local_storage.getItem("test_key"))
else:
    st.write("Value not found")

if st.button("Save"):
    local_storage.setItem("test_key", "hello world")
    st.write("Saved!")
