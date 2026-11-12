import json

with open(r"C:\Users\amogh\ibps-rrb-portal-upgrade\data\licensed_adda\adda-07.json", encoding="utf-8") as f:
    d = json.load(f)

for q in d["questions"]:
    if 55 <= q["number"] <= 75:
        print(f"Q{q['number']}: stem={repr(q['stem'][:70])}")
        print(f"   diags={q.get('diagrams')}")
        print(f"   options={q['options']}")
        print(f"   ans={q['answerIndex']}")
        print(f"   expl={repr(q['explanation'][:70])}")
