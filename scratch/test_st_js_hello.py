import streamlit as st
from streamlit_javascript import st_javascript

res = st_javascript(" 'hello' ")
st.write("Result:", res)
