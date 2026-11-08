"""Check all displayed puzzle answers from the solved layouts, without the generator."""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
data = json.loads((root / 'data/tests.json').read_text(encoding='utf-8'))
count = 0
for test in data['tests']:
    stimuli = {s['id']: s for s in test['stimuli']}
    for q in test['questions']:
        st = stimuli.get(q.get('stimulusId'))
        if not st or st['type'] != 'logic_puzzle':
            continue
        layout = [entry.rsplit(': ', 1)[1] for entry in st['solution'].split('; ')]
        positions = {name: i for i, name in enumerate(layout)}
        assert len(positions) == 8
        s = q['stem']
        kind = st['variant']
        mentioned = [name for name in re.findall(r'\b[A-Z][a-z]+\b', s) if name in positions]
        if s.startswith('Which of the following does not'):
            if kind == 'floor':
                parity = 0 if 'Flat A' in s else 1
                wrong = [name for name in q['options'] if positions[name] % 2 != parity]
            else:
                half = positions[q['options'][0]] // 4
                if kind == 'parallel':
                    groups = [[name for name in q['options'] if positions[name] // 4 == h] for h in [0, 1]]
                    assert sorted(map(len, groups)) == [1, 4]
                    wrong = next(g for g in groups if len(g) == 1)
                else:
                    half = 0 if '1–4' in s else 1
                    wrong = [name for name in q['options'] if positions[name] // 4 != half]
            assert len(wrong) == 1, q['id']
            expected = wrong[0]
        elif s.startswith('How many'):
            a, b = map(positions.get, mentioned)
            gap = abs(a - b)
            expected = str(max(0, abs(a//2-b//2)-1) if kind == 'floor' else (min(gap, 8-gap) if kind == 'circular' else gap) - 1)
        elif s.startswith('Who faces'):
            expected = layout[(positions[mentioned[0]] + 4) % 8]
        else:
            ref = positions[mentioned[0]]
            if kind == 'floor':
                dest = ref ^ 1 if 'other flat' in s else ref + (2 if 'above' in s else -2)
            else:
                step = int(re.search(r'\d+', s)[0])
                if kind == 'circular':
                    dest = (ref + step) % 8
                elif kind == 'parallel':
                    positive = ('left' in s) == (ref < 4)
                    dest = ref + (step if positive else -step)
                    assert dest // 4 == ref // 4
                else:
                    dest = ref + step
            expected = layout[dest]
        actual = q['options'][q['answerIndex']]
        assert actual == expected, (q['id'], actual, expected)
        count += 1
assert count == 400
print('PASS: all 400 puzzle question keys checked against their solved layouts.')
