import pypdf

reader = pypdf.PdfReader(r"tools\pdf_cache\adda-03.pdf")
print("=== PAGE 5 ===")
print(reader.pages[4].extract_text()[:600])

print("=== PAGE 6 ===")
print(reader.pages[5].extract_text()[:600])
