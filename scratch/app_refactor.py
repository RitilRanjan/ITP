import re

with open("app.py", "r") as f:
    content = f.read()

# Replace file references in app.py
content = re.sub(
    r'from StorageManager import save_environment_state, load_environment_state, save_history, load_history',
    r'from StorageManager import serialize_environment_state, deserialize_environment_state, serialize_history, deserialize_history\nfrom streamlit_javascript import st_javascript\nimport streamlit.components.v1 as components',
    content
)

# Replace init_session
init_session_old = """def init_session():
    if "active_program" not in st.session_state:
        st.session_state.active_program = None
    if "env_chain" not in st.session_state:
        st.session_state.env_chain = [get_default_env()]
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "command_history" not in st.session_state:
        st.session_state.command_history = []
    if "active_action" not in st.session_state:
        st.session_state.active_action = None
    if "selected_file" not in st.session_state:
        st.session_state.selected_file = None
    if "skip_load_env_confirm" not in st.session_state:
        st.session_state.skip_load_env_confirm = False
    if "skip_load_hist_confirm" not in st.session_state:
        st.session_state.skip_load_hist_confirm = False
    if "games_progress" not in st.session_state:
        if os.path.exists("games_progress.json"):
            with open("games_progress.json", "r") as f:
                st.session_state.games_progress = json.load(f)
        else:
            st.session_state.games_progress = {}
    if "active_game_state" not in st.session_state:
        st.session_state.active_game_state = {
            "is_playing": False,
            "game_name": None,
            "level": None,
            "goal_ast_str": None,
            "completed": False
        }"""

init_session_new = """def init_session():
    if "itp_data" not in st.session_state:
        ls_str = st_javascript("localStorage.getItem('itp_data');")
        if ls_str == 0:
            st.write("Loading from Local Storage...")
            st.stop()
        elif ls_str is None:
            st.session_state.itp_data = {"programs": {}, "games_progress": {}}
        else:
            try:
                st.session_state.itp_data = json.loads(ls_str)
            except:
                st.session_state.itp_data = {"programs": {}, "games_progress": {}}
    
    if "needs_save" not in st.session_state:
        st.session_state.needs_save = False
        
    if "active_program" not in st.session_state:
        st.session_state.active_program = None
    if "env_chain" not in st.session_state:
        st.session_state.env_chain = [get_default_env()]
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "command_history" not in st.session_state:
        st.session_state.command_history = []
    if "active_action" not in st.session_state:
        st.session_state.active_action = None
    if "selected_file" not in st.session_state:
        st.session_state.selected_file = None
    if "skip_load_env_confirm" not in st.session_state:
        st.session_state.skip_load_env_confirm = False
    if "skip_load_hist_confirm" not in st.session_state:
        st.session_state.skip_load_hist_confirm = False
    if "games_progress" not in st.session_state:
        st.session_state.games_progress = st.session_state.itp_data.get("games_progress", {})
    if "active_game_state" not in st.session_state:
        st.session_state.active_game_state = {
            "is_playing": False,
            "game_name": None,
            "level": None,
            "goal_ast_str": None,
            "completed": False
        }
    if "proofs_html" not in st.session_state:
        st.session_state.proofs_html = "# Foundational Proof Log\\n**Format**: `premise1: def, ... ⊢ conclusion: def  (justification)`\\n\\n---\\n"
"""
content = content.replace(init_session_old, init_session_new)

# Replace save_program / load_program
prog_management_old = """# --- PROGRAM MANAGEMENT ---
PROGRAMS_DIR = "saved_programs"
os.makedirs(PROGRAMS_DIR, exist_ok=True)

def get_program_dir(name: str) -> str:
    return os.path.join(PROGRAMS_DIR, name)

def save_program(name: str):
    p_dir = get_program_dir(name)
    os.makedirs(p_dir, exist_ok=True)
    
    if st.session_state.env_chain:
        save_environment_state(st.session_state.env_chain[-1], os.path.join(p_dir, f"{name}.env_state"))
        
    with open(os.path.join(p_dir, "chat.json"), "w") as f:
        json.dump(st.session_state.chat_history, f)
    with open(os.path.join(p_dir, "cmd.json"), "w") as f:
        json.dump(st.session_state.command_history, f)
        
    st.success(f"Program '{name}' saved successfully!")

def load_program(name: str):
    p_dir = get_program_dir(name)
    env_path = os.path.join(p_dir, f"{name}.env_state")
    if os.path.exists(env_path):
        top_env = load_environment_state(env_path)
        chain = []
        curr = top_env
        while curr is not None:
            chain.append(curr)
            curr = curr.parent
        chain.reverse()
        st.session_state.env_chain = chain
    else:
        st.session_state.env_chain = [get_default_env()]
        
    chat_path = os.path.join(p_dir, "chat.json")
    if os.path.exists(chat_path):
        with open(chat_path, "r") as f:
            st.session_state.chat_history = json.load(f)
    else:
        st.session_state.chat_history = []
        
    cmd_path = os.path.join(p_dir, "cmd.json")
    if os.path.exists(cmd_path):
        with open(cmd_path, "r") as f:
            st.session_state.command_history = json.load(f)
    else:
        st.session_state.command_history = []
        
    st.session_state.active_program = name
    proof_logger.open(os.path.join(p_dir, "proofs.html"))"""

prog_management_new = """# --- PROGRAM MANAGEMENT ---
def save_program(name: str):
    env_state = ""
    if st.session_state.env_chain:
        env_state = serialize_environment_state(st.session_state.env_chain[-1])
        
    if "programs" not in st.session_state.itp_data:
        st.session_state.itp_data["programs"] = {}
        
    st.session_state.itp_data["programs"][name] = {
        "env_state": env_state,
        "chat_history": st.session_state.chat_history,
        "command_history": st.session_state.command_history,
        "proofs_html": st.session_state.get("proofs_html", "")
    }
    st.session_state.needs_save = True
    st.success(f"Program '{name}' saved successfully!")

def load_program(name: str):
    prog_data = st.session_state.itp_data.get("programs", {}).get(name)
    if prog_data:
        if prog_data.get("env_state"):
            top_env = deserialize_environment_state(prog_data["env_state"], get_default_env)
            chain = []
            curr = top_env
            while curr is not None:
                chain.append(curr)
                curr = curr.parent
            chain.reverse()
            st.session_state.env_chain = chain
        else:
            st.session_state.env_chain = [get_default_env()]
            
        st.session_state.chat_history = prog_data.get("chat_history", [])
        st.session_state.command_history = prog_data.get("command_history", [])
        st.session_state.proofs_html = prog_data.get("proofs_html", "")
        
        st.session_state.active_program = name
        proof_logger.open()"""

content = content.replace(prog_management_old, prog_management_new)

# Replace games_progress saving
content = re.sub(
    r'st\.session_state\.games_progress\[level_id\] = True\n\s+with open\("games_progress\.json", "w"\) as f_prog:\n\s+json\.dump\(st\.session_state\.games_progress, f_prog\)',
    r'st.session_state.games_progress[level_id] = True\n                                st.session_state.itp_data["games_progress"] = st.session_state.games_progress\n                                st.session_state.needs_save = True',
    content
)

# Remove os.listdir(PROGRAMS_DIR) and replace with dict keys
content = re.sub(
    r'programs = \[d for d in os\.listdir\(PROGRAMS_DIR\) if os\.path\.isdir\(os\.path\.join\(PROGRAMS_DIR, d\)\)\]',
    r'programs = list(st.session_state.itp_data.get("programs", {}).keys())',
    content
)

# Update "Create New Program" block
create_old = """                    st.session_state.active_program = new_prog_name
                    st.session_state.env_chain = [get_default_env()]
                    st.session_state.chat_history = []
                    st.session_state.command_history = []
                    
                    p_dir = get_program_dir(new_prog_name)
                    os.makedirs(p_dir, exist_ok=True)
                    proof_logger.open(os.path.join(p_dir, "proofs.html"))
                    save_program(new_prog_name)"""
create_new = """                    st.session_state.active_program = new_prog_name
                    st.session_state.env_chain = [get_default_env()]
                    st.session_state.chat_history = []
                    st.session_state.command_history = []
                    st.session_state.proofs_html = "# Foundational Proof Log\\n**Format**: `premise1: def, ... ⊢ conclusion: def  (justification)`\\n\\n---\\n"
                    
                    proof_logger.open()
                    save_program(new_prog_name)"""
content = content.replace(create_old, create_new)

# Append needs_save handling at the very end
ls_sync_code = """
if st.session_state.get("needs_save", False):
    val_str = json.dumps(st.session_state.itp_data).replace('\\\\', '\\\\\\\\').replace("'", "\\\\'").replace('"', '\\\\"')
    js = f"<script>window.parent.localStorage.setItem('itp_data', \\"{val_str}\\");</script>"
    components.html(js, height=0, width=0)
    st.session_state.needs_save = False
"""
content += ls_sync_code

with open("app.py", "w") as f:
    f.write(content)
