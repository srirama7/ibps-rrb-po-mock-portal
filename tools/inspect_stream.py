import pypdf

reader = pypdf.PdfReader(r"tools\pdf_cache\adda-05.pdf")
p24 = reader.pages[23]

# Inspect content stream for Do operator
text_stream = p24.get_contents().get_data().decode('latin1', errors='ignore')
for line in text_stream.split('\n'):
    if '/Image120' in line or '/Image121' in line:
        print(line)
