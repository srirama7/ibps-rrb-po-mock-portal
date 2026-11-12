from PIL import Image
import os

repo = r"C:\Users\amogh\ibps-rrb-portal-upgrade"
images = [
    "data/diagrams/adda-08_page24_Image120.png",
    "data/diagrams/adda-08_page25_Image125.png",
    "data/diagrams/adda-09_page27_Image136.png",
    "data/diagrams/adda-10_page26_Image133.png",
    "data/diagrams/adda-04_page25_Image124.png",
]

for img_rel in images:
    p = os.path.join(repo, img_rel)
    if os.path.exists(p):
        im = Image.open(p)
        print(f"{img_rel}: format={im.format}, size={im.size}, mode={im.mode}")
    else:
        print(f"{img_rel}: NOT FOUND")
