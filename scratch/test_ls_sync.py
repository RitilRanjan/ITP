import streamlit as st
from streamlit_javascript import st_javascript
import json

if "itp_data" not in st.session_state:
    ls_str = st_javascript("localStorage.getItem('itp_data');")
    if ls_str == 0:
        st.write("Loading...")
        st.stop()
    elif ls_str is None:
        st.session_state.itp_data = {"count": 0}
    else:
        st.session_state.itp_data = json.loads(ls_str)

st.write("Data:", st.session_state.itp_data)

if st.button("Increment"):
    st.session_state.itp_data["count"] += 1
    # Save back to LS
    val_str = json.dumps(st.session_state.itp_data)
    js = f"localStorage.setItem('itp_data', '{val_str}');"
    st_javascript(js)
    st.rerun()

