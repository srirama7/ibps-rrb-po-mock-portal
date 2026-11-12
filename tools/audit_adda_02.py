import json, re, os

REPO_ROOT = r"C:\Users\amogh\ibps-rrb-portal-upgrade"
JSON_PATH = os.path.join(REPO_ROOT, "data", "licensed_adda", "adda-02.json")

with open(JSON_PATH, encoding='utf-8') as f:
    paper = json.load(f)

print("=" * 60)
print(f"AUDITING {paper.get('title', 'adda-02')} ({len(paper['questions'])} questions)")
print("=" * 60)

# Check 1: Options length and answer indices
bad_options = []
bad_indices = []
for q in paper['questions']:
    if len(q.get('options', [])) != 5:
        bad_options.append((q['number'], len(q.get('options', []))))
    if not (0 <= q.get('answerIndex', -1) <= 4):
        bad_indices.append((q['number'], q.get('answerIndex')))

print(f"Questions with != 5 options: {len(bad_options)}")
print(f"Questions with invalid answerIndex: {len(bad_indices)}")

# Check 2: Hindi characters
hindi_matches = []
for q in paper['questions']:
    for fld in ['stem', 'explanation'] + q.get('options', []):
        h = re.findall(r'[\u0900-\u097F]', fld)
        if h:
            hindi_matches.append((q['number'], len(h)))
print(f"Devanagari/Hindi matches: {len(hindi_matches)}")

# Check 3: Check Q41-Q45 formula images
print("\n--- Check Q41-Q45: Formula Images ---")
for qnum in range(41, 46):
    q = paper['questions'][qnum - 1]
    diags = q.get('diagrams', [])
    caption = q.get('diagramCaption', '')
    exists = [os.path.exists(os.path.join(REPO_ROOT, d.replace('/', os.sep))) for d in diags]
    print(f"Q{qnum}: diagrams={diags}, caption='{caption}', exists={exists}")

# Check 4: Check Q46-Q51 Cupboard line graph
print("\n--- Check Q46-Q51: Cupboard Line Graph ---")
for qnum in range(46, 52):
    q = paper['questions'][qnum - 1]
    diags = q.get('diagrams', [])
    caption = q.get('diagramCaption', '')
    exists = [os.path.exists(os.path.join(REPO_ROOT, d.replace('/', os.sep))) for d in diags]
    print(f"Q{qnum}: diagrams={diags}, caption='{caption}', exists={exists}")

# Check 5: Check Q57-Q62 Companies table
print("\n--- Check Q57-Q62: Companies Table ---")
for qnum in range(57, 63):
    q = paper['questions'][qnum - 1]
    has_table = '|---|' in q.get('stem', '')
    print(f"Q{qnum}: has_markdown_table={has_table}")

# Check 6: Check for missing words/fractions across all questions
print("\n--- Check for Suspicious Stems (Dropped fractions/text) ---")
patterns = [
    (r'\bspends\s+of\b', 'Missing fraction after "spends"'),
    (r'\bis\s+of\b', 'Missing fraction after "is"'),
    (r'\bdecreased\s+by\s+(?:kg|%|cm|m)\b', 'Missing value before unit in "decreased by"'),
    (r'\bincreased\s+by\s+(?:kg|%|cm|m)\b', 'Missing value before unit in "increased by"'),
    (r'\bby\s+%\b', 'Missing percentage value'),
    (r'\bworth\s+Rs\.\s*\n', 'Missing amount'),
]

for q in paper['questions']:
    stem = q.get('stem', '')
    for p, desc in patterns:
        m = re.search(p, stem, re.IGNORECASE)
        if m:
            print(f"Q{q['number']}: {desc} -> match: '{m.group(0)}' in: {repr(stem[:80])}")

# Check 7: Explanations audit
print("\n--- Check Explanations ---")
boilerplate = 0
detailed = 0
for q in paper['questions']:
    exp = q.get('explanation', '')
    if 'Formulating the problem equation' in exp or 'Evaluating the given logical' in exp:
        boilerplate += 1
    else:
        detailed += 1
print(f"Boilerplate explanations: {boilerplate}")
print(f"Detailed explanations: {detailed}")
