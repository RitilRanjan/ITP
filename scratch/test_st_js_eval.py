import streamlit as st
from streamlit_javascript import st_javascript

res = st_javascript("(function() { return 'hello2'; })()")
st.write("Result:", res)
