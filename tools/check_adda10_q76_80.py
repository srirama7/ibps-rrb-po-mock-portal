import json, os, pymupdf as fitz

REPO_ROOT = r"C:\Users\amogh\ibps-rrb-portal-upgrade"

# adda-10
with open(os.path.join(REPO_ROOT, "data/licensed_adda/adda-10.json"), encoding='utf-8') as f:
    d10 = json.load(f)

for q in d10['questions']:
    if q['number'] in range(76, 81):
        print(f"Q{q['number']}:")
        print("  Options in json:", q['options'])
        print("  answerIndex in json:", q['answerIndex'], "->", q['options'][q['answerIndex']])
        print("  Explanation:", q['explanation'][:100])
