# Implementation Plan: Priority for Terms and Formulas

## User Review Required
Please review the proposed approach for parsing priorities and disambiguating `ct` / `cf` commands.

## Open Questions
- When a short term/formula has a priority, should it be matched during the "highest priority long/short terms" phase? (My plan assumes YES, treating them as 1-token patterns during the priority matching phase).
- Should pre-defined constants and relations (like `=`, `∈`, `S`, `0`) also be integrated into this priority system (default priority 0)? (My plan assumes YES).

## Proposed Changes

### `backend/AST.py`
- Modify `Constant` to include an optional `priority` field (default 0).
- Modify `LongTerm` and `LongFormula` to include an optional `priority` field (default 0).
- Modify `Connective` and other predefined tokens to support `priority` where applicable, or handle their priority mapping in the `Environment` / `Parser`.

### `backend/CommandHandlers/env_handlers.py`
- **Argument Disambiguation for `ct` and `cf`**:
  - **No quotes**: It's a short term/formula.
    - If 2 arguments: `ct <name> <definition>` (priority = 0).
    - If 3 arguments: `ct <priority> <name> <definition>`. (We will try to parse the first argument as an integer. If it is an integer, it's priority, else throw an error).
  - **With quotes**: It's a long term/formula.
    - Parse everything before `"`:
      - 1 argument: `<identifier>` (priority = 0).
      - 2 arguments: `<identifier> <priority>`.
    - Inside `"`: `<pattern>`.
    - After `"`:
      - 0 arguments: definition-less schema.
      - 1+ arguments: `<definition>`.

### `backend/Environment.py`
- Pre-defined terms/formulas (like `S`, `0`, `=`, `∈`, logical connectives) will be assigned a default priority of 0.

### `backend/Parser.py`
- Update `__init__` to build the `prefix_patterns` and `infix_patterns` lists by including:
  - `LongTerm` and `LongFormula` patterns with their respective `priority`.
  - Short terms (macros) and Short formulas as 1-token patterns with their respective `priority`.
  - Sort these patterns first by `priority` (descending), then by `length` (descending).
- Modify `parse_prefix` and `parse_expr` to respect this sorted order. Since short terms are now in the `prefix_patterns`, `try_match_pattern` will need to support returning a `Constant` (or the expanded macro) when a 1-token short pattern is matched.

## Verification Plan
- Create test cases combining long terms and short terms with different priorities.
- Verify that a priority 1 short term matches before a priority 0 long term.
