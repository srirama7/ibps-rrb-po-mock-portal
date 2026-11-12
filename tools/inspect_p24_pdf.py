import pypdf

reader = pypdf.PdfReader(r"tools\pdf_cache\adda-05.pdf")
p24 = reader.pages[23]
print("Images on p24:")
for k, v in p24.images.items():
    print(k, len(v.data))
