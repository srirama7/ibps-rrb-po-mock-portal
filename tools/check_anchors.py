import re

with open('adda.js', 'r', encoding='utf-8') as f:
    old_code = f.read()

# Let's inspect the exact lines to replace
print("Reading old adda.js...")
assert 'function syncDeadline' in old_code
assert 'function renderExam' in old_code
assert 'function goTo' in old_code
assert 'function submitTest' in old_code
assert 'function showResult' in old_code
print("All core anchor functions found in adda.js!")
