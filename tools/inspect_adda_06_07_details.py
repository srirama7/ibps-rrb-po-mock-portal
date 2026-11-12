import fitz
import os

pdf6_path = r"C:\Users\amogh\ibps-rrb-portal-upgrade\tools\pdf_cache\adda-06.pdf"
pdf7_path = r"C:\Users\amogh\ibps-rrb-portal-upgrade\tools\pdf_cache\adda-07.pdf"

print("--- ADDA-06 IMAGES ---")
doc6 = fitz.open(pdf6_path)
for p in range(len(doc6)):
    page = doc6[p]
    imgs = page.get_images()
    # Filter out common logo/watermark by size or xref if needed
    for img in imgs:
        xref = img[0]
        b = doc6.extract_image(xref)
        if b["width"] > 50 and b["height"] > 20: # skip tiny icons
            print(f"Page {p+1}: xref {xref}, {b['width']}x{b['height']}, ext: {b['ext']}")

print("\n--- ADDA-07 IMAGES ---")
doc7 = fitz.open(pdf7_path)
for p in range(len(doc7)):
    page = doc7[p]
    imgs = page.get_images()
    for img in imgs:
        xref = img[0]
        b = doc7.extract_image(xref)
        if b["width"] > 50 and b["height"] > 20:
            print(f"Page {p+1}: xref {xref}, {b['width']}x{b['height']}, ext: {b['ext']}")
