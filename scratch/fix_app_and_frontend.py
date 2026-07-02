import re

with open("Frontend.py", "r") as f:
    frontend_code = f.read()

# Replace reconstruct_string_html and reconstruct_string in Frontend.py
start_idx = frontend_code.find("def reconstruct_string_html(node: Node, depth_ref: list) -> str:")
if start_idx == -1:
    print("reconstruct_string_html not found")
    exit(1)

# We will replace from start_idx to the end of reconstruct_string (before parse_term)
end_idx = frontend_code.find("def parse_term(input_str: str, env: Environment) -> Node:")

new_reconstruct = """def reconstruct_string_html(node: Node, depth_ref: list, target_name: str = None, target_type: str = None, occ_map: dict = None) -> str:
    if occ_map is None: occ_map = {}
    colors = ["#008B8B", "#FF00FF", "#FFA500", "#00FF00", "#6495ED", "#FF4500"]
    res = ""
    
    for f in node.prefix_formatting:
        if isinstance(f, Bracket):
            if f.name in "([{":
                color = colors[depth_ref[0] % len(colors)]
                res += f'<span style="color: {color}">{f.name}</span>'
                depth_ref[0] += 1
            elif f.name in ")]}":
                depth_ref[0] = max(0, depth_ref[0] - 1)
                color = colors[depth_ref[0] % len(colors)]
                res += f'<span style="color: {color}">{f.name}</span>'
        else:
            res += f.name
            
    tooltip = ""
    if isinstance(node, Variable): tooltip = "Variable"
    elif isinstance(node, DummyVariable): tooltip = "Dummy Variable"
    elif isinstance(node, PropositionalVariable): tooltip = "Propositional Variable"
    elif isinstance(node, MetaVariable): tooltip = "Meta Variable"
    elif isinstance(node, Quantifier): tooltip = "Quantifier"
    elif isinstance(node, (Iota, Epsilon)): tooltip = "Choice Operator"
    elif isinstance(node, Connective): tooltip = "Connective"
    elif isinstance(node, SetBuilder): tooltip = "Set Builder"
    elif isinstance(node, Function):
        type_str = node.func_type.value.replace("_", "-").title()
        tooltip = f"{type_str} Function"
    elif isinstance(node, Relation):
        type_str = node.rel_type.value.replace("_", "-").title()
        tooltip = f"{type_str} Relation"

    def get_occ(sym: str) -> int:
        if sym not in occ_map:
            occ_map[sym] = 1
        else:
            occ_map[sym] += 1
        return occ_map[sym]

    def wrap(text: str, is_symbol: bool = False, sym_name: str = None) -> str:
        classes = "itp-tooltip" if tooltip else ""
        if is_symbol and target_name:
            classes += " interactive-symbol"
            s = sym_name if sym_name else text
            occ = get_occ(s)
            t_attr = f' data-tooltip="{tooltip}"' if tooltip else ""
            return f'<span class="{classes.strip()}" data-target="{target_name}" data-symbol="{s}" data-occ="{occ}"{t_attr}>{text}</span>'
        else:
            if tooltip:
                return f'<span class="{classes.strip()}" data-tooltip="{tooltip}">{text}</span>'
            return text

    if isinstance(node, (Variable, DummyVariable, PropositionalVariable, MetaVariable)):
        res += wrap(node.name, True)
    elif isinstance(node, (Quantifier, Iota, Epsilon)):
        op_str = wrap(node.name, True)
        res += op_str
        res += reconstruct_string_html(node.variable, depth_ref, target_name, target_type, occ_map)
        res += " "
        res += reconstruct_string_html(node.formula, depth_ref, target_name, target_type, occ_map)
    elif isinstance(node, SetBuilder):
        op_str = wrap(node.name, True)
        res += op_str
        res += reconstruct_string_html(node.variable, depth_ref, target_name, target_type, occ_map)
        res += wrap("∈", True)
        res += reconstruct_string_html(node.base_set, depth_ref, target_name, target_type, occ_map)
        res += wrap("|")
        res += reconstruct_string_html(node.formula, depth_ref, target_name, target_type, occ_map)
    elif isinstance(node, (Function, Relation, Connective)):
        if node.arity == 1:
            if node.name in ["¬", "∀", "∃"]:
                op_str = wrap(node.name, True)
                res += op_str
                if isinstance(node.arguments[0], Relation) and node.arguments[0].arity == 2:
                    color = colors[depth_ref[0] % len(colors)]
                    res += f'<span style="color: {color}">(</span>'
                    depth_ref[0] += 1
                    res += reconstruct_string_html(node.arguments[0], depth_ref, target_name, target_type, occ_map)
                    depth_ref[0] = max(0, depth_ref[0] - 1)
                    color = colors[depth_ref[0] % len(colors)]
                    res += f'<span style="color: {color}">)</span>'
                else:
                    res += reconstruct_string_html(node.arguments[0], depth_ref, target_name, target_type, occ_map)
            else:
                op_str = wrap(node.name, True)
                res += op_str
                color = colors[depth_ref[0] % len(colors)]
                res += f'<span style="color: {color}">(</span>'
                depth_ref[0] += 1
                res += reconstruct_string_html(node.arguments[0], depth_ref, target_name, target_type, occ_map)
                depth_ref[0] = max(0, depth_ref[0] - 1)
                color = colors[depth_ref[0] % len(colors)]
                res += f'<span style="color: {color}">)</span>'
        elif node.arity == 2:
            op_str = wrap(node.name, True)
            left_str = reconstruct_string_html(node.arguments[0], depth_ref, target_name, target_type, occ_map)
            right_str = reconstruct_string_html(node.arguments[1], depth_ref, target_name, target_type, occ_map)
            res += left_str
            res += f" {op_str} "
            res += right_str
        elif node.arity > 2:
            op_str = wrap(node.name, True)
            res += op_str
            color = colors[depth_ref[0] % len(colors)]
            res += f'<span style="color: {color}">(</span>'
            depth_ref[0] += 1
            
            args_res = [reconstruct_string_html(arg, depth_ref, target_name, target_type, occ_map) for arg in node.arguments]
            res += ", ".join(args_res)
            
            depth_ref[0] = max(0, depth_ref[0] - 1)
            color = colors[depth_ref[0] % len(colors)]
            res += f'<span style="color: {color}">)</span>'
        elif node.arity == 0:
            res += wrap(node.name, True)
            
    for f in node.postfix_formatting:
        if isinstance(f, Bracket):
            if f.name in "([{":
                color = colors[depth_ref[0] % len(colors)]
                res += f'<span style="color: {color}">{f.name}</span>'
                depth_ref[0] += 1
            elif f.name in ")]}":
                depth_ref[0] = max(0, depth_ref[0] - 1)
                color = colors[depth_ref[0] % len(colors)]
                res += f'<span style="color: {color}">{f.name}</span>'
        else:
            res += f.name
            
    return res

def reconstruct_string(node: Node, color_mode: str = "ansi", target_name: str = None, target_type: str = None) -> str:
    \"\"\"Reconstructs the AST and applies depth-based colorization or HTML tooltips.\"\"\"
    if color_mode == "html":
        return reconstruct_string_html(node, [0], target_name=target_name, target_type=target_type)
    raw = reconstruct_string_raw(node)
    if color_mode == "none":
        return raw
    return colorize_formula(raw, mode=color_mode)

"""

frontend_code = frontend_code[:start_idx] + new_reconstruct + frontend_code[end_idx:]
with open("Frontend.py", "w") as f:
    f.write(frontend_code)
print("Updated Frontend.py")

with open("app.py", "r") as f:
    app_code = f.read()

# Fix app.py JS logic for interactive-symbol and fold all
app_code = app_code.replace("""                        if (targetElement.classList.contains('interactive-symbol')) {
                            cmds = ['st', 'sb', 'sf', 'sp', 'sa'];
                        } else {""", """                        if (targetElement.classList.contains('interactive-symbol')) {
                            let isLogical = ['∀', '∃', '∃!', 'ε', 'ι', '∨', '∧', '¬', '⇒', '⇔', '=', '∈'].includes(symbol);
                            cmds = ['st', 'sb', 'sf', 'sp', 'sa'];
                            if (isLogical) {
                                cmds = []; // No substitution for logical symbols
                            }
                            // fold command for quantifiers, choice ops, or user-defined symbols
                            if (['∀', '∃', '∃!', 'ε', 'ι'].includes(symbol) || !isLogical) {
                                cmds.push('fold');
                            }
                        } else {""")

# Add 'fold all' to interactive-name
app_code = app_code.replace("""                            if (obj_type === 'unproven') {
                                cmds = ["mission", "contra", "apply", "auto", "search", "backward_search", "advanced_search"];""", """                            if (obj_type === 'unproven') {
                                cmds = ["mission", "contra", "apply", "auto", "search", "backward_search", "advanced_search", "fold all"];""")

app_code = app_code.replace("""                            } else if (obj_type === 'goal') {
                                cmds = ["apply", "apply2", "apply3", "auto", "search", "backward_search", "advanced_search"];""", """                            } else if (obj_type === 'goal') {
                                cmds = ["apply", "apply2", "apply3", "auto", "search", "backward_search", "advanced_search", "fold all"];""")

app_code = app_code.replace("""                            } else if (obj_type === 'proven') {
                                cmds = ["dt"];
                            } else {
                                cmds = ['simp_l_eq', 'simp_r_eq', 'simp_l_bi', 'simp_r_bi', 'apply', 'apply2', 'apply3', 'intro', 'intro2', 'contra', 'mission', 'auto', 'search', 'backward_search', 'advanced_search', 'dt', 'and', 'left', 'right', 'imply', 'neg-'];
                            }""", """                            } else if (obj_type === 'proven') {
                                cmds = ["dt", "fold all"];
                            } else {
                                cmds = ['simp_l_eq', 'simp_r_eq', 'simp_l_bi', 'simp_r_bi', 'apply', 'apply2', 'apply3', 'intro', 'intro2', 'contra', 'mission', 'auto', 'search', 'backward_search', 'advanced_search', 'dt', 'and', 'left', 'right', 'imply', 'neg-', 'fold all'];
                            }""")

# Handle fold command in payload parsing
app_code = app_code.replace("""                    elif selected_cmd in ["st", "sb", "sf", "sp"]:
                        parts = [selected_cmd, symbol]
                        if len(args) > 0: parts.append(args[0])
                        parts.extend([str(occ), target])""", """                    elif selected_cmd in ["st", "sb", "sf", "sp"]:
                        parts = [selected_cmd, symbol]
                        if len(args) > 0: parts.append(args[0])
                        parts.extend([str(occ), target])
                    elif selected_cmd == "fold all":
                        parts = ["fold", "all", target]
                    elif selected_cmd == "fold":
                        parts = ["fold", symbol, str(occ), target]""")

with open("app.py", "w") as f:
    f.write(app_code)
print("Updated app.py")
