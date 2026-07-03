import streamlit as st
from streamlit_javascript import st_javascript

res = st_javascript("(function(){ try { var x = window.localStorage; return 'success'; } catch(e) { return 'caught'; } })();")
st.write("Result:", res)
