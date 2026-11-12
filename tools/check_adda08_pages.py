import pymupdf as fitz

doc = fitz.open(r"C:\Users\amogh\ibps-rrb-portal-upgrade\tools\pdf_cache\adda-08.pdf")
print("=== ADDA-08 PAGE 24 (idx 23) ===")
print(doc[23].get_text()[:600])

print("=== ADDA-08 PAGE 25 (idx 24) ===")
print(doc[24].get_text()[:600])
