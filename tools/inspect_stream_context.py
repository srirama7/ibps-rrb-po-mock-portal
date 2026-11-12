import pypdf

reader = pypdf.PdfReader(r"tools\pdf_cache\adda-05.pdf")
p24 = reader.pages[23]

text_stream = p24.get_contents().get_data().decode('latin1', errors='ignore')
lines = text_stream.split('\n')
for idx, line in enumerate(lines):
    if '/Image120' in line or '/Image121' in line:
        print("--- CONTEXT ---")
        for l in lines[max(0, idx-5):idx+2]:
            print(l)
