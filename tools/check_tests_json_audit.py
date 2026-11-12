import json, os

REPO_ROOT = r"C:\Users\amogh\ibps-rrb-portal-upgrade"
with open(os.path.join(REPO_ROOT, "data/adda_tests.json"), encoding='utf-8') as f:
    tests = json.load(f)['tests']

for t in tests:
    pid = t['id']
    if pid in ['adda-08', 'adda-09', 'adda-10']:
        print(f"\n================= {pid} =================")
        print(f"Total Qs: {len(t['questions'])}")
        diags_cnt = sum(len(q.get('diagrams', [])) for q in t['questions'])
        tables_cnt = sum(1 for q in t['questions'] if '|---|' in q['stem'])
        print(f"Diagram references: {diags_cnt}, Rendered tables: {tables_cnt}")
        for q in t['questions']:
            num = q['number']
            if num in [41, 46, 51, 56, 64, 66, 71, 76]:
                print(f"  Q{num}: diags={q.get('diagrams')}, table={'|---|' in q['stem']}, caption={q.get('diagramCaption')}")
                if num in [76, 78] and pid == 'adda-10':
                    print("    Options:", q['options'])
                    print("    ans_idx:", q['answerIndex'])
