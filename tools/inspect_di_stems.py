import json

data = json.load(open('data/adda_tests.json', encoding='utf-8'))['tests']
for t in data:
    print('===', t['id'], '===')
    for q in t['questions'][40:55]:
        print(f"Q{q['number']}: {q['stem'][:100]} | diagrams: {len(q.get('diagrams', []))}")
