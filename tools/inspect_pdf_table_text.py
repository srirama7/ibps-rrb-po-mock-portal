import pypdf

def get_page(pdf_name, page_num):
    reader = pypdf.PdfReader(f"tools\\pdf_cache\\{pdf_name}.pdf")
    return reader.pages[page_num - 1].extract_text() or ''

print("=== ADDA-02 PAGE 20 (Q57-62) ===")
print(get_page("adda-02", 20)[:800])

print("\n=== ADDA-06 PAGE 24 (Q41-46) ===")
print(get_page("adda-06", 24)[800:1800])

print("\n=== ADDA-08 PAGE 24 (Q41-45) ===")
print(get_page("adda-08", 24)[:1000])

print("\n=== ADDA-09 PAGE 26 (Q51-55) ===")
print(get_page("adda-09", 26)[:1000])

print("\n=== ADDA-10 PAGE 26 (Q64-68) ===")
print(get_page("adda-10", 26)[:1000])
