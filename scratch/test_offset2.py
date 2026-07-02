import streamlit as st
import streamlit.components.v1 as components

st.markdown("""
<style>
.interactive-symbol {
    cursor: pointer;
    padding: 0 2px;
    border-radius: 3px;
    color: red;
}
.itp-popover {
    z-index: 10000;
    background: #ffffff;
    border: 1px solid #d1d5db;
    padding: 6px;
    display: none;
    width: 100px;
}
</style>
""", unsafe_allow_html=True)

st.write("Scroll down!")
for i in range(20):
    st.write(f"Line {i}")

st.markdown("Created formula 'f1' = '<span class=\"interactive-symbol\" id=\"testspan\">x</span> ∈ y'", unsafe_allow_html=True)

for i in range(20):
    st.write(f"Line {i}")

components.html("""
<script>
    if (!window.parent.document.itpTestAttached3) {
        window.parent.document.itpTestAttached3 = true;
        window.parent.document.addEventListener('click', function(e) {
            if (e.target.classList.contains('interactive-symbol')) {
                let targetElement = e.target;
                
                let popover = window.parent.document.createElement('div');
                popover.className = 'itp-popover';
                popover.innerText = 'Test Popover';
                
                targetElement.parentNode.style.position = 'relative';
                targetElement.parentNode.appendChild(popover);
                
                popover.style.display = 'block';
                popover.style.position = 'absolute';
                
                let pHeight = popover.offsetHeight;
                popover.style.top = (targetElement.offsetTop - pHeight - 8) + 'px';
                popover.style.left = targetElement.offsetLeft + 'px';
            }
        });
    }
</script>
""", height=0, width=0)
