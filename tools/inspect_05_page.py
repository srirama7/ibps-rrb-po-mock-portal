import pypdf

reader = pypdf.PdfReader(r"tools\pdf_cache\adda-05.pdf")
for p_idx in range(25, 30):
    t = reader.pages[p_idx].extract_text() or ''
    if 'Q54.' in t or 'Q58.' in t:
        print(f"=== PAGE {p_idx+1} ===")
        print(t)
