import json

transcript_file = '/Users/ritilranjan/.gemini/antigravity-ide/brain/c1ebe070-7021-465f-a667-cfb0e82f8429/.system_generated/logs/transcript_full.jsonl'
lines = []

with open(transcript_file, 'r') as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get('source') == 'MODEL' and data.get('type') == 'VIEW_FILE':
                content = data.get('content', '')
                if 'Showing lines 450 to 500' in content:
                    lines.append(content)
                elif 'Showing lines 500 to 550' in content or 'Showing lines 500 to 577' in content:
                    lines.append(content)
        except:
            pass

with open('scratch/def_expand.txt', 'w') as f:
    f.write("\n".join(lines))
