import streamlit as st
import streamlit.components.v1 as components
import json

# Setup JS receiver
from streamlit_javascript import st_javascript

if "itp_data" not in st.session_state:
    ls_str = st_javascript("localStorage.getItem('itp_data');")
    if ls_str == 0:
        st.write("Loading...")
        st.stop()
    elif ls_str is None:
        st.session_state.itp_data = {"count": 0}
    else:
        try:
            st.session_state.itp_data = json.loads(ls_str)
        except:
            st.session_state.itp_data = {"count": 0}

st.write("Data:", st.session_state.itp_data)

if st.button("Increment"):
    st.session_state.itp_data["count"] += 1
    st.session_state.needs_save = True
    st.rerun()

if st.session_state.get("needs_save", False):
    val_str = json.dumps(st.session_state.itp_data).replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"')
    js = f"<script>window.parent.localStorage.setItem('itp_data', \"{val_str}\");</script>"
    components.html(js, height=0, width=0)
    st.session_state.needs_save = False

