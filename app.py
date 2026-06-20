import streamlit as st
import io
import contextlib
import re
import os
import json

# Set page config for wider layout
st.set_page_config(page_title="Interactive Theorem Prover", layout="wide")

from Environment import Environment
from CommandHandlers.CommandRegistry import registry
from Frontend import reconstruct_string
from AST import Variable, PropositionalVariable, DummyVariable, Function, Relation
from main import get_default_env
from ProofLogger import proof_logger
from StorageManager import save_environment_state, load_environment_state
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
    proof_logger.open(os.path.join(p_dir, "proofs.html"))

# --- SESSION INITIALIZATION ---
def init_session():
    if "active_program" not in st.session_state:
        st.session_state.active_program = None
    if "env_chain" not in st.session_state:
        st.session_state.env_chain = [get_default_env()]
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "command_history" not in st.session_state:
        st.session_state.command_history = []
        
init_session()

# --- MAIN UI ---
st.title("Interactive Theorem Prover")

tab_home, tab_programs, tab_help, tab_about, tab_contact = st.tabs([
    "🏠 Home", "💻 Programs", "❓ Help", "ℹ️ About", "📧 Contact Us"
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
    st.markdown("1. Head over to the **Programs** tab.")
    st.markdown("2. Click **Create New Program** to establish a fresh workspace.")
    st.markdown("3. Open the **Help** tab if you need a quick reference to the command syntax!")

with tab_programs:
    if st.session_state.active_program is None:
        st.subheader("📁 Saved Programs")
        
        programs = [d for d in os.listdir(PROGRAMS_DIR) if os.path.isdir(os.path.join(PROGRAMS_DIR, d))]
        if not programs:
            st.write("No programs created yet.")
        else:
            for p in programs:
                col_name, col_btn = st.columns([4, 1])
                with col_name:
                    st.write(f"**{p}**")
                with col_btn:
                    if st.button("Load", key=f"load_{p}"):
                        load_program(p)
                        st.rerun()
                        
        st.divider()
        st.subheader("✨ Create New Program")
        new_prog_name = st.text_input("Program Name")
        if st.button("Create"):
            if new_prog_name:
                if new_prog_name in programs:
                    st.error("Program already exists!")
                else:
                    st.session_state.active_program = new_prog_name
                    st.session_state.env_chain = [get_default_env()]
                    st.session_state.chat_history = []
                    st.session_state.command_history = []
                    
                    p_dir = get_program_dir(new_prog_name)
                    os.makedirs(p_dir, exist_ok=True)
                    proof_logger.open(os.path.join(p_dir, "proofs.html"))
                    save_program(new_prog_name)
                    st.rerun()
            else:
                st.error("Please enter a valid name.")
    else:
        # PROVER INTERFACE
        col_hdr1, col_hdr2 = st.columns([4, 1])
        with col_hdr1:
            st.subheader(f"Active Program: {st.session_state.active_program}")
        with col_hdr2:
            if st.button("Save & Exit", use_container_width=True):
                save_program(st.session_state.active_program)
                proof_logger.close()
                st.session_state.active_program = None
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
                p_dir = get_program_dir(st.session_state.active_program)
                proofs_path = os.path.join(p_dir, "proofs.html")
                try:
                    with open(proofs_path, "r") as f:
                        proof_html = f.read()
                    st.components.v1.html(proof_html, height=400, scrolling=True)
                    
                    with open(proofs_path, "rb") as f:
                        st.download_button(
                            label="Export proofs.html", 
                            data=f, 
                            file_name=f"{st.session_state.active_program}_proofs.html", 
                            mime="text/html"
                        )
                except FileNotFoundError:
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
                            st.markdown(f"**Goal**: " + reconstruct_string(env.target_goal, color_mode="html"), unsafe_allow_html=True)
                            
                        st.markdown("**Terms**")
                        for name, term in env.local_terms.items():
                            if isinstance(term, Function) and name == term.name:
                                st.markdown(f'<span style="color: #6495ED">{name}</span> : {term.arity}', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<span style="color: #6495ED">{name}</span> = ' + reconstruct_string(term, color_mode="html"), unsafe_allow_html=True)
                        
                        st.markdown("**Formulae**")
                        for name, formula in env.local_formulae.items():
                            if isinstance(formula, Relation) and name == formula.name:
                                st.markdown(f'<span style="color: #6495ED">{name}</span> : {formula.arity}', unsafe_allow_html=True)
                            else:
                                prefix = "<strong>[Proven]</strong> " if name in env.local_theorems else ""
                                st.markdown(f'{prefix}<span style="color: #6495ED">{name}</span> = ' + reconstruct_string(formula, color_mode="html"), unsafe_allow_html=True)

        st.divider()
        st.subheader("Console")
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_history:
                st.markdown(msg, unsafe_allow_html=True)

        prompt_str = f"ITP {len(st.session_state.env_chain)-1}> "
        
        # Real-time Autocomplete UI
        if st_keyup is not None:
            # We need a clear button or form to submit, but st_keyup doesn't natively submit on enter unless we use a button
            # We'll use two columns: input and submit button
            st.markdown("### Command Input")
            
            # Use session state to hold the partial input so suggestions can update it
            if "current_cmd" not in st.session_state:
                st.session_state.current_cmd = ""
                
            # If the user clicks a suggestion, it updates st.session_state.current_cmd
            
            col_input, col_btn = st.columns([5, 1])
            with col_input:
                partial_command = st_keyup("Type your command:", value=st.session_state.current_cmd, key="live_input", debounce=100)
            with col_btn:
                # Add some vertical margin so button aligns with input
                st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                submit_clicked = st.button("Run Command", use_container_width=True)
                
            # Compute and render suggestions
            if partial_command:
                suggestions = autocomplete_engine.get_suggestions(partial_command, current_env)
                
                if suggestions == ["ERROR: INVALID REPL COMMAND"]:
                    st.markdown("<span style='color:red;'>❌ Invalid REPL Command</span>", unsafe_allow_html=True)
                elif suggestions:
                    st.markdown("**Suggestions:**")
                    # Render chips horizontally
                    cols = st.columns(min(len(suggestions), 8))
                    for idx, sug in enumerate(suggestions[:8]):
                        with cols[idx]:
                            # If a user clicks a suggestion, we append it to the partial command
                            if st.button(sug, key=f"sug_{sug}_{idx}", use_container_width=True):
                                # Logic to append suggestion properly
                                tokens = partial_command.lstrip().split(" ")
                                tokens[-1] = sug
                                new_cmd = " ".join(tokens) + " "
                                st.session_state.current_cmd = new_cmd
                                st.rerun()
                else:
                    st.write("*(No suggestions)*")
            else:
                submit_clicked = False
                
            command = partial_command if submit_clicked else None
            
            # Clear input after run
            if submit_clicked:
                st.session_state.current_cmd = ""
        else:
            # Fallback if streamlit-keyup is not installed
            command = st.chat_input("Enter command here (install streamlit-keyup for autocomplete)")

        if command:
            parts = command.strip().split(maxsplit=1)
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
                elif registry.is_registered(cmd):
                    try:
                        new_env = registry.dispatch(cmd, current_env, args_str, get_default_env=get_default_env)
                        if new_env is not None and new_env is not current_env:
                            st.session_state.env_chain.append(new_env)
                    except Exception as e:
                        print(f"Error: {e}")
                elif cmd == "clear":
                    st.session_state.chat_history.clear()
                else:
                    print(f"Unknown command '{cmd}'.")
                    
            output = f.getvalue()
            if output:
                st.session_state.chat_history.append(ansi_to_html(output))
                
            st.rerun()

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
    
    with st.expander("Provide Advice"):
        advice_text = st.text_area("Your Advice / Suggestions:", key="advice_text")
        if st.button("Submit Advice"):
            if advice_text.strip():
                try:
                    import datetime
                    with open("complaints.json", "a") as f:
                        entry = {"type": "advice", "timestamp": str(datetime.datetime.now()), "text": advice_text}
                        f.write(json.dumps(entry) + "\n")
                    st.success("Advice submitted successfully! Thank you.")
                except Exception as e:
                    st.error(f"Failed to submit: {e}")
            else:
                st.warning("Please enter some text before submitting.")

    with st.expander("Submit a Complaint"):
        complaint_text = st.text_area("Your Complaint / Bug Report:", key="complaint_text")
        if st.button("Submit Complaint"):
            if complaint_text.strip():
                try:
                    import datetime
                    with open("complaints.json", "a") as f:
                        entry = {"type": "complaint", "timestamp": str(datetime.datetime.now()), "text": complaint_text}
                        f.write(json.dumps(entry) + "\n")
                    st.success("Complaint submitted successfully! Thank you.")
                except Exception as e:
                    st.error(f"Failed to submit: {e}")
            else:
                st.warning("Please enter some text before submitting.")
