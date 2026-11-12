import os, sys, re, json

REPO_ROOT = r"C:\Users\amogh\ibps-rrb-portal-upgrade"
DATA_DIR = os.path.join(REPO_ROOT, "data")
DIAGRAMS_DIR = os.path.join(DATA_DIR, "diagrams")
LICENSED_DIR = os.path.join(DATA_DIR, "licensed_adda")

# Clean, strictly verified diagram & chart mappings for all papers
# 1 image per single-chart/formula question; 2 images ONLY for legitimate dual charts (Pie Chart I & II)
DIAGRAM_MAPPINGS = {
    "adda-01": [
        {"range": (76, 80), "images": ["data/diagrams/adda-01_page24_Image115.png"], "caption": "Colleges Student Distribution (Pie Charts)"}
    ],
    "adda-02": [
        {"range": (41, 41), "images": ["data/diagrams/adda-02_page16_Image83.png"], "caption": "Approximation Equation Formula"},
        {"range": (42, 42), "images": ["data/diagrams/adda-02_page16_Image84.png"], "caption": "Approximation Equation Formula"},
        {"range": (43, 43), "images": ["data/diagrams/adda-02_page17_Image89.png"], "caption": "Approximation Equation Formula"},
        {"range": (44, 44), "images": ["data/diagrams/adda-02_page17_Image90.png"], "caption": "Approximation Equation Formula"},
        {"range": (45, 45), "images": ["data/diagrams/adda-02_page17_Image91.png"], "caption": "Approximation Equation Formula"},
        {"range": (46, 51), "images": ["data/diagrams/adda-02_page17_Image92.png"], "caption": "Monthly Cupboard & Dashboard Data (Line Graph)"}
    ],
    "adda-03": [
        # Q5-Q8 removed: no diagram needed for reasoning puzzles/inequalities
        {"range": (47, 52), "images": ["data/diagrams/adda-03_page27_Image135.jpeg", "data/diagrams/adda-03_page27_Image136.jpeg"], "caption": "Twiggy & Xomato Orders (Dual Pie Charts: Total & Twiggy)"},
        {"range": (53, 58), "images": ["data/diagrams/adda-03_page30_Image149.png", "data/diagrams/adda-03_page30_Image150.png"], "caption": "Quarterly Songs Download Data (Dual Tables: Quarter 1 & Quarter 2)"},
        {"range": (59, 59), "images": ["data/diagrams/adda-03_page32_Image159.png"], "caption": "Approximation Equation Formula"},
        {"range": (60, 60), "images": ["data/diagrams/adda-03_page32_Image160.png"], "caption": "Approximation Equation Formula"},
        {"range": (61, 61), "images": ["data/diagrams/adda-03_page33_Image165.png"], "caption": "Approximation Equation Formula"},
        {"range": (62, 62), "images": ["data/diagrams/adda-03_page33_Image166.png"], "caption": "Approximation Equation Formula"},
        {"range": (63, 63), "images": ["data/diagrams/adda-03_page33_Image167.png"], "caption": "Approximation Equation Formula"}
    ],
    "adda-04": [
        {"range": (41, 45), "images": ["data/diagrams/adda-04_page25_Image124.png"], "caption": "School Students & Boys (Line Graph)"}
    ],
    "adda-05": [
        # Exactly 1 English image (Image120 is English, Image121 is Hindi)
        {"range": (41, 45), "images": ["data/diagrams/adda-05_page24_Image120.png"], "caption": "Company TVs Sold (Bar Chart)"},
        # Exactly 1 English image (Image130 is English, Image131 is Hindi)
        {"range": (46, 50), "images": ["data/diagrams/adda-05_page26_Image130.png"], "caption": "Company Employees Distribution (Pie Chart)"},
        {"range": (56, 56), "images": ["data/diagrams/adda-05_page31_Image162.png"], "caption": "Approximation Equation Formula"},
        {"range": (57, 57), "images": ["data/diagrams/adda-05_page31_Image163.png"], "caption": "Approximation Equation Formula"}
    ],
    "adda-06": [
        {"range": (50, 50), "images": ["data/diagrams/adda-06_page27_Image137.png"], "caption": "Approximation Equation Formula"},
        {"range": (52, 57), "images": ["data/diagrams/adda-06_page28_Image142.jpeg", "data/diagrams/adda-06_page28_Image143.jpeg"], "caption": "Office People & Males Distribution (Dual Pie Charts: Total & Males)"}
    ],
    "adda-07": [
        {"range": (41, 46), "images": ["data/diagrams/adda-07_page25_Image124.png", "data/diagrams/adda-07_page26_Image129.png"], "caption": "Villages Population Distribution (Dual Pie Charts: 2021+2022 & 2022)"},
        # Exactly 1 image (Image147 was duplicate crop)
        {"range": (51, 55), "images": ["data/diagrams/adda-07_page29_Image142.png"], "caption": "Cities Population & Males Data (Bar Graph)"},
        {"range": (56, 56), "images": ["data/diagrams/adda-07_page34_Image164.png"], "caption": "Quadratic Equation Formula"},
        {"range": (57, 57), "images": ["data/diagrams/adda-07_page34_Image165.png"], "caption": "Quadratic Equation Formula"},
        {"range": (58, 58), "images": ["data/diagrams/adda-07_page35_Image170.png"], "caption": "Quadratic Equation Formula"},
        {"range": (59, 59), "images": ["data/diagrams/adda-07_page35_Image171.png"], "caption": "Quadratic Equation Formula"},
        {"range": (60, 60), "images": ["data/diagrams/adda-07_page35_Image172.png"], "caption": "Quadratic Equation Formula"},
        {"range": (61, 61), "images": ["data/diagrams/adda-07_page36_Image177.png"], "caption": "Approximation Equation Formula"},
        {"range": (62, 62), "images": ["data/diagrams/adda-07_page36_Image178.png"], "caption": "Approximation Equation Formula"},
        {"range": (63, 63), "images": ["data/diagrams/adda-07_page36_Image179.png"], "caption": "Approximation Equation Formula"},
        {"range": (64, 64), "images": ["data/diagrams/adda-07_page37_Image184.png"], "caption": "Approximation Equation Formula"},
        {"range": (65, 65), "images": ["data/diagrams/adda-07_page37_Image185.png"], "caption": "Approximation Equation Formula"}
    ],
    "adda-08": [
        # Exactly 1 image (Image125 was duplicate crop)
        {"range": (41, 45), "images": ["data/diagrams/adda-08_page24_Image120.png"], "caption": "Physics & Chemistry Student Distribution (Table)"},
        # Exactly 1 image (Image135 was duplicate crop)
        {"range": (46, 50), "images": ["data/diagrams/adda-08_page26_Image130.png"], "caption": "Villages Total Population Distribution (Pie Chart)"},
        {"range": (51, 51), "images": ["data/diagrams/adda-08_page28_Image140.png"], "caption": "Quadratic Equation Formula"},
        {"range": (52, 52), "images": ["data/diagrams/adda-08_page29_Image145.png"], "caption": "Quadratic Equation Formula"},
        {"range": (53, 53), "images": ["data/diagrams/adda-08_page29_Image146.png"], "caption": "Quadratic Equation Formula"},
        {"range": (54, 54), "images": ["data/diagrams/adda-08_page29_Image147.png"], "caption": "Quadratic Equation Formula"},
        {"range": (55, 55), "images": ["data/diagrams/adda-08_page30_Image162.png"], "caption": "Quadratic Equation Formula"},
        {"range": (56, 56), "images": ["data/diagrams/adda-08_page30_Image163.png"], "caption": "Quadratic Equation Formula"},
        {"range": (57, 57), "images": ["data/diagrams/adda-08_page30_Image164.png"], "caption": "Approximation Equation Formula"},
        {"range": (58, 58), "images": ["data/diagrams/adda-08_page31_Image169.png"], "caption": "Approximation Equation Formula"},
        {"range": (59, 59), "images": ["data/diagrams/adda-08_page31_Image170.png"], "caption": "Approximation Equation Formula"},
        {"range": (60, 60), "images": ["data/diagrams/adda-08_page32_Image175.png"], "caption": "Approximation Equation Formula"}
    ],
    "adda-09": [
        {"range": (51, 55), "images": ["data/diagrams/adda-09_page27_Image136.png"], "caption": "Hotels Total & Vacant Rooms (Table)"},
        {"range": (56, 56), "images": ["data/diagrams/adda-09_page30_Image149.png"], "caption": "Approximation Equation Formula"},
        {"range": (57, 57), "images": ["data/diagrams/adda-09_page30_Image150.png"], "caption": "Approximation Equation Formula"},
        {"range": (58, 58), "images": ["data/diagrams/adda-09_page30_Image151.png"], "caption": "Approximation Equation Formula"},
        {"range": (59, 59), "images": ["data/diagrams/adda-09_page31_Image156.png"], "caption": "Approximation Equation Formula"},
        {"range": (60, 60), "images": ["data/diagrams/adda-09_page31_Image157.png"], "caption": "Approximation Equation Formula"},
        {"range": (66, 70), "images": ["data/diagrams/adda-09_page33_Image166.png"], "caption": "Restaurant Visitors Vegetarian & Non-Veg (Bar Chart)"},
        {"range": (76, 76), "images": ["data/diagrams/adda-09_page37_Image187.png"], "caption": "Quadratic Equation Formula"},
        {"range": (77, 77), "images": ["data/diagrams/adda-09_page37_Image188.png"], "caption": "Quadratic Equation Formula"},
        {"range": (78, 78), "images": ["data/diagrams/adda-09_page37_Image189.png"], "caption": "Quadratic Equation Formula"},
        {"range": (79, 79), "images": ["data/diagrams/adda-09_page40_Image194.png"], "caption": "Quadratic Equation Formula"},
        {"range": (80, 80), "images": ["data/diagrams/adda-09_page40_Image195.png"], "caption": "Quadratic Equation Formula"}
    ],
    "adda-10": [
        {"range": (46, 46), "images": ["data/diagrams/adda-10_page21_Image108.png"], "caption": "Approximation Equation Formula"},
        {"range": (47, 47), "images": ["data/diagrams/adda-10_page21_Image109.png"], "caption": "Approximation Equation Formula"},
        {"range": (48, 48), "images": ["data/diagrams/adda-10_page22_Image114.png"], "caption": "Approximation Equation Formula"},
        {"range": (49, 49), "images": ["data/diagrams/adda-10_page22_Image115.png"], "caption": "Approximation Equation Formula"},
        {"range": (50, 50), "images": ["data/diagrams/adda-10_page22_Image116.png"], "caption": "Approximation Equation Formula"},
        {"range": (64, 68), "images": ["data/diagrams/adda-10_page26_Image133.png"], "caption": "Company Employees Distribution (Table)"},
        {"range": (71, 75), "images": ["data/diagrams/adda-10_page28_Image142.png"], "caption": "Stores Cupboards & Drawers (Bar Chart)"},
        # Q76-Q80: EXACTLY 1 quadratic formula image per question (Image155 removed!)
        {"range": (76, 76), "images": ["data/diagrams/adda-10_page31_Image156.png"], "caption": "Quadratic Equation Formula"},
        {"range": (77, 77), "images": ["data/diagrams/adda-10_page31_Image157.png"], "caption": "Quadratic Equation Formula"},
        {"range": (78, 78), "images": ["data/diagrams/adda-10_page34_Image162.png"], "caption": "Quadratic Equation Formula"},
        {"range": (79, 79), "images": ["data/diagrams/adda-10_page34_Image163.png"], "caption": "Quadratic Equation Formula"},
        {"range": (80, 80), "images": ["data/diagrams/adda-10_page34_Image164.png"], "caption": "Quadratic Equation Formula"}
    ]
}

# Clean Markdown Tables
TABLE_ADDA_01 = """
| Shops | Total number of mangoes sold | Percentage of mangoes sold to females |
|---|---|---|
| A | 480 | 75% |
| B | 560 | 60% |
| C | 320 | 45% |
| D | 750 | 80% |
""".strip()

TABLE_ADDA_02 = """
| Companies | Ratio of Male : Female | Females |
|---|---|---|
| A | 7:5 | 25 |
| B | 3:4 | 64 |
| C | 6:11 | 88 |
| D | 3:7 | 70 |
| E | 9:13 | 65 |
""".strip()

TABLE_ADDA_04 = """
| Malls | Total People | Percentage of males out of total males |
|---|---|---|
| A | 200 | 14% |
| B | 350 | 24% |
| C | 320 | 29% |
| D | 240 | 18% |
| E | 180 | 15% |
""".strip()

TABLE_ADDA_06 = """
| Year | Percentage of products exports by company A | Number of products exports by company B | Total number of products exports |
|---|---|---|---|
| 2010 | 56% | 136 | 400 |
| 2011 | 40% | 48 | 380 |
| 2012 | 72% | 30 | 250 |
""".strip()

def clean_fractions_and_math(text):
    if not text:
        return text
    # Fix broken multiline fraction like "349+ 5 9 of 35" -> "349 + (5/9) of 35"
    text = re.sub(r'349\s*\+\s*5\s*\n?\s*9\s*[𝑜o][𝑓f]\s*35[^\n]*', '349 + (5/9) of 35 = ? - 19.98% of 240', text)
    text = re.sub(r'89\.99%[𝑜o][𝑓f]240\s*\+\s*3\s*\n?\s*5\s*[𝑜o][𝑓f]79[^\n]*', '89.99% of 240 + (3/5) of 79 = ? - 79.98', text)
    text = re.sub(r'\b(\d+)\s+(\d+)\s+of\b', r'(\1/\2) of', text)
    text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1/\2)', text)
    text = re.sub(r'\\frac\s*(\d+)\s*(\d+)', r'(\1/\2)', text)
    text = re.sub(r'(\d+)\s*²\b', r'\1²', text)
    text = re.sub(r'(\d+)\s*³\b', r'\1³', text)
    # Strip any stray Hindi/Devanagari characters (Unicode block 0900-097F)
    text = re.sub(r'[\u0900-\u097F]+', '', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text.strip()

def enrich_all():
    tests_path = os.path.join(DATA_DIR, "adda_tests.json")
    with open(tests_path, encoding='utf-8') as f:
        tests_data = json.load(f)['tests']

    for test in tests_data:
        pid = test['id']
        mappings = DIAGRAM_MAPPINGS.get(pid, [])

        for q in test['questions']:
            q_num = q['number']

            # Clean math and fractions
            q['stem'] = clean_fractions_and_math(q['stem'])
            q['options'] = [clean_fractions_and_math(opt) for opt in q['options']]
            q['explanation'] = clean_fractions_and_math(q['explanation'])

            # Embed Markdown tables where applicable
            if pid == "adda-01" and 41 <= q_num <= 46:
                if TABLE_ADDA_01 not in q['stem']:
                    q['stem'] = f"Directions (41-46): Read the following table carefully and answer the questions given below. The table shows the total number of mangoes sold and the percentage of mangoes sold to females by four shops.\n\n{TABLE_ADDA_01}\n\n{q['stem']}"

            elif pid == "adda-02" and 57 <= q_num <= 62:
                if TABLE_ADDA_02 not in q['stem']:
                    q['stem'] = f"Directions (57-62): Read the information and answer the following question. The table shows the total number of females and ratio of male to females in five different companies.\n\n{TABLE_ADDA_02}\n\n{q['stem']}"

            elif pid == "adda-04" and 46 <= q_num <= 50:
                if TABLE_ADDA_04 not in q['stem']:
                    q['stem'] = f"Directions (46-50): Read the following table carefully and answer the questions given below. The table shows the total number of people (males + females) who visit five malls, and it also shows the percentage of males out of total males who visit these malls. Note: Total males = 1000\n\n{TABLE_ADDA_04}\n\n{q['stem']}"

            elif pid == "adda-06" and 41 <= q_num <= 46:
                if TABLE_ADDA_06 not in q['stem']:
                    q['stem'] = f"Directions (41-46): The table shows the percentage of products export by company A out of total product and the number of products exports by company B in three years. The table also shows the total number of products exports in these years. Note: Total number of products exports = Number of products export by company A + Number of products export by company B + Number of products export by company C.\n\n{TABLE_ADDA_06}\n\n{q['stem']}"

            # Attach diagrams & formula images
            q['diagrams'] = []
            for m in mappings:
                r_start, r_end = m['range']
                if r_start <= q_num <= r_end:
                    q['diagrams'].extend(m['images'])
                    q['diagramCaption'] = m.get('caption', 'Reference Diagram / Formula Chart')

        # Save individual JSON
        out_paper_path = os.path.join(LICENSED_DIR, f"{pid}.json")
        with open(out_paper_path, 'w', encoding='utf-8') as f:
            json.dump(test, f, indent=2, ensure_ascii=False)

    # Save combined JSON
    with open(tests_path, 'w', encoding='utf-8') as f:
        json.dump({"tests": tests_data}, f, indent=2, ensure_ascii=False)

    # Save JS bundle
    bundle_path = os.path.join(DATA_DIR, "adda_tests_data.js")
    with open(bundle_path, 'w', encoding='utf-8') as f:
        f.write(f"window.__ADDA_TESTS_DATA__ = {{ tests: {json.dumps(tests_data, ensure_ascii=False)} }};\n")

    print("SUCCESS: Fully enriched all 10 Adda mock papers with strict clean mappings.")

if __name__ == '__main__':
    enrich_all()
