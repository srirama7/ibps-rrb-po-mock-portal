# Script to inspect app.js before updating
with open('app.js', 'r', encoding='utf-8') as f:
    text = f.read()

print("Original app.js length:", len(text))
print("Original lines:", len(text.splitlines()))
