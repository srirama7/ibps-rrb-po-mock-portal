import pypdf, os
from PIL import Image

REPO_ROOT = r"C:\Users\amogh\ibps-rrb-portal-upgrade"
pdf_path = os.path.join(REPO_ROOT, r"tools\pdf_cache\adda-10.pdf")
reader = pypdf.PdfReader(pdf_path)

print("Page 31 text:")
print(repr(reader.pages[30].extract_text()))

print("\nPage 31 images:")
for img_name, img_obj in reader.pages[30].images.items():
    print(img_name, len(img_obj.data))

# Let's inspect the image directly using python
im155_path = os.path.join(REPO_ROOT, "data/diagrams/adda-10_page31_Image155.png")
if os.path.exists(im155_path):
    im = Image.open(im155_path)
    print("Image155 size:", im.size, im.mode)
