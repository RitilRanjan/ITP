import re

def parse_pattern_structure(pattern):
    res = []
    i = 0
    while i < len(pattern):
        if pattern[i] == '?(':
            scope = []
            i += 1
            while i < len(pattern) and not re.match(r'^\)r\d+$', pattern[i]):
                scope.append(pattern[i])
                i += 1
            if i < len(pattern):
                index = int(pattern[i][2:])
                res.append(('rep', scope, index))
            i += 1
        else:
            res.append(pattern[i])
            i += 1
    return res

def get_placeholders_from_struct(struct):
    placeholders = []
    for el in struct:
        if isinstance(el, tuple) and el[0] == 'rep':
            scope_ph = get_placeholders_from_struct(el[1])
            placeholders.append(('rep', scope_ph, el[2]))
        else:
            if el.startswith('?'):
                placeholders.append(el)
    return placeholders

def map_flat_nodes_to_pattern(flat_nodes, f1_pattern):
    struct = parse_pattern_structure(f1_pattern)
    ph_struct = get_placeholders_from_struct(struct)
    
    # Check if there is more than 1 rep
    reps = [p for p in ph_struct if isinstance(p, tuple) and p[0] == 'rep']
    if len(reps) > 1:
        raise ValueError("Cannot map to a replacement pattern with more than 1 repetition block.")
        
    term_placeholders = {}
    var_placeholders = {}
    formula_placeholders = {}
    repetition_counts = {}
    
    node_idx = 0
    
    def process_ph_list(ph_list, is_rep=False, rep_count=1, rep_idx=None):
        nonlocal node_idx
        for i in range(rep_count):
            for ph in ph_list:
                if isinstance(ph, tuple) and ph[0] == 'rep':
                    scope_size = len(ph[1])
                    if scope_size == 0: continue
                    nodes_left = len(flat_nodes) - node_idx
                    # nodes required after this rep block
                    after_ph = get_placeholders_from_struct(ph_list[ph_list.index(ph)+1:])
                    after_size = len(after_ph)
                    if (nodes_left - after_size) % scope_size != 0:
                        raise ValueError("Placeholder count mismatch!")
                    count = (nodes_left - after_size) // scope_size
                    if count < 0: raise ValueError("Not enough nodes for replacement.")
                    repetition_counts[ph[2]] = count
                    process_ph_list(ph[1], is_rep=True, rep_count=count, rep_idx=ph[2])
                else:
                    node = flat_nodes[node_idx]
                    node_idx += 1
                    if ph.startswith('?t') or ph.startswith('?u'):
                        d = term_placeholders
                    elif ph.startswith('?v'):
                        d = var_placeholders
                    elif ph.startswith('?f'):
                        d = formula_placeholders
                    else:
                        raise ValueError(f"Unknown placeholder {ph}")
                        
                    if is_rep:
                        if ph not in d: d[ph] = []
                        d[ph].append(node)
                    else:
                        d[ph] = node
                        
    process_ph_list(ph_struct)
    if node_idx != len(flat_nodes):
        raise ValueError("Not all nodes were consumed.")
        
    return term_placeholders, var_placeholders, formula_placeholders, repetition_counts

pattern = ["?t1", "?(", "?t2_", ")r1", "?t3"]
nodes = ["A", "B", "C", "D", "E"]
print(map_flat_nodes_to_pattern(nodes, pattern))
def extract_flat_nodes(pattern, term_placeholders, repetition_counts):
    struct = parse_pattern_structure(pattern)
    ph_struct = get_placeholders_from_struct(struct)
    
    flat_nodes = []
    
    def process_ph_list(ph_list, is_rep=False, rep_count=1, rep_idx=None):
        for i in range(rep_count):
            for ph in ph_list:
                if isinstance(ph, tuple) and ph[0] == 'rep':
                    count = repetition_counts.get(ph[2], 0)
                    process_ph_list(ph[1], is_rep=True, rep_count=count, rep_idx=ph[2])
                else:
                    if ph.startswith('?t') or ph.startswith('?u'):
                        val = term_placeholders.get(ph)
                    
                    if is_rep:
                        flat_nodes.append(val[i])
                    else:
                        flat_nodes.append(val)
                        
    process_ph_list(ph_struct)
    return flat_nodes

extracted = extract_flat_nodes(["?t1", "?(", "?t2_", ")r1", "?t3"], {'?t1': 'A', '?t2_': ['B', 'C', 'D'], '?t3': 'E'}, {1: 3})
print("Extracted:", extracted)
