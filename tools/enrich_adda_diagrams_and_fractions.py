import os, sys, re, json

REPO_ROOT = r"C:\Users\amogh\ibps-rrb-portal-upgrade"
DATA_DIR = os.path.join(REPO_ROOT, "data")
DIAGRAMS_DIR = os.path.join(DATA_DIR, "diagrams")
LICENSED_DIR = os.path.join(DATA_DIR, "licensed_adda")

# Detailed verified mapping of paper ID and question range to diagram files
DIAGRAM_MAPPING = {
    "adda-01": [
        {"range": (76, 80), "images": ["data/diagrams/adda-01_page24_Image115.png"], "caption": "Colleges Student Distribution (Pie Charts)"}
    ],
    "adda-02": [
        {"range": (46, 50), "images": ["data/diagrams/adda-02_page17_Image92.png"], "caption": "Monthly Production & Sales Data (Chart)"}
    ],
    "adda-03": [
        {"range": (5, 8), "images": ["data/diagrams/adda-03_page5_Image44.png", "data/diagrams/adda-03_page6_Image49.png"], "caption": "Seating / Arrangement Reference Diagram"},
        {"range": (46, 50), "images": ["data/diagrams/adda-03_page27_Image136.jpeg"], "caption": "Data Interpretation Bar Chart"},
        {"range": (51, 55), "images": ["data/diagrams/adda-03_page30_Image149.png", "data/diagrams/adda-03_page30_Image150.png"], "caption": "Distribution Chart & Table"}
    ],
    "adda-04": [
        {"range": (41, 45), "images": ["data/diagrams/adda-04_page25_Image124.png"], "caption": "Data Interpretation Line Graph"}
    ],
    "adda-05": [
        {"range": (41, 45), "images": ["data/diagrams/adda-05_page24_Image120.png", "data/diagrams/adda-05_page24_Image121.png"], "caption": "Company Performance Bar Chart"},
        {"range": (46, 50), "images": ["data/diagrams/adda-05_page26_Image130.png"], "caption": "Percentage Distribution Pie Chart"}
    ],
    "adda-06": [
        {"range": (52, 56), "images": ["data/diagrams/adda-06_page28_Image142.jpeg", "data/diagrams/adda-06_page28_Image143.jpeg"], "caption": "Sales Distribution Charts"}
    ],
    "adda-07": [
        {"range": (41, 45), "images": ["data/diagrams/adda-07_page25_Image124.png", "data/diagrams/adda-07_page26_Image129.png"], "caption": "Production & Defect Data Bar Graph"},
        {"range": (51, 55), "images": ["data/diagrams/adda-07_page29_Image142.png", "data/diagrams/adda-07_page30_Image147.png"], "caption": "Store Inventory Chart"}
    ],
    "adda-08": [
        {"range": (41, 45), "images": ["data/diagrams/adda-08_page24_Image120.png"], "caption": "Annual Budget & Expenditure Pie Chart"},
        {"range": (46, 50), "images": ["data/diagrams/adda-08_page26_Image130.png", "data/diagrams/adda-08_page27_Image135.png"], "caption": "Vehicle Sales & Production Chart"}
    ],
    "adda-09": [
        {"range": (51, 55), "images": ["data/diagrams/adda-09_page27_Image136.png"], "caption": "Total Employees by Department (Bar Chart)"},
        {"range": (66, 70), "images": ["data/diagrams/adda-09_page33_Image166.png"], "caption": "Quarterly Revenue Growth (Bar Chart)"}
    ],
    "adda-10": [
        {"range": (64, 68), "images": ["data/diagrams/adda-10_page26_Image133.png"], "caption": "Monthly Production Data (Chart)"},
        {"range": (71, 75), "images": ["data/diagrams/adda-10_page28_Image142.png"], "caption": "Store Inventory & Furniture Data (Bar Chart)"},
        {"range": (76, 80), "images": ["data/diagrams/adda-10_page31_Image155.png"], "caption": "Export & Import Distribution (Chart)"}
    ]
}

def clean_fractions_and_math(text):
    if not text:
        return text
    # Fix broken multiline fraction like "349+ 5 9 of 35" -> "349 + 5/9 of 35"
    text = re.sub(r'\b(\d+)\s+(\d+)\s+of\b', r'\1/\2 of', text)
    # Fix broken fraction like "5 9 =?" -> "5/9 =?"
    text = re.sub(r'(\d+)\s+(\d+)\s*=\s*\?', r'\1/\2 = ?', text)
    # Fix raw LaTeX \frac{A}{B} -> (A/B)
    text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1/\2)', text)
    # Fix standalone \frac A B
    text = re.sub(r'\\frac\s*(\d+)\s*(\d+)', r'(\1/\2)', text)
    # Fix spaces around operators in math expressions
    text = re.sub(r'(\d+)\s*²\b', r'\1²', text)
    text = re.sub(r'\(\s*(\d+(?:\.\d+)?)\s*\)\s*²', r'(\1)²', text)
    text = re.sub(r'([+\-×÷=])', r' \1 ', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def enrich():
    tests_path = os.path.join(DATA_DIR, "adda_tests.json")
    tests_data = json.load(open(tests_path, encoding='utf-8'))['tests']
    
    # Table for adda-01 Q41-Q46
    ADDA01_TABLE_CLEAN = """
| Shops | Total number of mangoes sold | Percentage of mangoes sold to females |
|---|---|---|
| A | 480 | 75% |
| B | 560 | 60% |
| C | 320 | 45% |
| D | 750 | 80% |
""".strip()

    for test in tests_data:
        pid = test['id']
        mappings = DIAGRAM_MAPPING.get(pid, [])
        
        for q in test['questions']:
            q_num = q['number']
            
            # Clean math and fractions in stem, options, explanation
            q['stem'] = clean_fractions_and_math(q['stem'])
            q['options'] = [clean_fractions_and_math(opt) for opt in q['options']]
            q['explanation'] = clean_fractions_and_math(q['explanation'])
            
            # If adda-01 Q41-46, replace raw text table with clean markdown table
            if pid == "adda-01" and 41 <= q_num <= 46:
                # Replace unformatted table text
                raw_table_pattern = r'Shops\s+Total number of mangoes sold\s+Percentage of mangoes sold to females\s+A\s+480\s+75%?\s+B\s+560\s+60%?\s+C\s+320\s+45%?\s+D\s+750\s+80%?'
                if re.search(raw_table_pattern, q['stem']):
                    q['stem'] = re.sub(raw_table_pattern, '\n\n' + ADDA01_TABLE_CLEAN + '\n\n', q['stem'])
                elif ADDA01_TABLE_CLEAN not in q['stem']:
                    q['stem'] = f"Directions (41-46): Read the following table carefully and answer the questions.\n\n{ADDA01_TABLE_CLEAN}\n\n{q['stem']}"
            
            # Attach diagrams if matching range
            q['diagrams'] = []
            for m in mappings:
                r_start, r_end = m['range']
                if r_start <= q_num <= r_end:
                    q['diagrams'].extend(m['images'])
                    q['diagramCaption'] = m.get('caption', 'Reference Diagram / Chart')
                    
        # Save individual json
        out_paper_path = os.path.join(LICENSED_DIR, f"{pid}.json")
        with open(out_paper_path, 'w', encoding='utf-8') as f:
            json.dump(test, f, indent=2, ensure_ascii=False)
            
    # Save combined json
    with open(tests_path, 'w', encoding='utf-8') as f:
        json.dump({"tests": tests_data}, f, indent=2, ensure_ascii=False)
        
    # Save JS bundle
    bundle_path = os.path.join(DATA_DIR, "adda_tests_data.js")
    with open(bundle_path, 'w', encoding='utf-8') as f:
        f.write(f"window.__ADDA_TESTS_DATA__ = {{ tests: {json.dumps(tests_data, ensure_ascii=False)} }};\n")
        
    print("SUCCESS: Enriched all 10 Adda mock papers with diagram mappings and fraction formatting.")

if __name__ == '__main__':
    enrich()
