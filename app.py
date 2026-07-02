import streamlit as st
import io
import contextlib
import re
import os
import json
import zipfile

@st.cache_data
def get_desktop_zip():
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for root, dirs, files in os.walk("."):
            if ".git" in root or "__pycache__" in root or ".gemini" in root or ".venv" in root or "scratch" in root:
                continue
            for file in files:
                if file.endswith(".py") or file.endswith(".txt") or file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    zip_file.write(file_path, os.path.relpath(file_path, "."))
    return zip_buffer.getvalue()

# Set page config for wider layout
st.set_page_config(page_title="Interactive Theorem Prover", layout="wide")

from Environment import Environment
from CommandHandlers.CommandRegistry import registry
from Frontend import reconstruct_string
from AST import Variable, PropositionalVariable, DummyVariable, Function, Relation
from main import get_default_env
from ProofLogger import proof_logger
from StorageManager import serialize_environment_state, deserialize_environment_state, serialize_history, deserialize_history
from streamlit_javascript import st_javascript
import streamlit.components.v1 as components
from Autocomplete import autocomplete_engine

try:
    from st_keyup import st_keyup
except ImportError:
    st_keyup = None

# Import all handlers to register them
import CommandHandlers.env_handlers
import CommandHandlers.logic_handlers
import CommandHandlers.mission_handlers
import CommandHandlers.state_handlers
import CommandHandlers.transformation_handlers
import CommandHandlers.definition_handlers

# Patch get_user_input to prevent hanging in Streamlit
import CommandHandlers.utils
def mock_get_user_input(prompt: str, command_queue: list = None, inputs_collected: list = None) -> str:
    if command_queue:
        ans = command_queue.pop(0)
        if inputs_collected is not None:
            inputs_collected.append(ans)
        return ans
    raise NotImplementedError("Interactive prompts (e.g., for saving, loading, or variable disambiguation) are not supported in the web UI.")
CommandHandlers.utils.get_user_input = mock_get_user_input

# --- UTILS ---
def ansi_to_html(text: str) -> str:
    html = text.replace('\n', '<br>')
    ansi_regex = re.compile(r'\033\[(\d+)m')
    color_map = {
        '31': 'color: #FF4500', '32': 'color: #00FF00', '33': 'color: #FFA500',
        '34': 'color: #6495ED', '35': 'color: #FF00FF', '36': 'color: #008B8B',
        '1': 'font-weight: bold',
    }
    def replacer(match):
        code = match.group(1)
        if code == '0': return '</span>'
        if code in color_map: return f'<span style="{color_map[code]}">'
        return ''
    return ansi_regex.sub(replacer, html)

# --- PROGRAM MANAGEMENT ---
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
        
        st.session_state.rb_manager.cleanup()
        st.session_state.rb_manager.history_commands.clear()
        st.session_state.rb_manager.permanent_recycle_bin.clear()
        st.session_state.rb_manager.temporary_recycle_bin.clear()
        st.session_state.rb_manager.history_pointer = None
        
        st.session_state.active_program = name
        proof_logger.open(use_streamlit=True)

# --- SESSION INITIALIZATION ---
def init_session():
    if "itp_data" not in st.session_state:
        # Wrap in single-line IIFE with try/catch to prevent st_javascript from hanging on SecurityErrors (Streamlit Cloud cross-origin iframes)
        ls_code = "(function(){ try { var ls = null; try { ls = window.parent.localStorage; } catch(e) { ls = window.localStorage; } return ls.getItem('itp_data') || 'null'; } catch(e) { return 'null'; } })();"
        ls_str = st_javascript(ls_code)
        
        if ls_str == 0:
            st.write("Loading from Local Storage...")
            st.stop()
        elif ls_str == "null" or ls_str is None:
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
        st.session_state.proofs_html = "# Foundational Proof Log\n**Format**: `premise1: def, ... ⊢ conclusion: def  (justification)`\n\n---\n"
        
    if "session_id" not in st.session_state:
        import uuid
        st.session_state.session_id = uuid.uuid4().hex
        
    if "rb_manager" not in st.session_state:
        from RecycleBinManager import RecycleBinManager
        st.session_state.rb_manager = RecycleBinManager(swap_dir=f"/tmp/swap_files_{st.session_state.session_id}")
init_session()

# --- MAIN UI ---
def render_prover_interface(is_game_mode=False):
    # PROVER INTERFACE
    col_hdr1, col_env_s, col_env_l, col_hst_s, col_hst_l, col_hdr2 = st.columns([2.5, 1, 1, 1, 1, 1])
    with col_hdr1:
        st.subheader(f"Active: {st.session_state.active_program}")
        
    def toggle_action(action_name):
        if st.session_state.active_action == action_name:
            st.session_state.active_action = None
        else:
            st.session_state.active_action = action_name
            st.session_state.selected_file = None
            
    with col_env_s:
        if not is_game_mode and st.button("💾 Save Env", use_container_width=True): toggle_action("save_env")
    with col_env_l:
        if not is_game_mode and st.button("📂 Load Env", use_container_width=True): toggle_action("load_env")
    with col_hst_s:
        if not is_game_mode and st.button("💾 Save Hist", use_container_width=True): toggle_action("save_hist")
    with col_hst_l:
        if not is_game_mode and st.button("📂 Load Hist", use_container_width=True): toggle_action("load_hist")
    with col_hdr2:
        if st.button("Save & Exit" if not is_game_mode else "Exit Game", use_container_width=True):
            if not is_game_mode:
                save_program(st.session_state.active_program)
                proof_logger.close()
            else:
                st.session_state.active_game_state["is_playing"] = False
                st.session_state.active_game_state["level"] = None
                
            st.session_state.active_program = None
            st.session_state.active_action = None
            st.rerun()

    # Render Active Action Container directly below the buttons
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
                    st.rerun()


    col_top1, col_top2 = st.columns(2)
    with col_top1:
        with st.expander("Current Command History"):
            if st.session_state.command_history:
                st.code("\n".join(st.session_state.command_history), language="text")
            else:
                st.write("No commands executed yet.")

    with col_top2:
        with st.expander("proofs.html"):
            proof_html = st.session_state.get("proofs_html", "")
            if len(proof_html) > 100:  # Has more than just header
                import markdown
                import streamlit.components.v1 as components
                html_rendered = markdown.markdown(proof_html)
                components.html(html_rendered, height=400, scrolling=True)
                st.download_button(
                    label="Export proofs.md", 
                    data=proof_html.encode("utf-8"), 
                    file_name=f"{st.session_state.active_program}_proofs.md", 
                    mime="text/markdown"
                )
            else:
                st.write("No proofs generated yet. Prove a theorem to generate the log!")

    st.divider()

    # Display the environment
    current_env = st.session_state.env_chain[-1]
    ground_env = st.session_state.env_chain[0]

    col_env1, col_env2 = st.columns([1, 1])

    with col_env1:
        st.subheader("Global Environment Objects")
        with st.expander("Variables"):
            for name in ground_env.variables:
                st.markdown(f'<span style="color: #6495ED">{name}</span>', unsafe_allow_html=True)
                
        with st.expander("Propositional Variables"):
            for name in ground_env.propositional_variables:
                st.markdown(f'<span style="color: #6495ED">{name}</span>', unsafe_allow_html=True)
                
        with st.expander("Dummy Variables"):
            for name in ground_env.dummy_variables:
                st.markdown(f'<span style="color: #6495ED">{name}</span>', unsafe_allow_html=True)
                
        with st.expander("Functions"):
            for name, term in ground_env.terms.items():
                if isinstance(term, Function) and name == term.name:
                    st.markdown(f'<span style="color: #6495ED">{name}</span> : {term.arity}', unsafe_allow_html=True)
                    
        with st.expander("Relations"):
            for name, formula in ground_env.formulae.items():
                if isinstance(formula, Relation) and name == formula.name:
                    st.markdown(f'<span style="color: #6495ED">{name}</span> : {formula.arity}', unsafe_allow_html=True)

    with col_env2:
        st.subheader("Environments")
        with st.expander("Active Environments Chain", expanded=True):
            for i, env in enumerate(st.session_state.env_chain):
                with st.expander(f"Environment Level {i} {'(Ground)' if i==0 else '(Mission)'}", expanded=(i == len(st.session_state.env_chain)-1)):
                    if i > 0 and env.target_goal:
                        goal_name = env.goal_formula_name
                        goal_html = reconstruct_string(env.target_goal, color_mode="html", target_name=goal_name, target_type="fol")
                        st.markdown(f'**Goal**: <span class="interactive-name itp-tooltip" data-obj-type="goal" data-target="{goal_name}" data-tooltip="Goal Formula" style="color: #FFA500; font-weight: bold;">{goal_name}</span> : {goal_html}', unsafe_allow_html=True)
                        
                    st.markdown("**Terms**")
                    has_terms = False
                    for name, term in env.local_terms.items():
                        if isinstance(term, Function) and name == term.name:
                            continue
                        term_html = reconstruct_string(term, color_mode="html", target_name=name, target_type="term")
                        st.markdown(f'<span class="itp-tooltip" data-tooltip="Term Definition"><span style="color: #6495ED">{name}</span></span> : {term_html}', unsafe_allow_html=True)
                        has_terms = True
                    if not has_terms:
                        st.markdown("*(None)*")
                    
                    st.markdown("**Formulae**")
                    has_formulae = False
                    for name, formula in env.local_formulae.items():
                        if isinstance(formula, Relation) and name == formula.name:
                            continue
                        
                        is_proven = name in env.local_theorems
                        is_goal = (i > 0 and name == env.goal_formula_name)
                        
                        if is_goal:
                            obj_type = "goal"
                            color = "#FFA500"
                        elif is_proven:
                            obj_type = "proven"
                            color = "#00FF00"
                        else:
                            obj_type = "unproven"
                            color = "#6495ED"
                            
                        prefix = "<strong>[Proven]</strong> " if is_proven else ""
                        
                        form_html = reconstruct_string(formula, color_mode="html", target_name=name, target_type="fol")
                        name_span = f'<span class="interactive-name itp-tooltip" data-obj-type="{obj_type}" data-target="{name}" data-tooltip="Formula Definition" style="color: {color}">{name}</span>'
                        
                        st.markdown(f'{prefix}{name_span} : {form_html}', unsafe_allow_html=True)
                        has_formulae = True
                    if not has_formulae:
                        st.markdown("*(None)*")

    st.divider()
    st.subheader("Console")
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            st.markdown(msg, unsafe_allow_html=True)

    # --- INTERACTIVE CLICK HANDLING ---
    import json
    import streamlit.components.v1 as components
    
    # Hide the text input completely and style the popover
    st.markdown("""
    <style>
    div[data-testid="stElementContainer"]:has(input[aria-label="itp_click_data"]) {
        position: absolute !important;
        width: 1px !important;
        height: 1px !important;
        opacity: 0.01 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        z-index: -1 !important;
    }
    .itp-popover {
        position: absolute;
        z-index: 10000;
        background: #ffffff;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        padding: 6px;
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        max-width: 300px;
    }
    .itp-popover button {
        background: #f3f4f6;
        border: 1px solid #e5e7eb;
        border-radius: 4px;
        padding: 4px 10px;
        font-size: 13px;
        font-weight: 500;
        cursor: pointer;
        color: #374151;
        transition: all 0.1s;
    }
    .itp-popover button:hover {
        background: #e5e7eb;
        border-color: #d1d5db;
    }
    .itp-popover-input {
        width: 100%;
        padding: 4px 6px;
        margin-bottom: 4px;
        border: 1px solid #d1d5db;
        border-radius: 4px;
        font-size: 13px;
        box-sizing: border-box;
        outline: none;
    }
    .itp-popover-input:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 1px #3b82f6;
    }
    </style>
    """, unsafe_allow_html=True)
    
    clicked_payload_raw = st.text_input("itp_click_data", key="itp_click_data", label_visibility="collapsed")

    if clicked_payload_raw and clicked_payload_raw != st.session_state.get("last_clicked_payload"):
        print(f"BACKEND RECEIVED CLICK DATA: {clicked_payload_raw}", flush=True)
        st.session_state.last_clicked_payload = clicked_payload_raw
        try:
            data = json.loads(clicked_payload_raw)
            selected_cmd = data.get("cmd")
            target = data.get("target")
            occ = data.get("occ")
            symbol = data.get("symbol")
            
            args = data.get("args", [])
            
            if selected_cmd:
                if selected_cmd in ["simp_l_eq", "simp_r_eq", "simp_l_bi", "simp_r_bi"]:
                    parts = [selected_cmd]
                    if len(args) > 0: parts.append(args[0])
                    if len(args) > 1 and args[1].strip(): parts.append(args[1])
                    parts.append(target)
                elif selected_cmd in ["apply", "apply2", "apply3", "intro2"]:
                    parts = [selected_cmd, target]
                    if len(args) > 0: parts.append(args[0])
                elif selected_cmd == "intro":
                    parts = [selected_cmd, target]
                    if len(args) > 0: parts.append(args[0])
                    if len(args) > 1 and args[1].strip(): parts.append(args[1])
                elif selected_cmd in ["st", "sb", "sf", "sp"]:
                    parts = [selected_cmd, symbol]
                    if len(args) > 0: parts.append(args[0])
                    parts.extend([str(occ), target])
                elif selected_cmd == "fold all":
                    parts = ["fold", "all", target]
                elif selected_cmd == "fold":
                    parts = ["fold", symbol, str(occ), target]
                elif selected_cmd == "sa":
                    parts = [selected_cmd, symbol]
                    if len(args) > 0: parts.append(args[0])
                    parts.append(target)
                elif selected_cmd == "contra":
                    parts = [selected_cmd, target]
                    if len(args) > 0: parts.append(args[0])
                    if len(args) > 1: parts.append(args[1])
                elif selected_cmd in ["dt", "and", "imply"]:
                    parts = [selected_cmd, target]
                    if len(args) > 0: parts.append(args[0])
                    if len(args) > 1: parts.append(args[1])
                elif selected_cmd in ["neg-", "neg+", "left", "right"]:
                    parts = [selected_cmd, target]
                    if len(args) > 0: parts.append(args[0])
                elif selected_cmd == "rw":
                    parts = [selected_cmd]
                    if len(args) > 1 and args[1].strip(): parts.append(args[1])
                    if len(args) > 2 and args[2].strip(): parts.append(args[2])
                    parts.append(target)
                    if len(args) > 0 and args[0].strip(): parts.append(args[0])
                elif selected_cmd in ["mission", "auto", "search", "backward_search", "advanced_search"]:
                    parts = [selected_cmd, target]
                else:
                    parts = [selected_cmd, target, str(occ)]
                
                final_cmd = " ".join([p for p in parts if p])
                
                # Run immediately now that arguments are collected in the popup!
                print(f"BACKEND SETTING COMMAND TO: {final_cmd}", flush=True)
                st.session_state.interactive_cmd_to_run = final_cmd
        except Exception as e:
            print(f"Error parsing click data: {e}")
        st.rerun()

    allowed_commands_js = "null"
    if is_game_mode:
        allowed_cmds = st.session_state.active_game_state["level"].get("allowed_commands", [])
        allowed_commands_js = json.dumps(allowed_cmds)

    components.html("""
    <script>
        let existing = window.parent.document.getElementById('itp-click-script');
        if (existing) {
            existing.remove();
        }
        let script = window.parent.document.createElement('script');
        script.id = 'itp-click-script';
        script.innerHTML = `
        window.ITPAllowedCommands = __ALLOWED_COMMANDS_PLACEHOLDER__;
        if (window.itpClickListener) {
            window.document.removeEventListener('click', window.itpClickListener);
        }
        window.itpClickListener = function(e) {
            try {
                if (e.target.classList && (e.target.classList.contains('interactive-symbol') || e.target.classList.contains('interactive-name'))) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    let oldPopover = window.document.getElementById('itp-custom-popover');
                    if (oldPopover) {
                        oldPopover.remove();
                    }
                    
                    let targetElement = e.target;
                    let target_name = targetElement.getAttribute('data-target');
                    let symbol = targetElement.getAttribute('data-symbol') || targetElement.innerText;
                    let occ = targetElement.getAttribute('data-occ') || 1;
                    let cmds = [];
                    
                    if (targetElement.classList.contains('interactive-symbol')) {
                        let isLogical = ['∀', '∃', '∃!', 'ε', 'ι', '∨', '∧', '¬', '⇒', '⇔', '=', '∈'].includes(symbol);
                        cmds = ['st', 'sb', 'sf', 'sp', 'sa'];
                        if (isLogical) {
                            cmds = []; // No substitution for logical symbols
                        }
                        // fold command for quantifiers, choice ops, or user-defined symbols
                        if (['∀', '∃', '∃!', 'ε', 'ι'].includes(symbol) || !isLogical) {
                            cmds.push('fold');
                        }
                    } else {
                        let obj_type = targetElement.getAttribute('data-obj-type');
                        if (obj_type === 'unproven') {
                            cmds = ["mission", "contra", "apply", "auto", "search", "backward_search", "advanced_search", "fold all"];
                        } else if (obj_type === 'goal') {
                            cmds = ["intro2", "apply", "apply2", "apply3", "auto", "search", "backward_search", "advanced_search", "fold all", 'neg-', 'neg+', 'simp_l_eq', 'simp_r_eq', 'simp_l_bi', 'simp_r_bi', 'rw'];
                        } else if (obj_type === 'proven') {
                            cmds = ['intro', 'apply', 'apply2', 'apply3', 'dt', 'and', 'left', 'right', 'imply', 'neg-', 'neg+', 'simp_l_eq', 'simp_r_eq', 'simp_l_bi', 'simp_r_bi', 'rw', 'fold all'];
                        } else {
                            cmds = ['fold all'];
                        }
                    }
                    
                    
                    if (window.ITPAllowedCommands !== null) {
                        cmds = cmds.filter(cmd => window.ITPAllowedCommands.includes(cmd));
                    }
                    
                    if (cmds.length === 0) {
                        return;
                    }
                    
                    let popover = window.document.createElement('div');
                    popover.id = 'itp-custom-popover';
                    popover.className = 'itp-popover';
                    
                    let rect = e.target.getBoundingClientRect();
                    
                    cmds.forEach(cmd => {
                        let btn = window.document.createElement('button');
                        btn.innerText = cmd;
                        btn.onclick = function(ev) {
                            ev.preventDefault();
                            ev.stopPropagation();
                            
                            let needsArgs = 0;
                            let arg1Label = "Argument";
                            let arg2Label = "Argument 2";
                            
                            if (["simp_l_eq", "simp_r_eq", "simp_l_bi", "simp_r_bi", "apply", "apply2", "apply3", "st", "sb", "sf", "sa", "sp", "intro2"].includes(cmd)) {
                                needsArgs = 1;
                                if (["st", "sb", "sf", "sa", "sp"].includes(cmd)) arg1Label = "Formula/Term";
                                else arg1Label = "Theorem Name";
                                
                                if (cmd.startsWith("simp_")) {
                                    needsArgs = 2;
                                    arg2Label = "Occurrences (optional)";
                                }
                            } else if (cmd === "contra") {
                                needsArgs = 2;
                                arg1Label = "Formula 1";
                                arg2Label = "Formula 2";
                            } else if (cmd === "intro") {
                                needsArgs = 2;
                                arg1Label = "Variable/Term";
                                arg2Label = "New Formula Name (optional for goals)";
                            } else if (["neg-", "neg+", "left", "right"].includes(cmd)) {
                                needsArgs = 1;
                                arg1Label = "New Formula Name";
                            } else if (["dt", "and", "imply"].includes(cmd)) {
                                needsArgs = 2;
                                arg1Label = "New Formula Name(s)";
                                arg2Label = "Variables/Theorems";
                                if (cmd === "and") { arg1Label = "Left Formula"; arg2Label = "Right Formula"; }
                            } else if (cmd === "rw") {
                                needsArgs = 3;
                                arg1Label = "New Formula";
                                arg2Label = "Rewrite Theorem";
                            }
                            
                            let submitCmd = function(argsList) {
                                let data = {
                                    target: target_name,
                                    symbol: symbol,
                                    occ: occ,
                                    cmd: cmd,
                                    args: argsList,
                                    _nonce: Date.now()
                                };
                                let input = window.parent.document.querySelector('input[aria-label="itp_click_data"]');
                                if (input) {
                                    input.focus();
                                    setTimeout(() => {
                                        let nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                                        nativeSetter.call(input, JSON.stringify(data));
                                        input.dispatchEvent(new Event('input', { bubbles: true }));
                                        input.dispatchEvent(new Event('change', { bubbles: true }));
                                        setTimeout(() => {
                                            input.blur();
                                        }, 50);
                                    }, 50);
                                }
                                popover.remove();
                            };

                            if (needsArgs === 0) {
                                submitCmd([]);
                                return;
                            }
                            
                            // Show secondary form inline
                            popover.innerHTML = '';
                            popover.style.flexDirection = 'column';
                            
                            let title = window.document.createElement('div');
                            title.innerText = "Command: " + cmd;
                            title.style.fontWeight = 'bold';
                            title.style.marginBottom = '6px';
                            title.style.fontSize = '14px';
                            popover.appendChild(title);
                            
                            let input1 = null;
                            let input2 = null;
                            
                            if (needsArgs >= 1) {
                                input1 = window.document.createElement('input');
                                input1.type = 'text';
                                input1.placeholder = arg1Label;
                                input1.className = 'itp-popover-input';
                                popover.appendChild(input1);
                            }
                            if (needsArgs >= 2) {
                                input2 = window.document.createElement('input');
                                input2.type = 'text';
                                input2.placeholder = arg2Label;
                                input2.className = 'itp-popover-input';
                                popover.appendChild(input2);
                            }
                            
                            let input3 = null;
                            if (needsArgs >= 3) {
                                input3 = window.document.createElement('input');
                                input3.type = 'text';
                                input3.placeholder = "Occurrences (optional)";
                                input3.className = 'itp-popover-input';
                                popover.appendChild(input3);
                            }
                            
                            let btnContainer = window.document.createElement('div');
                            btnContainer.style.display = 'flex';
                            btnContainer.style.gap = '6px';
                            btnContainer.style.width = '100%';
                            
                            let runBtn = window.document.createElement('button');
                            runBtn.innerText = 'Run';
                            runBtn.style.flex = '1';
                            runBtn.style.background = '#3b82f6';
                            runBtn.style.color = 'white';
                            runBtn.style.borderColor = '#2563eb';
                            
                            runBtn.onclick = function(eRun) {
                                eRun.preventDefault(); eRun.stopPropagation();
                                
                                let val1 = input1 ? input1.value : "";
                                let val2 = input2 ? input2.value : "";
                                let val3 = input3 ? input3.value : "";
                                
                                let occ = targetElement.getAttribute('data-occ') || 1;
                                let symbol = targetElement.getAttribute('data-symbol') || targetElement.innerText;
                                
                                let argsArr = [];
                                if (needsArgs >= 1) argsArr.push(val1);
                                if (needsArgs >= 2) argsArr.push(val2);
                                if (needsArgs >= 3) argsArr.push(val3);
                                
                                let payload = JSON.stringify({
                                    cmd: cmd,
                                    target: target_name,
                                    occ: parseInt(occ),
                                    symbol: symbol,
                                    args: argsArr,
                                    _nonce: Date.now()
                                });
                                
                                let input = window.parent.document.querySelector('input[aria-label="itp_click_data"]');
                                if (input) {
                                    input.focus();
                                    setTimeout(() => {
                                        let nativeSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                                        nativeSetter.call(input, payload);
                                        input.dispatchEvent(new Event('input', { bubbles: true }));
                                        input.dispatchEvent(new Event('change', { bubbles: true }));
                                        setTimeout(() => {
                                            input.blur();
                                        }, 50);
                                    }, 50);
                                }
                                popover.remove();
                            };
                            
                            let cancelBtn = window.document.createElement('button');
                            cancelBtn.innerText = 'Cancel';
                            cancelBtn.style.flex = '1';
                            cancelBtn.onclick = function(eCancel) {
                                eCancel.preventDefault(); eCancel.stopPropagation();
                                popover.remove();
                            };
                            
                            btnContainer.appendChild(runBtn);
                            btnContainer.appendChild(cancelBtn);
                            popover.appendChild(btnContainer);
                            
                            if (input1) setTimeout(() => input1.focus(), 50);
                            
                            let handleEnter = function(eKey) {
                                if (eKey.key === 'Enter') runBtn.click();
                            };
                            if (input1) input1.addEventListener('keydown', handleEnter);
                            if (input2) input2.addEventListener('keydown', handleEnter);
                        };
                        popover.appendChild(btn);
                    });
                    
                    
                    window.document.body.appendChild(popover);
                    popover.style.position = 'fixed';
                    popover.style.zIndex = '999999';
                    
                    let updatePosition = function() {
                        let rect = targetElement.getBoundingClientRect();
                        let pHeight = popover.offsetHeight;
                        let topPos = rect.top - pHeight - 8;
                        if (topPos < 0) {
                            topPos = rect.bottom + 8;
                        }
                        popover.style.top = topPos + 'px';
                        popover.style.left = rect.left + 'px';
                    };
                    updatePosition();
                    
                    let scrollListener = function() {
                        if (window.document.body.contains(popover)) {
                            updatePosition();
                        } else {
                            window.parent.removeEventListener('scroll', scrollListener, true);
                        }
                    };
                    window.parent.addEventListener('scroll', scrollListener, true);
                    
                    const observer = new ResizeObserver(() => {
                        if (window.document.body.contains(popover)) {
                            updatePosition();
                        } else {
                            observer.disconnect();
                        }
                    });
                    observer.observe(popover);
                    
                } else {
                    let popover = window.document.getElementById('itp-custom-popover');
                    if (popover && !popover.contains(e.target)) {
                        popover.remove();
                    }
                }
            } catch(err) {
                console.error(err);
            }
        };
        window.document.addEventListener('click', window.itpClickListener);
        `;
        window.parent.document.body.appendChild(script);
    </script>
    """.replace("__ALLOWED_COMMANDS_PLACEHOLDER__", allowed_commands_js), height=0, width=0)
    if st.session_state.get("interactive_cmd_to_run"):
        command = st.session_state.interactive_cmd_to_run
        st.session_state.interactive_cmd_to_run = None
        interactive_submit = True
    else:
        command = None
        interactive_submit = False

    prompt_str = f"ITP {len(st.session_state.env_chain)-1}> "
    
    # Real-time Autocomplete UI
    if st_keyup is not None:
        # We need a clear button or form to submit, but st_keyup doesn't natively submit on enter unless we use a button
        # We'll use two columns: input and submit button
        st.markdown("### Command Input")
        
        # Use session state to hold the partial input so suggestions can update it
        if "current_cmd" not in st.session_state:
            st.session_state.current_cmd = ""
        if "keyup_key" not in st.session_state:
            st.session_state.keyup_key = 0
            
        # If the user clicks a suggestion, it updates st.session_state.current_cmd
        
        col_input, col_btn = st.columns([5, 1])
        with col_input:
            partial_command = st_keyup("Type your command:", value=st.session_state.current_cmd, key=f"live_input_{st.session_state.keyup_key}", debounce=0)
        with col_btn:
            # Add some vertical margin so button aligns with input
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            btn_clicked = st.button("Run Command", use_container_width=True)
            submit_clicked = btn_clicked or interactive_submit
            
        # Compute and render suggestions
        if partial_command is not None and not submit_clicked:
            if is_game_mode:
                game_allowed = st.session_state.active_game_state["level"].get("allowed_commands", [])
                suggestions = autocomplete_engine.get_suggestions(partial_command, current_env, game_allowed)
            else:
                suggestions = autocomplete_engine.get_suggestions(partial_command, current_env)
            
            if suggestions == ["ERROR: INVALID REPL COMMAND"]:
                st.markdown("<span style='color:red;'>❌ Invalid REPL Command</span>", unsafe_allow_html=True)
            elif suggestions:
                st.markdown("**Suggestions:**")
                # Render chips inside a scrollable container
                with st.container(height=180):
                    max_sugs = min(len(suggestions), 50)
                    
                    selection = st.pills(
                        "Suggestions",
                        options=suggestions[:max_sugs],
                        label_visibility="collapsed",
                        key=f"sug_pills_{st.session_state.keyup_key}"
                    )
                    
                    if selection:
                        tokens = partial_command.lstrip().split(" ")
                        tokens[-1] = selection
                        new_cmd = " ".join(tokens) + " "
                        st.session_state.current_cmd = new_cmd
                        st.session_state.keyup_key += 1
                        st.rerun()
            else:
                st.write("*(No suggestions)*")
        elif not submit_clicked:
            submit_clicked = False
            
        if not command:
            command = partial_command if submit_clicked else None
        
        # Clear input after run
        if submit_clicked:
            st.session_state.current_cmd = ""
            st.session_state.keyup_key += 1
            
        # Disable native browser autocomplete and add button CSS
        st.components.v1.html(
            """<script>
            window.parent.document.querySelectorAll('input').forEach(i => i.setAttribute('autocomplete', 'off'));
            
            let oldCss = window.parent.document.getElementById('custom-button-css');
            if (oldCss) oldCss.remove();
            
            window.parent.document.head.insertAdjacentHTML("beforeend", `<style id='custom-button-css'>
            .stButton > button { transition: all 0.1s ease !important; }
                .stButton > button:hover { background-color: #f0f8ff !important; border-color: #1e90ff !important; color: #1e90ff !important; }
                .stButton > button:active { background-color: #e6f2ff !important; transform: scale(0.95) !important; border-color: #0066cc !important; color: #0066cc !important; }
                
                /* Increase font size for the suggestions in the st.pills component */
                div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stPills"] span,
                div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stPills"] p {
                    font-size: 1.2rem !important;
                    padding: 0.2rem 0 !important;
                }
                
                /* Tooltip CSS */
                .itp-tooltip {
                    position: relative;
                    cursor: help;
                    display: inline-block;
                    padding: 0 1px;
                    border-radius: 2px;
                }
                .itp-tooltip:hover {
                    outline: 1px solid rgba(100, 149, 237, 0.6);
                    background-color: rgba(100, 149, 237, 0.1);
                }
                .interactive-symbol, .interactive-name {
                    cursor: pointer;
                    border-bottom: 1px dashed rgba(100, 149, 237, 0.5);
                }
                .interactive-symbol:hover, .interactive-name:hover {
                    background-color: rgba(255, 165, 0, 0.2);
                    outline: 1px solid rgba(255, 165, 0, 0.8);
                }
                
                /* Hide custom click listener component */
                iframe[title="click_listener"] {
                    position: absolute !important;
                    width: 0px !important;
                    height: 0px !important;
                    border: none !important;
                    visibility: hidden !important;
                    opacity: 0 !important;
                }
                div[data-testid="stElementContainer"]:has(iframe[title="click_listener"]) {
                    height: 0px !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    overflow: hidden !important;
                }
                .itp-tooltip::after {
                    content: attr(data-tooltip);
                    position: absolute;
                    bottom: 100%;
                    left: 50%;
                    transform: translateX(-50%);
                    background-color: #333;
                    color: #fff;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    white-space: nowrap;
                    opacity: 0;
                    pointer-events: none;
                    transition: opacity 0.2s;
                    z-index: 1000;
                    font-family: sans-serif;
                }
                .itp-tooltip:hover::after {
                    opacity: 1;
                }
                </style>`);
            
            let oldScript = window.parent.document.getElementById('itp-enter-script');
            if (oldScript) oldScript.remove();
            
            setInterval(() => {
                // Inject a script directly into the parent window to escape the iframe sandbox
                if (!window.parent.document.getElementById('itp-enter-script')) {
                    const script = window.parent.document.createElement('script');
                    script.id = 'itp-enter-script';
                    script.innerHTML = `
                        setInterval(() => {
                            const iframes = document.querySelectorAll('iframe');
                            iframes.forEach(iframe => {
                                try {
                                    const input = iframe.contentWindow.document.querySelector('input');
                                    if (input && !input.dataset.enterListenerAdded) {
                                        input.setAttribute('autocomplete', 'new-password');
                                        input.setAttribute('name', 'itp_cmd_' + Math.random());
                                        input.setAttribute('spellcheck', 'false');
                                        input.setAttribute('autocorrect', 'off');
                                        
                                        input.addEventListener('keydown', function(e) {
                                            if (e.key === 'Enter') {
                                                input.blur();
                                                
                                                let clickAttempts = 0;
                                                function tryClick() {
                                                    const btns = window.parent.document.querySelectorAll('button');
                                                    let found = null;
                                                    for(let i=0; i<btns.length; i++) {
                                                        if (btns[i].innerText && btns[i].innerText.toLowerCase().includes('run command')) {
                                                            found = btns[i];
                                                            break;
                                                        }
                                                    }
                                                    if (found && !found.disabled) {
                                                        found.click();
                                                    } else if (clickAttempts < 10) {
                                                        clickAttempts++;
                                                        setTimeout(tryClick, 50);
                                                    }
                                                }
                                                // Wait 150ms for st_keyup debounce to sync value to backend
                                                setTimeout(tryClick, 150);
                                            }
                                        }, true);
                                        input.dataset.enterListenerAdded = "true";
                                    }
                                } catch(e) {}
                            });
                        }, 500);
                    `;
                    window.parent.document.body.appendChild(script);
                }
            }, 1000);
            </script>
            """,
            height=0, width=0
        )
    else:
        # Fallback if streamlit-keyup is not installed
        command = st.chat_input("Enter command here (install streamlit-keyup for autocomplete)")

    if command:
        command_lines = command.strip().splitlines()
        first_line = command_lines[0]
        command_queue = command_lines[1:] if len(command_lines) > 1 else []
        parts = first_line.strip().split(maxsplit=1)
        cmd = parts[0]
        args_str = parts[1] if len(parts) > 1 else ""
        
        st.session_state.chat_history.append(f'<strong>{prompt_str}{command}</strong>')
        st.session_state.command_history.append(command)
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            if cmd == "exit":
                if len(st.session_state.env_chain) > 1:
                    st.session_state.env_chain.pop()
                    print("Exited child environment.")
                else:
                    print("Already at ground environment.")
            elif cmd == "undo":
                success, env, msg = st.session_state.rb_manager.undo(current_env)
                print(msg)
                if success:
                    chain = []
                    curr = env
                    while curr is not None:
                        chain.append(curr)
                        curr = curr.parent
                    chain.reverse()
                    st.session_state.env_chain = chain
            elif cmd == "redo":
                success, env, msg = st.session_state.rb_manager.redo(current_env)
                print(msg)
                if success:
                    chain = []
                    curr = env
                    while curr is not None:
                        chain.append(curr)
                        curr = curr.parent
                    chain.reverse()
                    st.session_state.env_chain = chain
            elif cmd == "rb_stat":
                print(st.session_state.rb_manager.stat())
            elif cmd == "rb_empty":
                sub_args = args_str.split()
                target = sub_args[0] if len(sub_args) > 0 else "all"
                try:
                    count = int(sub_args[1]) if len(sub_args) > 1 else None
                except ValueError:
                    print("Error: Count must be an integer.")
                    count = None
                if count is not None or len(sub_args) <= 1:
                    print(st.session_state.rb_manager.empty(target, count))
            elif cmd == "rb_swap":
                sub_args = args_str.split()
                if len(sub_args) < 2:
                    print("Error: Usage: rb_swap <perm|temp> <count>")
                else:
                    target = sub_args[0]
                    try:
                        count = int(sub_args[1])
                        print(st.session_state.rb_manager.swap(target, count))
                    except ValueError:
                        print("Error: Count must be an integer.")
            elif registry.is_registered(cmd):
                try:
                    st.session_state.rb_manager.truncate_history_if_needed(cmd)
                    mission_entered = False
                    mission_resolved = False
                    old_env_ref = current_env
                    
                    if is_game_mode:
                        level = st.session_state.active_game_state["level"]
                        if cmd not in level.get("allowed_commands", []):
                            raise Exception(f"Command '{cmd}' is not allowed in this level.")
                        if cmd.startswith("apply"):
                            # The first argument is target formula, second is the rule/axiom name
                            parts = args_str.strip().split()
                            if len(parts) > 1:
                                rule_name = parts[1]
                            else:
                                rule_name = parts[0]
                            allowed_axioms = level.get("allowed_axioms", [])
                            allowed_rules = level.get("allowed_rules", [])
                            if rule_name not in allowed_axioms and rule_name not in allowed_rules:
                                if rule_name not in current_env.theorems:
                                    raise Exception(f"Rule/Axiom '{rule_name}' is not allowed in this level.")

                    new_env = registry.dispatch(cmd, current_env, args_str, get_default_env=get_default_env, command_queue=command_queue)
                    if new_env is not None and new_env is not current_env:
                        if new_env.parent is current_env:
                            st.session_state.env_chain.append(new_env)
                            mission_entered = True
                        elif current_env.parent is new_env:
                            st.session_state.env_chain.pop()
                            mission_resolved = True
                        
                    current_env = st.session_state.env_chain[-1]
                    
                    if cmd not in {"save", "save_h", "load", "load_h", "help", "guide", "clear", "rb_stat", "rb_empty", "rb_swap"}:
                        st.session_state.rb_manager.record_command(first_line, old_env_ref, current_env, mission_entered, mission_resolved)
                        
                    # Goal checking for game mode
                    if is_game_mode and not st.session_state.active_game_state["completed"]:
                        goal_str = st.session_state.active_game_state["level"]["goal_statement"]
                        from Frontend import Parser
                        parser = Parser(current_env)
                        goal_node = parser.parse(goal_str, "goal")
                        
                        # Check if any theorem matches goal_node
                        for thm_name in current_env.theorems:
                            if current_env.formulae[thm_name].is_structurally_equal(goal_node):
                                st.session_state.active_game_state["completed"] = True
                                level_id = st.session_state.active_game_state["level_id"]
                                st.session_state.games_progress[level_id] = True
                                st.session_state.itp_data["games_progress"] = st.session_state.games_progress
                                st.session_state.needs_save = True
                                break
                except Exception as e:
                    print(f"Error: {e}")
            elif cmd == "clear":
                st.session_state.chat_history.clear()
            else:
                print(f"Unknown command '{cmd}'.")
                
        output = f.getvalue()
        if output:
            # Add CSS styling for errors if output contains "Error:"
            formatted_output = []
            for line in output.split('\\n'):
                if line.startswith('Error:'):
                    formatted_output.append(f"<span style='color:red;'>{line}</span>")
                else:
                    formatted_output.append(ansi_to_html(line))
            
            output_str = "<br>".join(formatted_output)
            st.session_state.chat_history.append(f"<div style='font-family: monospace; white-space: pre-wrap;'>{output_str}</div>")
            
        st.rerun()

st.title("Interactive Theorem Prover")

tab_home, tab_programs, tab_games, tab_help, tab_about, tab_contact = st.tabs([
    "🏠 Home", "💻 Programs", "🎮 Games", "❓ Help", "ℹ️ About", "📧 Contact Us"
])

with tab_home:
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); border-radius: 10px; color: white;">
        <h1>Welcome to the Interactive Theorem Prover!</h1>
        <p style="font-size: 1.2rem; margin-top: 10px;">A rigorous platform for constructing verifiable proofs in First-Order Logic and Set Theory.</p>
    </div>
    <br>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("### 📐 Mathematical Rigor\nEvery proof rests entirely on fundamental axioms like Modus Ponens and Universal Instantiation.")
    with col2:
        st.success("### 📜 Foundational Logging\nYour proofs are elegantly documented in `proofs.html` making verification easy.")
    with col3:
        st.warning("### 🧠 Interactive Missions\nEnter child environments to isolate proof context, assume premises, and resolve complex theorem structures.")
        
    st.markdown("---")
    st.markdown("### Getting Started")
    st.markdown("1. Head over to the **Games** tab.")
    st.markdown("2. Select the **basics of ITP** game.")
    st.markdown("3. Play all the levels sequentially from Level 1 to Level 22 to master the system!")
    
    st.markdown("---")
    st.markdown("### Desktop / Terminal Version")
    st.markdown("Want to run the Interactive Theorem Prover in your own local terminal instead? You can download the entire source code here. Extract the zip file and run `python main.py` to start the CLI version!")
    
    zip_bytes = get_desktop_zip()
    st.download_button(
        label="⬇️ Download Desktop Version (ZIP)",
        data=zip_bytes,
        file_name="itp_desktop_version.zip",
        mime="application/zip"
    )

with tab_programs:
    is_in_game = st.session_state.active_game_state.get("is_playing", False)
    if st.session_state.active_program is None or is_in_game:
        st.subheader("📁 Saved Programs")
        if is_in_game:
            st.info("You are currently in Game Mode. Return to the Games tab to continue playing, or exit the game to load a different program.")
        
        programs = list(st.session_state.itp_data.get("programs", {}).keys())
        if not programs:
            st.write("No programs created yet.")
        else:
            for p in programs:
                col_name, col_btn = st.columns([4, 1])
                with col_name:
                    st.write(f"**{p}**")
                with col_btn:
                    if st.button("Load", key=f"load_{p}", disabled=is_in_game):
                        load_program(p)
                        st.rerun()
                        
        st.divider()
        st.subheader("✨ Create New Program")
        new_prog_name = st.text_input("Program Name", disabled=is_in_game)
        if st.button("Create", disabled=is_in_game):
            if new_prog_name:
                if new_prog_name in programs:
                    st.error("Program already exists!")
                else:
                    st.session_state.active_program = new_prog_name
                    st.session_state.env_chain = [get_default_env()]
                    st.session_state.chat_history = []
                    st.session_state.command_history = []
                    st.session_state.proofs_html = "# Foundational Proof Log\n**Format**: `premise1: def, ... ⊢ conclusion: def  (justification)`\n\n---\n"
                    st.session_state.rb_manager.cleanup()
                    st.session_state.rb_manager.history_commands.clear()
                    st.session_state.rb_manager.permanent_recycle_bin.clear()
                    st.session_state.rb_manager.temporary_recycle_bin.clear()
                    st.session_state.rb_manager.history_pointer = None
                    
                    proof_logger.open(use_streamlit=True)
                    save_program(new_prog_name)
                    st.rerun()
            else:
                st.error("Please enter a valid name.")
    else:
        render_prover_interface(is_game_mode=False)

with tab_games:
    st.header("🎮 Games")
    games_dir = "games"
    if not os.path.exists(games_dir):
        os.makedirs(games_dir, exist_ok=True)
    
    games = [d for d in os.listdir(games_dir) if os.path.isdir(os.path.join(games_dir, d))]
    
    if not games:
        st.info("No games available.")
    else:
        # Check if currently playing a level
        if st.session_state.active_game_state["is_playing"]:
            if st.button("⬅️ Back to Levels"):
                st.session_state.active_game_state["is_playing"] = False
                st.session_state.active_game_state["level"] = None
                st.session_state.active_program = None
                st.rerun()
                
            st.divider()
            col_guide, col_prover = st.columns([1, 2.5])
            with col_guide:
                level_data = st.session_state.active_game_state["level"]
                
                if "guide_hints" in level_data:
                    if "hint_index" not in st.session_state.active_game_state:
                        st.session_state.active_game_state["hint_index"] = 0
                        
                    hint_idx = st.session_state.active_game_state["hint_index"]
                    hints = level_data["guide_hints"]
                    
                    for i in range(min(hint_idx + 1, len(hints))):
                        st.markdown(hints[i])
                        
                    if hint_idx < len(hints) - 1:
                        if st.button("Next Hint"):
                            st.session_state.active_game_state["hint_index"] += 1
                            st.rerun()
                else:
                    st.markdown(level_data.get("guide_markdown", ""))
                
                if st.session_state.active_game_state["completed"]:
                    st.success("🎉 **LEVEL COMPLETE!** 🎉")
                    st.markdown(level_data.get("completion_message", ""))
                    if st.button("Next / Return"):
                        st.session_state.active_game_state["is_playing"] = False
                        st.session_state.active_game_state["level"] = None
                        st.session_state.active_program = None
                        st.rerun()
            with col_prover:
                render_prover_interface(is_game_mode=True)
        else:
            st.subheader("Select a Game")
            selected_game = st.selectbox("Available Games", games)
            
            if selected_game:
                st.divider()
                st.subheader(f"Levels for: {selected_game}")
                game_path = os.path.join(games_dir, selected_game)
                levels = [f for f in os.listdir(game_path) if f.endswith(".json")]
                
                if not levels:
                    st.info("No levels found yet.")
                else:
                    import re
                    def extract_level_num(filename):
                        match = re.search(r'\d+', filename)
                        return int(match.group()) if match else 0
                        
                    # Sort levels numerically
                    levels.sort(key=extract_level_num)
                    
                    # Check if all levels are completed to show tick on game
                    all_completed = True
                    for level in levels:
                        level_id = f"{selected_game}/{level}"
                        if not st.session_state.games_progress.get(level_id, False):
                            all_completed = False
                            
                    if all_completed and len(levels) > 0:
                        st.success(f"🏆 You have completed all levels in **{selected_game}**!")
                    
                    for level in levels:
                        level_path = os.path.join(game_path, level)
                        with open(level_path, "r") as f:
                            level_data = json.load(f)
                        
                        level_id = f"{selected_game}/{level}"
                        is_completed = st.session_state.games_progress.get(level_id, False)
                        
                        col_text, col_btn = st.columns([4, 1])
                        with col_text:
                            status = "✅ " if is_completed else ""
                            level_num = extract_level_num(level)
                            level_name = level_data.get('name', level)
                            st.write(f"#### {status}Level {level_num}: {level_name}")
                        with col_btn:
                            if st.button("Play", key=f"play_{level_id}"):
                                st.session_state.active_game_state["is_playing"] = True
                                st.session_state.active_game_state["game_name"] = selected_game
                                st.session_state.active_game_state["level"] = level_data
                                st.session_state.active_game_state["level_id"] = level_id
                                st.session_state.active_game_state["completed"] = False
                                st.session_state.active_game_state["hint_index"] = 0
                                st.session_state.active_program = f"game_{selected_game}_{level_data['id']}"
                                
                                # Setup environment
                                proof_logger.open(use_streamlit=True)
                                
                                # Clear existing environment to load fresh
                                env = Environment()
                                from AST import RelationType, FunctionType, DummyVariable, Relation, Function
                                dummy = DummyVariable("x")
                                env.add_formula(Relation(name="=", arity=2, rel_type=RelationType.PRE_DEFINED, arguments=[dummy, dummy]))
                                
                                for f_def in level_data.get("default_functions", []):
                                    env.add_term(Function(name=f_def["name"], arity=f_def["arity"], func_type=FunctionType.PRE_DEFINED, arguments=[dummy]*f_def["arity"]))
                                for r_def in level_data.get("default_relations", []):
                                    env.add_formula(Relation(name=r_def["name"], arity=r_def["arity"], rel_type=RelationType.PRE_DEFINED, arguments=[dummy]*r_def["arity"]))
                                if level_data.get("start_env"):
                                    # load the start env from the game directory
                                    start_env_path = os.path.join(game_path, level_data["start_env"])
                                    if os.path.exists(start_env_path):
                                        with open(start_env_path, "r", encoding="utf-8") as f:
                                            start_env_content = f.read()
                                        env = deserialize_environment_state(start_env_content, get_default_env)
                                st.session_state.env_chain = [env]
                                st.session_state.chat_history = []
                                st.session_state.command_history = []
                                
                                st.rerun()
                        st.divider()

with tab_help:
    st.header("Command Reference")
    st.markdown("This section contains all syntax and variants for the commands available in the Interactive Theorem Prover.")

    with st.expander("Definitions & Environment Objects"):
        st.markdown("""
        - **`cv <name1> [name2...]`**: Create one or more First-Order Logic standard variables.
          *Example*: `cv x y z`
        - **`cV <name1> [name2...]`**: Create one or more Propositional Variables.
          *Example*: `cV P Q`
        - **`ct <name> <term>`**: Create a new term expression and assign it to `<name>`.
          *Example*: `ct t1 S(x)`
        - **`cf <name> <formula>`**: Create a new 1st-order logic formula and assign it to `<name>`.
          *Example*: `cf f1 ∀x (x = x)`
        - **`cp <name> <formula>`**: Create a new propositional logic formula and assign it to `<name>`.
          *Example*: `cp p1 P ∨ ¬P`
        - **`def_f <name> <arity> <definition>`**: Define a new user function.
          *Example*: `def_f id 1 _1`
        - **`def_r <name> <arity> <definition>`**: Define a new user relation.
          *Example*: `def_r LessEq 2 (_1 < _2) ∨ (_1 = _2)`
        - **`dt <name>`**: Delete a proven theorem.
        """)

    with st.expander("Substitutions & Folding"):
        st.markdown("""
        All substitution commands follow a variant of the fold syntax: `command [args] [occurrences] <target> [<out>] [<equiv>]`
        - **`st <var> <term> [occ] <target> [<out>]`**: Substitute term for a variable in a term.
          *Example*: `st x y 1 t1 t2` (In term t1, replace the 1st occurrence of x with y, output as t2).
        - **`sf <var> <term> [occ] [<target>] [<out>]`**: Substitute term for a **free** variable in a formula.
          *Example*: `sf x y f1 f2`
        - **`sb <var> <term> [occ] [<target>] [<out>] [<equiv>]`**: Rename a bound variable in a formula.
          *Example*: `sb x y f1 f2`
        - **`sa <var> <term> [occ] [<target>] [<out>]`**: Substitute term for ALL occurrences of a variable.
        - **`sp <prop_var> <prop_formula> [occ] [<target>] [<out>]`**: Substitute a propositional formula for a propositional variable.
        - **`fold <sym> [occ] [<target>] [<out>] [<equiv>]`**: Fold or unroll a definition.
          *Example*: `fold S f1 f2`
        - **`simp_l_eq <thm> [occ] [<target>] [<out>] [<equiv>]`**: Replace LHS with RHS of a theorem.
        """)

    with st.expander("Mission Tactics & Rules"):
        st.markdown("""
        - **`mission <formula>`**: Create a sub-environment with `<formula>` as the goal.
          *Example*: `mission ∀x (x=x)`
        - **`intro [<target>] <term> [<out>] [<equiv>]`**: Instantiate universal quantifiers or reduce goals.
          *Example*: `intro f1 x f2` (Instantiate `∀x Ψ` with `x`)
        - **`left [<target>] [<out>]`**: Reduce `Ψ ∨ Φ` to `Ψ`.
        - **`right [<target>] [<out>]`**: Reduce `Ψ ∨ Φ` to `Φ`.
        - **`and [<target>] [<out1>] <out2>`**: Split `Ψ ∧ Φ` into two goals.
        - **`imply [<target>] [<out1>] <out2>`**: Resolve implication `Ψ ⇒ Φ`.
        - **`contra [<f1>] f2 f3`**: Complete a proof by contradiction `f2 = ¬f1` leading to `⊥`.
        """)

    with st.expander("Resolution & Automation"):
        st.markdown("""
        - **`apply [<target>] <axiom_or_theorem>`**: Attempt backward unification of the active goal using an axiom.
          *Example*: `apply E1`
        - **`auto <formula>`**: Attempt fundamental automated resolution.
        - **`backward_search <formula>`**: Trigger deep backward proof-search using Resolution refutation.
        """)

with tab_about:
    st.header("About the Application")
    try:
        with open("README.md", "r") as f:
            readme_contents = f.read()
        st.markdown(readme_contents)
    except FileNotFoundError:
        st.write("README.md not found. The codebase is missing the primary documentation file.")

with tab_contact:
    st.header("Contact Us")
    st.write("Email: **ritilranjan5@gmail.com**")
    st.markdown("We value your feedback! Whether you want to suggest an improvement, report a bug, or give general advice, please leave your comments below.")
    
    with st.expander("Contact Us (Feedback & Suggestions)"):
        st.write("We'd love to hear from you! Please let us know about any bugs, or share your suggestions for the game.")
        
        feedback_type = st.radio("Type", ["Suggestion", "Complaint"], horizontal=True)
        user_email = st.text_input("Your Email Address")
        feedback_text = st.text_area("Description:")
        
        if st.button("Submit"):
            if not user_email.strip():
                st.warning("Please enter your email address so we can confirm receipt.")
            elif not feedback_text.strip():
                st.warning("Please enter some text before submitting.")
            elif "WEBHOOK_URL" not in st.secrets:
                st.error("Server is not configured to receive feedback yet (WEBHOOK_URL missing in secrets).")
            else:
                try:
                    import requests
                    import datetime
                    payload = {
                        "type": feedback_type,
                        "email": user_email.strip(),
                        "text": feedback_text.strip(),
                        "timestamp": str(datetime.datetime.now())
                    }
                    # We send the data to the Google Apps Script Webhook
                    # Apps Script web apps return 200 OK even if they fail internally, so we must parse the JSON
                    # Wait, requests.post to Google Apps Script returns a 302 redirect to a script.googleusercontent.com URL, which requests follows automatically.
                    response = requests.post(st.secrets["WEBHOOK_URL"], json=payload, timeout=15)
                    
                    if response.status_code == 200:
                        try:
                            # Try to parse the response as JSON (if it's our ContentService output)
                            resp_json = response.json()
                            if resp_json.get("status") == "success":
                                st.success(f"{feedback_type} submitted successfully! A confirmation email has been sent to you.")
                            else:
                                st.error(f"Webhook error: {resp_json.get('message', 'Unknown error')}")
                                st.write("Raw response:", resp_json)
                        except json.JSONDecodeError:
                            # If it's not JSON, it might be an HTML error page from Google (e.g. script authorization issue)
                            st.error(f"Failed to submit. Webhook returned non-JSON response. Ensure your Apps Script is deployed to 'Anyone'.")
                            with st.expander("Show raw response"):
                                st.write(response.text)
                    else:
                        st.error(f"Failed to submit. Server returned status code: {response.status_code}")
                except Exception as e:
                    st.error(f"Failed to submit: {e}")

if st.session_state.get("needs_save", False):
    val_str = json.dumps(st.session_state.itp_data).replace('\\', '\\\\').replace("'", "\\'").replace('"', '\\"')
    js = f"(function(){{ try {{ var ls = null; try {{ ls = window.parent.localStorage; }} catch(e) {{ ls = window.localStorage; }} ls.setItem('itp_data', '{val_str}'); return 'ok'; }} catch(e) {{ return 'error'; }} }})();"
    st_javascript(js)
    st.session_state.needs_save = False
