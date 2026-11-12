import pytesseract
from PIL import Image

im = Image.open(r"C:\Users\amogh\ibps-rrb-portal-upgrade\data\diagrams\adda-10_page31_Image155.png")
print("Size:", im.size)
# Try OCR if tesseract is installed, otherwise inspect
try:
    text = pytesseract.image_to_string(im)
    print("OCR text:", repr(text))
except Exception as e:
    print("OCR error:", e)
