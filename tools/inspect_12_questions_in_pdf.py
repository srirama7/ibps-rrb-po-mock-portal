import os, pypdf, re

CACHE_DIR = r"tools\pdf_cache"

targets = [
    ("adda-03", [6, 7, 8]),
    ("adda-04", [66]),
    ("adda-08", [62]),
    ("adda-09", [6, 7, 8]),
    ("adda-10", [2, 3, 4, 5]),
]

for pid, qnums in targets:
    pdf_path = os.path.join(CACHE_DIR, f"{pid}.pdf")
    reader = pypdf.PdfReader(pdf_path)
    full_text = "\n".join([f"--- PAGE {idx+1} ---\n" + (p.extract_text() or '') for idx, p in enumerate(reader.pages)])
    print(f"\n=================== {pid} ===================")
    for qn in qnums:
        m = re.search(rf'Q\s*\.?\s*{qn}\b(.*?)(?=Q\s*\.?\s*{qn+1}\b|Directions\s*\(|\Z)', full_text, re.DOTALL | re.IGNORECASE)
        if m:
            print(f"--- Q{qn} text in PDF ---")
            lines = [l.strip() for l in m.group(1).split('\n') if l.strip()]
            for l in lines[:10]:
                print("  ", l)
