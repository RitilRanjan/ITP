import streamlit as st
import streamlit.components.v1 as components

st.write("Testing save")
components.html("<script>try { window.localStorage.setItem('test', '1'); document.body.innerHTML='Saved local'; } catch(e) { try { window.parent.localStorage.setItem('test', '1'); document.body.innerHTML='Saved parent'; } catch(e2) { document.body.innerHTML='Failed: ' + e2.message; } }</script>", height=100)
