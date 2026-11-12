import pypdf

reader = pypdf.PdfReader(r"tools\pdf_cache\adda-10.pdf")
print("=== ADDA-10 PAGE 31 ===")
print(reader.pages[30].extract_text()[:1200])
