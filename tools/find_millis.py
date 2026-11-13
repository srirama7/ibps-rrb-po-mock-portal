with open('app.js', 'r', encoding='utf-8') as f:
    text = f.read()

for line in text.split('\n'):
    if 'function millisLeft' in line or 'millisLeft' in line:
        print(line)
