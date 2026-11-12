import pypdf

reader = pypdf.PdfReader(r"tools\pdf_cache\adda-05.pdf")
print("=== ADDA-05 PAGE 24 ===")
print(reader.pages[23].extract_text()[:600])

print("=== ADDA-05 PAGE 26 ===")
print(reader.pages[25].extract_text()[:600])
