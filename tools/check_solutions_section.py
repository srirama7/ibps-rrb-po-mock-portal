import pypdf

reader = pypdf.PdfReader(r"tools\pdf_cache\adda-02.pdf")
total_pages = len(reader.pages)
print(f"Total pages in adda-02.pdf: {total_pages}")

for p_idx in range(total_pages - 10, total_pages):
    text = reader.pages[p_idx].extract_text() or ''
    if 'Solutions' in text or 'S41.' in text or '41.' in text:
        print(f"Page {p_idx+1}:")
        for line in text.split('\n')[:15]:
            print("  ", line)
