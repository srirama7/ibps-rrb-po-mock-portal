import json

data = json.load(open('data/adda_tests.json', encoding='utf-8'))['tests']

for t in data:
    pid = t['id']
    broken_q = []
    for q in t['questions']:
        opts = [str(o) for o in q['options']]
        if any(o.startswith('Option ') for o in opts):
            broken_q.append(q['number'])
    print(f"{pid}: {len(broken_q)} questions with 'Option [A-E]' -> {broken_q[:15]}...")
