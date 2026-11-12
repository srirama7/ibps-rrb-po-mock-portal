import os, pypdf, re

CACHE_DIR = r"C:\Users\amogh\ibps-rrb-portal-upgrade\tools\pdf_cache"

for pid in ["adda-09", "adda-10"]:
    pdf_path = os.path.join(CACHE_DIR, f"{pid}.pdf")
    reader = pypdf.PdfReader(pdf_path)
    print(f"\n==================== {pid} ====================")
    for p_idx in range(20, len(reader.pages)):
        text = reader.pages[p_idx].extract_text() or ''
        lines = [line.strip() for line in text.split('\n') if any(w in line.lower() for w in ['direction', 'table', 'chart', 'graph', 'bar', 'pie', 'line'])]
        if lines:
            print(f"Page {p_idx+1}:")
            for l in lines[:5]:
                print(f"   {l}")
