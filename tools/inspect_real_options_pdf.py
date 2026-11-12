import pypdf

reader = pypdf.PdfReader(r"tools\pdf_cache\adda-03.pdf")
print("=== ADDA-03 PAGE 5 ===")
p5 = reader.pages[4]
text = p5.extract_text()
print(text[text.find('Q5.'):text.find('Q6.') if 'Q6.' in text else text.find('Q5.')+1000])
