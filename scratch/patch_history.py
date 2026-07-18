import re

with open("app.py", "r") as f:
    app_code = f.read()

# 1. Remove unconditional command_history.append
app_code = app_code.replace("st.session_state.command_history.append(command)\n        \n        f = io.StringIO()", "f = io.StringIO()")

# 2. Add has_error check before rb_manager.record_command
target_record = """                    if cmd not in {"save", "save_h", "load", "load_h", "help", "guide", "clear", "rb_stat", "rb_empty", "rb_swap"}:
                        st.session_state.rb_manager.record_command(first_line, before_snapshot, old_env_ref, current_env, mission_entered, mission_resolved)"""

repl_record = """                    has_error = any(line.startswith("Error:") or line.startswith("Parser Error:") or line.startswith("Warning:") for line in f.getvalue().splitlines())
                    if not has_error and cmd not in {"save", "save_h", "load", "load_h", "help", "guide", "clear", "rb_stat", "rb_empty", "rb_swap"}:
                        st.session_state.rb_manager.record_command(first_line, before_snapshot, old_env_ref, current_env, mission_entered, mission_resolved)"""

app_code = app_code.replace(target_record, repl_record)

# 3. Remove st.session_state.command_history.pop() in InteractiveInputRequired
target_pop = """                    st.session_state.chat_history.pop()
                    st.session_state.command_history.pop()
                    st.rerun()"""

repl_pop = """                    st.session_state.chat_history.pop()
                    st.rerun()"""

app_code = app_code.replace(target_pop, repl_pop)

# 4. Conditionally append to command_history at the end
target_end = """        output = f.getvalue()
        if output:"""

repl_end = """        output = f.getvalue()
        
        has_error = any(line.startswith("Error:") or line.startswith("Parser Error:") or line.startswith("Warning:") or line.startswith("Unknown command") for line in output.splitlines())
        if not has_error:
            st.session_state.command_history.append(command)
            
        if output:"""

app_code = app_code.replace(target_end, repl_end)

with open("app.py", "w") as f:
    f.write(app_code)

print("Patched app.py")
