with open('adda.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(50, 207):
    print(f"{i+1}: {lines[i]}", end="")
