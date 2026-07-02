import streamlit as st

st.components.v1.html("""
<script>
    let input = window.parent.document.querySelector('input[aria-label="itp_click_data"]');
    if (input) {
        let nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
        nativeSetter.call(input, JSON.stringify({
            cmd: "sb",
            symbol: "x",
            occ: "1",
            target: "f1",
            args: ["t1"],
            _nonce: Date.now()
        }));
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        input.blur();
    }
</script>
""", height=0, width=0)
