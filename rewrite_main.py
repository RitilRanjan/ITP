import re

def rewrite():
    with open('/Users/ritilranjan/ITP/main.py', 'r') as f:
        content = f.read()

    lines = content.split('\n')
    
    start_idx = -1
    for i, line in enumerate(lines):
        if 'if cmd == "exit":' in line:
            start_idx = i
            break
            
    end_idx = -1
    for i, line in enumerate(lines):
        if 'else:' in line and 'Unknown command' in lines[i+1]:
            end_idx = i
            break
            
    if start_idx == -1 or end_idx == -1:
        print("Could not find bounds")
        return

    imports = """from CommandHandlers.mission_handlers import handle_mission, handle_contra
from CommandHandlers.logic_handlers import (
    handle_left_right, handle_and, handle_and2, handle_imply, handle_intro, handle_intro2,
    handle_apply, handle_apply2, handle_apply3, handle_ua, handle_ir
)
from CommandHandlers.env_handlers import (
    handle_cv, handle_cV, handle_ct, handle_cf, handle_cp,
    handle_st, handle_sf, handle_sb, handle_sa, handle_sp
)
from CommandHandlers.definition_handlers import (
    handle_def_f, handle_def_r, handle_iota, handle_epsilon
)
from CommandHandlers.state_handlers import (
    handle_show, handle_help, handle_save, handle_load, handle_save_h, handle_load_h,
    handle_auto, handle_search, handle_backward_search, handle_advanced_search, handle_dt
)
from CommandHandlers.transformation_handlers import (
    handle_fold, handle_simp, handle_neg
)
"""

    repl_block = """        if cmd == "exit":
            if env.parent is not None:
                goal_name = env.goal_formula_name
                env = env.parent
                print(f"Terminated child environment for goal '{goal_name}' without proving it. Returned to parent environment.")
                continue
            else:
                print("Goodbye!")
                sys.exit(0)
            
        elif cmd == "show":
            handle_show(env, args_str)
            
        elif cmd in {"help", "guide"}:
            handle_help(env, args_str)
            
        elif cmd == "save":
            handle_save(env, args_str)
            
        elif cmd == "load":
            new_env = handle_load(env, args_str, get_default_env)
            if new_env: env = new_env
            
        elif cmd == "save_h":
            handle_save_h(env, args_str, history_commands)
            
        elif cmd == "load_h":
            handle_load_h(env, args_str, history_commands, command_queue)
            
        elif cmd == "auto":
            handle_auto(env, args_str)
            
        elif cmd == "search":
            handle_search(env, args_str)
            
        elif cmd == "backward_search":
            handle_backward_search(env, args_str)
            
        elif cmd == "advanced_search":
            handle_advanced_search(env, args_str)
            
        elif cmd == "mission":
            new_env = handle_mission(env, args_str)
            if new_env: env = new_env
            
        elif cmd == "contra":
            new_env = handle_contra(env, args_str, validate_new_name)
            if new_env: env = new_env
            
        elif cmd in {"left", "right"}:
            handle_left_right(env, args_str, cmd, validate_new_name)
            
        elif cmd == "and":
            env = handle_and(env, args_str, validate_new_name)
            
        elif cmd == "and2":
            handle_and2(env, args_str, validate_new_name)
            
        elif cmd == "imply":
            handle_imply(env, args_str, validate_new_name)
            
        elif cmd == "intro":
            handle_intro(env, args_str, validate_new_name)
            
        elif cmd == "intro2":
            handle_intro2(env, args_str, validate_new_name)
            
        elif cmd == "apply":
            handle_apply(env, args_str)
            
        elif cmd == "apply2":
            handle_apply2(env, args_str, validate_new_name)
            
        elif cmd == "apply3":
            handle_apply3(env, args_str, validate_new_name)
            
        elif cmd == "ua":
            handle_ua(env, args_str)
            
        elif cmd == "ir":
            handle_ir(env, args_str)
            
        elif cmd == "dt":
            handle_dt(env, args_str)
            
        elif cmd in {"cv", "cV"}:
            handle_cv(env, args_str, cmd, validate_new_name)
            
        elif cmd in {"ct", "cf", "cp"}:
            handle_ct(env, args_str, cmd, validate_new_name)
            
        elif cmd in {"st", "sf", "sb", "sa", "sp"}:
            handle_st(env, args_str, cmd, validate_new_name)
            
        elif cmd == "def_f":
            handle_def_f(env, args_str, validate_new_name)
            
        elif cmd == "def_r":
            handle_def_r(env, args_str, validate_new_name)
            
        elif cmd == "iota":
            handle_iota(env, args_str, validate_new_name)
            
        elif cmd == "epsilon":
            handle_epsilon(env, args_str, validate_new_name)
            
        elif cmd == "fold":
            handle_fold(env, args_str, validate_new_name, get_target_resolutions, handle_variable_capture_interactive)
            
        elif cmd in {"simp_l_eq", "simp_r_eq", "simp_l_bi", "simp_r_bi"}:
            handle_simp(env, args_str, cmd, validate_new_name, get_target_resolutions)
            
        elif cmd in {"neg-", "neg+"}:
            handle_neg(env, args_str, cmd, validate_new_name)
"""
    
    new_lines = []
    # insert imports at the top
    for line in lines[:start_idx]:
        new_lines.append(line)
        
    new_lines.insert(3, imports)
    
    new_lines.append(repl_block)
    
    for line in lines[end_idx:]:
        new_lines.append(line)
        
    with open('/Users/ritilranjan/ITP/main_new.py', 'w') as f:
        f.write('\n'.join(new_lines))

if __name__ == "__main__":
    rewrite()
