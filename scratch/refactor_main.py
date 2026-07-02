import re

with open("main.py", "r") as f:
    content = f.read()

# Remove the old functions and SwapRef class
# It starts at "def snapshot_env_keys" and ends just before "def main():"
start_str = "def snapshot_env_keys(env) -> dict:"
end_str = "def main():"
start_idx = content.find(start_str)
end_idx = content.find(end_str)

if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + "from RecycleBinManager import RecycleBinManager, SwapRef, snapshot_env_keys, compute_env_delta\n\n" + content[end_idx:]

# Inside main(), replace the recycle bin logic
main_start = "    import atexit"
main_end = "    while True:"
idx1 = content.find(main_start)
idx2 = content.find(main_end)
if idx1 != -1 and idx2 != -1:
    setup_code = """    rb = RecycleBinManager(swap_dir="swap_files_cli")
    
    import atexit
    atexit.register(proof_logger.close)
    atexit.register(rb.cleanup)
    rb.cleanup()
    
    command_queue = []
"""
    content = content[:idx1] + setup_code + content[idx2:]

# Now the big loop: replace all the recycle bin commands and dispatch wrapping
loop_content_start = "        if cmd == \\"undo\\":"
loop_content_end = "            # Update mission state if mission was resolved"
idx_loop1 = content.find(loop_content_start)
idx_loop2 = content.find(loop_content_end)

if idx_loop1 != -1 and idx_loop2 != -1:
    new_loop_code = """        if cmd == "undo":
            success, env, msg = rb.undo(env)
            print(msg)
            continue
            
        if cmd == "redo":
            success, env, msg = rb.redo(env)
            print(msg)
            continue
            
        if cmd == "rb_stat":
            print(rb.stat())
            continue
            
        if cmd == "rb_empty":
            sub_args = args_str.split()
            target = sub_args[0] if len(sub_args) > 0 else "all"
            try:
                count = int(sub_args[1]) if len(sub_args) > 1 else None
            except ValueError:
                print("Error: Count must be an integer.")
                continue
            print(rb.empty(target, count))
            continue
            
        if cmd == "rb_swap":
            sub_args = args_str.split()
            if len(sub_args) < 2:
                print("Error: Usage: rb_swap <perm|temp> <count>")
                continue
            target = sub_args[0]
            try:
                count = int(sub_args[1])
            except ValueError:
                print("Error: Count must be an integer.")
                continue
            print(rb.swap(target, count))
            continue
            
        # If a normal command is executed while pointer is active, truncate history
        rb.truncate_history_if_needed(cmd)
            
        old_env_ref = env
        mission_entered = False
        mission_resolved = False
        
        # Dispatch the command via registry
        from CommandHandlers.CommandRegistry import registry
        
        # Check if the command is registered
        if registry.is_registered(cmd):
            inputs_collected = []
            kwargs = {
                "command_queue": command_queue,
                "inputs_collected": inputs_collected
            }
            if cmd in {"load", "load_h"}:
                kwargs["get_default_env"] = get_default_env
            if cmd in {"save_h", "load_h"}:
                kwargs["history_commands"] = rb.history_commands
                
            new_env = registry.dispatch(cmd, env, args_str, **kwargs)
            if new_env is not None and new_env is not env:
                # Mission entered or exited?
                if new_env.parent is env:
                    mission_entered = True
                elif env.parent is new_env:
                    mission_resolved = True
                env = new_env
        else:
            print(f"Unknown command '{cmd}'.")
            
        if has_error:
            continue
            
        if cmd in {"save", "save_h", "load", "load_h", "help", "guide", "rb_stat", "rb_empty", "rb_swap"}:
            continue
            
        rb.record_command(line, old_env_ref, env, mission_entered, mission_resolved)
        
"""
    content = content[:idx_loop1] + new_loop_code + content[idx_loop2:]

# Next, we must remove the remaining "Update mission state if mission was resolved" block and the old record_command block which is now handled by rb.record_command!
# The end of the while loop is around line 527.
end_while_str = "                    permanent_recycle_bin.append({\n                        \"removed_objects\": removed_objects\n                    })\n"
idx_end_while = content.find(end_while_str)
if idx_end_while != -1:
    # Delete everything from new_loop_code end to end_while_str
    # Wait, the `idx_loop2` is exactly at "            # Update mission state if mission was resolved"
    # We should just delete from idx_loop2 up to idx_end_while + len(end_while_str).
    # But wait, there might be other code that we need? No, the rest of the loop was just calculating the delta and pushing to bins!
    content = content[:idx_loop2] + content[idx_end_while + len(end_while_str):]


with open("main.py", "w") as f:
    f.write(content)
