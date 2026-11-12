import os, sys, json, re

REPO_ROOT = r"C:\Users\amogh\ibps-rrb-portal-upgrade"
DATA_DIR = os.path.join(REPO_ROOT, "data")
DIAGRAMS_DIR = os.path.join(DATA_DIR, "diagrams")
TESTS_FILE = os.path.join(DATA_DIR, "adda_tests.json")

def audit():
    print("=" * 60)
    print("COMPREHENSIVE AUDIT OF ALL 10 ADDA MOCK TESTS (800 QUESTIONS)")
    print("=" * 60)

    with open(TESTS_FILE, encoding='utf-8') as f:
        data = json.load(f)
    
    tests = data['tests']
    assert len(tests) == 10, f"Expected 10 tests, got {len(tests)}"

    total_questions = 0
    total_diagrams = 0
    total_tables = 0
    total_fractions = 0
    hindi_chars_found = 0
    missing_images = []
    suspicious_questions = []

    for t in tests:
        pid = t['id']
        questions = t['questions']
        assert len(questions) == 80, f"Test {pid} has {len(questions)} questions instead of 80"
        total_questions += len(questions)

        for q in questions:
            qnum = q['number']
            stem = q['stem']
            options = q['options']
            expl = q['explanation']
            ans_idx = q['answerIndex']

            # 1. Answer Index validation
            assert 0 <= ans_idx < len(options), f"{pid} Q{qnum} has invalid answer index {ans_idx}"
            assert len(options) == 5, f"{pid} Q{qnum} does not have exactly 5 options"

            # 2. Hindi character check (Unicode block 0900-097F)
            for text_to_check in [stem, expl] + options:
                if re.search(r'[\u0900-\u097F]', text_to_check):
                    hindi_chars_found += 1
                    suspicious_questions.append((pid, qnum, "Devanagari text detected"))

            # 3. Diagrams check
            diags = q.get('diagrams', [])
            if diags:
                total_diagrams += len(diags)
                for d in diags:
                    img_path = os.path.join(REPO_ROOT, d.replace('/', os.sep))
                    if not os.path.exists(img_path) or os.path.getsize(img_path) == 0:
                        missing_images.append((pid, qnum, d))

            # 4. Tables check
            if '|---|' in stem:
                total_tables += 1

            # 5. Fractions check
            if re.search(r'\b\d+\s*/\s*\d+\b', stem) or re.search(r'\b\d+\s*/\s*\d+\b', expl):
                total_fractions += 1

            # 6. Check for mentions of charts/graphs/tables where diagram or table might be missing
            stem_lower = stem.lower()
            table_words = ['the following table', 'the given table', 'table given below', 'table below shows', 'study the table']
            chart_words = ['bar graph', 'pie chart', 'line graph', 'radar chart', 'given graph', 'given chart', 'study the following graph']
            
            for cw in chart_words:
                if cw in stem_lower and not diags:
                    suspicious_questions.append((pid, qnum, f"Mentions chart '{cw}' but has no diagram attached"))
            
            for tw in table_words:
                if tw in stem_lower and '|---|' not in stem and not diags:
                    suspicious_questions.append((pid, qnum, f"Mentions table '{tw}' but has no markdown table or diagram"))

    print(f"Total Questions Audited: {total_questions}")
    print(f"Total Diagram References: {total_diagrams}")
    print(f"Total Questions with Rendered Tables: {total_tables}")
    print(f"Total Questions with Mathematical Fractions: {total_fractions}")
    print(f"Hindi Characters Found: {hindi_chars_found}")
    print(f"Missing Image Files: {len(missing_images)}")
    if missing_images:
        for m in missing_images:
            print("  MISSING:", m)

    print(f"\nSuspicious / Potential Missing Assets: {len(suspicious_questions)}")
    for s in suspicious_questions:
        print(f"  [{s[0]} Q{s[1]:02d}] {s[2]}")

if __name__ == '__main__':
    audit()
