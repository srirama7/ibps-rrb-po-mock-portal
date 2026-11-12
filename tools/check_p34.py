import pymupdf as fitz

doc = fitz.open(r"C:\Users\amogh\ibps-rrb-portal-upgrade\tools\pdf_cache\adda-10.pdf")
print("=== PAGE 34 (idx 33) ===")
print(doc[33].get_text())
