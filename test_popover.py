import streamlit as st
import streamlit.components.v1 as components

st.write("Current CMD:", st.session_state.get("current_cmd", ""))

components.html("""
<script>
    console.log("Syntax is OK");
</script>
""", height=0, width=0)
