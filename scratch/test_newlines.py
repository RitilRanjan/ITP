import streamlit as st
from streamlit_javascript import st_javascript

res = st_javascript("(function() {\nreturn 'hello3';\n})();")
st.write("Result:", res)
