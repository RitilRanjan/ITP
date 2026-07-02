import streamlit as st

st.title("Enter Key Test")

st.write("Test 1: Standard Text Input (Does NOT click the button natively on Enter)")
col1, col2 = st.columns([3, 1])
with col1:
    val1 = st.text_input("Type here and press Enter")
with col2:
    if st.button("Submit 1"):
        st.success(f"Button 1 clicked! Value: {val1}")

st.write("---")

st.write("Test 2: Streamlit Form (DOES submit on Enter natively)")
with st.form("my_form"):
    col3, col4 = st.columns([3, 1])
    with col3:
        val2 = st.text_input("Type here and press Enter")
    with col4:
        sub = st.form_submit_button("Submit 2")
        if sub:
            st.success(f"Button 2 clicked! Value: {val2}")

st.write("---")

st.write("Test 3: Javascript Global Enter Listener")
st.components.v1.html(
    """
    <script>
    // Listen on the parent window for ANY Enter key press
    window.parent.document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const display = window.parent.document.getElementById('js-output');
            if (display) {
                display.innerText = "JAVASCRIPT DETECTED ENTER KEY PRESS! KeyCode: " + e.keyCode;
                display.style.color = "red";
                display.style.fontWeight = "bold";
            }
        }
    }, true);
    </script>
    """, height=0
)
st.markdown("<div id='js-output'>Javascript output will appear here...</div>", unsafe_allow_html=True)
