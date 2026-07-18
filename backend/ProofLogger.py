"""
ProofLogger.py — Foundational Proof Step Logger

Writes every proven theorem to proofs.html in formal sequent notation:

    premise1name: premise1_definition, ... ⊢ conclusion_name: conclusion_definition  (justification)

Each justification names the exact primitive axiom or rule used, so a human
can verify that even advanced tactics ultimately rest on the fundamental axioms
E1–E3, Q1–Q2, QR1–QR2, PC1–PC2 and the ZFC axioms.

For Tier-3 search commands (backward_search, forward_search, auto), a single
summary line is written.  Full sub-step traces for those can be added later.
"""

import sys
import os
from typing import List, Tuple, Optional
from backend.Parser import reconstruct_string
from backend.AST import Node


class ProofLogger:
    """Singleton proof-step logger.  Opened once at startup and closed on exit."""

    def __init__(self):
        self.enabled: bool = False
        self.use_streamlit: bool = False
        self.filename = None

    # ------------------------------------------------------------------ #
    #  Life-cycle                                                          #
    # ------------------------------------------------------------------ #

    def open(self, filename: str = "proofs.md", use_streamlit: bool = False) -> None:
        """Initialize the proof log."""
        self.enabled = True
        self.use_streamlit = use_streamlit
        self.filename = filename
        
        if self.use_streamlit:
            import streamlit as st
            if "proofs_html" not in st.session_state:
                st.session_state.proofs_html = "# Foundational Proof Log\n**Format**: `premise1: def, ... ⊢ conclusion: def  (justification)`\n\n---\n"
        else:
            with open(self.filename, "w", encoding="utf-8") as f:
                f.write("# Foundational Proof Log\n**Format**: `premise1: def, ... ⊢ conclusion: def  (justification)`\n\n---\n")

    def close(self) -> None:
        """Disable logging."""
        self.enabled = False

    # ------------------------------------------------------------------ #
    #  Core logging                                                        #
    # ------------------------------------------------------------------ #

    def log(
        self,
        premises: List[Tuple[str, Node]],
        conclusion_name: str,
        conclusion_node: Node,
        justification: str,
    ) -> None:
        if not self.enabled:
            return

        try:
            parts = []
            for name, node in premises:
                color_mode = 'html' if self.use_streamlit else 'ansi'
                parts.append(f"{name}: {reconstruct_string(node, color_mode=color_mode)}")

            lhs = ", ".join(parts) + " " if parts else ""
            rhs = f"{conclusion_name}: {reconstruct_string(conclusion_node, color_mode=color_mode if self.use_streamlit else 'ansi')}"
            
            if self.use_streamlit:
                import streamlit as st
                line = f"{lhs}⊢ {rhs}  ({justification})<br>\n"
                if "proofs_html" in st.session_state:
                    st.session_state.proofs_html += line
            else:
                line = f"{lhs}⊢ {rhs}  ({justification})\n"
                if self.filename:
                    with open(self.filename, "a", encoding="utf-8") as f:
                        f.write(line)
        except Exception as e:
            # Never let logging crash the prover
            print(f"[ProofLogger] Warning: failed to write step: {e}", file=sys.stderr)

    # ------------------------------------------------------------------ #
    #  Convenience helpers (call from main.py at each proof site)         #
    # ------------------------------------------------------------------ #

    def log_axiom(self, conclusion_name: str, conclusion_node: Node, axiom_name: str) -> None:
        """Log a direct axiom application (no premises)."""
        self.log([], conclusion_name, conclusion_node, f"axiom: {axiom_name}")

    def log_rule(
        self,
        premises: List[Tuple[str, Node]],
        conclusion_name: str,
        conclusion_node: Node,
        rule_name: str,
        note: str = "",
    ) -> None:
        """Log an inference-rule application."""
        justification = f"rule: {rule_name}"
        if note:
            justification += f" ({note})"
        self.log(premises, conclusion_name, conclusion_node, justification)

    def log_summary(self, conclusion_name: str, conclusion_node: Node, method: str) -> None:
        """Log a Tier-3 compound search / auto proof as a single summary line."""
        self.log([], conclusion_name, conclusion_node, method)


# ─────────────────────────────────────────────────────────────────────────────
# Global singleton used throughout main.py
# ─────────────────────────────────────────────────────────────────────────────
proof_logger = ProofLogger()
