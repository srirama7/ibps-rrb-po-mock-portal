import pymupdf as fitz
import json, os

REPO_ROOT = r"C:\Users\amogh\ibps-rrb-portal-upgrade"

# adda-08 Q41-Q45
with open(os.path.join(REPO_ROOT, "data/licensed_adda/adda-08.json"), encoding='utf-8') as f:
    d8 = json.load(f)

print("=== ADDA-08 Q41-Q45 ===")
for q in d8['questions']:
    if 41 <= q['number'] <= 45:
        print(f"Q{q['number']}:")
        print("  STEM:", repr(q['stem']))
        print("  DIAGRAMS:", q.get('diagrams'))
        print("  CAPTION:", q.get('diagramCaption'))
        print("  EXPLANATION:", repr(q.get('explanation')[:100]))
