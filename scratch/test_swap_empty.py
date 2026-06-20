import sys, os
sys.path.append(os.path.abspath("."))
from Environment import Environment

import main
main.cleanup_swap_files()
main.has_error = False

env = Environment()
main.history_commands = []
main.permanent_recycle_bin = []
main.temporary_recycle_bin = []
main.history_pointer = None

def simulate_cmd(cmd, env):
    main.has_error = False
    
    if main.history_pointer is not None and cmd not in {"save", "save_h", "load", "load_h", "help", "guide"}:
        main.history_commands = main.history_commands[:main.history_pointer + 1]
        main.temporary_recycle_bin.clear()
        main.history_pointer = None
        
    env_before = main.snapshot_env_keys(env)
    old_env_ref = env
    
    parts = cmd.split(maxsplit=1)
    args_str = parts[1] if len(parts) > 1 else ""
    
    from CommandHandlers.CommandRegistry import registry
    new_env = registry.dispatch(parts[0], env, args_str, get_default_env=main.get_default_env, history_commands=main.history_commands, command_queue=[])
    if new_env is not None and isinstance(new_env, Environment):
        env = new_env
        
    env_after = main.snapshot_env_keys(env)
    delta = main.compute_env_delta(env_before, env_after)
    
    removed_objects = {}
    for k, names in delta.get("removed", {}).items():
        if k == "theorems":
            removed_objects[k] = set(names)
        else:
            removed_objects[k] = {}
            dict_ref = getattr(old_env_ref, f"local_{k}", {})
            for name in names:
                if name in dict_ref:
                    removed_objects[k][name] = dict_ref[name]
    
    if removed_objects:
        delta["removed_objects"] = removed_objects
    
    closed_env = None
    if env_before["id"] != env_after["id"]:
        if getattr(env, "parent", None) and id(env.parent) == env_before["id"]:
            delta["mission_entered"] = True
        else:
            delta["mission_resolved"] = True
            closed_env = old_env_ref
            delta["closed_env"] = closed_env
    
    if removed_objects or closed_env:
        main.permanent_recycle_bin.append({
            "removed_objects": removed_objects,
            "closed_env": closed_env
        })
    
    main.history_commands.append((cmd, delta))
    return env

def simulate_undo(env):
    main.has_error = False
    if not main.history_commands: return env
    if main.history_pointer is None: main.history_pointer = len(main.history_commands) - 1
    elif main.history_pointer < 0: return env
        
    line_str, delta = main.history_commands[main.history_pointer]
    undone_added = {}
    for k, names in delta.get("added", {}).items():
        if k == "theorems":
            undone_added[k] = set()
            for name in names:
                if name in env.local_theorems:
                    env.local_theorems.remove(name)
                    undone_added[k].add(name)
        else:
            undone_added[k] = {}
            dict_ref = getattr(env, f"local_{k}")
            for name in names:
                if name in dict_ref:
                    undone_added[k][name] = dict_ref.pop(name)
                
    if delta.get("mission_entered"):
        undone_added["child_env"] = env
        env = env.parent
    elif delta.get("mission_resolved"):
        if not main.permanent_recycle_bin:
            print("Error: Memory wiped perm bin")
            return env
        perm_item = main.permanent_recycle_bin.pop()
        if isinstance(perm_item, main.SwapRef): perm_item = perm_item.load()
        env = perm_item["closed_env"]
    
    if "removed_objects" in delta:
        if not delta.get("mission_resolved"):
            if not main.permanent_recycle_bin:
                print("Error: Memory wiped perm bin")
                return env
            perm_item = main.permanent_recycle_bin.pop()
            if isinstance(perm_item, main.SwapRef): perm_item = perm_item.load()
        removed_objects = perm_item["removed_objects"]
        for k, objs in removed_objects.items():
            if k == "theorems":
                env.local_theorems.update(objs)
            else:
                dict_ref = getattr(env, f"local_{k}")
                dict_ref.update(objs)
    
    main.temporary_recycle_bin.append(undone_added)
    main.history_pointer -= 1
    print(f"Undid: {line_str}")
    return env

def simulate_redo(env):
    if not main.temporary_recycle_bin:
        print("Error: Memory wiped temp bin")
        return env
    if main.history_pointer is None or main.history_pointer == len(main.history_commands) - 1: return env
    main.history_pointer += 1
    line_str, delta = main.history_commands[main.history_pointer]
    undone_added = main.temporary_recycle_bin.pop()
    if isinstance(undone_added, main.SwapRef): undone_added = undone_added.load()
    
    for k, objs in undone_added.items():
        if k == "child_env": continue
        if k == "theorems":
            env.local_theorems.update(objs)
        else:
            dict_ref = getattr(env, f"local_{k}")
            dict_ref.update(objs)
            
    if delta.get("mission_entered"):
        env = undone_added["child_env"]
    elif delta.get("mission_resolved"):
        closed_env = env
        env = env.parent
        
    if "removed_objects" in delta or delta.get("mission_resolved"):
        perm_item = {}
        if delta.get("mission_resolved"):
            perm_item["closed_env"] = closed_env
        if "removed_objects" in delta:
            removed_objects = {}
            for k, names in delta.get("removed", {}).items():
                if k == "theorems":
                    removed_objects[k] = set()
                    for name in names:
                        if name in env.local_theorems:
                            env.local_theorems.remove(name)
                            removed_objects[k].add(name)
                else:
                    removed_objects[k] = {}
                    dict_ref = getattr(env, f"local_{k}")
                    for name in names:
                        if name in dict_ref:
                            removed_objects[k][name] = dict_ref.pop(name)
            perm_item["removed_objects"] = removed_objects
        main.permanent_recycle_bin.append(perm_item)
        
    print(f"Redid: {line_str}")
    if main.history_pointer == len(main.history_commands) - 1:
        main.history_pointer = None
    return env

env = simulate_cmd("cv x y", env)
env = simulate_cmd("cf goal x ∈ y", env)
env = simulate_cmd("mission goal", env)

print("\n--- Test empty perm 1 (partial delete) ---")
print("Perm bin size:", len(main.permanent_recycle_bin)) # should be 0 because we just entered mission, not resolved

env = simulate_cmd("apply PC1 goal", env) # this resolves the mission!
print("Perm bin size:", len(main.permanent_recycle_bin)) # should be 1
print("Executing: rb_empty perm 1")
def clear_bin(bin_list, c):
    if c is None or c >= len(bin_list):
        for item in bin_list:
            if isinstance(item, main.SwapRef): item.delete()
        bin_list.clear()
    else:
        for item in bin_list[:c]:
            if isinstance(item, main.SwapRef): item.delete()
        del bin_list[:c]
clear_bin(main.permanent_recycle_bin, 1)

print("Attempting to undo resolved mission...")
env = simulate_undo(env) # should fail due to wiped memory

print("\n--- Test SwapRef ---")
# clear history for clean test
main.history_commands.clear()
env = simulate_cmd("cv a b", env)
env = simulate_cmd("mission goal", env)
env = simulate_cmd("apply PC1 goal", env) # adds 1 to perm bin
print("Executing: rb_swap perm 1")
main.permanent_recycle_bin[0] = main.SwapRef(main.permanent_recycle_bin[0])
print("Is SwapRef?", isinstance(main.permanent_recycle_bin[0], main.SwapRef))
print("Swap files in dir:", len(os.listdir("swap_files")))

print("Attempting to undo resolved mission (should load from swap)...")
env = simulate_undo(env)
print("Swap files in dir after undo:", len(os.listdir("swap_files")))

print("Executing: rb_swap temp 1")
main.temporary_recycle_bin[0] = main.SwapRef(main.temporary_recycle_bin[0])
print("Attempting to redo...")
env = simulate_redo(env)

print("All tests completed.")
