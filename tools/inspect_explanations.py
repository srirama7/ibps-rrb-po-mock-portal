import json

data = json.load(open('data/adda_tests.json', encoding='utf-8'))['tests']

def print_q(pid, qnum):
    test = [t for t in data if t['id'] == pid][0]
    q = [q for q in test['questions'] if q['number'] == qnum][0]
    print(f"=== {pid} Q{qnum} ===")
    print("STEM:", q['stem'])
    print("OPTIONS:", q['options'])
    print("EXPLANATION:", q['explanation'])
    print()

print_q('adda-02', 41)
print_q('adda-05', 56)
print_q('adda-10', 76)
