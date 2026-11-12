import os, pypdf, re

CACHE_DIR = r"C:\Users\amogh\ibps-rrb-portal-upgrade\tools\pdf_cache"

for i in range(1, 11):
    pid = f"adda-{i:02d}"
    pdf_path = os.path.join(CACHE_DIR, f"{pid}.pdf")
    reader = pypdf.PdfReader(pdf_path)
    
    print(f"\n==================== {pid} ====================")
    for p_idx, page in enumerate(reader.pages):
        text = page.extract_text() or ''
        # Look for Directions in the page
        matches = re.finditer(r'(?:Directions?|Direction)\s*[\(\[]?(\d+)\s*[-–to]+\s*(\d+)[\)\]]?([^\.\n\r]+[\.\n\r])', text, re.IGNORECASE)
        for m in matches:
            q_start = int(m.group(1))
            q_end = int(m.group(2))
            snippet = m.group(0).replace('\n', ' ')[:100]
            print(f"Page {p_idx+1}: Q{q_start}-Q{q_end}: {snippet}")
