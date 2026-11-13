with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("app.js total lines:", len(lines))
# Check if any other functions depend on sectionIndex
for i, l in enumerate(lines):
    if 'sectionIndex' in l:
        print(f"L{i+1}: {l.strip()}")
