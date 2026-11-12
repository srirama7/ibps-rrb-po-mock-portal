import pypdf

reader_04 = pypdf.PdfReader(r"tools\pdf_cache\adda-04.pdf")
print("=== ADDA-04 PAGE 27 ===")
print(reader_04.pages[26].extract_text()[:1500])

reader_06 = pypdf.PdfReader(r"tools\pdf_cache\adda-06.pdf")
print("=== ADDA-06 PAGE 24 ===")
print(reader_06.pages[23].extract_text()[:1500])
