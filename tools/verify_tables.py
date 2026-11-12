import pymupdf as fitz
from PIL import Image
import io

doc = fitz.open(r"C:\Users\amogh\ibps-rrb-portal-upgrade\tools\pdf_cache\adda-08.pdf")
img120_data = doc.extract_image(139) # Image120 xref
img125_data = doc.extract_image(143) # Image125 xref

print("Image 120:", img120_data['width'], img120_data['height'], img120_data['ext'])
print("Image 125:", img125_data['width'], img125_data['height'], img125_data['ext'])
