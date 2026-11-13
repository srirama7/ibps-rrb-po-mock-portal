with open('app.js', 'r', encoding='utf-8') as f:
    app_text = f.read()

for line in app_text.split('\n'):
    if 'tabReasoning' in line or 'tabQuant' in line:
        print(line)

with open('adda.js', 'r', encoding='utf-8') as f:
    adda_text = f.read()

for line in adda_text.split('\n'):
    if 'section-tab' in line or 'switchSection' in line:
        print(line)
