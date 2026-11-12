import json, os, re
from PIL import Image

REPO_ROOT = r"C:\Users\amogh\ibps-rrb-portal-upgrade"

def inspect_paper(pid):
    filepath = os.path.join(REPO_ROOT, f"data/licensed_adda/{pid}.json")
    with open(filepath, encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\n==================== {pid.upper()} AUDIT ====================")
    print(f"Title: {data.get('title')}")
    print(f"Paper Label: {data.get('paperLabel')}")
    questions = data.get('questions', [])
    print(f"Total Questions: {len(questions)}")
    
    devanagari_count = 0
    missing_images = []
    short_explanations = []
    fractions_found = []
    diagram_groups = {}
    
    for q in questions:
        num = q['number']
        stem = q['stem']
        options = q['options']
        expl = q.get('explanation', '')
        ans_idx = q.get('answerIndex')
        diags = q.get('diagrams', [])
        
        # 1. Check options count and ans_idx
        if len(options) != 5:
            print(f"  [ERROR] Q{num}: Has {len(options)} options, expected 5")
        if ans_idx not in range(5):
            print(f"  [ERROR] Q{num}: Invalid answerIndex {ans_idx}")
            
        # 2. Check Devanagari
        for field_name, text in [('stem', stem), ('explanation', expl)] + [(f'opt{i}', opt) for i, opt in enumerate(options)]:
            if re.search(r'[\u0900-\u097F]', text):
                devanagari_count += 1
                print(f"  [Devanagari] Q{num} in {field_name}: {text[:60]}")
                
        # 3. Check step-by-step solution
        if not expl or len(expl.strip()) < 15:
            short_explanations.append(num)
            
        # 4. Check fractions
        fracs = re.findall(r'(?:\b|\()(\d+(?:\.\d+)?|\?)\s*/\s*(\d+(?:\.\d+)?|\?)(?:\b|\))', stem + " " + expl)
        if fracs:
            fractions_found.append((num, fracs))
            
        # 5. Check diagrams
        if diags:
            for d in diags:
                full_p = os.path.join(REPO_ROOT, d.replace('/', os.sep))
                if not os.path.exists(full_p) or os.path.getsize(full_p) == 0:
                    missing_images.append((num, d))
                else:
                    try:
                        im = Image.open(full_p)
                        dims = (im.width, im.height)
                    except Exception as e:
                        dims = str(e)
                    diagram_groups.setdefault(q.get('diagramCaption', 'No Caption'), []).append((num, d, dims))
                    
    print(f"Devanagari violations: {devanagari_count}")
    print(f"Short explanations (<15 chars): {len(short_explanations)} {short_explanations}")
    print(f"Missing images: {len(missing_images)} {missing_images}")
    print(f"Questions with fractions: {len(fractions_found)}")
    print(f"Diagram Groups:")
    for cap, items in diagram_groups.items():
        qnums = sorted(list(set(x[0] for x in items)))
        img_info = list(set((x[1], x[2]) for x in items))
        print(f"  - Q{qnums[0]}-Q{qnums[-1]} [{cap}]:")
        for img_path, dims in img_info:
            print(f"      {img_path} (dimensions: {dims})")

for pid in ['adda-08', 'adda-09', 'adda-10']:
    inspect_paper(pid)
