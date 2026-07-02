import re

with open("main.py", "r") as f:
    content = f.read()

start_str = '            if cmd in {"load", "load_h"} and not has_error:'
start_idx = content.find(start_str)

end_str = '            if cmd in {"save", "save_h", "load", "load_h", "help", "guide", "rb_stat", "rb_empty", "rb_swap"}:'
end_idx = content.find(end_str)

if start_idx != -1 and end_idx != -1:
    print("Found indices! start_idx", start_idx, "end_idx", end_idx)
    # Wait, the end_idx in the current main.py doesn't have "rb_stat". I already replaced the top half but the bottom half is still using old logic.
    pass

