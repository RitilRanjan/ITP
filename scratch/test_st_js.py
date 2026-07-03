import streamlit as st
from streamlit_javascript import st_javascript

st.write("Testing st_javascript")
ls_code = """
(function() {
    try {
        return window.localStorage.getItem('itp_data') || 'null';
    } catch (e) {
        return 'null';
    }
})();
"""
res = st_javascript(ls_code)
st.write("Result:", res)
