from PIL import Image
import os, hashlib

repo = r"C:\Users\amogh\ibps-rrb-portal-upgrade"

def file_hash(path):
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

pairs = [
    # adda-03
    ["data/diagrams/adda-03_page5_Image44.png", "data/diagrams/adda-03_page6_Image49.png", "data/diagrams/adda-03_page6_Image50.png"],
    ["data/diagrams/adda-03_page27_Image135.jpeg", "data/diagrams/adda-03_page27_Image136.jpeg"],
    ["data/diagrams/adda-03_page30_Image149.png", "data/diagrams/adda-03_page30_Image150.png"],
    # adda-04
    ["data/diagrams/adda-04_page25_Image124.png", "data/diagrams/adda-04_page26_Image124.png"],
    # adda-05
    ["data/diagrams/adda-05_page24_Image120.png", "data/diagrams/adda-05_page24_Image121.png"],
    ["data/diagrams/adda-05_page26_Image130.png", "data/diagrams/adda-05_page26_Image131.jpeg"],
    # adda-06
    ["data/diagrams/adda-06_page28_Image142.jpeg", "data/diagrams/adda-06_page28_Image143.jpeg"],
    # adda-07
    ["data/diagrams/adda-07_page25_Image124.png", "data/diagrams/adda-07_page26_Image129.png"],
    ["data/diagrams/adda-07_page29_Image142.png", "data/diagrams/adda-07_page30_Image147.png"],
    # adda-08
    ["data/diagrams/adda-08_page24_Image120.png", "data/diagrams/adda-08_page25_Image125.png"],
    ["data/diagrams/adda-08_page26_Image130.png", "data/diagrams/adda-08_page27_Image135.png"],
    # adda-10
    ["data/diagrams/adda-10_page31_Image155.png", "data/diagrams/adda-10_page31_Image156.png"],
]

for group in pairs:
    print(f"\n--- Group: {group[0].split('/')[-1]} ... ---")
    for p in group:
        full_p = os.path.join(repo, p)
        if os.path.exists(full_p):
            im = Image.open(full_p)
            print(f"  {p.split('/')[-1]}: {im.size}, mode={im.mode}, hash={file_hash(full_p)[:8]}")
        else:
            print(f"  {p.split('/')[-1]}: NOT FOUND")
