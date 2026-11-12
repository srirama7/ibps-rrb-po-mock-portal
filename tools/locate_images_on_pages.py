import fitz

doc = fitz.open(r"C:\Users\amogh\ibps-rrb-portal-upgrade\tools\pdf_cache\adda-07.pdf")

pages_to_check = [34, 35, 36, 37] # 0-indexed: 33, 34, 35, 36
for p_idx in [33, 34, 35, 36]:
    page = doc[p_idx]
    print(f"\n================ PAGE {p_idx+1} ================")
    # Get text with bounding boxes
    blocks = page.get_text("blocks")
    for b in blocks:
        # (x0, y0, x1, y1, text, block_no, block_type)
        if b[6] == 0: # text
            first_line = b[4].strip().split('\n')[0]
            print(f"Text at y={b[1]:.1f}-{b[3]:.1f}: {first_line[:60]}")
        elif b[6] == 1: # image
            print(f"IMAGE block at y={b[1]:.1f}-{b[3]:.1f}")
            
    # Also get images with their bbox using get_image_info
    img_info = page.get_image_info(xrefs=True)
    for info in img_info:
        bbox = info['bbox']
        print(f"Image xref {info['xref']} at bbox ({bbox[0]:.1f}, {bbox[1]:.1f}, {bbox[2]:.1f}, {bbox[3]:.1f})")
