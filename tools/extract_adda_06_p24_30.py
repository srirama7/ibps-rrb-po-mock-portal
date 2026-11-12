import fitz

doc = fitz.open(r"C:\Users\amogh\ibps-rrb-portal-upgrade\tools\pdf_cache\adda-06.pdf")
print("=== ADDA-06 PAGES 24-30 ===")
for p in range(23, 30):
    print(f"\n================ PAGE {p+1} ================")
    print(doc[p].get_text())
