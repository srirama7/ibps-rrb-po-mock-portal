with open('app.js', 'r', encoding='utf-8') as f:
    app_lines = f.readlines()

for j in range(430, 520):
    if j < len(app_lines):
        print(f"  {j+1}: {app_lines[j].rstrip()}")
