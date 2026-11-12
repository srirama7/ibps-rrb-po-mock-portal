import os, pypdf, re, json
from PIL import Image

REPO_ROOT = r"C:\Users\amogh\ibps-rrb-portal-upgrade"
CACHE_DIR = os.path.join(REPO_ROOT, r"tools\pdf_cache")
DIAGRAMS_DIR = os.path.join(REPO_ROOT, r"data\diagrams")
DATA_DIR = os.path.join(REPO_ROOT, "data")

all_diag_files = sorted(os.listdir(DIAGRAMS_DIR))

# Let's see what each diagram file is
print(f"Total extracted diagram/formula files: {len(all_diag_files)}")

# Group files by paper and page
paper_page_files = {}
for f in all_diag_files:
    m = re.match(r'(adda-\d+)_page(\d+)_(.+)', f)
    if m:
        pid, pnum, iname = m.group(1), int(m.group(2)), m.group(3)
        paper_page_files.setdefault((pid, pnum), []).append(f)

print(f"Total (paper, page) groups with images: {len(paper_page_files)}")
for (pid, pnum), flist in sorted(paper_page_files.items()):
    # Get image dimensions
    dim_str = []
    for fn in flist:
        try:
            im = Image.open(os.path.join(DIAGRAMS_DIR, fn))
            dim_str.append(f"{fn.split('_')[-1]} ({im.width}x{im.height})")
        except:
            dim_str.append(fn)
    print(f"  {pid} Page {pnum}: {len(flist)} images -> {', '.join(dim_str)}")
