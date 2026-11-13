with open('adda.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(330, 485):
    print(f"{i+1}: {lines[i]}", end="")
