def move():
    with open('/Users/ritilranjan/ITP/main.py', 'r') as f:
        lines = f.readlines()
    
    start_idx = -1
    end_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('def show_environment'):
            start_idx = i
        elif start_idx != -1 and line.startswith('def validate_new_name'):
            end_idx = i
            break
            
    if start_idx == -1 or end_idx == -1:
        print("Could not find bounds")
        return
        
    func_lines = lines[start_idx:end_idx]
    
    with open('/Users/ritilranjan/ITP/Frontend.py', 'a') as f:
        f.write('\n')
        f.writelines(func_lines)
        
    new_lines = lines[:start_idx] + lines[end_idx:]
    with open('/Users/ritilranjan/ITP/main.py', 'w') as f:
        f.writelines(new_lines)

if __name__ == "__main__":
    move()
