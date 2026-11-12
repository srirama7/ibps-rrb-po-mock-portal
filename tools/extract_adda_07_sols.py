import fitz

doc = fitz.open(r"C:\Users\amogh\ibps-rrb-portal-upgrade\tools\pdf_cache\adda-07.pdf")
print("=== ADDA-07 SOLUTIONS PAGES ===")
# Find which pages contain "S56." or "S65."
for p in range(len(doc)):
    text = doc[p].get_text()
    if "S56." in text or "S65." in text or "Solutions (56-" in text:
        print(f"--- Page {p+1} ---")
        print(text[:2000])
