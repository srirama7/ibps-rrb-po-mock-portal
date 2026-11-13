with open('app.js', 'r', encoding='utf-8') as f:
    app_lines = f.readlines()

for i, l in enumerate(app_lines):
    if 'function startTest' in l or 'syncDeadline' in l or 'function goTo' in l:
        print(f"app.js line {i+1}: {l.strip()}")
        for j in range(i, min(i+35, len(app_lines))):
            print(f"  {j+1}: {app_lines[j].rstrip()}")
        print("="*40)

with open('adda.js', 'r', encoding='utf-8') as f:
    adda_lines = f.readlines()

for i, l in enumerate(adda_lines):
    if 'function startTest' in l or 'syncDeadline' in l or 'function goTo' in l:
        print(f"adda.js line {i+1}: {l.strip()}")
        for j in range(i, min(i+35, len(adda_lines))):
            print(f"  {j+1}: {adda_lines[j].rstrip()}")
        print("="*40)
