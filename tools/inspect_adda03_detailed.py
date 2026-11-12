import json
import os
import re

REPO_ROOT = r"C:\Users\amogh\ibps-rrb-portal-upgrade"
JSON_PATH = os.path.join(REPO_ROOT, "data", "licensed_adda", "adda-03.json")

with open(JSON_PATH, encoding='utf-8') as f:
    data = json.load(f)

print(f"Total questions: {len(data['questions'])}")

# 1. Inspect Q5 - Q8 (Seating diagrams)
print("\n" + "="*60)
print("AUDITING Q5-Q8 (Seating Arrangement Diagrams)")
print("="*60)
for q in data['questions'][4:8]:
    print(f"\n--- Question {q['number']} ---")
    print("Topic:", q['topic'])
    print("Stem:\n", q['stem'])
    print("Diagrams:", q.get('diagrams', []))
    print("Options:", q['options'])
    print(f"Answer Index: {q['answerIndex']} -> ({chr(65+q['answerIndex'])})")
    print("Explanation:\n", q['explanation'])
    for d in q.get('diagrams', []):
        full_d = os.path.join(REPO_ROOT, d.replace('/', os.sep))
        exists = os.path.exists(full_d)
        size = os.path.getsize(full_d) if exists else 0
        print(f"  Diagram file: {d} | Exists: {exists} | Size: {size} bytes")

# 2. Inspect Q47 - Q52 (Twiggy / Xomato pie charts)
print("\n" + "="*60)
print("AUDITING Q47-Q52 (Twiggy / Xomato Pie Charts)")
print("="*60)
for q in data['questions'][46:52]:
    print(f"\n--- Question {q['number']} ---")
    print("Topic:", q['topic'])
    print("Stem:\n", q['stem'][:300] + ("..." if len(q['stem']) > 300 else ""))
    print("Diagrams:", q.get('diagrams', []))
    print("Options:", q['options'])
    print(f"Answer Index: {q['answerIndex']} -> ({chr(65+q['answerIndex'])})")
    print("Explanation:\n", q['explanation'][:300] + ("..." if len(q['explanation']) > 300 else ""))
    for d in q.get('diagrams', []):
        full_d = os.path.join(REPO_ROOT, d.replace('/', os.sep))
        exists = os.path.exists(full_d)
        size = os.path.getsize(full_d) if exists else 0
        print(f"  Diagram file: {d} | Exists: {exists} | Size: {size} bytes")

# 3. Inspect Q53 - Q58 (Songs download table)
print("\n" + "="*60)
print("AUDITING Q53-Q58 (Songs Download Table)")
print("="*60)
for q in data['questions'][52:58]:
    print(f"\n--- Question {q['number']} ---")
    print("Topic:", q['topic'])
    print("Stem:\n", q['stem'])
    print("Diagrams:", q.get('diagrams', []))
    print("Options:", q['options'])
    print(f"Answer Index: {q['answerIndex']} -> ({chr(65+q['answerIndex'])})")
    print("Explanation:\n", q['explanation'][:300] + ("..." if len(q['explanation']) > 300 else ""))

# 4. Inspect Q59 - Q63 (Formula images)
print("\n" + "="*60)
print("AUDITING Q59-Q63 (Formula Images)")
print("="*60)
for q in data['questions'][58:63]:
    print(f"\n--- Question {q['number']} ---")
    print("Topic:", q['topic'])
    print("Stem:\n", q['stem'])
    print("Diagrams:", q.get('diagrams', []))
    print("Options:", q['options'])
    print(f"Answer Index: {q['answerIndex']} -> ({chr(65+q['answerIndex'])})")
    print("Explanation:\n", q['explanation'])
    for d in q.get('diagrams', []):
        full_d = os.path.join(REPO_ROOT, d.replace('/', os.sep))
        exists = os.path.exists(full_d)
        size = os.path.getsize(full_d) if exists else 0
        print(f"  Diagram file: {d} | Exists: {exists} | Size: {size} bytes")
