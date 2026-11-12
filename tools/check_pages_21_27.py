import pypdf

reader = pypdf.PdfReader(r"tools\pdf_cache\adda-02.pdf")
for p in range(21, len(reader.pages)):
    t = reader.pages[p].extract_text() or ''
    print(f"Page {p+1}: {t[:200]}...")
