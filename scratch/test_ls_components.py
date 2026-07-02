import streamlit as st
import streamlit.components.v1 as components
from streamlit_javascript import st_javascript
import json

def get_ls(key):
    return st_javascript(f"localStorage.getItem('{key}');")

def set_ls(key, value):
    val_str = json.dumps(value)
    # properly escape for JS
    val_str = val_str.replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"')
    
    js = f"<script>window.parent.localStorage.setItem('{key}', \"{val_str}\");</script>"
    components.html(js, height=0, width=0)

st.write("Fetching from local storage...")
val = get_ls("test_components_key")
st.write("Value:", val)

if st.button("Save"):
    set_ls("test_components_key", {"status": "success", "data": 123})
    st.write("Saved!")
