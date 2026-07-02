import streamlit as st
import streamlit.components.v1 as components

st.write("Value is:", st.session_state.get("hidden_input", "empty"))

st.text_input("hidden_input", key="hidden_input")

st.write("Click this word: <span class='click-me' style='color:red;cursor:pointer'>HELLO</span>", unsafe_allow_html=True)

components.html("""
<script>
    if (!window.parent.document.testListenerAttached) {
        window.parent.document.testListenerAttached = true;
        window.parent.document.addEventListener('click', function(e) {
            if (e.target.classList.contains('click-me')) {
                let input = window.parent.document.querySelector('input[aria-label="hidden_input"]');
                if (input) {
                    let nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                    nativeSetter.call(input, "DATA " + Date.now());
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new Event('blur', { bubbles: true }));
                }
            }
        });
    }
</script>
""", height=0, width=0)
