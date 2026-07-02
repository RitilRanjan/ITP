import streamlit as st
from st_keyup import st_keyup
import time

st_keyup("Test", key="test")

st.components.v1.html(
    """<script>
    setInterval(() => {
        const iframes = window.parent.document.querySelectorAll('iframe');
        let out = "";
        iframes.forEach((iframe, idx) => {
            try {
                const doc = iframe.contentWindow.document;
                const input = doc.querySelector('input');
                out += `Iframe ${idx}: input found: ${!!input} | `;
            } catch(e) {
                out += `Iframe ${idx}: Error ${e.message} | `;
            }
        });
        console.log(out);
        const div = window.parent.document.getElementById('iframe-debug');
        if(div) div.innerText = out;
    }, 2000);
    </script>""", height=0
)
st.markdown("<div id='iframe-debug'></div>", unsafe_allow_html=True)
