with open('scratch/handle_rw_clean.py', 'r') as f:
    rw = f.read()
    
# Remove trailing `def _handle_swap_base` from rw because my regex was a bit sloppy?
# Wait, let's just make sure.
rw = rw.replace('\ndef _handle_swap_base', '')

with open('scratch/clean_swap.py_out', 'r') as f:
    swap = f.read()

with open('backend/CommandHandlers/transformation_handlers.py', 'a') as f:
    f.write("\n\n@registry.register(\"rw\", category=\"Transformations\", help_text=\"Rewrite a term/formula definition within another\")\n")
    f.write(rw)
    f.write("\n\n")
    f.write(swap)
