import streamlit as st
import json

st.markdown("""
<style>
/* Hide the hidden input container */
div[data-testid="stTextInput"]:has(input[aria-label="hidden_clicked_data"]) { display: none; }
</style>
""", unsafe_allow_html=True)

clicked_data = st.text_input("hidden_clicked_data", key="hidden_clicked_data", label_visibility="hidden")

if clicked_data:
    st.write(f"Received click data: {clicked_data}")
    # Reset it
    st.session_state.hidden_clicked_data = ""

st.markdown('<span class="interactive-symbol" data-target="f1" data-symbol="∀" data-occ="1" data-cmds="intro,fold" style="cursor: pointer; color: blue;">Click me! (∀)</span>', unsafe_allow_html=True)

st.components.v1.html("""
<script>
window.parent.document.addEventListener('click', function(e) {
    if (e.target.classList.contains('interactive-symbol')) {
        const data = {
            target: e.target.getAttribute('data-target'),
            symbol: e.target.getAttribute('data-symbol'),
            occ: e.target.getAttribute('data-occ'),
            cmds: e.target.getAttribute('data-cmds').split(',')
        };
        const hiddenInput = window.parent.document.querySelector('input[aria-label="hidden_clicked_data"]');
        if (hiddenInput) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype, "value").set;
            nativeInputValueSetter.call(hiddenInput, JSON.stringify(data));
            hiddenInput.dispatchEvent(new Event('input', { bubbles: true }));
            
            // To trigger Streamlit to submit, we send an Enter keydown
            hiddenInput.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', keyCode: 13, bubbles: true }));
        }
    }
});
</script>
""", height=0)
