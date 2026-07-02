import streamlit as st

st.markdown("""
<style>
.interactive-symbol { cursor: pointer; color: blue; }
.itp-popover {
    background: white;
    border: 1px solid black;
    padding: 10px;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)

with st.expander("Test Expander", expanded=True):
    st.markdown("Here is a <span class='interactive-symbol' id='testspan'>test</span> inside an expander.", unsafe_allow_html=True)
    st.markdown("<br>"*5, unsafe_allow_html=True)

st.components.v1.html("""
<script>
    let span = window.parent.document.getElementById('testspan');
    if (span) {
        let popover = window.parent.document.createElement('div');
        popover.className = 'itp-popover';
        popover.innerText = 'This is a popover that is very tall and might be clipped by the expander if overflow is hidden. Let us make it very tall: <br> 1 <br> 2 <br> 3 <br> 4 <br> 5 <br> 6';
        popover.innerHTML = popover.innerText;
        
        span.parentNode.insertBefore(popover, span.nextSibling);
        popover.style.position = 'absolute';
        popover.style.zIndex = '9999';
        
        let pHeight = 200;
        popover.style.top = (span.offsetTop - pHeight) + 'px';
        popover.style.left = span.offsetLeft + 'px';
    }
</script>
""", height=0)
