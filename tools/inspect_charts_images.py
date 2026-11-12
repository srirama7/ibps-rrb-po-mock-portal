import os, sys, re, json, pypdf

CACHE_DIR = r"C:\Users\amogh\ibps-rrb-portal-upgrade\tools\pdf_cache"

for i in range(1, 11):
    pid = f"adda-{i:02d}"
    pdf_path = os.path.join(CACHE_DIR, f"{pid}.pdf")
    reader = pypdf.PdfReader(pdf_path)
    
    # Check images in pages
    total_images = 0
    pages_with_images = []
    for p_idx, page in enumerate(reader.pages):
        img_count = len(page.images)
        if img_count > 0:
            total_images += img_count
            pages_with_images.append((p_idx + 1, img_count))
            
    # Check DI terms in text
    full_text = '\n'.join([p.extract_text() or '' for p in reader.pages])
    di_terms = []
    for term in ['bar chart', 'bar graph', 'pie chart', 'given table', 'table shows', 'following table', 'line graph']:
        matches = len(re.findall(term, full_text, re.IGNORECASE))
        if matches > 0:
            di_terms.append(f"{term}: {matches}")
            
    print(f"{pid}: {len(reader.pages)} pages | Total images: {total_images} (pages: {pages_with_images[:6]}) | DI mentions: {', '.join(di_terms)}")
