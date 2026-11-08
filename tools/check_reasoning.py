"""Recheck non-puzzle reasoning from public stems, without importing the generator."""
import itertools, json, re, math
from pathlib import Path
data=json.loads((Path(__file__).resolve().parents[1]/'data/tests.json').read_text(encoding='utf-8'))
options=['Only I follows','Only II follows','Both I and II follow','Neither I nor II follows','Either I or II follows']
count=0
def compare(a,op,b): return {'>':a>b,'<':a<b,'=':a==b,'≥':a>=b,'≤':a<=b}[op]
for t in data['tests']:
    for q in t['questions']:
        if q['section']!='reasoning' or q.get('stimulusId'): continue
        s=q['stem'];topic=q['topic']
        if topic=='Inequality':
            chain=s.split('Statements: ')[1].split('.')[0].split()
            letters=chain[::2];ops=chain[1::2]
            worlds=[w for w in itertools.product(range(5),repeat=5) if all(compare(w[i],ops[i],w[i+1]) for i in range(4))]
            conclusions=re.findall(r'I{1,2}\. ([A-Z]) ([<>≥≤]) ([A-Z])',s)
            truth=[[compare(w[letters.index(a)],op,w[letters.index(b)]) for a,op,b in conclusions] for w in worlds]
            one,two=all(v[0] for v in truth),all(v[1] for v in truth)
            idx=2 if one and two else 0 if one else 1 if two else 4 if all(any(v) for v in truth) else 3
            answer=options[idx]
        elif topic=='Syllogism':
            statements=s.split('Statements: ')[1].split('\nConclusions:')[0]
            relation=r'(Only a few|All|No|Some) (\w+) (?:are|is a) (not )?(\w+)'
            facts=re.findall(relation,statements)
            terms=sorted({word for _,a,_,b in facts for word in [a,b]})
            worlds=list(range(1<<len(terms)))
            has=lambda w,a:bool(w & (1<<terms.index(a)))
            allowed=[w for w in worlds if all(not(has(w,a) and (not has(w,b) if kind=='All' else has(w,b))) for kind,a,neg,b in facts if kind in ['All','No'])]
            required=[]
            for kind,a,neg,b in facts:
                if kind in ['Some','Only a few']: required.append([w for w in allowed if has(w,a) and has(w,b)])
                if kind=='Only a few': required.append([w for w in allowed if has(w,a) and not has(w,b)])
            assert all(required)
            truth=[]
            for kind,a,neg,b in re.findall(relation,s.split('\nConclusions:')[1]):
                region=[w for w in allowed if has(w,a) and (not has(w,b) if neg or kind=='All' else has(w,b))]
                if kind=='Some': follows=any(all(w in region for w in witness) for witness in required)
                else: follows=not region
                truth.append(follows)
            assert len(truth)==2,(q['id'],facts,truth)
            answer=options[2 if all(truth) else 0 if truth[0] else 1 if truth[1] else 3]
        elif topic=='Coding and decoding':
            lines=[line.split(' = ') for line in s.splitlines() if ' = ' in line]
            words=sorted({w for line,_ in lines for w in line.split()})
            codes=sorted({c for _,line in lines for c in line.split()})
            mappings=[]
            for perm in itertools.permutations(codes):
                mapping=dict(zip(words,perm))
                if all({mapping[w] for w in line.split()}==set(code.split()) for line,code in lines): mappings.append(mapping)
            assert len(mappings)==1,(q['id'],len(mappings))
            word=re.search(r'code for “(\w+)”',s)[1];answer=mappings[0][word]
        elif topic=='Direction sense':
            first,perpendicular,last=map(int,re.findall(r'(\d+) km',s))
            assert len(set(re.findall(r'turns (left|right)',s)))==1
            dist=math.isqrt((first-last)**2+perpendicular**2);assert dist*dist==(first-last)**2+perpendicular**2
            answer=str(dist)
        elif topic=='Ranking':
            total,front,move=map(int,re.findall(r'\d+',s));answer=str(total-front-move+1)
        elif topic=='Blood relations':
            if 'only daughter' in s: answer='Maternal grandfather'
            elif 'brother' in s: answer='Maternal uncle'
            else: answer='Granddaughter' if 'is the daughter' in s else 'Grandson'
        else: raise AssertionError(topic)
        actual=q['options'][q['answerIndex']]
        assert actual==answer,(q['id'],actual,answer)
        count+=1
assert count==400
audit=json.loads((Path(__file__).resolve().parents[1]/'data/solver_audit.json').read_text())
assert len(audit)==80 and all(x['solutions']==1 for x in audit)
print('PASS: 400 standalone reasoning keys recomputed; 80 arrangement sets have one enumerated solution each.')
