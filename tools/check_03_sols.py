import json

reader = json.load(open('data/licensed_adda/adda-03.json', encoding='utf-8'))
print("=== ADDA-03 SOLUTIONS FOR Q6, Q7, Q8 ===")
for q in reader['questions']:
    if q['number'] in [6, 7, 8]:
        print(f"Q{q['number']}: Ans={q['answerIndex']} ({'ABCDE'[q['answerIndex']]})")
        print("Expl:", q['explanation'])
