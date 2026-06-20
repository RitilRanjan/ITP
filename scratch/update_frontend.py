import re

def update():
    with open('/Users/ritilranjan/ITP/Frontend.py', 'r') as f:
        content = f.read()

    replacement = """def reconstruct_string(node: Node, color_mode: str = "ansi") -> str:
    \"\"\"Reconstructs the AST and applies depth-based colorization.\"\"\"
    raw = reconstruct_string_raw(node)
    if color_mode == "none":
        return raw
    return colorize_formula(raw, mode=color_mode)

def parse_term(input_str: str, env: Environment) -> Node:
    parser = Parser(env)
    return parser.parse(input_str, "term")

def parse_fol_formula(input_str: str, env: Environment) -> Node:
    parser = Parser(env)
    return parser.parse(input_str, "fol")

def parse_prop_formula(input_str: str, env: Environment) -> Node:
    parser = Parser(env)
    return parser.parse(input_str, "prop")

def colorize_formula(text: str, mode: str = "ansi") -> str:
    \"\"\"Applies depth-based color cycling to brackets and inner contents.\"\"\"
    if mode == "none":
        return text
        
    if mode == "ansi":
        colors = [
            "\\033[96m", # Cyan
            "\\033[95m", # Magenta
            "\\033[93m", # Yellow
            "\\033[92m", # Green
            "\\033[94m", # Blue
            "\\033[91m", # Red
        ]
        reset = "\\033[0m"
        
        result = []
        depth = 0
        
        for char in text:
            if char in "([{":
                color = colors[depth % len(colors)]
                result.append(f"{color}{char}")
                depth += 1
                if depth > 0:
                    result.append(colors[depth % len(colors)])
            elif char in ")]}":
                depth = max(0, depth - 1)
                color = colors[depth % len(colors)]
                result.append(f"{color}{char}")
                if depth == 0:
                    result.append(reset)
            else:
                if len(result) == 0 or depth == 0:
                    result.append(f"{reset}{char}")
                else:
                    result.append(char)
                    
        return "".join(result) + reset
        
    elif mode == "html":
        colors = ["#00FFFF", "#FF00FF", "#FFA500", "#00FF00", "#6495ED", "#FF4500"]
        result = []
        depth = 0
        
        for char in text:
            if char in "([{":
                color = colors[depth % len(colors)]
                # Add bracket with its color
                result.append(f'<span style="color: {color}">{char}</span>')
                depth += 1
                # Content inside will have the next depth color
                next_color = colors[depth % len(colors)]
                result.append(f'<span style="color: {next_color}">')
            elif char in ")]}":
                # Close the content span
                if depth > 0:
                    result.append("</span>")
                depth = max(0, depth - 1)
                color = colors[depth % len(colors)]
                result.append(f'<span style="color: {color}">{char}</span>')
                # Reopen span for content at the outer depth, if any
                if depth > 0:
                    outer_color = colors[depth % len(colors)]
                    result.append(f'<span style="color: {outer_color}">')
            else:
                result.append(char)
                
        # Close any unclosed spans (for malformed input, though shouldn't happen)
        result.append("</span>" * depth)
        
        # We need to clean up empty spans that might have been created
        html = "".join(result)
        html = re.sub(r'<span style="color: [^>]+"></span>', '', html)
        return html
"""

    start_str = "def reconstruct_string(node: Node) -> str:"
    end_str = "def strip_ansi(text: str) -> str:"
    
    start_idx = content.find(start_str)
    end_idx = content.find(end_str)
    
    if start_idx != -1 and end_idx != -1:
        new_content = content[:start_idx] + replacement + "\n" + content[end_idx:]
        with open('/Users/ritilranjan/ITP/Frontend.py', 'w') as f:
            f.write(new_content)
    else:
        print("Could not find start/end indices")

if __name__ == "__main__":
    update()
