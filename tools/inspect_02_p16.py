import pypdf

reader = pypdf.PdfReader(r"tools\pdf_cache\adda-02.pdf")
print("=== ADDA-02 PAGE 16 ===")
p16 = reader.pages[15]
print("Text:", p16.extract_text()[:600])
print("Images on page 16:")
for img_name, img_obj in p16.images.items():
    print(f"  {img_name}: {len(img_obj.data)} bytes")
