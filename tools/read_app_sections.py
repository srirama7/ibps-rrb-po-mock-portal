with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("app.js lines 70-130:")
for i in range(70, 130):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}", end="")

print("\n" + "="*40)
print("app.js lines 235-275:")
for i in range(235, 275):
    if i < len(lines):
        print(f"{i+1}: {lines[i]}", end="")
