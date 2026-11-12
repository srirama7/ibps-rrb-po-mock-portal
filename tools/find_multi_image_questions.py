import json

data = json.load(open('data/adda_tests.json', encoding='utf-8'))['tests']

print("=" * 60)
print("QUESTIONS WITH MULTIPLE IMAGES ATTACHED")
print("=" * 60)

count = 0
for t in data:
    for q in t['questions']:
        diags = q.get('diagrams', [])
        if len(diags) > 1:
            count += 1
            print(f"[{t['id']} Q{q['number']:02d}] {len(diags)} images:")
            for d in diags:
                print(f"    - {d}")
            print(f"    Stem: {q['stem'][:120]}...\n")

print(f"Total questions with >1 image: {count}")
