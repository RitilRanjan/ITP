import sys
from typing import Dict, Tuple, List, Any
from AST import FormulaNode
from Frontend import reconstruct_string

def clause_to_string(clause: List[FormulaNode]) -> str:
    if not clause:
        return "□ (Empty Clause)"
    lits = [reconstruct_string(l) for l in clause]
    return " ∨ ".join(lits)

class ProofGenerator:
    def __init__(self, clause_history: Dict[int, Tuple[str, Tuple[int, ...], List[FormulaNode]]], empty_clause_id: int):
        self.clause_history = clause_history
        self.empty_clause_id = empty_clause_id

    def generate_proof(self) -> str:
        if self.empty_clause_id not in self.clause_history:
            return "Error: Empty clause ID not found in history."

        # 1. Backtrack to find all relevant clause IDs
        relevant_ids = set()
        stack = [self.empty_clause_id]
        
        while stack:
            curr_id = stack.pop()
            if curr_id not in relevant_ids:
                relevant_ids.add(curr_id)
                op, parents, clause = self.clause_history[curr_id]
                for p in parents:
                    stack.append(p)

        # 2. Topological sort of relevant_ids
        visited = set()
        topo_order = []
        
        def dfs(node_id):
            if node_id in visited:
                return
            visited.add(node_id)
            op, parents, clause = self.clause_history[node_id]
            for p in parents:
                dfs(p)
            topo_order.append(node_id)

        for curr_id in relevant_ids:
            if curr_id not in visited:
                dfs(curr_id)

        # 3. Format the proof
        proof_lines = []
        proof_lines.append("--- Resolution Proof ---")
        
        # Map IDs to step numbers
        id_to_step = {}
        for step_num, node_id in enumerate(topo_order, 1):
            id_to_step[node_id] = step_num
            op, parents, clause = self.clause_history[node_id]
            
            parent_steps = [str(id_to_step[p]) for p in parents]
            parent_str = f" [from {', '.join(parent_steps)}]" if parent_steps else ""
            
            proof_lines.append(f"{step_num}. {clause_to_string(clause)}")
            proof_lines.append(f"   Reason: {op}{parent_str}")
        
        proof_lines.append("--- End of Proof ---")
        return "\n".join(proof_lines)

    def get_structured_proof(self) -> List[Tuple[int, str, Tuple[int, ...], List[FormulaNode]]]:
        if self.empty_clause_id not in self.clause_history:
            return []

        relevant_ids = set()
        stack = [self.empty_clause_id]
        
        while stack:
            curr_id = stack.pop()
            if curr_id not in relevant_ids:
                relevant_ids.add(curr_id)
                op, parents, clause = self.clause_history[curr_id]
                for p in parents:
                    stack.append(p)

        visited = set()
        topo_order = []
        
        def dfs(node_id):
            if node_id in visited:
                return
            visited.add(node_id)
            op, parents, clause = self.clause_history[node_id]
            for p in parents:
                dfs(p)
            topo_order.append(node_id)

        for curr_id in relevant_ids:
            if curr_id not in visited:
                dfs(curr_id)

        structured = []
        for node_id in topo_order:
            op, parents, clause = self.clause_history[node_id]
            structured.append((node_id, op, parents, clause))
            
        return structured
