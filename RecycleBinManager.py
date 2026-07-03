import os
import uuid
import pickle
import shutil
from typing import Dict, List, Tuple, Optional, Any

class SwapRef:
    def __init__(self, obj, swap_dir: str):
        os.makedirs(swap_dir, exist_ok=True)
        self.filename = os.path.join(swap_dir, f"swap_{uuid.uuid4().hex}.pkl")
        with open(self.filename, "wb") as f:
            pickle.dump(obj, f)
            
    def load(self):
        if not os.path.exists(self.filename):
            raise FileNotFoundError(f"Swap file {self.filename} missing.")
        with open(self.filename, "rb") as f:
            obj = pickle.load(f)
        os.remove(self.filename)
        return obj
        
    def delete(self):
        if os.path.exists(self.filename):
            try:
                os.remove(self.filename)
            except OSError:
                pass

def snapshot_env_keys(env) -> dict:
    return {
        "id": id(env),
        "variables": set(env.local_variables.keys()),
        "dummy_variables": set(env.local_dummy_variables.keys()),
        "meta_variables": set(env.local_meta_variables.keys()),
        "propositional_variables": set(env.local_propositional_variables.keys()),
        "terms": set(env.local_terms.keys()),
        "formulae": set(env.local_formulae.keys()),
        "theorems": set(env.local_theorems),
        "user_functions": set(env.local_user_functions.keys()),
        "user_relations": set(env.local_user_relations.keys())
    }

def compute_env_delta(before: dict, after: dict) -> dict:
    delta = {"added": {}, "removed": {}}
    for k in before.keys():
        if k == "id":
            continue
        added = after[k] - before[k]
        removed = before[k] - after[k]
        if added:
            delta["added"][k] = added
        if removed:
            delta["removed"][k] = removed
    return delta

class RecycleBinManager:
    def __init__(self, swap_dir="swap_files"):
        self.swap_dir = swap_dir
        self.history_commands = []
        self.permanent_recycle_bin = []
        self.temporary_recycle_bin = []
        self.history_pointer = None
        
    def cleanup(self):
        if os.path.exists(self.swap_dir):
            shutil.rmtree(self.swap_dir, ignore_errors=True)
            
    def record_command(self, line_str: str, before_snapshot: dict, before_env: Any, after_env: Any, mission_entered: bool, mission_resolved: bool):
        delta = compute_env_delta(before_snapshot, snapshot_env_keys(after_env))
        if mission_entered:
            delta["mission_entered"] = True
        if mission_resolved:
            delta["mission_resolved"] = True
            
        # Store the removed objects in delta for later permanent recycle bin usage
        removed_objects = {}
        for k, names in delta.get("removed", {}).items():
            if k == "theorems":
                removed_objects[k] = set()
                for name in names:
                    if name in before_env.local_theorems:
                        removed_objects[k].add(name)
            else:
                removed_objects[k] = {}
                dict_ref = getattr(before_env, f"local_{k}")
                for name in names:
                    if name in dict_ref:
                        removed_objects[k][name] = dict_ref[name]
        
        if removed_objects:
            delta["removed_objects"] = removed_objects
            
        # Push to history
        self.history_commands.append((line_str, delta))
        
        # Any removed objects and closed environments go to permanent recycle bin
        if "removed_objects" in delta or mission_resolved:
            perm_item = {}
            if mission_resolved:
                perm_item["closed_env"] = before_env
            if "removed_objects" in delta:
                perm_item["removed_objects"] = removed_objects
            self.permanent_recycle_bin.append(perm_item)

    def undo(self, env: Any) -> Tuple[bool, Any, str]:
        # Returns (success, new_env, message)
        if not self.history_commands:
            return False, env, "Error: Nothing to undo."
        if self.history_pointer is None:
            self.history_pointer = len(self.history_commands) - 1
        elif self.history_pointer < 0:
            return False, env, "Error: Already at the oldest command. Nothing more to undo."
            
        line_str, delta = self.history_commands[self.history_pointer]
        
        # 1. Added objects -> Temporary recycle bin
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
                    
        # 2. Revert mission entries/resolves
        if delta.get("mission_entered"):
            undone_added["child_env"] = env
            env = env.parent
        elif delta.get("mission_resolved"):
            if not self.permanent_recycle_bin:
                return False, env, "Error: Memory wiped. The required objects were permanently deleted from the permanent recycle bin."
            perm_item = self.permanent_recycle_bin.pop()
            if isinstance(perm_item, SwapRef): perm_item = perm_item.load()
            env = perm_item["closed_env"]
        
        # 3. Restored objects -> Pop from Permanent recycle bin
        if "removed_objects" in delta:
            if not delta.get("mission_resolved"):
                if not self.permanent_recycle_bin:
                    return False, env, "Error: Memory wiped. The required objects were permanently deleted from the permanent recycle bin."
                perm_item = self.permanent_recycle_bin.pop()
                if isinstance(perm_item, SwapRef): perm_item = perm_item.load()
            removed_objects = perm_item["removed_objects"]
            for k, objs in removed_objects.items():
                if k == "theorems":
                    env.local_theorems.update(objs)
                else:
                    dict_ref = getattr(env, f"local_{k}")
                    dict_ref.update(objs)
        
        # Push to temporary recycle bin
        self.temporary_recycle_bin.append(undone_added)
            
        self.history_pointer -= 1
        return True, env, f"Undid: {line_str}"
        
    def redo(self, env: Any) -> Tuple[bool, Any, str]:
        # Returns (success, new_env, message)
        if not self.history_commands:
            return False, env, "Error: Nothing to redo."
        if self.history_pointer is None or self.history_pointer == len(self.history_commands) - 1:
            return False, env, "Error: Already at the newest command. Nothing more to redo."
            
        if not self.temporary_recycle_bin:
            return False, env, "Error: Memory wiped. The required objects were deleted from the temporary recycle bin."
            
        self.history_pointer += 1
        line_str, delta = self.history_commands[self.history_pointer]
        
        undone_added = self.temporary_recycle_bin.pop()
        if isinstance(undone_added, SwapRef): undone_added = undone_added.load()
        
        # 1. Restore added objects from temporary recycle bin
        for k, objs in undone_added.items():
            if k == "child_env":
                continue
            if k == "theorems":
                env.local_theorems.update(objs)
            else:
                dict_ref = getattr(env, f"local_{k}")
                dict_ref.update(objs)
        
        # 2. Re-apply mission entries/resolves
        if delta.get("mission_entered"):
            env = undone_added["child_env"]
        elif delta.get("mission_resolved"):
            closed_env = env
            env = env.parent
            
        # 3. Remove objects and push to permanent recycle bin
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
            self.permanent_recycle_bin.append(perm_item)
            
        # If we reached the end, reset pointer
        if self.history_pointer == len(self.history_commands) - 1:
            self.history_pointer = None
            
        return True, env, f"Redid: {line_str}"
        
    def stat(self) -> str:
        perm_count = sum(len(item.get("removed_objects", {})) + (1 if item.get("closed_env") else 0) for item in self.permanent_recycle_bin if isinstance(item, dict))
        # Add swapped items as well
        perm_count += sum(1 for item in self.permanent_recycle_bin if isinstance(item, SwapRef))
        temp_count = sum(len(item) for item in self.temporary_recycle_bin if isinstance(item, dict))
        temp_count += sum(1 for item in self.temporary_recycle_bin if isinstance(item, SwapRef))
        msg = "Recycle Bin Status:\n"
        msg += f"  Permanent Bin: {perm_count} operations containing deleted objects/environments.\n"
        msg += f"  Temporary Bin: {temp_count} operations containing undone created objects."
        return msg
        
    def empty(self, target: str, count: Optional[int]) -> str:
        def clear_bin(bin_list, c):
            if c is None or c >= len(bin_list):
                for item in bin_list:
                    if isinstance(item, SwapRef): item.delete()
                bin_list.clear()
            else:
                for item in bin_list[:c]:
                    if isinstance(item, SwapRef): item.delete()
                del bin_list[:c]
                
        if target in {"all", "perm"}: clear_bin(self.permanent_recycle_bin, count)
        if target in {"all", "temp"}: clear_bin(self.temporary_recycle_bin, count)
        
        return f"Recycle bins emptied successfully ({target}{' ' + str(count) if count else ''})."
        
    def swap(self, target: str, count: int) -> str:
        target_bin = self.permanent_recycle_bin if target == "perm" else (self.temporary_recycle_bin if target == "temp" else None)
        if target_bin is None:
            return "Error: Target must be 'perm' or 'temp'."
            
        swapped = 0
        for i in range(min(count, len(target_bin))):
            if not isinstance(target_bin[i], SwapRef):
                target_bin[i] = SwapRef(target_bin[i], self.swap_dir)
                swapped += 1
        return f"Successfully swapped {swapped} items from {target} bin to disk."

    def truncate_history_if_needed(self, cmd: str):
        if self.history_pointer is not None and cmd not in {"save", "save_h", "load", "load_h", "help", "guide", "rb_stat", "rb_empty", "rb_swap"}:
            self.history_commands = self.history_commands[:self.history_pointer + 1]
            self.empty("temp", None)
            self.history_pointer = None
