with open('adda.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(480, 560):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}", end="")
