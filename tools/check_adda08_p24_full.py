import pymupdf as fitz

doc = fitz.open(r"C:\Users\amogh\ibps-rrb-portal-upgrade\tools\pdf_cache\adda-08.pdf")
print("=== PAGE 24 FULL TEXT ===")
print(doc[23].get_text())

print("=== PAGE 24 IMAGES ===")
for img in doc[23].get_images():
    print(img)

print("=== PAGE 25 IMAGES ===")
for img in doc[24].get_images():
    print(img)
