import pypdf, re, json, os

CACHE_DIR = r"C:\Users\amogh\ibps-rrb-portal-upgrade\tools\pdf_cache"
DIAGRAMS_DIR = r"C:\Users\amogh\ibps-rrb-portal-upgrade\data\diagrams"

diagram_files = os.listdir(DIAGRAMS_DIR)

mapping = {}

for i in range(1, 11):
    pid = f"adda-{i:02d}"
    pdf_path = os.path.join(CACHE_DIR, f"{pid}.pdf")
    reader = pypdf.PdfReader(pdf_path)
    
    # Check each page for Q numbers and if it has a diagram image
    for p_idx, page in enumerate(reader.pages):
        p_num = p_idx + 1
        page_text = page.extract_text() or ''
        q_on_page = [int(m) for m in re.findall(r'Q\s*\.?\s*(\d+)[\.\s]', page_text)]
        dir_matches = re.findall(r'(?:Directions?|Direction)\s*[\(\[]?(\d+)\s*[-–to]+\s*(\d+)[\)\]]?', page_text, re.IGNORECASE)
        
        # Check if any diagram was extracted for this page
        matching_diags = [f for f in diagram_files if f.startswith(f"{pid}_page{p_num}_")]
        if matching_diags:
            print(f"{pid} Page {p_num} has diagrams: {matching_diags}")
            print(f"  Questions on page: {q_on_page}")
            print(f"  Directions on page: {dir_matches}")
            for d in matching_diags:
                mapping[d] = {
                    "paper": pid,
                    "page": p_num,
                    "questions": q_on_page,
                    "directions": dir_matches
                }
