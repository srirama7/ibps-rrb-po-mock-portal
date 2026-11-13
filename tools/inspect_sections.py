import re

with open('app.js', 'r', encoding='utf-8') as f:
    app_text = f.read()

print("--- APP.JS SECTIONS ---")
for line in app_text.split('\n'):
    if 'section-tab' in line or 'switchSection' in line or 'sectionIndex' in line:
        print(line)

with open('adda.js', 'r', encoding='utf-8') as f:
    adda_text = f.read()

print("\n--- ADDA.JS ACTIVE TEST STATE ---")
for line in adda_text.split('\n'):
    if 'sectionIndex' in line or 'sectionEndAt' in line or 'startTest' in line:
        print(line)
