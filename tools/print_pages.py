import pypdf, os

REPO_ROOT = r"C:\Users\amogh\ibps-rrb-portal-upgrade"
pdf_path = os.path.join(REPO_ROOT, r"tools\pdf_cache\adda-10.pdf")
reader = pypdf.PdfReader(pdf_path)

print("=== PAGE 28 (idx 27) ===")
print(reader.pages[27].extract_text())

print("=== PAGE 29 (idx 28) ===")
print(reader.pages[28].extract_text())

print("=== PAGE 30 (idx 29) ===")
print(reader.pages[29].extract_text())

print("=== PAGE 31 (idx 30) ===")
print(reader.pages[30].extract_text())
