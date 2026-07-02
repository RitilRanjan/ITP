import streamlit as st
import time

st.write("Scroll down!")
for i in range(50):
    st.write(f"Line {i}")

st.components.v1.html("""
<script>
    let div = window.parent.document.createElement('div');
    div.innerText = "I should stick!";
    div.style.position = 'fixed';
    div.style.background = 'red';
    div.style.color = 'white';
    div.style.zIndex = '10000';
    div.style.top = '100px';
    div.style.left = '100px';
    window.parent.document.body.appendChild(div);

    let scrollTarget = window.parent.document.querySelector('[data-testid="stAppViewContainer"] .stMainBlockContainer') || 
                       window.parent.document.querySelector('[data-testid="stAppViewContainer"]') || 
                       window.parent;
    
    // Attempt to track scroll
    let startY = 100;
    scrollTarget.addEventListener('scroll', () => {
        // Not sticking to an element, just testing if scroll event fires
        console.log("Scrolling!");
    }, true);
    
    // Or we can just use an interval!
    // setInterval is very robust and doesn't rely on finding the exact scrolling container
</script>
""", height=0, width=0)

for i in range(50):
    st.write(f"More line {i}")
