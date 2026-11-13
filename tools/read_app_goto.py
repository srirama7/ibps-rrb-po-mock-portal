with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("app.js lines 515-555:")
for i in range(515, 555):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}", end="")
