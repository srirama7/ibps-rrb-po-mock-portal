import pypdf

reader = pypdf.PdfReader(r"tools\pdf_cache\adda-05.pdf")
for p in reader.pages[26:30]:
    t = p.extract_text() or ''
    if 'Q54.' in t or 'Q58.' in t:
        print("--- PAGE ---")
        for line in t.split('\n'):
            if any(k in line for k in ['Q54', 'Q55', 'Q57', 'Q58', '349', '89.99']):
                print("  ", line)
