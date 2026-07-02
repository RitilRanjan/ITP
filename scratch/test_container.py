import streamlit as st
import streamlit.components.v1 as components

st.write("Scroll down!")
for i in range(20):
    st.write(f"Line {i}")

st.markdown("Created formula 'f1' = '<span class=\"interactive-symbol\" id=\"testspan\">x</span> ∈ y'", unsafe_allow_html=True)

for i in range(20):
    st.write(f"Line {i}")

components.html("""
<script>
    if (!window.parent.document.itpTestAttached4) {
        window.parent.document.itpTestAttached4 = true;
        window.parent.document.addEventListener('click', function(e) {
            if (e.target.classList.contains('interactive-symbol')) {
                let targetElement = e.target;
                
                let popover = window.parent.document.createElement('div');
                popover.innerText = 'Test Popover';
                popover.style.display = 'block';
                popover.style.position = 'absolute';
                popover.style.background = 'red';
                popover.style.padding = '10px';
                
                let container = window.parent.document.querySelector('.stMainBlockContainer') || window.parent.document.body;
                container.style.position = 'relative';
                container.appendChild(popover);
                
                let rect = targetElement.getBoundingClientRect();
                let containerRect = container.getBoundingClientRect();
                
                let pHeight = popover.offsetHeight;
                popover.style.top = (rect.top - containerRect.top + container.scrollTop - pHeight - 8) + 'px';
                popover.style.left = (rect.left - containerRect.left + container.scrollLeft) + 'px';
                console.log("Appended to container");
            }
        });
    }
</script>
""", height=0, width=0)
