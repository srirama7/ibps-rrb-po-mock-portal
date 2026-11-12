import json
import os
import re

REPO_ROOT = r"C:\Users\amogh\ibps-rrb-portal-upgrade"
DATA_DIR = os.path.join(REPO_ROOT, "data")

def audit_paper(pid):
    filepath = os.path.join(DATA_DIR, "licensed_adda", f"{pid}.json")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def run():
    p6 = audit_paper("adda-06")
    p7 = audit_paper("adda-07")

    print("=========================================")
    print("AUDITING ADDA-06")
    print("=========================================")
    print(f"Title: {p6.get('title')}, Total Questions: {len(p6.get('questions', []))}")
    
    # Q41-Q46
    print("\n--- ADDA-06 Q41-Q46 (Product Export Table) ---")
    for q in p6['questions']:
        num = q['number']
        if 41 <= num <= 46:
            print(f"\n[Q{num}]")
            print("Stem:\n", q['stem'])
            print("Options:", q['options'])
            ans_idx = q['answerIndex']
            opt_letter = chr(65 + ans_idx) if 0 <= ans_idx < 5 else "INVALID"
            print(f"answerIndex: {ans_idx} ({opt_letter})")
            print("Diagrams:", q.get('diagrams'))
            print("Explanation:\n", q['explanation'])

    # Q52-Q57
    print("\n--- ADDA-06 Q52-Q57 (Office Pie Chart) ---")
    for q in p6['questions']:
        num = q['number']
        if 52 <= num <= 57:
            print(f"\n[Q{num}]")
            print("Stem:\n", q['stem'])
            print("Options:", q['options'])
            ans_idx = q['answerIndex']
            opt_letter = chr(65 + ans_idx) if 0 <= ans_idx < 5 else "INVALID"
            print(f"answerIndex: {ans_idx} ({opt_letter})")
            print("Diagrams:", q.get('diagrams'))
            print("Explanation:\n", q['explanation'])

    print("\n=========================================")
    print("AUDITING ADDA-07")
    print("=========================================")
    print(f"Title: {p7.get('title')}, Total Questions: {len(p7.get('questions', []))}")

    # Q41-Q46
    print("\n--- ADDA-07 Q41-Q46 (Pie Charts) ---")
    for q in p7['questions']:
        num = q['number']
        if 41 <= num <= 46:
            print(f"\n[Q{num}]")
            print("Stem:\n", q['stem'])
            print("Options:", q['options'])
            ans_idx = q['answerIndex']
            opt_letter = chr(65 + ans_idx) if 0 <= ans_idx < 5 else "INVALID"
            print(f"answerIndex: {ans_idx} ({opt_letter})")
            print("Diagrams:", q.get('diagrams'))
            print("Explanation:\n", q['explanation'])

    # Q51-Q55
    print("\n--- ADDA-07 Q51-Q55 (Bar Graph) ---")
    for q in p7['questions']:
        num = q['number']
        if 51 <= num <= 55:
            print(f"\n[Q{num}]")
            print("Stem:\n", q['stem'])
            print("Options:", q['options'])
            ans_idx = q['answerIndex']
            opt_letter = chr(65 + ans_idx) if 0 <= ans_idx < 5 else "INVALID"
            print(f"answerIndex: {ans_idx} ({opt_letter})")
            print("Diagrams:", q.get('diagrams'))
            print("Explanation:\n", q['explanation'])

    # Q56-Q65
    print("\n--- ADDA-07 Q56-Q65 (Formula Images) ---")
    for q in p7['questions']:
        num = q['number']
        if 56 <= num <= 65:
            print(f"\n[Q{num}]")
            print("Stem:\n", q['stem'])
            print("Options:", q['options'])
            ans_idx = q['answerIndex']
            opt_letter = chr(65 + ans_idx) if 0 <= ans_idx < 5 else "INVALID"
            print(f"answerIndex: {ans_idx} ({opt_letter})")
            print("Diagrams:", q.get('diagrams'))
            print("Explanation:\n", q['explanation'])

if __name__ == '__main__':
    run()
