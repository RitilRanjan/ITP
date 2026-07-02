import streamlit as st
import streamlit.components.v1 as components

components.html("""
<script>
    console.log("Component is running!");
</script>
""", height=0, width=0)
