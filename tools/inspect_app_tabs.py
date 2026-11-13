with open('app.js', 'r', encoding='utf-8') as f:
    app_lines = f.readlines()

for i, l in enumerate(app_lines):
    if 'tabReasoning' in l or 'tabQuant' in l:
        print(f"app.js line {i+1}:")
        for j in range(max(0, i-5), min(i+40, len(app_lines))):
            print(f"  {j+1}: {app_lines[j].rstrip()}")
        print("="*40)
