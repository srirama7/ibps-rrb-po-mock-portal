import pymupdf as fitz

doc = fitz.open(r"C:\Users\amogh\ibps-rrb-portal-upgrade\tools\pdf_cache\adda-10.pdf")
print("Searching adda-10 for 'export':")
found = False
for pno, page in enumerate(doc):
    t = page.get_text()
    if 'export' in t.lower():
        print(f"Found 'export' on page {pno+1}:")
        print(t[:200])
        found = True
if not found:
    print("NO MENTION of 'export' anywhere in adda-10.pdf!")
