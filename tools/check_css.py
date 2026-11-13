with open('adda.css', 'r', encoding='utf-8') as f:
    adda_css = f.read()

print("adda.css length:", len(adda_css))
for line in adda_css.split('\n'):
    if 'section-tab' in line or 'pause' in line or 'modal' in line or 'timer' in line:
        print(line)
