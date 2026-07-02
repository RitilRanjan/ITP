import streamlit as st
import streamlit.components.v1 as components

st.write("Test DOM structure")
st.markdown("Created formula 'f1' = '<span class=\"interactive-symbol\" id=\"testspan\">x</span> ∈ y'", unsafe_allow_html=True)

components.html("""
<script>
    let el = window.parent.document.getElementById('testspan');
    let parent = el.parentNode;
    console.log("Parent tag:", parent.tagName);
    console.log("Parent's parent tag:", parent.parentNode.tagName);
    console.log("Parent's parent class:", parent.parentNode.className);
    
    let mainBlock = window.parent.document.querySelector('.stMainBlockContainer');
    console.log("Main Block found:", !!mainBlock);
    if (mainBlock) {
        console.log("Main block tag:", mainBlock.tagName);
        console.log("Main block children count:", mainBlock.children.length);
        console.log("Main block offsetHeight:", mainBlock.offsetHeight);
        console.log("Main block getBoundingClientRect:", JSON.stringify(mainBlock.getBoundingClientRect()));
    }
</script>
""", height=0, width=0)
