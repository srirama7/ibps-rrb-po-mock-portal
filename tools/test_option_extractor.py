import pypdf, re

def inspect_options_in_pdf(pdf_path, q_start, q_end):
    reader = pypdf.PdfReader(pdf_path)
    full_text = "\n".join([p.extract_text() or '' for p in reader.pages])

    for qnum in range(q_start, q_end + 1):
        # Look for Q{qnum}. to Q{qnum+1}.
        pattern = rf'Q\s*\.?\s*{qnum}\b(.*?)(?=Q\s*\.?\s*{qnum+1}\b|Directions|\Z)'
        m = re.search(pattern, full_text, re.DOTALL | re.IGNORECASE)
        if m:
            q_chunk = m.group(1)
            # Find (a), (b), (c), (d), (e)
            opt_matches = list(re.finditer(r'\(([a-e])\)\s*([^(\n\r]+)', q_chunk, re.IGNORECASE))
            print(f"\n--- Q{qnum} ---")
            for om in opt_matches:
                raw_opt = om.group(2).strip()
                # Clean English: if has slash '/', English is before '/'
                if '/' in raw_opt:
                    clean_eng = raw_opt.split('/')[0].strip()
                else:
                    # Strip any Devanagari
                    clean_eng = re.sub(r'[\u0900-\u097F]+.*', '', raw_opt).strip()
                print(f"  ({om.group(1).lower()}) {clean_eng}")

print("=== INSPECTING ADDA-03 Q5-Q10 ===")
inspect_options_in_pdf(r"tools\pdf_cache\adda-03.pdf", 5, 10)
