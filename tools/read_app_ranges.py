with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("app.js lines 100-140:")
for i in range(99, 135):
    print(f"{i+1}: {lines[i]}", end="")

print("\n" + "="*40 + "\napp.js lines 600-640:")
for i in range(599, 640):
    print(f"{i+1}: {lines[i]}", end="")
