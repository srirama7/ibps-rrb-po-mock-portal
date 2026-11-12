from PIL import Image

for name in ['adda-03_page5_Image44.png', 'adda-03_page6_Image49.png', 'adda-03_page6_Image50.png']:
    im = Image.open('data/diagrams/' + name)
    print(name, im.size)
