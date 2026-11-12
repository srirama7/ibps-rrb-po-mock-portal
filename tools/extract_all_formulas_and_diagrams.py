import pypdf, io, os
from PIL import Image
from collections import Counter

CACHE_DIR = r"tools\pdf_cache"
DIAGRAMS_DIR = r"data\diagrams"
os.makedirs(DIAGRAMS_DIR, exist_ok=True)

# Common repeated images across pages are headers/footers/watermarks/logos
# Find unique or semi-unique images on each page
for i in range(1, 11):
    pid = f"adda-{i:02d}"
    pdf_path = os.path.join(CACHE_DIR, f"{pid}.pdf")
    reader = pypdf.PdfReader(pdf_path)
    
    img_records = []
    for p_idx, page in enumerate(reader.pages):
        for img_name, img_file in page.images.items():
            img_records.append((p_idx + 1, img_name, len(img_file.data), img_file))
            
    len_counts = Counter(r[2] for r in img_records)
    
    # Images that appear <= 5 times and > 200 bytes
    candidates = [r for r in img_records if len_counts[r[2]] <= 5 and r[2] > 200]
    
    saved_count = 0
    for p_num, name, size, img_obj in candidates:
        clean_name = name.lstrip('/').replace('\\', '_')
        try:
            im = Image.open(io.BytesIO(img_obj.data))
            # Skip full page background ads
            if im.height > 1200 and im.width > 900:
                continue
            # Skip tiny dots < 10px
            if im.width < 15 or im.height < 10:
                continue
                
            diag_filename = f"{pid}_page{p_num}_{clean_name}"
            if not diag_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                diag_filename += f".{im.format.lower()}"
                
            out_path = os.path.join(DIAGRAMS_DIR, diag_filename)
            with open(out_path, 'wb') as f:
                f.write(img_obj.data)
            saved_count += 1
        except Exception as e:
            pass
            
    print(f"{pid}: Saved {saved_count} diagrams & formula images.")
