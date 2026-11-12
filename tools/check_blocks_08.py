import pymupdf as fitz

doc = fitz.open(r"C:\Users\amogh\ibps-rrb-portal-upgrade\tools\pdf_cache\adda-08.pdf")

print("=== PAGE 24 BLOCKS ===")
for b in doc[23].get_text("blocks"):
    print(f"({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}): {repr(b[4][:60])}")

print("\n=== PAGE 25 BLOCKS ===")
for b in doc[24].get_text("blocks"):
    print(f"({b[0]:.1f}, {b[1]:.1f}, {b[2]:.1f}, {b[3]:.1f}): {repr(b[4][:60])}")
