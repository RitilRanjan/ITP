import streamlit as st
import streamlit.components.v1 as components

st.write("Test interval")
for i in range(20):
    st.write(f"Line {i}")

st.markdown("<span class='interactive-symbol' id='testspan'>x</span> ∈ y", unsafe_allow_html=True)

for i in range(20):
    st.write(f"Line {i}")

components.html("""
<script>
    if (!window.parent.document.itpTestAttached2) {
        window.parent.document.itpTestAttached2 = true;
        let popover = window.parent.document.createElement('div');
        popover.innerText = 'Test Interval';
        popover.style.position = 'fixed';
        popover.style.background = 'red';
        popover.style.padding = '10px';
        window.parent.document.body.appendChild(popover);
        
        let target = window.parent.document.getElementById('testspan');
        
        setInterval(() => {
            if (target) {
                let rect = target.getBoundingClientRect();
                popover.style.top = (rect.top - 40) + 'px';
                popover.style.left = rect.left + 'px';
            }
        }, 16);
    }
</script>
""", height=0, width=0)
