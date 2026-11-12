import json, re

data = json.load(open('data/adda_tests.json', encoding='utf-8'))['tests']

print("=" * 60)
print("AUDIT FOR GENERIC / MISSING QUESTION CONTENT")
print("=" * 60)

missing_content = []

for t in data:
    pid = t['id']
    for q in t['questions']:
        qnum = q['number']
        stem = q['stem'].strip()
        diags = q.get('diagrams', [])
        has_table = '|---|' in stem

        # 1. Inequality questions missing Statements / Conclusions
        if 'relationships between different elements' in stem.lower() or 'conclusions based on the given statements' in stem.lower():
            if 'statements' not in stem.lower() or 'conclusions' not in stem.lower() or len(stem) < 250:
                # Check if it has a diagram image attached
                if not diags:
                    missing_content.append((pid, qnum, "Inequality missing statements/conclusions and has NO image"))

        # 2. Syllogism missing statements/conclusions
        if 'commonly known facts' in stem.lower():
            if 'statements:' not in stem.lower() or 'conclusions:' not in stem.lower():
                if not diags:
                    missing_content.append((pid, qnum, "Syllogism missing statements/conclusions and has NO image"))

        # 3. Approximation missing equation
        if 'approximate value should come in place of' in stem.lower():
            has_eq = any(c in stem for c in ['=', '+', '-', '×', '÷', '%', '²'])
            if not has_eq and not diags:
                missing_content.append((pid, qnum, "Approximation missing equation and has NO image"))

        # 4. Quadratic equations missing I. and II. equations
        if 'two equations are given' in stem.lower() or 'two equations (i) and (ii)' in stem.lower():
            has_eq = ('i.' in stem.lower() and 'ii.' in stem.lower()) or any(c in stem for c in ['=', '²', 'x', 'y'])
            if ('i.' not in stem.lower() or 'ii.' not in stem.lower()) and not diags:
                missing_content.append((pid, qnum, "Quadratic missing equation I & II and has NO image"))

print(f"Total questions with missing content: {len(missing_content)}")
for m in missing_content:
    print(f"[{m[0]} Q{m[1]:02d}] {m[2]}")
