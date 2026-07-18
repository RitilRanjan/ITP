import re

with open('backend/game_creator_ui.py', 'r') as f:
    content = f.read()

content = content.replace('"start_env": None,', '"start_env_commands": None,')

pattern = r"""start_env_val = json\.dumps\(data\.get\("start_env"\)\) if data\.get\("start_env"\) else ""
\s*start_env_input = st\.text_area\("Start Env \(JSON\)", value=start_env_val\)"""

replacement = """start_env_val = "\\n".join(data.get("start_env_commands")) if data.get("start_env_commands") else ""
        start_env_input = st.text_area("Start Env Commands (One command per line)", value=start_env_val)"""
content = re.sub(pattern, replacement, content)

pattern2 = r"""try:
\s*data\["start_env"\] = json\.loads\(start_env_input\) if start_env_input\.strip\(\) else None
\s*except:
\s*data\["start_env"\] = None"""

replacement2 = """data["start_env_commands"] = [cmd.strip() for cmd in start_env_input.split("\\n") if cmd.strip()] if start_env_input.strip() else None"""
content = re.sub(pattern2, replacement2, content)

with open('backend/game_creator_ui.py', 'w') as f:
    f.write(content)
