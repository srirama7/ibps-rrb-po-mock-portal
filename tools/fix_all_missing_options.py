import os, pypdf, re, json

REPO_ROOT = r"C:\Users\amogh\ibps-rrb-portal-upgrade"
DATA_DIR = os.path.join(REPO_ROOT, "data")
CACHE_DIR = os.path.join(REPO_ROOT, r"tools\pdf_cache")
LICENSED_DIR = os.path.join(DATA_DIR, "licensed_adda")

def extract_clean_english_options_from_pdf(pdf_path):
    reader = pypdf.PdfReader(pdf_path)
    full_text = "\n".join([p.extract_text() or '' for p in reader.pages])

    extracted_by_q = {}

    for qnum in range(1, 81):
        # Match from Q{qnum} to Q{qnum+1} or Directions or End
        pattern = rf'Q\s*\.?\s*{qnum}\b(.*?)(?=Q\s*\.?\s*{qnum+1}\b|Directions\s*\(|\Z)'
        m = re.search(pattern, full_text, re.DOTALL | re.IGNORECASE)
        if not m:
            continue
        chunk = m.group(1)

        # Find all option matches: (a) text, (b) text, etc.
        # Options usually stop at the next (x) or at Ans. or at \n\n
        opts = {}
        opt_matches = list(re.finditer(r'\(([a-e])\)\s*([^(\n\r]+(?:\n(?!\([a-e]\)|Ans\.|Q\d)[^(\n\r]+)*)', chunk, re.IGNORECASE))
        for om in opt_matches:
            letter = om.group(1).lower()
            if letter in opts: # Keep first occurrence
                continue
            raw_val = om.group(2).strip()
            # Clean English:
            # 1. If has slash '/', English is before '/'
            if '/' in raw_val:
                clean = raw_val.split('/')[0].strip()
            else:
                # 2. Strip Devanagari Unicode \u0900-\u097F
                clean = re.sub(r'[\u0900-\u097F]+.*', '', raw_val).strip()

            # Clean line breaks inside option text
            clean = re.sub(r'\s+', ' ', clean).strip()

            # Remove trailing stray dashes or dots
            clean = clean.rstrip(' .-')

            if clean:
                opts[letter] = clean

        if len(opts) == 5:
            extracted_by_q[qnum] = [opts['a'], opts['b'], opts['c'], opts['d'], opts['e']]

    return extracted_by_q

def fix_all():
    tests_path = os.path.join(DATA_DIR, "adda_tests.json")
    with open(tests_path, encoding='utf-8') as f:
        tests_data = json.load(f)['tests']

    total_fixed = 0

    for test in tests_data:
        pid = test['id']
        pdf_file = os.path.join(CACHE_DIR, f"{pid}.pdf")
        if not os.path.exists(pdf_file):
            print(f"Warning: {pdf_file} not found")
            continue

        pdf_options = extract_clean_english_options_from_pdf(pdf_file)
        print(f"{pid}: Successfully extracted clean options for {len(pdf_options)}/80 questions from PDF.")

        fixed_in_paper = 0
        for q in test['questions']:
            qnum = q['number']
            cur_opts = q['options']

            # Check if current options are generic "Option A", "Option B", etc.
            is_generic = any(re.match(r'^Option\s+[A-E]$', str(opt).strip(), re.IGNORECASE) for opt in cur_opts)

            if is_generic and qnum in pdf_options:
                recovered = pdf_options[qnum]
                # Double check recovered options are not generic
                if not any(re.match(r'^Option\s+[A-E]$', str(o).strip(), re.IGNORECASE) for o in recovered):
                    q['options'] = recovered
                    fixed_in_paper += 1
                    total_fixed += 1

        print(f"  -> Fixed {fixed_in_paper} questions in {pid} with real English options.")

    # Save combined JSON
    with open(tests_path, 'w', encoding='utf-8') as f:
        json.dump({"tests": tests_data}, f, indent=2, ensure_ascii=False)

    # Save licensed individual JSON files
    for test in tests_data:
        pid = test['id']
        out_paper_path = os.path.join(LICENSED_DIR, f"{pid}.json")
        with open(out_paper_path, 'w', encoding='utf-8') as f:
            json.dump(test, f, indent=2, ensure_ascii=False)

    # Save JS bundle
    bundle_path = os.path.join(DATA_DIR, "adda_tests_data.js")
    with open(bundle_path, 'w', encoding='utf-8') as f:
        f.write(f"window.__ADDA_TESTS_DATA__ = {{ tests: {json.dumps(tests_data, ensure_ascii=False)} }};\n")

    print(f"\nSUCCESS: Fixed a total of {total_fixed} questions with real English options across all papers!")

if __name__ == '__main__':
    fix_all()
