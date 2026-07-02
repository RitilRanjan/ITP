import streamlit as st
import json

if "last_payload" not in st.session_state:
    st.session_state.last_payload = None

if "cmd" not in st.session_state:
    st.session_state.cmd = None

payload = st.text_input("Payload", key="my_payload")

if payload and payload != st.session_state.last_payload:
    st.session_state.last_payload = payload
    st.session_state.cmd = json.loads(payload).get("cmd")
    st.rerun()

st.write("Cmd:", st.session_state.cmd)

st.components.v1.html("""
<button id="btn">Click Me</button>
<script>
document.getElementById('btn').onclick = function() {
    let input = window.parent.document.querySelector('input[aria-label="Payload"]');
    if (input) {
        let nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
        nativeSetter.call(input, JSON.stringify({cmd: "Hello " + Math.random()}));
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        input.blur();
    } else {
        alert("Input not found!");
    }
}
</script>
""", height=200)
