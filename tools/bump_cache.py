with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('?v=7', '?v=8')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated index.html to ?v=8!")
