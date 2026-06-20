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
from typing import List, Tuple, Optional
from Frontend import reconstruct_string
from AST import Node


class ProofLogger:
    """Singleton proof-step logger.  Opened once at startup and closed on exit."""

    def __init__(self):
        self.enabled: bool = False
        self._file = None

    # ------------------------------------------------------------------ #
    #  Life-cycle                                                          #
    # ------------------------------------------------------------------ #

    def open(self, filename: str = "proofs.md") -> None:
        """Create/truncate the proof file and enable logging."""
        try:
            self._file = open(filename, "w", encoding="utf-8")
            self.enabled = True
            self._file.write("# Foundational Proof Log\n")
            self._file.write("**Format**: `premise1: def, ... ⊢ conclusion: def  (justification)`\n\n")
            self._file.write("---\n")
            self._file.flush()
        except OSError as e:
            print(f"[ProofLogger] Warning: could not open '{filename}': {e}", file=sys.stderr)
            self.enabled = False

    def close(self) -> None:
        """Flush and close the proof file."""
        if self._file is not None:
            try:
                self._file.flush()
                self._file.close()
            except OSError:
                pass
            self._file = None
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
        if not self.enabled or self._file is None:
            return

        try:
            parts = []
            for name, node in premises:
                parts.append(f"{name}: {reconstruct_string(node, color_mode='html')}")

            lhs = ", ".join(parts) + " " if parts else ""
            rhs = f"{conclusion_name}: {reconstruct_string(conclusion_node, color_mode='html')}"
            line = f"{lhs}⊢ {rhs}  ({justification})<br>\n"

            self._file.write(line)
            self._file.flush()
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
