with open("README.md", "r") as f:
    readme = f.read()

new_section = """
### `swap_eq` and `swap_bi`
- **Syntax:** `swap_eq (occ) <target> <out> <equiv>`
- **Description:** Searches for occurrences of `=` (or `⇔` for `swap_bi`) inside the target term or formula and swaps the LHS with the RHS. If `occ` is provided, only those specific occurrences are swapped.
- **Example:**
  - `swap_eq goal` - Swaps all `=` in the goal formula.
  - `swap_eq (1,2) f1 f2 equiv1` - Swaps the 1st and 2nd occurrence of `=` in formula `f1`, saves the result as `f2`, and creates the equivalence `equiv1` (which is `f1 ⇔ f2`).
"""

if "### `rw`" in readme:
    readme = readme.replace("### `rw`", new_section + "\n### `rw`")
else:
    readme += "\n" + new_section

with open("README.md", "w") as f:
    f.write(readme)

print("Updated README.md")
