import pypdf

reader = pypdf.PdfReader(r"tools\pdf_cache\adda-03.pdf")
for p_idx in [4, 5]: # pages 5 and 6
    p = reader.pages[p_idx]
    print(f"=== PAGE {p_idx+1} ===")
    for img_name in p.images.keys():
        print("  Image on page:", img_name)
    print("Text on page:")
    print(p.extract_text()[:600])
