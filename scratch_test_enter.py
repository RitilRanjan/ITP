import streamlit as st
from st_keyup import st_keyup

st.write("Test keyup")

if "cnt" not in st.session_state:
    st.session_state.cnt = 0

val = st_keyup("Input", key=f"k_{st.session_state.cnt}")
btn = st.button("Run Command")

if btn:
    st.write(f"Button clicked! Val: {val}")
    st.session_state.cnt += 1
    st.rerun()

st.write(f"Val is {val}")

st.components.v1.html(
    """<script>
    setInterval(() => {
        const iframes = window.parent.document.querySelectorAll('iframe');
        iframes.forEach(iframe => {
            try {
                const input = iframe.contentWindow.document.querySelector('input');
                if (input && !input.dataset.enterListenerAdded) {
                    input.addEventListener('keydown', function(e) {
                        if (e.key === 'Enter') {
                            const btns = window.parent.document.querySelectorAll('button');
                            let found = null;
                            for(let i=0; i<btns.length; i++) {
                                if (btns[i].textContent && btns[i].textContent.toLowerCase().includes('run command')) {
                                    found = btns[i];
                                    break;
                                }
                            }
                            if (found) {
                                found.click();
                            }
                        }
                    });
                    input.dataset.enterListenerAdded = "true";
                }
            } catch(e) {}
        });
    }, 500);
    </script>""", height=0
)
