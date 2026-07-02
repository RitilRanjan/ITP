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
    if (!window.parent.document.itpTestAttached5) {
        window.parent.document.itpTestAttached5 = true;
        window.parent.document.addEventListener('click', function(e) {
            if (e.target.classList.contains('interactive-symbol')) {
                let targetElement = e.target;
                
                let popover = window.parent.document.createElement('div');
                popover.className = 'itp-popover';
                popover.innerText = 'Test Popover';
                
                let container = window.parent.document.querySelector('.stMainBlockContainer');
                if (!container) container = window.parent.document.body;
                
                if (window.parent.getComputedStyle(container).position === 'static') {
                    container.style.position = 'relative';
                }
                container.appendChild(popover);
                
                popover.style.display = 'block';
                popover.style.position = 'absolute';
                
                let rect = targetElement.getBoundingClientRect();
                let cRect = container.getBoundingClientRect();
                let pHeight = popover.offsetHeight;
                popover.style.top = (rect.top - cRect.top + container.scrollTop - pHeight - 8) + 'px';
                popover.style.left = (rect.left - cRect.left + container.scrollLeft) + 'px';
            }
        });
    }
</script>
""", height=0, width=0)
