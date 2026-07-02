import streamlit as st
import streamlit.components.v1 as components

st.markdown("<span class='interactive-symbol' id='testspan'>x</span> ∈ y", unsafe_allow_html=True)

components.html("""
<script>
    let el = window.parent.document.getElementById('testspan');
    let container = el.closest('div');
    console.log("Container overflow:", window.parent.getComputedStyle(container).overflow);
    console.log("Container display:", window.parent.getComputedStyle(container).display);
</script>
""", height=0, width=0)
