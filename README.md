# Interactive Theorem Prover (ITP)

> A text-based interactive proof assistant for First-Order Logic and Zermelo–Fraenkel set theory.
> No programming knowledge required — just mathematics.

---

## Table of Contents

1. [What is this program?](#1-what-is-this-program)
2. [How to run the program](#2-how-to-run-the-program)
3. [The mathematical language](#3-the-mathematical-language)
   - [Variables and Terms](#31-variables-and-terms)
   - [First-Order Formulae](#32-first-order-formulae)
   - [Propositional Formulae](#33-propositional-formulae)
4. [Environments and the object namespace](#4-environments-and-the-object-namespace)
5. [Basic object-creation commands](#5-basic-object-creation-commands)
6. [Substitution commands](#6-substitution-commands)
7. [Rewriting by proven equations and bi-implications](#7-rewriting-by-proven-equations-and-bi-implications)
8. [Double-negation commands](#8-double-negation-commands)
9. [User-defined symbols and definition folding](#9-user-defined-symbols-and-definition-folding)
10. [Direct proof commands](#10-direct-proof-commands)
    - [Axioms (ua)](#101-axioms-ua)
    - [Inference rules (ir)](#102-inference-rules-ir)
    - [Auto-prover (auto)](#103-auto-prover-auto)
    - [Forward Search (search)](#104-semi-automated-search-search)
    - [Backward Search (resolution) (backward_search)](#105-backward-search-resolution-backward_search)
    - [Advanced Backward Search (advanced_search)](#106-advanced-backward-search-advanced_search)
    - [Foundational Proof Logging](#107-foundational-proof-logging-proofshtml)
11. [Mission environments — proving goals interactively](#11-mission-environments--proving-goals-interactively)
    - [Opening a mission](#111-opening-a-mission)
    - [Mission tactics](#112-mission-tactics)
    - [Closing a mission](#113-closing-a-mission)
12. [Advanced proving techniques (advanced-proving branch)](#12-advanced-proving-techniques-advanced-proving-branch)
    - [apply — use an axiom or rule to close a goal](#121-apply--use-an-axiom-or-rule-to-close-a-goal)
    - [apply2 — back-compute a QR premise](#122-apply2--back-compute-a-qr-premise)
    - [apply3 — modus ponens backwards](#123-apply3--modus-ponens-backwards)
    - [left / right — disjunction tactics](#124-left--right--disjunction-tactics)
    - [and — conjunction tactic](#125-and--conjunction-tactic)
    - [iff — equivalence tactic](#126-iff--equivalence-tactic)
    - [and2 — destructure a conjunction formula](#127-and2--destructure-a-conjunction-formula)
    - [imply — implication tactic](#128-imply--implication-tactic)
    - [intro — universal and existential introduction](#129-intro--universal-and-existential-introduction)
    - [intro2 — universal instantiation](#129-intro2--universal-instantiation)
    - [contra — proof by contradiction](#1210-contra--proof-by-contradiction)
    - [force — shortcut direct proof](#1211-force--shortcut-direct-proof)
13. [Saving and loading state](#13-saving-and-loading-state)
14. [The show command](#14-the-show-command)
15. [Reference: all axioms and inference rules](#15-reference-all-axioms-and-inference-rules)
16. [Full command quick-reference](#16-full-command-quick-reference)
17. [Worked examples](#17-worked-examples)

---

## 1. What is this program?

This is an **Interactive Theorem Prover** — a program that lets you build and verify mathematical proofs step by step, in a conversation with your computer.

You type commands at a prompt, and the program responds by telling you whether what you did was valid, updating its internal state, and showing you the result.

It works within the framework of **First-Order Logic (FOL)** with:
- The standard **logical axioms** (equality axioms E1, E2, E3; quantifier axioms Q1, Q2)
- The **ZFC axioms** of set theory (extension, pairing, union, power set, regularity, infinity, choice, specification, replacement)
- Four **inference rules** (QR1, QR2, PC1, PC2)

There are two versions of the program corresponding to two git branches:

| Branch | Description |
|--------|-------------|
| `main` | Full program including all advanced proving tactics |
| `advanced-proving` | Development branch — identical to `main` |

---

## 2. How to run the program

Open a terminal in the `ITP` folder and type:

```
python main.py
```

You will see a prompt like:

```
[Ground] >
```

This means the program is ready. Type a command and press Enter.

To quit at any time, type:
```
exit
```

To see this full guide at any time while the program is running, type:
```
guide
```

---

## 3. The mathematical language

### 3.1 Variables and Terms

The program starts with some default objects already available:

| Name | Type | Meaning |
|------|------|---------|
| `x`, `y` | variables | standard FOL variables |
| `S` | function (arity 1) | successor function (as in natural numbers) |
| `+` | function (arity 2) | addition (infix) |
| `=` | relation (arity 2) | equality (infix) |
| `∈` | relation (arity 2) | set membership (infix) |
| `p`, `q` | prop. variables | propositional variables |

**Terms** are built from variables and functions. Examples of valid terms:
- `x` — a variable
- `S x` — the successor of x
- `S S x` — the successor of the successor of x
- `x + y` — the sum of x and y
- `S x + S y` — can be written in the prompt using normal characters

**How to type special symbols:**

| Symbol | Meaning | Type |
|--------|---------|------|
| `∀` | for all | `∀` or copy-paste |
| `∃` | there exists | `∃` |
| `¬` | not | `¬` |
| `∧` | and | `∧` |
| `∨` | or | `∨` |
| `⇒` | implies | `⇒` |
| `⇔` | if and only if | `⇔` |
| `∈` | is a member of | `∈` |
| `=` | equals | `=` |

> **Tip:** On macOS you can use the Character Viewer (Edit → Emoji & Symbols) or copy symbols from this file. The program also accepts Unicode input directly.

### 3.2 First-Order Formulae

A **First-Order Formula (FOL formula)** is a mathematical statement that can be true or false. Examples:

| Formula | Meaning |
|---------|---------|
| `x = y` | x equals y |
| `x ∈ y` | x is an element of y |
| `¬ x = y` | x is not equal to y |
| `x = y ∧ y = z` | x equals y, and y equals z |
| `x = y ∨ x = z` | x equals y, or x equals z |
| `x = y ⇒ y = x` | if x equals y then y equals x |
| `∀ x x = x` | for all x, x equals x |
| `∃ x x = y` | there exists an x such that x equals y |

**Parentheses** can be added freely for clarity:
- `∀ x ( x = x )` means the same as `∀ x x = x`

### 3.3 Propositional Formulae

These are simpler formulae built only from propositional variables (`p`, `q`, etc.) and connectives, without quantifiers or terms:

- `p ∧ q` — p and q
- `p ⇒ q` — p implies q
- `p ⇔ q` — p if and only if q

---

## 4. Environments and the object namespace

The program maintains an **environment** — a collection of named objects. Everything you create gets a name, and no two objects can share the same name.

There are four kinds of objects:

| Kind | Created by | Example |
|------|-----------|---------|
| Variable | `cv` | `x`, `y` |
| Term | `ct` | `t1 = S x` |
| FOL Formula | `cf` | `f1 = ∀ x x = x` |
| Propositional Formula | `cp` | `p1 = p ∧ q` |

Additionally, any formula can be **proven**, making it a **theorem**. Theorems are the mathematical results you derive during a session.

### The environment stack

The program supports **nested environments** for interactive proof. The outermost environment is called the **ground environment**. When you open a proof mission, a **child environment** is created on top, inheriting everything from the parent. When the mission is closed, the child disappears and control returns to the parent.

```
[Ground]  ← you are always here when no mission is active
   └── [Child: proving f1]  ← created by the 'mission' command
          └── [Grandchild: proving f2]  ← created by 'and', 'imply', etc.
```

The `show` command displays the full current stack.

---

## 5. Basic object-creation commands

### `cv <name>` — Create a Variable

Creates a new logical variable.

```
cv z
```
→ Creates variable `z`.

### `cV <name>` — Create a Propositional Variable

Creates a new propositional variable (for use in propositional formulae).

```
cV r
```
→ Creates propositional variable `r`.

### `ct <name> <term expression>` — Create a Term

Creates a named term from existing variables and functions.

```
ct t1 S x
ct t2 x + y
ct t3 S S x
```

### `cf <name> <formula expression>` — Create a FOL Formula

Creates a named first-order formula.

```
cf f1 x = x
cf f2 ∀ x ( x = x )
cf f3 x = y ⇒ y = x
cf f4 ∃ z ( z = x ∧ z = y )
```

### `cp <name> <propositional expression>` — Create a Propositional Formula

```
cp p1 p ∧ q
cp p2 p ⇒ q
```

---

## 6. Substitution commands

Substitution is replacing a variable (or formula) everywhere (or at specific places) inside another object.

### General note on occurrence indices

All substitution commands accept an optional **`[idx]`** argument at the end. This is a 1-based index selecting which occurrence to substitute. If omitted, **all** occurrences are substituted.

```
st t1 x t2 t3       ← replace ALL x's in t1 with t2, store as t3
st t1 x t2 t3 2     ← replace only the 2nd occurrence of x
```

---

### `st <term1> <var> <term2> <term3> [idx]` — Substitute in a Term

Replace the variable `var` with term `term2` inside `term1`. The result is stored as `term3`.

**Example:**
```
cv x
cv y
ct t1 x + x
ct t2 S y
st t1 x t2 t3
```
→ `t3` = `S y + S y`

```
st t1 x t2 t4 1
```
→ `t4` = `S y + x`  (only the first `x` replaced)

---

### `sf <formula1> <var> <term1> <formula2> [idx]` — Substitute a term for a free variable in a formula

Replace free occurrences of `var` with `term1` inside `formula1`.

**Example:**
```
cf f1 x = y ∧ x = z
ct t1 S x
sf f1 x t1 f2
```
→ `f2` = `S x = y ∧ S x = z`

---

### `sb <formula1> <var> <term1> <formula2> [idx]` — Substitute for a bound variable (rename)

This renames a **bound** variable. The replacement (`term1`) must itself be a variable.

**Example:**
```
cf f1 ∀ x ( x = y )
cv z
sb f1 x z f2
```
→ `f2` = `∀ z ( z = y )`

---

### `sa <formula1> <var> <term1> <formula2> [idx]` — Substitute at ALL occurrences (free and bound)

Use with caution — this replaces the variable name everywhere, including inside quantifiers.

---

### `sp <p1> <pvar> <p2> <p3> [idx]` — Substitute a propositional formula for a propositional variable

Replace propositional variable `pvar` with propositional formula `p2` inside `p1`.

**Example:**
```
cp p1 p ∧ q
cV r
cp p2 r ⇒ r
sp p1 p p2 p3
```
→ `p3` = `( r ⇒ r ) ∧ q`

---

## 7. Rewriting by proven equations and bi-implications

These commands let you replace one expression with an equivalent one, using a **proven theorem**.

### `simp_l_eq` / `simp_r_eq` — Rewrite using a proven equality

If you have proven a theorem of the form **T3 = T4**, then:
- `simp_l_eq` rewrites occurrences of **T3** (the left side) by **T4** (the right side)
- `simp_r_eq` rewrites occurrences of **T4** (the right side) by **T3** (the left side)

**Syntax:**
```
simp_l_eq <target> <theorem> [idx] [new_name] [equiv_name]
```

- `target` — the name of the term or formula to rewrite
- `theorem` — the name of the proven equality theorem
- `idx` — (optional) which occurrence to rewrite; omit for all
- `new_name` — (optional) name for the result; omit to rewrite in place
- `equiv_name` — (optional) name to store the proven equivalence `(original ⇔ result)`

**Example:**
Suppose you have proven `r1 = (x = S z)` (meaning x equals S z).
```
ct t1 x + y + x
simp_l_eq t1 r1 2 t2
```
→ `t2` = `x + y + S z`  (the 2nd occurrence of `x` replaced by `S z`)

```
simp_l_eq t1 r1 t3
```
→ `t3` = `S z + y + S z`  (all occurrences replaced)

---

### `simp_l_bi` / `simp_r_bi` — Rewrite using a proven bi-implication

Works exactly like `simp_l_eq` / `simp_r_eq`, but for bi-implications **F3 ⇔ F4** applied to formulae.

---

## 8. Double-negation commands

### `neg-` — Remove a double negation (¬¬Ψ → Ψ)

By classical logic, `¬¬Ψ` is equivalent to `Ψ`. This command removes a double negation.

**Syntax variants:**
```
neg- f1 [idx] [f2] [f3]   ← act on named formula f1
neg- [idx] f2              ← act on the active goal, at occurrence idx
neg- f2                    ← act on active goal, all occurrences
```

- `idx` — which double-negation to remove (1-based). 0 or omitted = all.
- `f2` — name for the result. Omit to modify in place.
- `f3` — (only for named formula targets) name for the proven equivalence `(f1 ⇔ f2)`.

**Example:**
```
cf f1 ¬ ¬ ( x = y )
neg- f1 f2
```
→ `f2` = `x = y`  and  `f1` stays as `¬ ¬ ( x = y )`

If `f1` was a proven theorem, `f2` is also automatically proven.

---

### `neg+` — Introduce a double negation (Ψ → ¬¬Ψ)

The reverse: wraps a subformula in `¬¬`.

**Syntax:** identical to `neg-` above.

**Example:**
```
cf f1 x = y
neg+ f1 1 f2
```
→ `f2` = `¬ ¬ ( x = y )`

---

## 9. User-defined symbols and definition folding

### `def_f` — Define a new function symbol

```
def_f <arity> <F> <v1> ... <vn> <body_term>    ← prefix (arity ≠ 2)
def_f 2 <v1> <F> <v2> <body_term>              ← infix (arity = 2)
```

**Example:** Define `double(x) = x + x`
```
def_f 1 double x t_xx
```
where `t_xx` is the term `x + x`.

After this, you can write `double x` and it stands for `x + x`.

---

### `def_r` — Define a new relation symbol

```
def_r <arity> <R> <v1> ... <vn> <body_formula>  ← prefix
def_r 2 <v1> <R> <v2> <body_formula>            ← infix
```

**Example:** Define `x divides y` as `∃ z (x · z = y)` (if you have multiplication defined):
```
def_r 2 x divides y f_div
```

---

### Choice Operators (`ε` and `ι`)

You can define terms using choice operators directly in the language, similar to quantifiers:
- `ε x Ψ(x)`: An arbitrary object `x` such that `Ψ(x)` is true.
- `ι x Ψ(x)`: The unique object `x` such that `Ψ(x)` is true.

These act as core term nodes. You can unfold them in formulas using the `fold` command.

---

### `fold` — Fold a definition back into a formula

When you expand a user-defined symbol (the program unfolds it automatically), you sometimes want to fold it back. The `fold` command reverses an expansion.

```
fold <symbol> <occurrence> <input> [args...] <output> [f3]
fold ∃  <occurrence> <formula> <output> [f3]
fold ∃! <occurrence> <formula> <y> <output> [f3]
fold {  <occurrence> <formula> <u> <output> [f3]
fold ε  <occurrence> <formula> <u> <output> [f3]
fold ι  <occurrence> <formula> <u> <v> <output> [f3]
```

`f3` (optional) stores a proven equivalence `(input ⇔ output)`.

---

## 10. Direct proof commands

These commands are used in the **ground environment** (or any environment) to prove formulae directly from axioms and rules.

### 10.1 Axioms (`ua`)

```
ua <axiom_name> <formula_name>
```

Attempts to prove the named formula by checking it against the named axiom. If the formula is an instance of the axiom, it is added to the list of proven theorems.

**Logical axioms:**

| Name | Statement |
|------|-----------|
| `E1` | t = t (reflexivity of equality) |
| `E2` | x₁=y₁ ∧ … ∧ xₙ=yₙ ⇒ f(x₁,…,xₙ) = f(y₁,…,yₙ) |
| `E3` | x₁=y₁ ∧ … ∧ xₙ=yₙ ⇒ (R(x₁,…,xₙ) ⇒ R(y₁,…,yₙ)) |
| `Q1` | ∀x φ ⇒ φ[t/x]  (universal instantiation) |
| `Q2` | φ[t/x] ⇒ ∃x φ  (existential generalisation) |

**ZFC axioms of set theory:**

| Name | Principle |
|------|-----------|
| `extension` | Two sets are equal iff they have the same members |
| `pairing` | For any a, b there is a set {a, b} |
| `union` | For any family of sets, there is a set of all members |
| `power_set` | Every set has a power set |
| `regularity` | Every non-empty set has an ∈-minimal element |
| `infinity` | There exists an infinite set |
| `choice` | Every family of non-empty sets has a choice function |
| `specification` | For any set A and property φ, {x∈A : φ(x)} exists |
| `replacement` | The image of a set under a definable function is a set |

**Example:**
```
cf f1 x = x
ua E1 f1
```
→ `f1` is now a proven theorem.

---

### 10.2 Inference rules (`ir`)

```
ir <rule_name> <conclusion_formula> [premise1] [premise2] ...
```

Applies the named inference rule, checking that the premises (which must already be proven theorems) logically entail the conclusion formula.

**Inference rules:**

| Name | Rule |
|------|------|
| `PC1` | Any propositional tautology (checked algorithmically) |
| `PC2` | Any propositional tautology provable without premises |
| `QR1` | From `Ψ ⇒ φ`, derive `Ψ ⇒ ∀x φ` (where x not free in Ψ, not bound in φ) |
| `QR2` | From `φ ⇒ Ψ`, derive `∃x φ ⇒ Ψ` (where x not free in Ψ, not bound in φ) |

**Example using PC1:**
```
cf f1 x = y ⇒ x = y
ir PC1 f1
```
→ `f1` is proven (it is a propositional tautology p ⇒ p).

**Example using QR1:**
First, prove the premise `ψ ⇒ φ`, then apply QR1:
```
cf pre ( x = y ) ⇒ ( x = y )
ir PC1 pre
cf goal ( x = y ) ⇒ ( ∀ z ( x = y ) )
ir QR1 goal pre
```
→ `goal` is proven.

---

### 10.3 Auto-prover (`auto`)

```
auto <formula_name>
```

The program automatically tries to prove the formula by:
1. Testing all logical and ZFC axioms
2. Attempting PC2 (propositional tautology check)
3. Trying to decompose QR1 / QR2 goals recursively

This is a convenience shortcut — not a complete proof search. It works well for simple tautologies and axiom instances.

**Example:**
```
cf f1 x = x
auto f1
```
→ Proved using E1.

---

### 10.4 Semi-Automated Search (`search`)

```
search <formula_name> [time_limit_sec] [space_limit_nodes]
```

Runs a theoretically **complete** forward graph search to prove the target formula. The algorithm uses a dovetailed Breadth-First Search (BFS) / Forward Saturation strategy, generating terms, formulas, and applying primitive rules/axioms until the formula is proved.

*   `time_limit_sec` — (optional) maximum search time in seconds (default: `10.0`).
*   `space_limit_nodes` — (optional) maximum search space, quantified as the total number of unique terms, formulas, and proven theorems generated and stored in memory (default: `10000`).

The search will automatically abort if either the time limit or the space limit is exceeded.

**Example:**
```
cf f1 x = x
search f1 5.0 5000
```
→ Succeeds quickly in proving `f1` using the `E1` axiom at depth 0.

---

### 10.5 Backward Search (Resolution) (`backward_search`)

```
backward_search <formula_name> [time_limit_sec] [space_limit_nodes]
```

Runs a refutation-based theorem prover using Robinson's resolution and unification. It works backwards from the goal by negating it, converting it to Conjunctive Normal Form (CNF) along with all existing theorems, and deriving the empty clause.

*   `time_limit_sec` — (optional) maximum search time in seconds (default: `10.0`).
*   `space_limit_nodes` — (optional) maximum search space limit in clauses (default: `10000`).

**Example:**
```
cf f1 x = x
backward_search f1
```
→ Succeeds quickly if `E1` (reflexivity) is available to unify against `¬(x=x)`.

---

### 10.6 Advanced Backward Search (`advanced_search`)

```
advanced_search <formula_name> [time_limit_sec] [space_limit_nodes] [+sos] [+unit] [+subsumption] [+paramodulation] [+ordering]
```

Runs a highly optimized refutation-based theorem prover. It extends basic backward search with a priority queue and a suite of togglable heuristics:

*   `+sos` (Set of Support) — Partitions clauses into axioms and goals. Resolves only when one parent clause descends from the negated goal, strictly focusing the search direction.
*   `+unit` (Unit Preference) — Continually selects the shortest active clauses to resolve first, using a Min-Heap priority queue.
*   `+subsumption` (True Subsumption) — Performs forward and backward subsumption to prune logically redundant clauses.
*   `+paramodulation` (Paramodulation) — Handles equality (`=`) predicates natively by performing unifiable term substitutions, avoiding bulk ZFC equality axioms.
*   `+ordering` (Term Ordering) — Restricts paramodulation to strictly rewrite larger terms to smaller terms (using Knuth-Bendix/weight-based ordering). **Highly recommended to prevent infinite loops when paramodulation is active.** Note: SOS and Term Ordering combined can lead to incompleteness on certain equality proofs (e.g. Abelian group), so they are best used separately or in tandem with specific strategies.

**Example:**
```
advanced_search my_goal 10.0 50000 +unit +subsumption +paramodulation +ordering
```

---

### 10.7 Foundational Proof Logging (`proofs.html`)

When starting the REPL, you are prompted to enable **Foundational Proof Logging**. If enabled, the ITP will record mathematically rigorous, step-by-step proofs for all automated successes into an HTML file (`proofs.html`).

*   **Deskolemized Formulae**: Backward search traces use Skolemization internally, but the proof logger elegantly deskolemizes the trace clauses back into readable First-Order Logic featuring explicit `∀` and `∃` quantifiers.
*   **Color Highlighting**: The output utilizes a beautiful depth-based color highlighting scheme to trace nested parentheses and operations cleanly.
*   **Tethered Integration**: The HTML logger is directly integrated with `auto`, `backward_search`, and `advanced_search`.

---


### `dt` — Delete a proven theorem

```
dt <theorem_name>
```

Removes a theorem from the list of proven results (without deleting the formula itself). Useful if you want to undo a proof or reorganise.

---

## 11. Mission environments — proving goals interactively

For complex proofs, rather than constructing the full formula and then proving it, you can open a **mission** — an interactive goal-directed proof session.

### 11.1 Opening a mission

```
mission <formula_name>
```

Opens a child environment with `formula_name` as the **goal**. The prompt changes to show you are inside a mission:

```
[Child: goal=f1] >
```

You are now trying to prove `f1`. Inside the mission, you can:
- Create new variables, terms, and formulae (local to this child)
- Use any of the substitution, simplification, or substitution commands
- Apply **tactics** (see section 12) to simplify and transform the goal
- Use `ua`, `ir`, `auto` to close the goal directly

### 11.2 Mission tactics

Tactics are commands that transform the current goal into a simpler or equivalent goal, or split it into sub-goals, without immediately proving it. All tactics require an active mission.

See [Section 12](#12-advanced-proving-techniques-advanced-proving-branch) for the full list.

### 11.3 Closing a mission

A mission closes automatically whenever the current goal formula is **in the list of proven theorems**. This can happen:
- Because you applied a tactic that immediately recognised the goal was already proven
- Because you used `apply`, `ua`, `ir`, or `auto` directly on the goal

When a mission closes, control returns to the parent environment and the original goal formula is registered as a proven theorem there.

### `exit` — Leave a child environment

```
exit
```

Leaves the current child environment **without proving the goal**. The mission is abandoned. If you are in the ground environment, `exit` quits the program.

---

## 12. Advanced proving techniques (advanced-proving branch)

These are the tactics available inside mission environments to structure complex proofs.

---

### 12.1 `apply` — Use an axiom or rule to close a goal

```
apply <axiom_name>
apply <rule_name> p1 p2 ... pn
```

**`apply <axiom>`:** Tests the current goal directly against the named axiom. If the goal is an instance of the axiom, the mission is immediately closed.

```
[Child: goal=f1] > apply E1
```
→ If the goal `f1` is of the form `t = t`, the mission closes.

**`apply <rule> p1 p2 ... pn`:** Applies the inference rule, using the already-proven formulae `p1`, `p2`, …, `pn` as premises, testing whether the current goal follows. If yes, the mission closes.

```
[Child: goal=g] > apply PC1 lem1 lem2
```
→ Checks whether `g` follows from proven theorems `lem1`, `lem2` using PC1.

---

### 12.2 `apply2` — Back-compute a QR premise

```
apply2 QR1 f1
apply2 QR2 f1
```

This command works **backwards** from the current goal to figure out what you need to prove first.

- **For QR1:** The current goal must be of the form **Ψ ⇒ ∀x Φ**. The command creates the premise `Ψ ⇒ Φ` (named `f1`) and changes the goal to that premise. Once you prove `f1`, the original goal follows by QR1.

- **For QR2:** The current goal must be of the form **(∃x Φ) ⇒ Ψ**. The command creates the premise `Φ ⇒ Ψ` and changes the goal to it.

**Example:**
```
cf g ( x = y ) ⇒ ( ∀ z ( x = y ) )
mission g
  apply2 QR1 h
  [goal is now h = (x=y) ⇒ (x=y)]
  apply PC1
```

---

### 12.3 `apply3` — Modus ponens backwards

```
apply3 f1 f2
```

If you have already proven a theorem `f1` of the form **Ψ ⇒ Φ**, and the current goal matches **Φ**, this command changes the goal to **Ψ** (named `f2`). This is modus ponens in reverse: "to prove Φ, it suffices to prove Ψ, since we already know Ψ ⇒ Φ."

**Example:**
```
[Child: goal=conc]
> apply3 my_implication new_goal
```
→ Goal changes to `new_goal = Ψ` (the antecedent of `my_implication`).

---

### 12.4 `left` / `right` — Disjunction tactics

```
left  f1
right f1
```

Use when the current goal is of the form **Ψ ∨ Φ**.

- `left f1` changes the goal to **Ψ** (named `f1`). Proving Ψ is sufficient to prove the disjunction.
- `right f1` changes the goal to **Φ** (named `f1`). Proving Φ is sufficient.

**Example:**
```
cf g x = y ∨ x = x
mission g
  right f1
  [goal is now f1 = (x = x)]
  apply E1
```

---

### 12.5 `and` — Conjunction tactic

```
and f1 f2
```

Use when the current goal is of the form **Ψ ∧ Φ**. To prove a conjunction, you must prove both parts.

This command:
1. Sets the current goal name to `f1` and changes it to **Ψ** (the left part)
2. Opens a **nested child environment** with goal `f2 = Φ` (the right part)

You are first placed inside the nested child to prove **Φ**. Once that is done, control returns and you prove **Ψ** in the outer child. When both are proven, the original conjunction is proven.

---

### 12.6 `iff` — Equivalence tactic

```
iff f1 f2
```

Use when the current goal is of the form **Ψ ⇔ Φ**. To prove an equivalence, you must prove both implications.

This command:
1. Sets the current goal name to `f1` and changes it to **Ψ ⇒ Φ** (the left implication)
2. Opens a **nested child environment** with goal `f2` representing **Φ ⇒ Ψ** (the right implication)

You are first placed inside the nested child to prove **Φ ⇒ Ψ**. Once that is done, control returns and you prove **Ψ ⇒ Φ** in the outer child. When both are proven, the original equivalence is proven.

---

### 12.7 `and2` — Destructure a conjunction formula

```
and2 f1 f2
```

This is a general-purpose command (usable anywhere, not just in missions).

If `f1` is a formula of the form **Ψ ∧ Φ**:
- `f1` is **redefined** to just **Ψ**
- A new formula `f2` is created with definition **Φ**
- If `f1` was a proven theorem, both `f1` and `f2` become proven theorems

This is logically sound: a proven conjunction implies both conjuncts.

**Example:**
```
cf f1 x = y ∧ y = z
ua PC1 f1         ← (suppose you proved f1 somehow)
and2 f1 f2
```
→ `f1` is now `x = y` (proven), `f2` is `y = z` (proven).

---

### 12.8 `imply` — Implication tactic

```
imply f1 f2
```

Use when the current goal is of the form **Ψ ⇒ Φ**.

To prove an implication, it is standard to **assume the antecedent** and then prove the consequent. This command:
1. Changes the current goal to **Φ** (named `f1`)
2. Adds **Ψ** as a **proven assumption** in the child environment, named `f2`

Now you must prove Φ, knowing Ψ holds (as proven theorem `f2`).

**Example:**
```
cf g x = y ⇒ y = x
mission g
  imply f1 h
  [goal is now f1 = (y = x); h = (x = y) is a proven assumption]
  ...prove f1 using h...
```

---

### 12.9 `intro` — Universal and existential introduction

```
intro f1 v     ← for goal ∀x Ψ(x)
intro f1 t1    ← for goal ∃x Ψ(x)
```

**For a universal goal ∀x Ψ(x):**

`intro f1 v` introduces a **completely fresh** variable `v` (a name not used anywhere in the proof so far), renames the bound variable `x` to `v`, and sets the new goal to `Ψ(v)` (named `f1`).

The idea: to prove "for all x, Ψ(x)", it is enough to prove Ψ(v) for an arbitrary fresh v — because v has no special properties, anything you prove about it holds for all variables.

> **Important:** `v` must be a completely new name, never used before. The program enforces this.

**For an existential goal ∃x Ψ(x):**

`intro f1 t1` substitutes the term `t1` for the bound variable `x` and sets the new goal to `Ψ(definition of t1)`. The idea: to prove "there exists an x with Ψ(x)", it is enough to show that Ψ holds for the specific term `t1` — this is your **witness**.

---

### 12.9 `intro2` — Universal instantiation

```
intro2 f1 t1 f2
```

This is a general-purpose command (usable anywhere).

If `f1` is a formula of the form **∀x Ψ(x)**:
- `f1` is **redefined** to the body **Ψ(x)** (the formula without the ∀)
- A new formula `f2` is created as **Ψ(definition of t1)** — the body with `x` replaced by the term `t1`
- If `f1` was a proven theorem, `f2` is also a proven theorem

This is the classical **universal instantiation** rule: from ∀x Ψ(x), we can derive Ψ(t) for any specific term t.

**Example:**
```
cf f1 ∀ x ( x = x )
ua E1 f1      ← not the right form for E1, but for illustration
intro2 f1 x f2
```
→ `f2` = `x = x`  (proven, because f1 was proven)

---

### 12.10 `contra` — Proof by contradiction

```
contra f1 f2 f3 f4
```

**Mathematical idea:** To prove formula `f1` (which already exists in the environment), assume its negation is true and derive a contradiction. A contradiction is a formula of the form `A ∧ ¬A` — something and its negation both being true simultaneously, which is impossible. If such a contradiction follows from the assumption `¬f1`, then `f1` must be true.

**What the command does:**

| Object | Definition | Status |
|--------|-----------|--------|
| `f2` | `¬(definition of f1)` | proven theorem in child env |
| `f4` (goal) | `¬(definition of f3) ∧ (definition of f3)` | the contradiction to derive |

You are placed in a child environment where:
- `f2 = ¬f1` is already proven (this is your assumption)
- Your goal is to prove `f4`, which is the contradiction `¬f3 ∧ f3`

Once you prove `f4` (showing a contradiction follows from `¬f1`), the mission closes and `f1` is registered as a proven theorem in the parent environment.

**Naming rules:**
- `f1` must already exist in the environment
- `f2` must be a new name (or match `¬f1` if already exists)
- `f3` must already exist in the environment
- `f4` must be a new name (or match `¬f3 ∧ f3` if already exists)

**Example:**
```
cf f1 x = x
cf f3 x = y
ITP> contra f1 neg_f1 f3 falsum
...derive the contradiction...
```

---

### 12.11 `force` — Shortcut direct proof

**Syntax:**
```
force <target>
```
**Example:**
```
force lemma_1
```
**Mathematical idea:** Sometimes, you want to assume a lemma or theorem is true without spending the time to manually prove it, perhaps because you are more interested in proving a larger goal that depends on it. 

The `force` command allows you to instantly bypass the proof process. It will take an existing formula `<target>` and immediately register it as a proven theorem in the environment. If you force the active mission goal, the mission will close and succeed. 
*(Note: Because this bypasses the rules of logic, this command is strictly disabled in all Game levels to prevent cheating!)*

---

## 13. Saving and loading state

You can save your entire proof state (all variables, terms, formulae, theorems, and the environment stack) to a file and reload it later.

### `save` — Save the current state

```
save
```
→ The program asks for a filename. The state is saved to `save_files/<filename>`.

### `load` — Load a saved state

```
load
```
→ The program asks for a filename. The state is restored from `save_files/<filename>`.

### `save_h` — Save command history

```
save_h
```
→ Saves all commands you've typed this session to `history_files/<filename>`.

### `load_h` — Replay a history file

```
load_h
```
→ Loads a history file and replays all its commands automatically. Useful for replaying a proof.

---

## 14. The `show` command

```
show
```

Displays the full current environment stack. For each environment, it shows:
- All variables
- All terms
- All formulae (with their definitions)
- All proven theorems
- The current goal (if in a mission)

Use this frequently to keep track of what you have.

---

## 15. Reference: all axioms and inference rules

### Logical Axioms

| Name | Mathematical Statement |
|------|----------------------|
| **E1** | `t = t` for any term t (reflexivity) |
| **E2** | `(x₁=y₁ ∧…∧ xₙ=yₙ) ⇒ f(x₁,…,xₙ) = f(y₁,…,yₙ)` (congruence for functions) |
| **E3** | `(x₁=y₁ ∧…∧ xₙ=yₙ) ⇒ (R(x₁,…,xₙ) ⇒ R(y₁,…,yₙ))` (congruence for relations) |
| **Q1** | `∀x φ ⇒ φ[t/x]` when t is free for x in φ (universal instantiation) |
| **Q2** | `φ[t/x] ⇒ ∃x φ` when t is free for x in φ (existential generalisation) |

### ZFC Set-Theory Axioms

| Name | Principle |
|------|-----------|
| **extension** | `∀z(z∈x ⇔ z∈y) ⇒ x=y` |
| **pairing** | `∃z(x∈z ∧ y∈z)` |
| **union** | For any set, the union of its elements is a set |
| **power_set** | `∀x∃y∀z(z⊆x ⇒ z∈y)` |
| **regularity** | Every non-empty set has an ∈-minimal element |
| **infinity** | There exists a set containing ∅ and closed under successor |
| **choice** | Every family of non-empty sets has a choice function |
| **specification** | `∃y∀x(x∈y ⇔ x∈z ∧ φ(x))` for any formula φ |
| **replacement** | The image of a set under a definable class-function is a set |

### Inference Rules

| Name | Rule | Conditions |
|------|------|-----------|
| **PC1** | Any propositional tautology (check by truth table/sequent calculus) | — |
| **PC2** | Any propositional tautology without needing premises | — |
| **QR1** | From `Ψ ⇒ φ` derive `Ψ ⇒ ∀x φ` | x not free in Ψ; x not bound in φ |
| **QR2** | From `φ ⇒ Ψ` derive `∃x φ ⇒ Ψ` | x not free in Ψ; x not bound in φ |

---

## 16. Full command quick-reference

### Object Definitions
| Command | Description |
|---------|-------------|
| `cv name` | Create FOL variable |
| `cV name` | Create propositional variable |
| `ct name expr` | Create term |
| `cf name expr` | Create FOL formula |
| `cp name expr` | Create propositional formula |

### Substitution
| Command | Description |
|---------|-------------|
| `st t1 v t2 t3 [idx]` | Substitute term in term |
| `sf f1 v t1 f2 [idx]` | Substitute for free variable in formula |
| `sb f1 v t1 f2 [idx]` | Rename bound variable in formula |
| `sa f1 v t1 f2 [idx]` | Substitute at all occurrences |
| `sp p1 pv p2 p3 [idx]` | Substitute propositional formula |

### Rewriting
| Command | Description |
|---------|-------------|
| `simp_l_eq target thm [idx] [new] [equiv]` | Rewrite LHS of proven equality |
| `simp_r_eq target thm [idx] [new] [equiv]` | Rewrite RHS of proven equality |
| `simp_l_bi target thm [idx] [new] [equiv]` | Rewrite LHS of proven bi-implication |
| `simp_r_bi target thm [idx] [new] [equiv]` | Rewrite RHS of proven bi-implication |
| `neg- f1 [idx] [f2] [f3]` | Remove double negation |
| `neg+ f1 [idx] [f2] [f3]` | Introduce double negation |

### User-Defined Symbols
| Command | Description |
|---------|-------------|
| `def_f n F v1..vn t` | Define function symbol |
| `def_r n R v1..vn f` | Define relation symbol |
| `fold …` | Fold a definition back |

### Direct Proofs
| Command | Description |
|---------|-------------|
| `ua axiom formula` | Prove formula by axiom |
| `ir rule concl [p1..]` | Prove conclusion by inference rule |
| `dt theorem` | Delete a proven theorem |
| `auto formula` | Auto-prove formula |
| `search f [time] [space]` | Prove formula via forward graph search |

### Mission Management
| Command | Description |
|---------|-------------|
| `mission f` | Open a proof mission for goal f |
| `exit` | Leave child env / quit program |
| `show` | Display environment stack |

### Mission Tactics
| Command | Description |
|---------|-------------|
| `apply axiom` | Close goal using axiom |
| `apply rule p1..pn` | Close goal using rule with premises |
| `apply2 QR1\|QR2 f1` | Back-compute QR premise; change goal |
| `apply3 f1 f2` | Modus ponens backwards |
| `left f1` | Goal Ψ∨Φ → prove Ψ |
| `right f1` | Goal Ψ∨Φ → prove Φ |
| `and f1 f2` | Goal Ψ∧Φ → prove both parts |
| `imply f1 f2` | Goal Ψ⇒Φ → assume Ψ, prove Φ |
| `intro f1 v` | Goal ∀x Ψ(x) → introduce fresh var v |
| `intro f1 t1` | Goal ∃x Ψ(x) → provide witness t1 |
| `contra f1 f2 f3 f4` | Proof by contradiction |
| `force <target>` | Shortcut direct proof (not for games) |

### General-Purpose Destructuring
| Command | Description |
|---------|-------------|
| `and2 f1 f2` | Split Ψ∧Φ: redefine f1 as Ψ, create f2 as Φ |
| `intro2 f1 t1 f2` | Instantiate ∀x Ψ(x) at t1, create f2 = Ψ(t1) |

### Persistence
| Command | Description |
|---------|-------------|
| `save` | Save state to file |
| `load` | Load state from file |
| `save_h` | Save command history |
| `load_h` | Replay history file |

### Meta
| Command | Description |
|---------|-------------|
| `help` or `guide` | Show the in-program guide |

---

## 17. Worked examples

### Example 1: Proving `x = x` using E1

```
cf f1 x = x
ua E1 f1
show
```

Output: `f1` is now a proven theorem.

---

### Example 2: Proving a propositional tautology

```
cf f1 x = y ⇒ x = y
ir PC1 f1
```

→ PC1 checks: abstracting x=y as propositional variable P, the formula becomes P⇒P, which is a tautology.

---

### Example 3: Universal introduction using `intro`

Goal: prove `∀ z ( z = z )`.

```
cf g ∀ z ( z = z )
mission g
  intro f1 w
  [Goal is now f1 = (w = w)]
  apply E1
```

Mission closes. `g` is a proven theorem.

---

### Example 4: Proving a conjunction using `and`

Goal: prove `x = x ∧ y = y`.

```
cf g x = x ∧ y = y
mission g
  and left_part right_part
  [Now in nested child: goal = right_part = (y = y)]
  apply E1
  [Back in outer child: goal = left_part = (x = x)]
  apply E1
```

Both parts proven → conjunction is proven.

---

### Example 5: Implication introduction using `imply`

Goal: prove `x = y ⇒ x = y`.

```
cf g x = y ⇒ x = y
mission g
  imply concl hyp
  [concl = (x = y) is the new goal]
  [hyp = (x = y) is a proven assumption]
  apply PC1 hyp
```

Mission closes.

---

### Example 6: Using `apply2` for a QR1 goal

Goal: prove `( x = y ) ⇒ ( ∀ z ( x = y ) )`.

```
cf g ( x = y ) ⇒ ( ∀ z ( x = y ) )
mission g
  apply2 QR1 h
  [Goal is now h = ( (x=y) ⇒ (x=y) )]
  apply PC1
```

Mission closes by QR1 with premise h.

---

### Example 7: Proof by contradiction

We want to prove `x = x` by contradiction (contrived, but illustrative).

```
cf f1 x = x
cf f3 x = y
contra f1 neg_hyp f3 falsum
[Child environment]
[neg_hyp = ¬(x=x) is proven]
[Goal: falsum = ¬(x=y) ∧ (x=y)]
...build ¬(x=y) and (x=y) using available lemmas and apply and...
```

---

### Example 8: Using `and2` to split a known conjunction

```
cf f1 x = x ∧ x = x
ua E1 ...          ← prove f1 somehow
and2 f1 f2
```

→ `f1` is now `x = x` (proven), `f2` is `x = x` (proven).

---

### Example 9: Using `intro2` (universal instantiation)

```
cf f1 ∀ x ( x = x )
auto f1
ct t1 S x
intro2 f1 t1 f2
```

→ `f2` = `S x = S x` (proven by universal instantiation from `f1`).

---

*For any questions about the mathematical foundations, refer to a standard textbook on First-Order Logic and Set Theory.*

---

## 18. Game Mode (Interactive Tutorials)

The ITP includes an interactive **Game Mode** designed to teach users how to use the prover and understand mathematical foundations step-by-step. 
You can access the Game Mode by launching the Streamlit Web UI (`streamlit run app.py`) and navigating to the **Games** section.

Available games include:
- **Advanced REPL Commands**: Learn the basics of the prover, object creation, substitutions, and tactics.
- **Natural Number Game**: Build the foundations of arithmetic (addition, commutativity, additive identity) from scratch using Peano-style axioms and induction.

In Game Mode, certain commands (like `force`) are disabled, and you must strictly follow the level's objective to progress.

---

## 19. Project Structure and Guidelines

To keep the repository clean and manageable:

- **Root Directory (`/`)**: Contains the entry points for the Streamlit web app (`app.py`) and the terminal REPL (`main.py`), as well as configuration files.
- **`backend/`**: Contains all the core logic and engine source code of the Interactive Theorem Prover (e.g., `AST.py`, `Environment.py`, `Parser.py`, `BackwardSearch.py`, `ZFC_Rules.py`).
- **`games/`**: Stores the JSON configuration files for the interactive Game Mode levels.
- **`history_files/` & `logs/`**: Logs user REPL command history and runtime application logs.
- **`save_files/` & `saved_programs/`**: Stores serialized environments and user saves.
- **`scratch/`**: Contains temporary developer scripts, patches, and exploratory UI tests.
- **`tests/`**: Contains all unit tests (`test_*.py`), execution/debugging scripts (`run_tests.py`), and formal test suites.

When writing new tests or debugging scripts, **always** place them in the `tests/` or `scratch/` folder. Ensure any test runners modify `sys.path` to include the root directory so they can successfully locate and import the production modules.


### `swap_eq` and `swap_bi`
- **Syntax:** `swap_eq (occ) <target> <out> <equiv>`
- **Description:** Searches for occurrences of `=` (or `⇔` for `swap_bi`) inside the target term or formula and swaps the LHS with the RHS. If `occ` is provided, only those specific occurrences are swapped.
- **Example:**
  - `swap_eq goal` - Swaps all `=` in the goal formula.
  - `swap_eq (1,2) f1 f2 equiv1` - Swaps the 1st and 2nd occurrence of `=` in formula `f1`, saves the result as `f2`, and creates the equivalence `equiv1` (which is `f1 ⇔ f2`).
