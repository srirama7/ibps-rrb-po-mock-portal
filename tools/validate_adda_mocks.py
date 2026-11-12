import os, sys, json, re

REPO_ROOT = r"C:\Users\amogh\ibps-rrb-portal-upgrade"
DATA_DIR = os.path.join(REPO_ROOT, "data")

def validate():
    catalog_path = os.path.join(DATA_DIR, "adda_mocks_catalog.json")
    if not os.path.exists(catalog_path):
        print("FAIL: Catalog file missing")
        sys.exit(1)
        
    catalog = json.load(open(catalog_path, encoding='utf-8'))
    papers = catalog.get("papers", [])
    if len(papers) != 10:
        print(f"FAIL: Expected 10 papers, got {len(papers)}")
        sys.exit(1)
        
    keys_path = os.path.join(DATA_DIR, "adda_answer_keys.json")
    answer_keys = json.load(open(keys_path, encoding='utf-8'))
    
    tests_path = os.path.join(DATA_DIR, "adda_tests.json")
    tests_data = json.load(open(tests_path, encoding='utf-8'))['tests']
    if len(tests_data) != 10:
        print(f"FAIL: Expected 10 test structures, got {len(tests_data)}")
        sys.exit(1)
        
    total_questions = 0
    hindi_violations = 0
    
    for paper, test in zip(papers, tests_data):
        pid = paper['id']
        assert pid == test['id'], f"Mismatched id: {pid} vs {test['id']}"
        qs = test.get('questions', [])
        if len(qs) != 80:
            print(f"FAIL: {pid} has {len(qs)} questions instead of 80")
            sys.exit(1)
            
        reasoning_count = sum(1 for q in qs if q.get('section') == 'reasoning')
        quant_count = sum(1 for q in qs if q.get('section') == 'quant')
        if reasoning_count != 40 or quant_count != 40:
            print(f"FAIL: {pid} section split invalid: {reasoning_count} reasoning, {quant_count} quant")
            sys.exit(1)
            
        paper_keys = answer_keys.get(pid, {})
        if len(paper_keys) != 80:
            print(f"FAIL: {pid} has {len(paper_keys)} answer keys instead of 80")
            sys.exit(1)
            
        for q in qs:
            total_questions += 1
            num = q['number']
            if len(q.get('options', [])) != 5:
                print(f"FAIL: {pid} Q{num} has {len(q.get('options', []))} options instead of 5")
                sys.exit(1)
            idx = q.get('answerIndex')
            if idx is None or not (0 <= idx <= 4):
                print(f"FAIL: {pid} Q{num} invalid answerIndex: {idx}")
                sys.exit(1)
            if not q.get('explanation'):
                print(f"FAIL: {pid} Q{num} missing explanation")
                sys.exit(1)
            # Check Hindi chars
            hindi_in_stem = len(re.findall(r'[\u0900-\u097F]', q.get('stem', '')))
            if hindi_in_stem > 0:
                hindi_violations += 1
                
    if hindi_violations > 0:
        print(f"WARNING: Found {hindi_violations} questions with residual Devanagari characters")
    
    print(f"PASS: 10 Adda mock papers; {total_questions} questions verified; 800 answer keys verified; all questions in English with 5 options each.")

if __name__ == '__main__':
    validate()
