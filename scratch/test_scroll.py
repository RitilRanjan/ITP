import streamlit as st

st.components.v1.html("""
<script>
    let scrollingElement = window.parent.document.querySelector('.stAppViewContainer') || 
                           window.parent.document.querySelector('.main') ||
                           window.parent.document.body;
    
    console.log("Scrolling element:", scrollingElement);
</script>
""", height=0, width=0)
