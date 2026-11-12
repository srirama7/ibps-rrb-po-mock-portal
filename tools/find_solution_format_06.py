import fitz

doc = fitz.open(r"C:\Users\amogh\ibps-rrb-portal-upgrade\tools\pdf_cache\adda-06.pdf")
print("Total pages in adda-06.pdf:", len(doc))
for p in range(len(doc)-5, len(doc)):
    print(f"\n--- Page {p+1} ---")
    print(doc[p].get_text()[:600])
