import json, re

data = json.load(open('data/adda_tests.json', encoding='utf-8'))['tests']

print("=" * 60)
print("AUDIT OF ALL OPTIONS ACROSS ALL 800 QUESTIONS")
print("=" * 60)

broken_options = []

for t in data:
    pid = t['id']
    for q in t['questions']:
        qnum = q['number']
        options = q['options']

        # Check for placeholder options like "Option E", "None", empty strings, or Hindi text
        for o_idx, opt in enumerate(options):
            opt_str = str(opt).strip()
            # If option has Hindi
            if re.search(r'[\u0900-\u097F]', opt_str):
                broken_options.append((pid, qnum, o_idx, f"Contains Hindi: {opt_str}"))
            # If option is generic "Option E" or "Option A"
            elif re.match(r'^Option\s+[A-E]$', opt_str, re.IGNORECASE):
                broken_options.append((pid, qnum, o_idx, f"Generic placeholder: '{opt_str}'"))
            # If option is empty or just punctuation
            elif len(opt_str) == 0 or opt_str in ['.', '-', '?', 'null']:
                broken_options.append((pid, qnum, o_idx, f"Empty/Invalid option: '{opt_str}'"))

print(f"Total problematic options found: {len(broken_options)}")
for b in broken_options:
    print(f"[{b[0]} Q{b[1]:02d}] Option {b[2]} ({'ABCDE'[b[2]]}): {b[3]}")
