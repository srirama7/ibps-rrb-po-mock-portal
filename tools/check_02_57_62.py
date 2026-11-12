import json

data = json.load(open('data/adda_tests.json', encoding='utf-8'))['tests']
t2 = [t for t in data if t['id'] == 'adda-02'][0]
for q in t2['questions'][56:62]:
    print(f"=== Q{q['number']} ===")
    print(q['stem'][:200])
