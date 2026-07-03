import streamlit as st
from streamlit_javascript import st_javascript

res = st_javascript("window.localStorage.getItem('itp_data');")
st.write("Result:", res)
