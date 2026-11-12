import pypdf

reader = pypdf.PdfReader(r"tools\pdf_cache\adda-03.pdf")
print("=== ADDA-03 PAGE 6 TEXT ===")
print(reader.pages[5].extract_text())
