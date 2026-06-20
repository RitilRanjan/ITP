import streamlit as st
import io
import contextlib
import re

# Set page config for wider layout
st.set_page_config(page_title="Interactive Theorem Prover", layout="wide")

from Environment import Environment
from CommandHandlers.CommandRegistry import registry
from Frontend import reconstruct_string
from AST import Variable, PropositionalVariable, DummyVariable, Function, Relation
from main import get_default_env

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

def ansi_to_html(text: str) -> str:
    """Converts ANSI color codes to HTML spans."""
    html = text.replace('\n', '<br>')
    
    ansi_regex = re.compile(r'\033\[(\d+)m')
    
    color_map = {
        '31': 'color: #FF4500', # Red
        '32': 'color: #00FF00', # Green
        '33': 'color: #FFA500', # Yellow
        '34': 'color: #6495ED', # Blue
        '35': 'color: #FF00FF', # Magenta
        '36': 'color: #008B8B', # DarkCyan (was Cyan)
        '1': 'font-weight: bold',
    }
    
    def replacer(match):
        code = match.group(1)
        if code == '0':
            return '</span>'
        if code in color_map:
            return f'<span style="{color_map[code]}">'
        return ''

    html = ansi_regex.sub(replacer, html)
    return html

def init_session():
    if "env_chain" not in st.session_state:
        st.session_state.env_chain = [get_default_env()]
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
init_session()

st.title("Interactive Theorem Prover")
st.markdown("Host for mathematically rigorous First-Order Logic and Set Theory proofs.")

# Display the environment
current_env = st.session_state.env_chain[-1]
ground_env = st.session_state.env_chain[0]

col1, col2 = st.columns([1, 1])

with col1:
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

with col2:
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

# Chat history
st.subheader("Console")

# Create a container for the chat history
chat_container = st.container()
with chat_container:
    for msg in st.session_state.chat_history:
        st.markdown(msg, unsafe_allow_html=True)

# Command Input
prompt_str = f"ITP {len(st.session_state.env_chain)-1}> "
command = st.chat_input("Enter command here (e.g. cv x, cf f1 x=x, apply E1)")

if command:
    parts = command.strip().split(maxsplit=1)
    cmd = parts[0]
    args_str = parts[1] if len(parts) > 1 else ""
    
    # Log the command entered
    st.session_state.chat_history.append(f'<strong>{prompt_str}{command}</strong>')
    
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
