"""Independent structural and content QA for the 20-mock dataset."""
import json, csv, re
from pathlib import Path
from collections import Counter

root=Path(__file__).resolve().parents[1]
with (root/'data/tests.json').open(encoding='utf-8') as f:data=json.load(f)
assert data['totalMocks']==20 and data['totalQuestions']==1600
assert len(data['tests'])==20
stems=set();ids=set();sids=set();all_answers=[];breakdown=Counter()
for tno,t in enumerate(data['tests'],1):
    assert t['number']==tno and t['id']==f'MOCK-{tno:02d}'
    assert len(t['questions'])==80 and t['durationSeconds']==2700
    assert len(t['sections'])==2 and [s['durationSeconds'] for s in t['sections']]==[1500,1200]
    assert [q['section'] for q in t['questions']]==['reasoning']*40+['quant']*40
    stimuli={s['id']:s for s in t['stimuli']}
    assert len(stimuli)==len(t['stimuli'])==8
    assert len([s for s in stimuli.values() if s['type']=='logic_puzzle'])==4
    assert len([s for s in stimuli.values() if s['type']=='data_interpretation'])==3
    assert len([s for s in stimuli.values() if s['type']=='coding'])==1
    sids.update(stimuli)
    assert len([q for q in t['questions'] if q['topic']=='Puzzle & Seating Arrangement'])==20
    assert len([q for q in t['questions'] if q['topic']=='Data Interpretation'])==15
    assert len([q for q in t['questions'] if q['topic']=='Simplification'])==5
    assert len([q for q in t['questions'] if q['topic']=='Number Series'])==5
    assert len([q for q in t['questions'] if q['topic']=='Quadratic Comparison'])==5
    assert len([q for q in t['questions'] if q['topic'] in ('Inequality','Syllogism')])==10
    assert len([q for q in t['questions'] if q['topic']=='Coding-Decoding'])==4
    assert len([q for q in t['questions'] if q['topic']=='Direction & Distance'])==3
    assert len([q for q in t['questions'] if q['topic']=='Blood Relations'])==3
    for n,q in enumerate(t['questions'],1):
        assert q['number']==n and q['id']==f'M{tno:02d}-Q{n:02d}'
        assert q['id'] not in ids;ids.add(q['id'])
        assert len(q['options'])==5 and len(set(q['options']))==5
        assert isinstance(q['answerIndex'],int) and 0<=q['answerIndex']<5
        assert isinstance(q['explanation'],str) and len(q['explanation'].strip())>=12
        assert q['stem'] not in stems, ('duplicate',q['stem']);stems.add(q['stem'])
        if q.get('stimulusId'):assert q['stimulusId'] in stimuli
        breakdown[q['topic']]+=1
        all_answers.append({'mock':t['id'],'question':q['number'],'questionId':q['id'],
                            'topic':q['topic'],'correctOption':'ABCDE'[q['answerIndex']],
                            'correctAnswer':q['options'][q['answerIndex']],
                            'explanation':q['explanation']})
    for s in stimuli.values():
        if s['type']=='logic_puzzle':
            assert s['uniquenessVerified'] is True and len(s['solution'].split('; '))==7
            assert len(s['body'].splitlines())>=5
        if s['type']=='data_interpretation':
            assert len(s['rows'])==5 and len(s['columns'])==3
            assert all(row['a']>0 and row['b']>0 for row in s['rows'])
assert len(ids)==1600 and len(stems)==1600 and len(sids)==160

# Produce individual mock JSONs and a lightweight answer-key CSV.
for t in data['tests']:
    (root/'data'/f'mock_{t["number"]:02d}.json').write_text(json.dumps(t,ensure_ascii=False,indent=2),encoding='utf-8')
with (root/'data/answer_keys.csv').open('w',encoding='utf-8-sig',newline='') as fh:
    w=csv.DictWriter(fh,fieldnames=list(all_answers[0]));w.writeheader();w.writerows(all_answers)
(root/'data/qa_report.json').write_text(json.dumps({'status':'PASS','mocks':20,'uniqueStems':len(stems),'questions':len(ids),
    'sectionsPerPaper':[40,40],'durationSecondsPerPaper':2700,'stimuli':len(sids),'topicCounts':dict(breakdown)},indent=2),encoding='utf-8')
print('PASS: 20 mocks; 1,600 unique question stems; 160 common passages; 5 choices per question; answer key & explanation for every question.')
