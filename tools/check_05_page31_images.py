import pypdf

reader = pypdf.PdfReader(r"tools\pdf_cache\adda-05.pdf")
page = reader.pages[30] # 0-indexed page 31
print("Images on Page 31 of adda-05:")
for img_name, img_obj in page.images.items():
    print(img_name)
