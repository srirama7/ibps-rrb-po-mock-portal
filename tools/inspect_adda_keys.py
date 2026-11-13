with open('adda.js', 'r', encoding='utf-8') as f:
    text = f.read()

print("Length of adda.js:", len(text), "chars")
# Print section navigation, timer, active state handling, submit and result rendering
print("Keys in localStorage used in adda.js:")
import re
for m in re.finditer(r'localStorage\.[a-zA-Z]+[(][^)]+[)]', text):
    print(" ", m.group(0))
