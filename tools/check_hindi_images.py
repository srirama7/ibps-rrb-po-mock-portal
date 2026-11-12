from PIL import Image
import numpy as np

def check_image(path):
    im = Image.open(path).convert('L')
    print(path, im.size)

check_image('data/diagrams/adda-05_page24_Image120.png')
check_image('data/diagrams/adda-05_page24_Image121.png')
check_image('data/diagrams/adda-05_page26_Image130.png')
check_image('data/diagrams/adda-05_page26_Image131.jpeg')
