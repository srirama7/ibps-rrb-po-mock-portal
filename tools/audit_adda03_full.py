import json
import os
import re

REPO_ROOT = r"C:\Users\amogh\ibps-rrb-portal-upgrade"
DATA_PATH = os.path.join(REPO_ROOT, "data", "licensed_adda", "adda-03.json")

with open(DATA_PATH, encoding='utf-8') as f:
    data = json.load(f)

questions = data['questions']
print(f"Total questions: {len(questions)}")

# Check 1: Q5-Q8 Seating / Inequalities
print("\n" + "="*70)
print("1. DETAILS FOR Q5-Q8")
print("="*70)
for i in range(4, 8):
    q = questions[i]
    print(f"\n--- Q{q['number']} ({q['topic']}) ---")
    print("Stem:", repr(q['stem']))
    print("Options:", q['options'])
    print("AnswerIndex:", q['answerIndex'])
    print("Diagrams:", q.get('diagrams'))
    print("Explanation:", repr(q['explanation']))

# Check 2: Q47-Q52 Twiggy/Xomato pie charts
print("\n" + "="*70)
print("2. DETAILS FOR Q47-Q52 (Twiggy / Xomato Pie Charts)")
print("="*70)
for i in range(46, 52):
    q = questions[i]
    print(f"\n--- Q{q['number']} ({q['topic']}) ---")
    print("Stem:", repr(q['stem'][:150]))
    print("Options:", q['options'])
    print("AnswerIndex:", q['answerIndex'])
    print("Diagrams:", q.get('diagrams'))
    print("Explanation:", repr(q['explanation'][:150]))

# Check 3: Q53-Q58 Songs download table
print("\n" + "="*70)
print("3. DETAILS FOR Q53-Q58 (Songs Download Table)")
print("="*70)
for i in range(52, 58):
    q = questions[i]
    print(f"\n--- Q{q['number']} ({q['topic']}) ---")
    print("Stem:", repr(q['stem'][:150]))
    print("Options:", q['options'])
    print("AnswerIndex:", q['answerIndex'])
    print("Diagrams:", q.get('diagrams'))
    print("Explanation:", repr(q['explanation'][:150]))

# Check 4: Q59-Q63 Formula images
print("\n" + "="*70)
print("4. DETAILS FOR Q59-Q63 (Formula Images)")
print("="*70)
for i in range(58, 63):
    q = questions[i]
    print(f"\n--- Q{q['number']} ({q['topic']}) ---")
    print("Stem:", repr(q['stem']))
    print("Options:", q['options'])
    print("AnswerIndex:", q['answerIndex'])
    print("Diagrams:", q.get('diagrams'))
    print("Explanation:", repr(q['explanation'][:150]))

# Check 5: All 80 questions general check
print("\n" + "="*70)
print("5. GENERAL AUDIT ACROSS ALL 80 QUESTIONS")
print("="*70)
hindi_count = 0
invalid_opt_count = 0
invalid_ans_count = 0
empty_expl_count = 0
generic_opt_count = 0
diagram_not_found = []

for q in questions:
    qnum = q['number']
    # Check Hindi/Devanagari
    all_text = q['stem'] + " " + q.get('explanation', '') + " " + " ".join(q['options'])
    if re.search(r'[\u0900-\u097F]', all_text):
        hindi_count += 1
        print(f"Hindi text found in Q{qnum}")

    # Options count
    if len(q['options']) != 5:
        invalid_opt_count += 1
        print(f"Q{qnum} does not have 5 options: {len(q['options'])}")

    # Answer index
    if not (0 <= q['answerIndex'] < len(q['options'])):
        invalid_ans_count += 1
        print(f"Q{qnum} has invalid answerIndex: {q['answerIndex']}")

    # Explanation
    if not q.get('explanation') or len(q['explanation'].strip()) < 10:
        empty_expl_count += 1
        print(f"Q{qnum} has missing or empty explanation")

    # Generic options like ['Option A', 'Option B', ...]
    if all(re.match(r'^Option [A-E]$', opt, re.IGNORECASE) for opt in q['options']):
        generic_opt_count += 1
        print(f"Q{qnum} has generic options: {q['options']}")

    # Diagram files existence
    for d in q.get('diagrams', []):
        fpath = os.path.join(REPO_ROOT, d.replace('/', os.sep))
        if not os.path.exists(fpath):
            diagram_not_found.append((qnum, d))

print(f"\nSummary:")
print(f"- Total questions: {len(questions)}")
print(f"- Questions with Hindi/Devanagari: {hindi_count}")
print(f"- Questions with invalid option count: {invalid_opt_count}")
print(f"- Questions with invalid answerIndex: {invalid_ans_count}")
print(f"- Questions with missing/empty explanation: {empty_expl_count}")
print(f"- Questions with generic placeholder options: {generic_opt_count}")
print(f"- Missing diagram files: {len(diagram_not_found)}")
