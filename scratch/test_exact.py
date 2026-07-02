import streamlit as st
import streamlit.components.v1 as components
import time

st.markdown("""
<style>
.interactive-symbol {
    cursor: pointer;
    padding: 0 2px;
    border-radius: 3px;
    color: red;
}
.itp-popover {
    position: fixed;
    z-index: 10000;
    background: #ffffff;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    padding: 6px;
    display: none;
    flex-wrap: wrap;
    gap: 6px;
    max-width: 300px;
}
</style>
""", unsafe_allow_html=True)

st.write("Scroll down!")
for i in range(20):
    st.write(f"Line {i}")

st.markdown("Created formula 'f1' = '<span class=\"interactive-symbol\">x</span> ∈ y'", unsafe_allow_html=True)

for i in range(20):
    st.write(f"Line {i}")


components.html("""
<script>
    if (!window.parent.document.itpTestAttached) {
        window.parent.document.itpTestAttached = true;
        window.parent.document.addEventListener('click', function(e) {
            if (e.target.classList.contains('interactive-symbol')) {
                let popover = window.parent.document.createElement('div');
                popover.className = 'itp-popover';
                popover.innerText = 'Test Popover';
                window.parent.document.body.appendChild(popover);
                popover.style.display = 'flex';
                
                let targetElement = e.target;
                
                let updatePosition = function() {
                    let rect = targetElement.getBoundingClientRect();
                    console.log("Rect:", rect.top, rect.left);
                    let pHeight = popover.offsetHeight;
                    popover.style.top = (rect.top - pHeight - 8) + 'px';
                    popover.style.left = rect.left + 'px';
                };
                updatePosition();
                setInterval(updatePosition, 16);
            }
        });
    }
</script>
""", height=0, width=0)
