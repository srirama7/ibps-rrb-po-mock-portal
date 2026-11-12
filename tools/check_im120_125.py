from PIL import Image

im120 = Image.open(r"C:\Users\amogh\ibps-rrb-portal-upgrade\data\diagrams\adda-08_page24_Image120.png")
im125 = Image.open(r"C:\Users\amogh\ibps-rrb-portal-upgrade\data\diagrams\adda-08_page25_Image125.png")

print("im120:", im120.size)
print("im125:", im125.size)

# Let's save small crops or inspect if there is devanagari in im125!
# Or let's see why both are attached!
