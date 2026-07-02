from Environment import Environment
from CommandHandlers.CommandRegistry import registry
from Frontend import show_environment

@registry.register("show", category="Environment Tools", help_text="Show the current environment state")
def handle_show(env: Environment, args_str: str) -> None:
    """Prints the current environment to the terminal."""
    show_environment(env)

@registry.register("guide", category="Environment Tools", help_text="Show this command guide", aliases=["help"])
def handle_help(env: Environment, args_str: str) -> None:
    W = 80
    def _cyan(s: str) -> str: return f"\033[36m{s}\033[0m"
    def _blue(s: str) -> str: return f"\033[34m{s}\033[0m"
    def _bold(s: str) -> str: return f"\033[1m{s}\033[0m"
    def _green(s: str) -> str: return f"\033[32m{s}\033[0m"

    print(_cyan("=" * W))
    print(_cyan(_bold(" INTERACTIVE THEOREM PROVER — COMMAND GUIDE ".center(W, "="))))
    print(_cyan("=" * W))

    print("\n" + _blue(_bold("── Universal Transformation Syntax ────────────────────────────────────────────────")))
    print("  Many transformation commands share a standardized 'fold'-style syntax:")
    print("      " + _green("command [args...] [occurrences] [<target>] [<out>] [<equiv>]"))
    print("\n  " + _bold("Arguments:"))
    print("    [occ]      : Comma-separated list of 1-based indices (e.g. 1,3). 0/omit for all.")
    print("    <target>   : The formula or term to modify.")
    print("    <out>      : Optional name for the new formula/term. If omitted, it will")
    print("                 modify the <target> in-place (if created locally).")
    print("    <equiv>    : Optional name for a new proven equivalence (target ⇔ out).")
    print("\n  " + _bold("The 0-Argument Rule:"))
    print("    If <target> is omitted, the command defaults to the ACTIVE GOAL.")
    print("    If <out> is also omitted, it modifies the goal in-place.")

    print("\n" + _blue(_bold("── Substitutions & Transformations ────────────────────────────────────────────────")))
    print(_bold("  [Term Substitutions]"))
    print("  st   v t1        [occ] <target> [<out>]             Substitute term t1 for var v in term")
    print(_bold("  [Formula Substitutions]"))
    print("  sf   v t1        [occ] [<target>] [<out>]           Substitute term t1 for free var v")
    print("  sa   v t1        [occ] [<target>] [<out>]           Substitute t1 for ALL occurrences of v")
    print("  sp   pv p1       [occ] [<target>] [<out>]           Substitute prop-formula p1 for prop-var pv")
    print("  sb   v t1        [occ] [<target>] [<out>] [<equiv>] Rename bound variable v to var t1")
    print(_bold("  [Logic & Negation]"))
    print("  neg-             [occ] [<target>] [<out>] [<equiv>] Remove ¬¬Ψ→Ψ")
    print("  neg+             [occ] [<target>] [<out>] [<equiv>] Wrap Ψ→¬¬Ψ")
    print("  fold <sym>       [occ] [<target>] [<out>] [<equiv>] Unroll definitions (asks 1 var for ∃, ε; asks 2 vars for ∃!, ι)")
    print("  fold all               [<target>] [<out>] [<equiv>] Recursively unroll all definitions")
    print(_bold("  [Equational Rewriting]"))
    print("  simp_l_eq <thm>  [occ] [<target>] [<out>] [<equiv>] Replace LHS with RHS of theorem")
    print("  simp_r_eq <thm>  [occ] [<target>] [<out>] [<equiv>] Replace RHS with LHS of theorem")
    print("  simp_l_bi <thm>  [occ] [<target>] [<out>] [<equiv>] Replace LHS with RHS of bi-implication")
    print("  simp_r_bi <thm>  [occ] [<target>] [<out>] [<equiv>] Replace RHS with LHS of bi-implication")
    print("  rw <thm>         [occ] [<target>] [<out>] [<equiv>] Rewrite a term/formula definition within another")

    print("\n" + _blue(_bold("── Logic Elimination & Introduction (Mission Tactics) ─────────────────────────────")))
    print("  intro  [<target>] <term> [<out>] [<equiv>] Instantiates ∀/∃ premises or reduces goals")
    print("  intro2 <schema> <term/formula> [<target>] [<out>] [<equiv>] Instantiates a universally quantified schema goal")
    print("  left   [<target>] [<out>]                  Reduce goal/premise Ψ∨Φ to Ψ")
    print("  right  [<target>] [<out>]                  Reduce goal/premise Ψ∨Φ to Φ")
    print("  and    [<target>] [<out1>] <out2>          Split Ψ∧Φ into two goals/premises")
    print("  imply  [<target>] [<out1>] <out2>          Split Ψ⇒Φ or reduce goal to consequent")

    print("\n" + _blue(_bold("── Mission Management & Inference ─────────────────────────────────────────────────")))
    print("  mission <f>                 Enter a child environment to prove goal formula f")
    print("  contra  [<f1>] f2 f3        Proof by contradiction: f2 = ¬f1, goal f3 = ⊥")
    print("  exit                        Leave current environment / resolve mission")

    print("  apply   [<target>] <ax/r>   Prove goal or <target> using axiom/rule and premises")
    print("  apply2  <QR1|QR2> f1        Back-compute required premise from goal")
    print("  apply3  f1 f2               Modus ponens backwards (goal matches RHS of f1)")
    print("  auto    <formula>           Auto-prove via fundamental axioms, QR1/QR2, PC2/PC3")
    
    print("\n" + _blue(_bold("── Automated Search ───────────────────────────────────────────────────────────────")))
    print("  search <formula> [time] [space]              Forward graph search")
    print("  backward_search <formula> [time] [space]     Refutation-based backward search")
    print("  advanced_search <formula> [flags...]         Advanced heuristic backward search")

    print("\n" + _blue(_bold("── Definitions & Environment Tools ────────────────────────────────────────────────")))
    print("  cv  <name1> [name2 ...]     Create FOL variables")
    print("  cV  <name1> [name2 ...]     Create propositional variables")
    print("  ct  <name> <term_expr>      Create a term")
    print("  cf  <name> <fol_expr>       Create a 1st-order formula")
    print("  cp  <name> <prop_expr>      Create a propositional formula")
    print("  cfs <name> <arity>          Create a function/term schema (e.g. cfs T 2)")
    print("  crs <name> <arity>          Create a relation schema (e.g. crs Ψ 2)")
    print("  def_f <name> <arity> <def>  Define a user function")
    print("  def_r <name> <arity> <def>  Define a user relation")
    print("  dt  <theorem>               Delete a proven theorem (from any environment)")
    print("  show                        Show the current environment state")
    print("  save / load                 Save/Load environment state to disk")
    print("  save_h / load_h             Save/Load command history to disk")
    
    print("\n" + _blue(_bold("── Recycle Bin & Memory Management ────────────────────────────────────────────────")))
    print("  undo                        Revert the last environment change")
    print("  redo                        Restore the last undone environment change")
    print("  rb_stat                     View current recycle bin sizes")
    print("  rb_empty [perm|temp] [n]    Empty the recycle bins from memory")
    print("  rb_swap  <perm|temp> <n>    Swap bottom N items to disk (pickle) to save RAM")
    print("=" * W)
