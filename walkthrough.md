
### 8. Interactive Symbols & Popovers
The click-to-command feature has been significantly refined based on your feedback:
- **Logical Symbol Context Rules**: Substitution commands (`st`, `sb`, `sf`, `sp`, `sa`) are completely hidden when clicking on logical symbols (`∀`, `∃`, `∃!`, `ε`, `ι`, `∨`, `∧`, `¬`, `⇒`, `⇔`, `=`, `∈`), as it doesn't mathematically make sense to apply standard substitution to them. 
- **Fold Command**: The `fold` command has been correctly integrated into the popover menu when clicking on quantifiers (`∀`, `∃`, `∃!`), choice operators (`ε`, `ι`), and user-defined functions and relations. Clicking the popover automatically populates the chat box with the correctly targeted `fold` syntax!
- **Fold All Command**: Clicking on the name of any formula itself (e.g. `f1`, `m1` in orange text) will now pop open a context menu that includes a new **`fold all`** command!

### 9. Documentation and System Fixes
- `intro2` has been explicitly added to the terminal `guide` command docs to clarify its behavior as a command that instantiates a universally quantified schema goal.
- Addressed severe regressions in `Frontend.py` caused by a previous update, restoring the `data-target` and `data-symbol` HTML structure for interactive symbols and preventing a `TypeError` crash when parsing environment payloads.
