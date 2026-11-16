"""Derive English explanations from the displayed clues, rather than templates."""
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def inequality(q):
    from z3 import Real, Solver, Not, Or, sat, unsat
    stem=q['stem']
    if not stem.startswith('Statements:') or 'Conclusions:' not in stem:
        return None
    left,right=stem.split('Conclusions:',1)
    if not re.search(r'[A-Z]\s*[<>=≥≤]',left):return None
    names={c:Real(c) for c in set(re.findall(r'\b[A-Z]\b',stem))}
    def relation(a,op,b):
        a,b=names[a],names[b]
        return {'<':lambda:a<b,'>':lambda:a>b,'≤':lambda:a<=b,'≥':lambda:a>=b,'=':lambda:a==b}[op]()
    solver=Solver()
    edges=[]
    for chain in re.split('[;,]',left.removeprefix('Statements:')):
        tokens=re.findall(r'\b[A-Z]\b|[<>=≥≤]',chain)
        for i in range(0,len(tokens)-2,2):
            a,op,b=tokens[i:i+3]
            solver.add(relation(a,op,b));edges.append(f'{a} {op} {b}')
    assert solver.check()==sat,q['id']
    conclusions=re.findall(r'\b(II|I)\.\s*([A-Z])\s*([<>=≥≤])\s*([A-Z])',right)
    assert len(conclusions)==2,q['id']
    follows=[];expressions=[];proof=[]
    for label,a,op,b in conclusions:
        expr=relation(a,op,b);expressions.append(expr)
        solver.push();solver.add(Not(expr));status=solver.check()
        follows.append(status==unsat)
        if status==unsat:
            proof.append(f'Conclusion {label} ({a} {op} {b}) follows: its opposite contradicts the stated relationships.')
        else:
            model=solver.model()
            assignments=', '.join(f'{name} = {model.eval(value,model_completion=True)}' for name,value in sorted(names.items()))
            proof.append(f'Conclusion {label} ({a} {op} {b}) does not necessarily follow. '
                         f'For example, {assignments} satisfies all the statements but makes this conclusion false.')
        solver.pop()
    solver.push();solver.add(Not(Or(*expressions)));either=solver.check()==unsat;solver.pop()
    verdict='both' if all(follows) else 'only I' if follows[0] else 'only II' if follows[1] else 'either' if either else 'neither'
    def classify(option):
        option=option.lower()
        if 'both' in option:return 'both'
        if 'neither' in option:return 'neither'
        if 'either' in option:return 'either'
        if re.search(r'only\s+(?:conclusion\s+)?ii\b',option):return 'only II'
        if re.search(r'only\s+(?:conclusion\s+)?i\b',option):return 'only I'
    index=next(i for i,o in enumerate(q['options']) if classify(o)==verdict)
    if index!=q['answerIndex']:
        return {'text':'\n\n'.join(proof)+f'\n\nLogical result: {q["options"][index]}. '
                'This differs from the publisher answer key; the source key is retained pending review.',
                'status':'source-key-discrepancy','derivedAnswerIndex':index}
    return {'text':'\n\n'.join(proof)+f'\n\nTherefore: {q["options"][index]}.',
            'status':'independently-verified','derivedAnswerIndex':index}


def coding(q):
    text=q['stem'].replace('“','"').replace('”','"').replace('‘','"').replace('’','"')
    pairs=re.findall(r'"([^"\n]+)"\s+is\s+(?:coded|written)\s+as\s*(?:-\s*)?"([^"\n]+)"',text,re.I)
    if len(pairs)<3:return None
    wordrows=[set(re.findall(r'[a-z]+',words.lower())) for words,_ in pairs]
    coderows=[set(re.findall(r'[a-z]+',codes.lower())) for _,codes in pairs]
    if any(len(a)!=len(b) for a,b in zip(wordrows,coderows)):return None
    words=set.union(*wordrows);codes=set.union(*coderows)
    candidates={word:sorted(code for code in codes if
        all((word in wr)==(code in cr) for wr,cr in zip(wordrows,coderows))) for word in words}
    if any(not values for values in candidates.values()):return None
    mappings='\n'.join(f'{word} → '+(' or '.join(values)) for word,values in sorted(candidates.items()))
    return {'text':'Compare the repeated words across the given sentences. A word and its code occur '
        'in the same sentences. This gives:\n\n'+mappings+'\n\n'
        'Where two words share the same possible codes, their individual codes cannot be distinguished '
        'without an additional clue. Apply any extra code given in this question before selecting the answer.',
        'status':'derived-code-mapping'}


def pair_count(q):
    s=q['stem']
    if not re.search(r'pairs? of (?:the )?(?:letters|digits)',s,re.I) or not re.search('same number|as many',s,re.I):return None
    candidates=re.findall(r'[“‘’"\']\s*([A-Z]{4,}|\d{5,})\s*[”’"\']',s)
    if not candidates:return None
    seq=candidates[0];values=[int(x) if seq.isdigit() else ord(x)-64 for x in seq]
    matches=[(i+1,j+1,seq[i],seq[j]) for i in range(len(seq)) for j in range(i+1,len(seq)) if abs(values[i]-values[j])==j-i]
    details='\n'.join(f'Positions {i} and {j}: {a}–{b}; position gap = {j-i}, value gap = {j-i}.' for i,j,a,b in matches)
    return {'text':f'For {seq}, compare each pair\'s position gap with the absolute difference '
        f'between its alphabet positions or digit values. They must be equal.\n\n'
        +(details or 'No pair satisfies this condition.')+f'\n\nTotal qualifying pairs: {len(matches)}.',
        'status':'independently-verified','derivedPairCount':len(matches)}


def add_explanations(tests, curated=None):
    curated=curated or {}
    stats={}
    for test in tests:
        for q in test['questions'][:40]:
            item=curated.get(q['id']) or inequality(q) or coding(q) or pair_count(q)
            answer=f'Source answer: ({chr(97+q["answerIndex"])}) {q["options"][q["answerIndex"]]}'
            if item:
                if 'topic' in item:q['topic']=item['topic']
                if item['status']=='derived-code-mapping':q['topic']='Coding-Decoding'
                if 'derivedAnswerIndex' in item:q['topic']='Inequalities'
                if 'derivedPairCount' in item:q['topic']='Alphanumeric & Word Formation'
                if q['stem'].startswith('Statements:') and not re.search(r'\b[A-Z]\s*[<>=≥≤]',q['stem']):q['topic']='Syllogism'
                if item['status']=='worked-deduction':
                    if 'family' in q['stem'].lower():q['topic']='Blood Relations'
                    elif 'direction' in q['stem'].lower() or 'point ' in q['stem'].lower():q['topic']='Direction Sense'
                    elif not q['stem'].startswith('Statements:'):q['topic']='Alphanumeric & Word Formation'
                q['explanation']=answer+'\n\n'+item['text']
                q['explanationStatus']=item['status']
                if 'derivedAnswerIndex' in item:q['derivedAnswerIndex']=item['derivedAnswerIndex']
            else:
                q['explanation']=(answer+'\n\nThe linked publisher PDF supplies this question and answer key, '
                    'but does not include a worked explanation. Use the question\'s source-page link '
                    'to review its complete clues and choices.')
                q['explanationStatus']='source-key-only'
            stats[q['explanationStatus']]=stats.get(q['explanationStatus'],0)+1
    return stats


if __name__=='__main__':
    from repair_adda_quant import publish_copies
    from reasoning_puzzles import solve_all
    from reasoning_notes import notes
    tests=json.loads((ROOT/'data/adda_tests.json').read_text(encoding='utf-8'))['tests']
    curated=solve_all()
    curated.update(notes())
    print(add_explanations(tests,curated))
    publish_copies(tests)
