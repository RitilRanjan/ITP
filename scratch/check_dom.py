import streamlit as st
import streamlit.components.v1 as components

st.write("Checking DOM")

components.html("""
<script>
    let container = window.parent.document.querySelector('.stMainBlockContainer');
    console.log("Found container by class?", !!container);
</script>
""", height=0, width=0)
