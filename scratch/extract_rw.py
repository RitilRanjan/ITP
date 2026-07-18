import json

transcript_file = '/Users/ritilranjan/.gemini/antigravity-ide/brain/c1ebe070-7021-465f-a667-cfb0e82f8429/.system_generated/logs/transcript_full.jsonl'
lines = []

with open(transcript_file, 'r') as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get('source') == 'MODEL' and data.get('type') == 'PLANNER_RESPONSE':
                for tool in data.get('tool_calls', []):
                    if tool['name'] == 'run_command':
                        cmd = tool['args'].get('CommandLine', '')
                        if 'cat << \'EOF\' > rw_updater.py' in cmd:
                            lines.append(cmd)
        except:
            pass

if lines:
    with open('scratch/found_rw.py', 'w') as f:
        f.write(lines[-1])
    print("Found and wrote to scratch/found_rw.py")
else:
    print("Not found.")
