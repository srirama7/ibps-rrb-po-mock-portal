import json

data = json.load(open('data/adda_tests.json', encoding='utf-8'))['tests']

short_stems = []
for t in data:
    for q in t['questions']:
        stem = q['stem'].strip()
        lines = [l.strip() for l in stem.split('\n') if l.strip()]
        # Check if stem is just the generic question without equation
        if len(stem) < 130 and any(w in stem.lower() for w in ['approximate value', 'two equations', 'what will come in the place of']):
            # Check if there is an equation
            has_eq = any(c in stem for c in ['=', '+', '-', '×', '÷', '%', '²'])
            if not has_eq:
                short_stems.append((t['id'], q['number'], stem))

print(f"Total questions missing equations in stem: {len(short_stems)}")
for s in short_stems:
    print(f"[{s[0]} Q{s[1]:02d}] {s[2]}")
