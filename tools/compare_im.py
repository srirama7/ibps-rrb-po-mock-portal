from PIL import Image
import numpy as np

im1 = Image.open(r"C:\Users\amogh\ibps-rrb-portal-upgrade\data\diagrams\adda-10_page28_Image142.png")
im2 = Image.open(r"C:\Users\amogh\ibps-rrb-portal-upgrade\data\diagrams\adda-10_page31_Image155.png")

print("im1 (page28_Image142):", im1.size, im1.mode)
print("im2 (page31_Image155):", im2.size, im2.mode)

# Compare sizes and pixels if possible
if im1.size == im2.size:
    diff = np.mean(np.abs(np.array(im1, dtype=float) - np.array(im2, dtype=float)))
    print("Difference between im1 and im2:", diff)
else:
    print("Sizes differ!")
