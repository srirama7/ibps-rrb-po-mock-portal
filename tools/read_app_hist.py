with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'function history' in l or 'storeHistory' in l or 'function showResult' in l or 'function renderResult' in l:
        print(f"L{i+1}: {l.strip()}")
        for j in range(i, min(i+25, len(lines))):
            print(f"  {j+1}: {lines[j].rstrip()}")
        print("="*40)
