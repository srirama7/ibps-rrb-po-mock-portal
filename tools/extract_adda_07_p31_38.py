import fitz

doc = fitz.open(r"C:\Users\amogh\ibps-rrb-portal-upgrade\tools\pdf_cache\adda-07.pdf")
print("=== ADDA-07 PAGES 31-38 TEXT ===")
for p in range(30, 38):
    print(f"\n--- PAGE {p+1} ---")
    print(doc[p].get_text())
