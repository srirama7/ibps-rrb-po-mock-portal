with open('adda.js', 'r', encoding='utf-8') as f:
    adda_lines = f.readlines()

for j in range(845, 930):
    if j < len(adda_lines):
        print(f"  {j+1}: {adda_lines[j].rstrip()}")
