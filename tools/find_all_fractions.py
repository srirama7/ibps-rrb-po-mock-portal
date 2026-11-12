import json, re

data = json.load(open('data/adda_tests.json', encoding='utf-8'))['tests']

fraction_patterns = []

for t in data:
    for q in t['questions']:
        for field, text in [('stem', q['stem']), ('expl', q['explanation'])]:
            # Look for fraction patterns like 33 1/3, 5/9, 7/12th, \frac, etc.
            matches = re.findall(r'(\d+\s+\d+/\d+|\b\d+/\d+(?:th|nd|rd|st)?\b|\\frac\{[^}]+\}\{[^}]+\})', text)
            if matches:
                fraction_patterns.extend([(t['id'], q['number'], field, m) for m in matches])

print(f"Total fraction occurrences found: {len(fraction_patterns)}")
sample = fraction_patterns[:30]
for s in sample:
    print(f"  {s[0]} Q{s[1]} ({s[2]}): {s[3]}")
