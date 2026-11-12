import json, re

data = json.load(open('data/adda_tests.json', encoding='utf-8'))['tests']

target_sets = [
    ("adda-04", 46, 50),
    ("adda-06", 41, 46),
    ("adda-08", 41, 45),
    ("adda-09", 51, 55),
    ("adda-10", 64, 68),
]

for pid, qstart, qend in target_sets:
    test = [t for t in data if t['id'] == pid][0]
    print(f"\n=================== {pid} (Q{qstart}-Q{qend}) ===================")
    for q in test['questions']:
        if qstart <= q['number'] <= qend:
            print(f"--- Q{q['number']} ---")
            print("STEM:")
            print(q['stem'][:250])
            print("DIAGRAMS:", q.get('diagrams', []))
            print("EXPL:")
            print(q['explanation'][:150])
            print()
