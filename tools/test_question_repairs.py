"""Prove repair outcomes from constraints and verify complete practice coverage."""
import csv
from fractions import Fraction
import json
from pathlib import Path
import pymupdf
from audit_previous_models import all_models, absolute

ROOT=Path(__file__).resolve().parents[1]
bank=json.loads((ROOT/'data/previous/catalog.json').read_text(encoding='utf-8'))
repairs=json.loads((ROOT/'data/previous/question_repairs.json').read_text(encoding='utf-8'))
by_id={t['id']:t for t in bank['papers']}
assert bank['auditSummary']['verifiedAnswers']==960 and bank['auditSummary']['excludedQuestions']==0
assert bank['auditSummary']['repairedQuestions']==32
assert sum(len(t['questionRepairs']) for t in bank['papers'])==37
restored=0
for t in bank['papers']:
    assert not t['excludedQuestions'] and len(t['answers'])==80
    assert all(isinstance(a,int) and 0<=a<5 for a in t['answers'].values())
    assert 'preRepair' not in t['preRepair']
    for n,r in t['questionRepairs'].items():
        assert len(r['options'])==5 and len(set(r['options']))==5
        assert t['answers'][n]==r['answerIndex'] and t['answerDetails'][n]['repair']==r
        if n in t['preRepair']['excludedQuestions']:restored+=1
        if r['stem'].startswith('A man'):
            assert r['options'][r['answerIndex']]=='Son'
        if r['stem'].startswith('A woman'):
            assert r['options'][r['answerIndex']]=='Mother'
assert restored==32

models={m.name:m for m in all_models()}
m=models['2022_boxes'];p=m.groups['position']
m.s.add(absolute(p['P']-p['V'])==1,absolute(p['P']-p['S'])==1,p['V']==p['Q']+1)
solutions=m.solve();assert len(solutions)==1
positions=solutions[0]['position'];assert ''.join(sorted(positions,key=positions.get))=='UQVPSTWXYR'
assert positions['S']==5 and positions['W']==7 and positions['Y']-positions['W']==2
m=models['2022_colours'];p=m.groups['position'];c=m.groups['colour'];m.s.add(p['P']!=c['Blue'])
solutions=m.solve();assert len(solutions)==1
r=solutions[0];assert r['position']['P']==r['colour']['Orange']
assert abs(r['position']['R']-r['colour']['Green'])-1==3
assert r['position']['S']+1==r['position']['U']==r['position']['P']-1
m=models['2023s2_ages'];p=m.groups['position'];m.s.add(p['M']<p['P'])
solutions=m.solve();assert len(solutions)==1
r=solutions[0]['position'];assert r['O']==1 and r['K']==5 and r['J']==2 and r['P']==4
assert r['L']==r['N']+1
age_repair=by_id['prepp-2023-08-05-shift-2']['questionRepairs']['26']
assert age_repair['options'][age_repair['answerIndex']]=='L'
meeting=models['2022_meetings'].solve();assert len(meeting)==1
p=meeting[0]['position'];truth=[p['G'] in (5,6),abs(p['A']-p['B'])-1==3,p['D'] in (1,2,5,6,7,8),False,p['G']+1==p['B']]
assert truth==[True,True,True,False,True]
assert round(936.43)/13/round(3.99)*12-round(13.48)*round(13.33)==47
assert Fraction(280+200,(360-140)+(500-320))==Fraction(6,5)
ratio_repair=by_id['prepp-2023-08-05-shift-2']['questionRepairs']['51']
assert ratio_repair['options'][ratio_repair['answerIndex']]=='6:5'
# Consistent witness for the rewritten syllogism, and a counterexample to I.
cup={'a'};spoon={'b','c'};plate={'a','b'};tiffin={'b'}
assert not cup&spoon and spoon&tiffin and spoon-tiffin and plate&cup and plate&spoon
assert not plate<=tiffin and tiffin&spoon
with pymupdf.open(ROOT/'data/previous/repaired_questions.pdf') as doc:
    assert len(doc)==38
    assert all('EDITORIAL PRACTICE REPAIR' in p.get_text() for p in list(doc)[1:])
    assert 'M is older than P' in ''.join(p.get_text() for p in doc)
with (ROOT/'data/previous/reviewed_answers.csv').open(encoding='utf-8-sig') as f:
    rows=list(csv.DictReader(f))
assert len(rows)==960 and all(r['Reviewed answer'] in 'ABCDE' and r['Reviewed answer'] for r in rows)
assert sum(bool(r['Editorial repair']) for r in rows)==37
print('PASS: all 32 exclusions repaired, 960 scored questions, unique puzzle models, valid options, age answer L, 6:5 chart choice, PDF and CSV.')
