import streamlit as st
import streamlit.components.v1 as components
import json

if "click_data" not in st.session_state:
    st.session_state.click_data = ""

st.write("Click this word: <span class='click-me' style='color:red;cursor:pointer'>HELLO</span>", unsafe_allow_html=True)

st.text_input("hidden_input", key="hidden_input")
if st.button("Hidden Trigger", key="hidden_trigger"):
    st.write("TRIGGERED! Received:", st.session_state.hidden_input)

components.html("""
<script>
    if (!window.parent.document.testListenerAttached) {
        window.parent.document.testListenerAttached = true;
        window.parent.document.addEventListener('click', function(e) {
            if (e.target.classList.contains('click-me')) {
                let input = window.parent.document.querySelector('input[aria-label="hidden_input"]');
                if (input) {
                    let nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                    nativeSetter.call(input, "DATA FROM CLICK " + Date.now());
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    
                    setTimeout(() => {
                        let btn = Array.from(window.parent.document.querySelectorAll('button')).find(b => b.innerText === 'Hidden Trigger');
                        if (btn) btn.click();
                    }, 50);
                }
            }
        });
    }
</script>
""", height=0, width=0)
