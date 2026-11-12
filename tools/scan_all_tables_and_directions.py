import pypdf, re

CACHE_DIR = r"tools\pdf_cache"

def inspect_all_pdf_tables():
    for i in range(1, 11):
        pid = f"adda-{i:02d}"
        pdf_path = f"{CACHE_DIR}\\{pid}.pdf"
        reader = pypdf.PdfReader(pdf_path)
        print(f"\n==================== CHECKING {pid} ====================")
        for p_idx, page in enumerate(reader.pages):
            text = page.extract_text() or ''
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            for l_idx, line in enumerate(lines):
                # Detect Directions or table headers
                if re.search(r'Directions?\s*[\(\[]?\d+\s*[-–to]+\s*\d+[\)\]]?', line, re.IGNORECASE) or \
                   'table shows' in line.lower() or 'following table' in line.lower() or \
                   'bar graph' in line.lower() or 'line graph' in line.lower() or 'pie chart' in line.lower():
                    context = "\n   ".join(lines[max(0, l_idx-1):min(len(lines), l_idx+12)])
                    print(f"--- {pid} Page {p_idx+1} ---")
                    print(f"   {context}\n")

if __name__ == '__main__':
    inspect_all_pdf_tables()
