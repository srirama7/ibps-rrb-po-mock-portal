import pypdf

reader = pypdf.PdfReader(r"tools\pdf_cache\adda-09.pdf")
full_text = "\n".join([p.extract_text() or '' for p in reader.pages[:10]])
for qn in [6, 7]:
    pos = full_text.find(f"Q{qn}.")
    print(f"=== ADDA-09 Q{qn} ===")
    print(full_text[pos:pos+700])
