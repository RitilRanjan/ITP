import streamlit as st
from streamlit_javascript import st_javascript

st.write("Testing localStorage")
val = st_javascript("localStorage.getItem('test_key');")
st.write("Value from LS:", val)

if st.button("Set Value"):
    st_javascript("localStorage.setItem('test_key', 'hello world');")
    st.write("Value set!")
