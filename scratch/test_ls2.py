import streamlit as st
import extra_streamlit_components as stx

@st.cache_resource
def get_manager():
    return stx.LocalStorageManager()

local_storage = get_manager()

st.write("Fetching from local storage...")
val = local_storage.get("itp_data")
st.write("Value:", val)

if st.button("Save"):
    local_storage.set("itp_data", {"hello": "world"})
