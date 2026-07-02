import streamlit as st
import streamlit.components.v1 as components

st.title("Test Input")
st.markdown("""
<style>
div[data-testid="stElementContainer"]:has(input[aria-label="test_input"]) {
    position: absolute !important;
    width: 0px !important;
    height: 0px !important;
    opacity: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}
</style>
""", unsafe_allow_html=True)
val = st.text_input("test_input", key="test_input")
st.write(f"Received: {val}")

components.html("""
<script>
setTimeout(() => {
    let input = window.parent.document.querySelector('input[aria-label="test_input"]');
    if (input) {
        input.focus();
        setTimeout(() => {
            let nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
            nativeSetter.call(input, "HELLO WORLD");
            input.dispatchEvent(new Event('input', { bubbles: true }));
            input.dispatchEvent(new Event('change', { bubbles: true }));
            setTimeout(() => {
                input.blur();
            }, 50);
        }, 50);
    }
}, 2000);
</script>
""", height=0, width=0)
