import pypdf, io, os
from PIL import Image
from collections import Counter

CACHE_DIR = r"C:\Users\amogh\ibps-rrb-portal-upgrade\tools\pdf_cache"
DIAGRAMS_DIR = r"C:\Users\amogh\ibps-rrb-portal-upgrade\data\diagrams"
os.makedirs(DIAGRAMS_DIR, exist_ok=True)

for i in range(1, 11):
    pid = f"adda-{i:02d}"
    pdf_path = os.path.join(CACHE_DIR, f"{pid}.pdf")
    reader = pypdf.PdfReader(pdf_path)
    
    # Count frequency of image names/hashes to identify watermarks vs unique diagrams
    img_records = []
    for p_idx, page in enumerate(reader.pages):
        for img_name, img_file in page.images.items():
            img_records.append((p_idx + 1, img_name, len(img_file.data), img_file))
            
    # Count lengths to identify watermarks
    len_counts = Counter(r[2] for r in img_records)
    
    # Unique diagrams appear on <= 3 pages
    diagrams = [r for r in img_records if len_counts[r[2]] <= 3 and r[2] > 2000]
    print(f"\n=== {pid} Unique Diagrams ===")
    for d in diagrams:
        p_num, name, size, img_obj = d
        clean_name = name.lstrip('/').replace('\\', '_')
        try:
            im = Image.open(io.BytesIO(img_obj.data))
            # Filter out full page ads (around 1055x1491, 1131x1600, or aspect ratio > 1.35 with height > 1200)
            if im.height > 1200 and im.width > 900:
                print(f"  Skipping full-page ad: Page {p_num} {clean_name} {im.size}")
                continue
            # Filter out tiny icons
            if im.width < 120 or im.height < 60:
                continue
                
            print(f"  DIAGRAM Page {p_num}: {clean_name}, {im.size}, format={im.format}, bytes={size}")
            
            diag_filename = f"{pid}_page{p_num}_{clean_name}"
            if not diag_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                diag_filename += f".{im.format.lower()}"
            out_path = os.path.join(DIAGRAMS_DIR, diag_filename)
            with open(out_path, 'wb') as f:
                f.write(img_obj.data)
            print(f"    Saved: {diag_filename}")
        except Exception as e:
            print(f"  Error reading {clean_name}: {e}")
