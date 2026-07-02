import re

with open("app.py", "r") as f:
    content = f.read()

# Replace the manual save/load section
target_start = "    # Render Active Action Container directly below the buttons"
target_end = "                                        except OSError:\n                                            pass\n                                        st.rerun()"

start_idx = content.find(target_start)
end_idx = content.find(target_end) + len(target_end)

if start_idx != -1 and end_idx != -1:
    old_section = content[start_idx:end_idx]
    new_section = """    # Render Active Action Container directly below the buttons
    if st.session_state.active_action:
        with st.container(border=True):
            if st.session_state.active_action in ["save_env", "save_hist"]:
                is_env = (st.session_state.active_action == "save_env")
                title = "Save Environment State" if is_env else "Save Command History"
                st.write(f"**{title}**")
                
                if is_env:
                    data_str = serialize_environment_state(st.session_state.env_chain[-1])
                    file_name = f"{st.session_state.active_program}_env.md"
                    mime = "text/markdown"
                else:
                    clean_history = [cmd[0] if isinstance(cmd, tuple) else cmd for cmd in st.session_state.command_history]
                    data_str = serialize_history(clean_history)
                    file_name = f"{st.session_state.active_program}_history.md"
                    mime = "text/markdown"
                    
                st.download_button(
                    label=f"Download {title}",
                    data=data_str,
                    file_name=file_name,
                    mime=mime,
                    use_container_width=True
                )
                if st.button("Close", use_container_width=True):
                    st.session_state.active_action = None
                    st.rerun()
                                
            elif st.session_state.active_action in ["load_env", "load_hist"]:
                is_env = (st.session_state.active_action == "load_env")
                title = "Load Environment State" if is_env else "Load Command History"
                st.write(f"**{title}**")
                
                uploaded_file = st.file_uploader(f"Upload {title} (.md)", type=["md"])
                if uploaded_file is not None:
                    file_content = uploaded_file.read().decode("utf-8")
                    if is_env:
                        new_env = deserialize_environment_state(file_content, get_default_env)
                        chain = []
                        curr = new_env
                        while curr is not None:
                            chain.append(curr)
                            curr = curr.parent
                        chain.reverse()
                        st.session_state.env_chain = chain
                    else:
                        st.session_state.command_history = deserialize_history(file_content)
                        
                    st.success(f"Successfully loaded {title}!")
                    
                if st.button("Close", use_container_width=True):
                    st.session_state.active_action = None
                    st.rerun()"""
    
    content = content.replace(old_section, new_section)
    
    with open("app.py", "w") as f:
        f.write(content)
else:
    print("Could not find the target section to replace.")
