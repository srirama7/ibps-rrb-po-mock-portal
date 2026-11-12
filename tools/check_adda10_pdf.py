import pypdf, json, os

REPO_ROOT = r"C:\Users\amogh\ibps-rrb-portal-upgrade"

# Inspect adda-10.json Q70-Q80
with open(os.path.join(REPO_ROOT, "data/licensed_adda/adda-10.json"), encoding='utf-8') as f:
    d = json.load(f)

print("=== ADDA-10.JSON Q71-Q80 ===")
for q in d['questions']:
    if q['number'] >= 71:
        print(f"Q{q['number']}:")
        print("  STEM:", repr(q['stem'][:120]))
        print("  OPTIONS:", q['options'])
        print("  ANS_INDEX:", q['answerIndex'])
        print("  DIAGRAMS:", q.get('diagrams'))
        print("  CAPTION:", q.get('diagramCaption'))
        print("  EXPLANATION:", repr(q.get('explanation', '')[:100]))

# Inspect PDF pages around page 28-35 of adda-10.pdf
pdf_path = os.path.join(REPO_ROOT, r"tools\pdf_cache\adda-10.pdf")
reader = pypdf.PdfReader(pdf_path)
print("\n=== PDF PAGE COUNT ===", len(reader.pages))
for p in range(25, min(36, len(reader.pages))):
    text = reader.pages[p].extract_text() or ''
    # find question numbers on page
    q_matches = [line for line in text.split('\n') if any(line.strip().startswith(f"Q{n}.") or line.strip().startswith(f"{n}.") for n in range(60, 81))]
    print(f"Page {p+1}: {len(text)} chars | Qs detected: {q_matches[:5]}")
