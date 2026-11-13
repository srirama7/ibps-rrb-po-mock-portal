with open('app.js', 'r', encoding='utf-8') as f:
    app_lines = f.readlines()

for i, l in enumerate(app_lines):
    if 'function submitTest' in l or 'function renderResult' in l or 'function enterHome' in l:
        print(f"app.js line {i+1}: {l.strip()}")
        for j in range(i, min(i+35, len(app_lines))):
            print(f"  {j+1}: {app_lines[j].rstrip()}")
        print("="*40)
