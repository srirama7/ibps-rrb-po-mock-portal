import pypdf

reader_04 = pypdf.PdfReader(r"tools\pdf_cache\adda-04.pdf")
for p_idx, page in enumerate(reader_04.pages):
    text = page.extract_text() or ''
    if 'Directions (46-50)' in text or 'Directions (46 - 50)' in text or 'mall' in text.lower():
        print(f"adda-04 Page {p_idx+1}:")
        for line in text.split('\n')[:15]:
            print("  ", line)
