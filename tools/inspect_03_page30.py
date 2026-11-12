import pypdf

reader = pypdf.PdfReader(r"tools\pdf_cache\adda-03.pdf")
print("=== ADDA-03 PAGE 30 ===")
print(reader.pages[29].extract_text()[:1500])
