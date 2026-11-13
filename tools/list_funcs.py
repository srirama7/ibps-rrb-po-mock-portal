with open('adda.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines in adda.js: {len(lines)}")
# Find all function declarations
for idx, line in enumerate(lines):
    if line.strip().startswith('function ') or ' = function' in line:
        print(f"Line {idx+1}: {line.strip()}")
