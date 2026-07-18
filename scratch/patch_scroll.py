with open("app.py", "r") as f:
    code = f.read()

target = """            output_str = "<br>".join(formatted_output)
            st.session_state.chat_history.append(f"<div style='font-family: monospace; white-space: pre-wrap;'>{output_str}</div>")
            
        st.rerun()"""

repl = """            output_str = "<br>".join(formatted_output)
            st.session_state.chat_history.append(f"<div style='font-family: monospace; white-space: pre-wrap;'>{output_str}</div>")
            
        st.components.v1.html(
            \"\"\"<script>
            setTimeout(() => {
                const mainArea = window.parent.document.querySelector('.main') || window.parent.document.querySelector('section[data-testid="stMain"]');
                if (mainArea) {
                    mainArea.scrollTop = mainArea.scrollHeight;
                }
                const blockContainer = window.parent.document.querySelector('.block-container');
                if (blockContainer) {
                    blockContainer.scrollIntoView({ behavior: 'smooth', block: 'end' });
                }
            }, 100);
            </script>\"\"\",
            height=0, width=0
        )
        st.rerun()"""

code = code.replace(target, repl)

with open("app.py", "w") as f:
    f.write(code)

print("Patched app.py scroll")
