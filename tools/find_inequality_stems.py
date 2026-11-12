import json

data = json.load(open('data/adda_tests.json', encoding='utf-8'))['tests']

for t in data:
    for q in t['questions']:
        if q['number'] == 8 or 'relationships between different elements' in q['stem']:
            print(f"[{t['id']} Q{q['number']:02d}]")
            print("STEM:")
            print(q['stem'])
            print("EXPL:")
            print(q['explanation'][:150])
            print("-" * 50)
