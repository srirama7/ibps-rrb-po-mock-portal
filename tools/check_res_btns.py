with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'retakeBtn' in l or 'backToAllMocks' in l:
        print(f"L{i+1}: {l}")
        for j in range(max(0, i-5), min(len(lines), i+6)):
            print(f"  {j+1}: {lines[j].rstrip()}")
