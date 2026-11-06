"""Independent structural and content QA for the 20-mock dataset."""
import json, csv
from pathlib import Path
from collections import Counter

root = Path(__file__).resolve().parents[1]
with (root / 'data/tests.json').open(encoding='utf-8') as f:
    data = json.load(f)

assert data['totalMocks'] == 20 and data['totalQuestions'] == 1600
assert len(data['tests']) == 20

ids = set()
sids = set()
all_answers = []
breakdown = Counter()

for tno, t in enumerate(data['tests'], 1):
    assert t['number'] == tno and t['id'] == f'MOCK-{tno:02d}'
    assert len(t['questions']) == 80 and t['durationSeconds'] == 2700
    assert len(t['sections']) == 2 and [s['durationSeconds'] for s in t['sections']] == [1500, 1200]
    assert [q['section'] for q in t['questions']] == ['reasoning'] * 40 + ['quant'] * 40

    stimuli = {s['id']: s for s in t['stimuli']}
    assert len(stimuli) == len(t['stimuli']) == 7
    assert len([s for s in stimuli.values() if s['type'] == 'logic_puzzle']) == 4
    assert len([s for s in stimuli.values() if s['type'] == 'data_interpretation']) == 3
    sids.update(stimuli)

    # Check question counts
    assert len(t['questions']) == 80
    test_stems = set()

    for n, q in enumerate(t['questions'], 1):
        assert q['number'] == n and q['id'] == f'M{tno:02d}-Q{n:02d}'
        assert q['id'] not in ids
        ids.add(q['id'])

        # Strict 5 choices assertion
        assert len(q['options']) == 5, f"Question {q['id']} has {len(q['options'])} options instead of 5!"
        assert len(set(q['options'])) == 5, f"Question {q['id']} has duplicate options: {q['options']}"
        assert isinstance(q['answerIndex'], int) and 0 <= q['answerIndex'] < 5
        assert isinstance(q['explanation'], str) and len(q['explanation'].strip()) >= 15
        contextual_stem = (q.get('stimulusId'), q['stem'])
        assert contextual_stem not in test_stems, f"Duplicate question within mock {tno}: {q['stem'][:60]}"
        test_stems.add(contextual_stem)

        if q.get('stimulusId'):
            assert q['stimulusId'] in stimuli

        breakdown[q['topic']] += 1
        all_answers.append({
            'mock': t['id'],
            'question': q['number'],
            'questionId': q['id'],
            'topic': q['topic'],
            'correctOption': 'ABCDE'[q['answerIndex']],
            'correctAnswer': q['options'][q['answerIndex']],
            'explanation': q['explanation']
        })

    for s in stimuli.values():
        assert len(s['title'].strip()) > 5
        assert len(s['body'].strip()) > 10
        assert len(s['solution'].strip()) > 5

assert len(ids) == 1600
assert len(sids) == 140

# Write individual mock JSONs and answer-key CSV
for t in data['tests']:
    (root / 'data' / f'mock_{t["number"]:02d}.json').write_text(json.dumps(t, ensure_ascii=False, indent=2), encoding='utf-8')

with (root / 'data/answer_keys.csv').open('w', encoding='utf-8-sig', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=list(all_answers[0]), lineterminator='\n')
    w.writeheader()
    w.writerows(all_answers)

(root / 'data/qa_report.json').write_text(json.dumps({
    'status': 'PASS',
    'mocks': 20,
    'questions': len(ids),
    'optionsPerQuestion': 5,
    'sectionsPerPaper': [40, 40],
    'durationSecondsPerPaper': 2700,
    'stimuli': len(sids),
    'topicCounts': dict(breakdown)
}, indent=2), encoding='utf-8')

print('PASS: 20 mocks; 1,600 questions; 140 passages; five distinct options and valid references. Structural checks do not establish official difficulty parity.')
