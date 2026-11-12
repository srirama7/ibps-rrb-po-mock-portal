import json
from pathlib import Path

REPO_ROOT = Path(r"C:\Users\amogh\ibps-rrb-portal-upgrade")

def check_paper_3():
    with open(REPO_ROOT / "data/licensed_adda/adda-03.json", encoding="utf-8") as f:
        d3 = json.load(f)
    print("=== ADDA-03 ===")
    for qnum in [5, 6, 7, 8, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63]:
        q = d3["questions"][qnum - 1]
        has_table = "|" in q["stem"]
        print(f"Q{qnum:02d}: topic={q['topic']}, diagrams={q.get('diagrams')}, has_table={has_table}")

def check_paper_4():
    with open(REPO_ROOT / "data/licensed_adda/adda-04.json", encoding="utf-8") as f:
        d4 = json.load(f)
    print("\n=== ADDA-04 ===")
    for qnum in range(41, 51):
        q = d4["questions"][qnum - 1]
        has_table = "|" in q["stem"]
        print(f"Q{qnum:02d}: topic={q['topic']}, diagrams={q.get('diagrams')}, has_table={has_table}")

if __name__ == "__main__":
    check_paper_3()
    check_paper_4()
