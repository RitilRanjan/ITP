import os
import json
import re

games_dir = "/Users/ritilranjan/ITP/games"

def process_file(filepath):
    with open(filepath, 'r') as f:
        data = json.load(f)
        
    changed = False
    
    # 1. Update allowed commands
    if "allowed_commands" in data:
        cmds = data["allowed_commands"]
        new_cmds = []
        needs_ct_cf = False
        for cmd in cmds:
            if cmd in ["def_f", "def_r"]:
                needs_ct_cf = True
                changed = True
            else:
                new_cmds.append(cmd)
        if needs_ct_cf:
            if "ct" not in new_cmds: new_cmds.append("ct")
            if "cf" not in new_cmds: new_cmds.append("cf")
        data["allowed_commands"] = new_cmds

    # Helper to replace strings in lists
    def replace_in_list(lst):
        nonlocal changed
        new_lst = []
        for text in lst:
            orig_text = text
            # Basics of ITP level 19
            text = text.replace("def_f 2 f x y S x", 'ct f "f ?t1 ?t2" S ?t1')
            text = text.replace("def_f 1 add_2 x S S x", 'ct add_2 "add_2 ?t1" S S ?t1')
            text = text.replace("fold add_2", "rw add_2")
            
            # Basics of ITP level 20
            text = text.replace("def_r 2 R x y x=y", 'cf R "R ?t1 ?t2" ?t1= ?t2')
            text = text.replace("def_r 1 is_zero x x=x", 'cf is_zero "is_zero ?t1" ?t1= ?t1')
            text = text.replace("fold is_zero", "rw is_zero")
            
            # Basics of ITP level 21
            text = text.replace("def_f 1 P x εy S y = x", 'ct P "P ?t1" ε ?v1 S ?v1 = ?t1')
            text = text.replace("fold P", "rw P")
            
            # Natural Number Game level 2
            text = text.replace("def_f 1 P x ι y S y = x", 'ct P "P ?t1" ι ?v1 S ?v1 = ?t1')
            # Fold P already handled above
            
            # Natural Number Game level 3, 4, 5
            text = text.replace("def_r 2 u ≠ v ¬ u = v", 'cf neq "?t1 ≠ ?t2" ¬ ?t1 = ?t2')
            text = text.replace("fold ≠", "rw neq")
            
            # General fixes for def_f / def_r syntax explanations
            text = text.replace("def_f <arity> <name> <v1> <v2> ... <vn> <definition>", 'ct <name> "<pattern>" <definition>')
            text = text.replace("def_r <arity> <name> <v1> <v2> ... <vn> <definition>", 'cf <name> "<pattern>" <definition>')
            text = text.replace("def_f command", "ct command")
            text = text.replace("def_r command", "cf command")

            if text != orig_text:
                changed = True
            new_lst.append(text)
        return new_lst

    if "guide_hints" in data:
        data["guide_hints"] = replace_in_list(data["guide_hints"])
        
    if "solution" in data:
        data["solution"] = replace_in_list(data["solution"])

    if changed:
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write('\n')
        print(f"Updated {filepath}")

for root, _, files in os.walk(games_dir):
    for file in files:
        if file.endswith(".json"):
            process_file(os.path.join(root, file))
