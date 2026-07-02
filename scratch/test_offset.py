import streamlit as st
import streamlit.components.v1 as components

st.write("Hello")
components.html("""
<script>
    let container = window.parent.document.querySelector('.stAppViewContainer');
    console.log("Container position:", window.parent.getComputedStyle(container).position);
</script>
""", height=0, width=0)
