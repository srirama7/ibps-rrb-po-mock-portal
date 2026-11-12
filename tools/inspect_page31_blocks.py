import pymupdf as fitz
import os

doc = fitz.open(r"C:\Users\amogh\ibps-rrb-portal-upgrade\tools\pdf_cache\adda-10.pdf")
page = doc[30] # Page 31
print("=== PAGE 31 (idx 30) BLOCKS ===")
for b in page.get_text("blocks"):
    # b: (x0, y0, x1, y1, text, block_no, block_type)
    if b[6] == 0: # text
        print(f"Text block at ({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}):\n{repr(b[4][:80])}")
    else: # image
        print(f"Image block at ({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f})")

print("\n=== PAGE 31 IMAGES LIST ===")
for img in page.get_images():
    print(img)
