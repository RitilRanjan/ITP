import re
import ast

with open("backend/CommandHandlers/state_handlers.py", "r") as f:
    content = f.read()

def get_func_bounds(code, func_name):
    tree = ast.parse(code)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == func_name:
            return node.lineno - 1, node.end_lineno
    return -1, -1

s_start, s_end = get_func_bounds(content, 'handle_save')
l_start, l_end = get_func_bounds(content, 'handle_load')

new_handle_save = """@registry.register("save", category="Environment Tools", help_text="Save current environment state to disk")
def handle_save(env: Environment, args_str: str, command_queue: list = None, inputs_collected: list = None) -> None:
    try:
        from backend.CommandHandlers.utils import get_user_input
        name = get_user_input("Enter filename: ", command_queue, inputs_collected)
    except (KeyboardInterrupt, EOFError):
        print("\\nOperation cancelled.")
        return
    if not name:
        print("Error: Filename cannot be empty.")
        return
    filepath = os.path.join("save_files", name)
    if not filepath.endswith(".json"):
        filepath += ".json"
    if os.path.exists(filepath):
        print("Error: A save file with that name already exists.")
        return
    try:
        content = serialize_environment_state(env)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Saved state to '{filepath}'")
    except Exception as e:
        print(f"Error: {e}")
"""

new_handle_load = """@registry.register("load", category="Environment Tools", help_text="Load environment state from disk")
def handle_load(env: Environment, args_str: str, get_default_env, command_queue: list = None, inputs_collected: list = None) -> Any:
    try:
        from backend.CommandHandlers.utils import get_user_input
        name = get_user_input("Enter filename to load: ", command_queue, inputs_collected)
    except (KeyboardInterrupt, EOFError):
        print("\\nOperation cancelled.")
        return None
    if not name:
        print("Error: Filename cannot be empty.")
        return None
    filepath = os.path.join("save_files", name)
    if not filepath.endswith(".json") and not os.path.exists(filepath):
        filepath += ".json"
    if not os.path.exists(filepath):
        print(f"Error: Save file '{filepath}' not found.")
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        new_env = deserialize_environment_state(content, get_default_env)
        print(f"Loaded state from '{filepath}'")
        return new_env
    except Exception as e:
        print(f"Error: {e}")
        return None
"""

new_handle_show_s = """
@registry.register("show_s", category="Environment Tools", help_text="List and view saved environment states")
def handle_show_s(env: Environment, args_str: str, get_default_env, command_queue: list = None, inputs_collected: list = None) -> None:
    import datetime
    save_dir = "save_files"
    if not os.path.exists(save_dir):
        print("No save_files directory found.")
        return
    files = [f for f in os.listdir(save_dir) if f.endswith(".json")]
    if not files:
        print("No saved states found.")
        return
        
    print("Saved environment states:")
    for f in files:
        filepath = os.path.join(save_dir, f)
        mtime = os.path.getmtime(filepath)
        dt = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        print(f" - {f} (Last modified: {dt})")
        
    try:
        from backend.CommandHandlers.utils import get_user_input
        name = get_user_input("Enter filename to view: ", command_queue, inputs_collected)
    except (KeyboardInterrupt, EOFError):
        print("\\nOperation cancelled.")
        return
        
    if not name:
        print("Error: Filename cannot be empty.")
        return
        
    filepath = os.path.join(save_dir, name)
    if not filepath.endswith(".json") and not os.path.exists(filepath):
        filepath += ".json"
        
    if not os.path.exists(filepath):
        print("file not found")
        return
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        from backend.StorageManager import deserialize_environment_state
        temp_env = deserialize_environment_state(content, get_default_env)
        if temp_env:
            temp_env.show()
        else:
            print("Failed to parse environment state.")
    except Exception as e:
        print(f"Error reading file: {e}")
"""

# Now we need to remove old decorators too.
# The AST bounds give the def line to the end. The decorator is usually just above the def line.
# For simplicity, we just rebuild the file line by line, replacing the blocks.

lines = content.splitlines()

# process backwards so indices don't shift
if l_start != -1:
    lines = lines[:l_start-1] + [new_handle_load] + lines[l_end:]
if s_start != -1:
    lines = lines[:s_start-1] + [new_handle_save] + lines[s_end:]

lines.append(new_handle_show_s)

with open("backend/CommandHandlers/state_handlers.py", "w") as f:
    f.write('\\n'.join(lines))

print('Done')
