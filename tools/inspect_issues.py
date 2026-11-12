import json, re

data = json.load(open(r"C:\Users\amogh\ibps-rrb-portal-upgrade\data\adda_tests.json", encoding="utf-8"))['tests']

chart_questions = []
fraction_questions = []

for t in data:
    for q in t['questions']:
        stem = q['stem']
        num = q['number']
        # Check DI / chart / table / graph mentions
        if any(w in stem.lower() for w in ['bar chart', 'bar graph', 'pie chart', 'line graph', 'given table', 'following table', 'table shows', 'following chart', 'given chart', 'radar chart', 'caselet']):
            chart_questions.append((t['id'], num, stem[:120]))
        # Check broken fractions / math patterns
        # e.g. numbers separated by spaces that look like numerator/denominator or isolated numbers
        if re.search(r'\b\d+\s+\d+\s+of\b', stem) or re.search(r'\b\d+\s+/\s+\d+\b', stem) or '?' in stem and any(c in stem for c in ['+', '-', '×', '*', '/', '%', '²']):
            if any(f in stem for f in ['of', '%', '²']) and any(c in stem for c in ['+', '-', '=']):
                fraction_questions.append((t['id'], num, stem[:120]))

print(f"Total DI / Chart questions identified: {len(chart_questions)}")
print("Sample chart questions:")
for c in chart_questions[:10]:
    print(c)

print(f"\nTotal fraction / math questions identified: {len(fraction_questions)}")
print("Sample fraction / math questions:")
for f in fraction_questions[:10]:
    print(f)
