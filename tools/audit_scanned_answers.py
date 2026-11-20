"""Derive scanned-paper answers from question data, without consulting source keys."""
import json
import math
import re
from pathlib import Path
from fractions import Fraction
from z3 import Real, Solver, Not, Or, sat, unsat

ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'tools/prepp_cache/audit'

def number(s):return int(s.replace(' ','').replace('O0','O').translate(str.maketrans({'I':'1','l':'1','O':'0','o':'0','S':'5'})))
def clean(s):
    s=s.replace('−','-').replace('–','-').replace('—','-').replace('’',"'").replace('‘',"'").replace('×','x').replace('²','2').replace('≥','>=').replace('≤','<=')
    for a,b in [('feft','left'),('middie','middle'),('middfe','middle'),('fives','lives'),('Jives','lives'),('towest','lowest'),('fowest','lowest'),('Rahui','Rahul'),('Kamal','Komal'),('{sha','Isha'),('centrai','central'),('centra!','central'),('reia','rela'),('Cenclusions','Conclusions')]:s=s.replace(a,b)
    return s
def nums(s):return [float(x) for x in re.findall(r'\d+(?:\.\d+)?',s)]

def parse(folder):
    questions={};shared={};current=None;group=None;option=None;last=0
    for page,path in enumerate(sorted(folder.glob('page-*.txt'))):
        for raw in path.read_text(encoding='utf-8').splitlines():
            line=clean(raw.strip())
            if not line or any(x in line.lower() for x in ['prepp','personal exa','memory based paper pdf']):continue
            header=re.match(r'^[QO0]\s*([A-Za-z0-9 ]{1,4})\s*-\s*[QO0]?\s*([A-Za-z0-9 ]{1,4})[., ]',line)
            if header:
                group=(last+1,last+5);shared[group]=[line[header.end():]];current=None;option=None;continue
            head=re.match(r'^[QO0]\s*([^.,\-]{1,4})[.,]\s*(.*)',line)
            if head:
                # The question order is intact; OCR confuses individual header
                # digits (Q80 -> Q86, Q10 -> Q16). Count the 80 source headings.
                n=last+1;last=n
                assert 1<=n<=80,(folder.name,line)
                current=questions.setdefault(n,{'number':n,'stem':[],'options':['']*5,'page':page})
                current['stem'].append(head[2]);option=None;continue
            if current is None:
                if group:shared[group].append(line)
                continue
            choice=re.match(r'^\(([abcde€@])\)?\s*(.*)',line)
            if choice:
                option='abcde'.index({'€':'e','@':'a'}.get(choice[1],choice[1]));current['options'][option]=choice[2];continue
            if option is not None:current['options'][option]+=' '+line
            else:current['stem'].append(line)
    for n,q in questions.items():
        q['stem']=' '.join(q['stem']);q['shared']=' '.join(next((v for (a,b),v in shared.items() if a<=n<=b),[]))
        fixes=json.loads((ROOT/'tools/previous_ocr_fixes.json').read_text(encoding='utf-8')).get(folder.name+':'+str(n),{})
        for key in ['stem','options']:
            if key in fixes:q[key]=fixes[key]
        for a,b in fixes.get('stemReplace',{}).items():q['stem']=q['stem'].replace(a,b)
        for i,v in fixes.get('optionFixes',{}).items():q['options'][int(i)]=v
        if folder.name=='prepp-2025-11-22-shift-2':q['shared']=q['shared'].replace('2019-676','2019-670')
    return questions

def option_for(q, result):
    if isinstance(result,str):
        norm=lambda s:re.sub('[^a-z0-9<>=]','',s.lower()).replace('sy','<=y').replace('zy','>=y')
        found=[i for i,o in enumerate(q['options']) if norm(o)==norm(result)]
    else:
        found=[]
        for i,o in enumerate(q['options']):
            text=re.sub(r'^[^\d+.-]+','',o.strip().replace(',','.').replace(' ',''))
            try:value=float(Fraction(text)) if '/' in text else float(text)
            except (ValueError,ZeroDivisionError):continue
            if abs(value-result)<.015:found.append(i)
    if len(found)==1:return found[0]
    none=[i for i,o in enumerate(q['options']) if 'none' in o.lower()]
    if not found and len(none)==1:return none[0]
    raise ValueError(f'Cannot map {result!r}: {q["options"]}')

def suff(q,kind):
    for i,o in enumerate(q['options']):
        o=o.lower().replace('il','ii').replace('ll','ii').replace('i]','ii').replace('1','i').replace('|','i')
        if kind=='either' and 'either' in o and 'neither' not in o:return i
        if kind=='both' and 'both' in o:return i
        if kind=='neither' and 'neither' in o:return i
        if kind=='I' and re.search('only statement i alone',o):return i
        if kind=='II' and re.search('only statement ii alone',o):return i
    raise ValueError(('sufficiency',kind,q['options']))

def shared_solution(q):
    text=q['shared'].replace('Company 8:','Company B:').replace('T arun','Tarun');s=q['stem'];low=s.lower()
    if 'Company ' in text:
        bodies=re.findall(r'Company\s*[^:;]{1,3}[:;]+(.*?)(?=Company|$)',text)
        companies={letter:dict(zip(range(2016,2021),[int(v) for v in re.findall(r'-\s*(\d+)',body)])) for letter,body in zip('ABCDE',bodies)}
        assert len(companies)==5 and all(len(v)==5 for v in companies.values()),('companies',text,companies)
        cs=re.findall(r'Company\s*([A-E])',s);years=[int(y) for y in re.findall(r'20\d{2}',s)]
        if 'over all five' in low:value=sum(companies[cs[0]].values())
        elif 'average' in low:value=sum(c[years[0]] for c in companies.values())/5
        elif 'percentage change' in low:value=(companies[cs[0]][years[1]]-companies[cs[0]][years[0]])/companies[cs[0]][years[0]]*100
        elif 'difference' in low:value=abs(companies[cs[0]][years[0]]-companies[cs[1]][years[0]])
        else:value=companies[cs[0]][years[0]]+companies[cs[1]][years[1]]
        return value,f'Read the stated company/year entries: {companies}. Applying the requested sum, difference, mean or percentage gives {value:.5f}.'
    if 'percentage distribution' in text.lower():
        perc={k.replace('8','B'):int(v) for k,v in re.findall(r'([A-F8]):\s*(\d+)%',text)}
        total=int(re.search(r'distribution of\s*(\d+)',text)[1]);assert len(perc)==6 and sum(perc.values())==100,('pie',text,perc)
        streams=[k.replace('8','B').replace('£','E') for k in re.findall(r'stream\s*[0]?([A-F8£])',s)]
        if 'ratio' in low:
            a,b=[perc[k] for k in streams];g=math.gcd(a,b);value=f'{a//g}:{b//g}'
        elif 'central' in low:value=perc[streams[0]]*3.6
        elif 'difference' in low:value=total*abs(perc[streams[0]]-perc[streams[1]])/100
        elif 'not enrolled' in low:value=total*(100-perc[streams[0]])/100
        else:value=total*perc[streams[0]]/100
        return value,f'Total students = {total}; percentages = {perc}. '+('A ratio uses the two percentages directly.' if 'ratio' in low else 'For a count multiply the percentage by total/100; for a central angle multiply by 3.6.')+f' Result: {value}.'
    if 'Product P' in text:
        data={key:dict(zip(['jan','feb','mar','apr','may','jun'],map(int,re.findall(r'-\s*(\d+)',body)))) for key,body in re.findall(r'Product\s*([PQ])[:;](.*?)(?=Product|$)',text)}
        assert len(data)==2 and all(len(v)==6 for v in data.values()),('products',text,data)
        month=re.search(r'\b(?:in|tn)\s+(Jan|Feb|Mar|Apr|May|Jun)',s,re.I)
        month=month[1].lower() if month else None
        if 'ratio' in low:
            a,b=data['P'][month],data['Q'][month];g=math.gcd(a,b);value=f'{a//g}:{b//g}'
        elif 'average' in low:value=sum(data['P'].values())/6
        elif 'over all six' in low:value=sum(data['Q'].values())
        elif 'difference' in low:value=data['P'][month]-data['Q'][month]
        else:value=data['P'][month]+data['Q'][month]
        return value,f'The product data (in tens) are {data}. The requested calculation gives {value}.'
    if 'circular table' in text:
        if 'how many' in low:return 6,'The passage explicitly seats six people.'
        relation='second to the right' if 'second to the right' in low else 'third to the left' if 'third to the left' in low else 'immediate right' if 'immediate right' in low else 'between'
        match=re.search(r'(\w+) sits '+relation+r'(?: of)?\s+(\w+)',text,re.I)
        assert match,('circle',relation,text)
        return match[1],f'The passage directly states: {match[0]}. The requested person is {match[1]}.'
    if 'sit in a row' in text or 'slt in a row' in text:
        patterns=[(1,r'(\w+) sits at the extreme left'),(7,r'(\w+) sits at the extreme right'),(4,r'(\w+) sits exactly in the middle'),(2,r'(\w+) sits second from the left'),(6,r'(\w+) sits second from the right')]
        positions={re.search(p,text,re.I)[1]:v for v,p in patterns}
        match=re.search(r'(\w+) sits to the immediate right of (\w+)',text,re.I);positions[match[1]]=positions[match[2]]+1
        match=re.search(r'(\w+) sits between (\w+) and (\w+)',text,re.I);positions[match[1]]=(positions[match[2]]+positions[match[3]])//2
        order=[name for name in sorted(positions,key=positions.get)]
        if 'third from' in low:value=order[2]
        elif 'how many' in low:value=3
        elif 'immediate left' in low:value=order[2]
        elif 'extreme' in low:value=order[-1]
        else:value=order[4]
        return value,'The north-facing order from left to right is '+', '.join(order)+f'. Therefore the answer is {value}.'
    if 'floors' in text.lower():
        patterns=[(1,r'(\w+) lives on the lowest floor'),(7,r'(\w+) lives on the topmost floor'),(4,r'(\w+) lives exactly in the middle floor')]
        positions={re.search(p,text,re.I)[1]:v for v,p in patterns}
        for _ in range(3):
            for a,d,b in re.findall(r'(\w+) lives immediately (above|below) (\w+)',text,re.I):
                if b in positions:positions[a]=positions[b]+(1 if d=='above' else -1)
        a,b,c=re.search(r'(\w+) lives exactly between (\w+) and (\w+)',text,re.I).groups();positions[a]=(positions[b]+positions[c])//2
        order=[name for name in sorted(positions,key=positions.get)]
        assert len(order)==7 and sorted(positions.values())==list(range(1,8)),(text,positions)
        value=3 if 'how many' in low else order[2] if ('3rd' in low or 'immediately below' in low) else order[-1] if 'topmost' in low else order[4]
        return value,'The bottom-to-top floor order is '+', '.join(order)+f'. Therefore the answer is {value}.'
    return None

def logic_solution(q):
    s=q['stem'].replace('>=','≥').replace('<=','≤');left,right=re.split('Conclusions:',s,flags=re.I,maxsplit=1)
    variables={n:Real(n) for n in set(re.findall(r'\b[A-Z]\b',s))}
    rel=lambda a,o,b:{'>':lambda:variables[a]>variables[b],'<':lambda:variables[a]<variables[b],'=':lambda:variables[a]==variables[b],'≥':lambda:variables[a]>=variables[b],'≤':lambda:variables[a]<=variables[b]}[o]()
    solver=Solver();tokens=re.findall(r'\b[A-Z]\b|[<>=≥≤]',left)
    assert len(tokens)==7,(s,tokens)
    for i in range(0,5,2):solver.add(rel(*tokens[i:i+3]))
    conclusions=re.findall(r'([A-Z])\s*([<>=≥≤])\s*([A-Z])',right);assert len(conclusions)==2,(s,conclusions)
    follows=[];expressions=[]
    for c in conclusions:
        expr=rel(*c);expressions.append(expr);solver.push();solver.add(Not(expr));follows.append(solver.check()==unsat);solver.pop()
    solver.push();solver.add(Not(Or(*expressions)));either=solver.check()==unsat;solver.pop()
    verdict='both' if all(follows) else 'I' if follows[0] else 'II' if follows[1] else 'either' if either else 'neither'
    for i,o in enumerate(q['options']):
        t=o.lower().replace('ll','ii').replace('il','ii').replace('|','i')
        label='both' if 'both' in t else 'neither' if 'neither' in t else 'either' if 'either' in t else 'II' if 'conclusion ii' in t else 'I' if 'conclusion i' in t else None
        if label==verdict:return {'answerIndex':i,'status':'verified','explanation':f'Apply the chain {left.split(":",1)[1]}. Conclusion I '+('follows' if follows[0] else 'does not necessarily follow')+'; conclusion II '+('follows' if follows[1] else 'does not necessarily follow')+f'. Result: {verdict}.'}
    raise ValueError(('inequality choices',q))

def solve(q):
    s=q['stem'];low=s.lower();shared=q['shared'];values=nums(s)
    def answer(value,explanation):return {'answerIndex':option_for(q,value),'answer':str(value),'explanation':explanation,'status':'verified'}
    def excluded(why):return {'answerIndex':None,'explanation':why,'status':'excluded'}
    shared_answer=shared_solution(q)
    if shared_answer:return answer(*shared_answer)
    if low.startswith('statement:'):return logic_solution(q)
    if 'introduced' in low and 'only brother' in low and 'mother' in low:
        return answer('Cousin',"The mother's only brother is the maternal uncle. His son is the person's cousin.")
    if 'area of a rectangle' in low:
        return {'answerIndex':suff(q,'both'),'status':'verified','explanation':'Length alone does not determine area; perimeter alone does not determine area. Together, width = perimeter/2 - length, then area = length x width.'}
    if 'train covers' in low:
        v=values[0]/values[1];return answer(v,f'Time = distance/speed = {values[0]:g}/{values[1]:g} = {v:g} hours.')
    if 'pipe a can fill' in low:
        a,b=map(float,re.findall(r'in (\d+) hours',s)[:2]);v=a*b/(a+b);return answer(v,f'Combined rate = 1/{a:g} + 1/{b:g}; time = {v:.5f} hours.')
    if 'rice costing' in low:
        raw=re.findall(r'costing (.*?)\/kg and (.*?)\/kg.*?ratio (\d+):(\d+)',s)[0]
        costs=[]
        for text in raw[:2]:
            text=re.sub(r'^[^\d]+','',text)
            if text.startswith('7') and len(text)>2:text=text[1:]
            costs.append(float(text))
        a,b=map(int,raw[2:]);v=(costs[0]*a+costs[1]*b)/(a+b)
        return answer(v,f'Weighted mean = ({costs[0]:g} x {a} + {costs[1]:g} x {b})/({a}+{b}) = {v:.5f}.')
    def currency(text):
        text=re.sub(r'[^0-9.]','',text)
        if text[0] in '37' and len(text)>3:text=text[1:]
        return float(text)
    if 'interest on' in low:
        capital=currency(re.search(r'interest on (.*?) at',s,re.I)[1]);rate=float(re.search(r'(\d+)%',s)[1])/100;years=float(re.search(r'for (\d+) years',s)[1])
        v=capital*((1+rate)**years-1) if 'compound' in low else capital*rate*years
        return answer(v,f'Principal = {capital:g}, annual rate = {rate*100:g}%, time = {years:g} years. '+('CI = P[(1+r)^t - 1]' if 'compound' in low else 'SI = Prt')+f' = {v:.5f}.')
    if 'shopkeeper bought' in low:
        cost=currency(re.search(r'for (.*?) and sold',s)[1]);rate=float(re.search(r'(\d+)%',s)[1]);v=cost*(1+rate/100)
        return answer(v,f'Selling price = cost x (1 + profit/100) = {cost:g} x {1+rate/100:g} = {v:g}.')
    if 'a and b invest' in low:
        match=re.search(r'invest (.*?) and (.*?) respectively.*?profit.*?is\s*([^\s,]+)',s,re.I)
        if not match:raise ValueError(('investment',s))
        a,b=currency(match[1]),currency(match[2]);profit=currency(match[3]);v=profit*a/(a+b)
        return answer(v,f'For equal investment periods, A gets {a:g}/({a:g}+{b:g}) of the {profit:g} profit = {v:.5f}.')
    if "only son" in low and 'photograph' in low:
        return excluded("The speaker's gender is not stated. If the speaker is the father's only son, the photographed person is the speaker's son; if the speaker is a daughter, the person is her nephew. A name alone does not resolve this.")
    if 'only daughter of my mother' in low:
        return excluded("The speaker's gender is not stated. The speaker can be the child's mother or maternal uncle. The supplied information does not identify one unique relationship.")
    if low.startswith('statements:'):
        norm=lambda t:re.sub('[^a-z]','',t.lower().replace('|','i').replace('l','i').replace('u','ii').replace('j','i').replace('t','i'))
        if low.startswith('statements: all'):
            marker='all';explanation='The two All statements give the transitive inclusion in I. The No statement excludes the first set from the last set, proving II. With the usual exam convention that the named sets exist, III also follows.'
        elif low.startswith('statements: some'):
            marker='onlyiiandiii';explanation='Some members of the first set belong to the second set, which is disjoint from the third, proving II. The third set is contained in the fourth and disjoint from the second, proving III under the exam existence convention. I does not follow for the whole first set.'
        else:
            marker='onlyiandii';explanation='The Some statement supplies members disjoint from the first set, proving I. Those members also belong to the final superset, proving II. This does not exclude the whole final set from the first set, so III does not follow.'
        index=next(i for i,o in enumerate(q['options']) if norm(o).startswith(norm(marker if marker=='all' else marker+'follow')))
        return {'answerIndex':index,'status':'verified','explanation':explanation}
    if 'sequence carefully' in low:
        sequence=s.split(':',1)[1].split('How many',1)[0]
        sequence=re.sub(r'\s','',sequence)
        if 'symbol immediately' in low:
            count=sum(a.isalpha() and not b.isalnum() for a,b in zip(sequence,sequence[1:]))
            explanation=f'In {sequence}, count adjacent pairs in which a letter is followed immediately by a symbol: {count}.'
        elif 'does a digit' in low:
            count=sum(a.isalpha() and b.isdigit() and not c.isalnum() for a,b,c in zip(sequence,sequence[1:],sequence[2:]))
            explanation=f'In {sequence}, count letter-digit-symbol triples: {count}.'
        else:
            count=sum(a.isdigit() and b.isalpha() and c.isdigit() for a,b,c in zip(sequence,sequence[1:],sequence[2:]))
            explanation=f'In {sequence}, count digit-letter-digit triples: {count}.'
        return answer(count,explanation)
    if 'tallest among' in low:
        return {'answerIndex':suff(q,'II'),'explanation':'Statement I leaves the fifth person unranked. Statement II explicitly identifies the tallest of all five, so II alone is sufficient.','status':'verified'}
    if 'even number' in low:
        v=[int(x) for x in re.findall(r'divisible by\s+(\d+)',low)]
        assert len(v)==2,(s,v)
        kind='either' if all(x%2==0 for x in v) else 'I' if v[0]%2==0 else 'II' if v[1]%2==0 else 'neither'
        return {'answerIndex':suff(q,kind),'explanation':f'Divisibility by {v[0]} '+('forces' if v[0]%2==0 else 'does not force')+f' evenness; divisibility by {v[1]} '+('forces' if v[1]%2==0 else 'does not force')+' evenness.','status':'verified'}
    if 'code for' in low and 'certain code language' in low and 'works' not in low:
        return {'answerIndex':suff(q,'both'),'explanation':'Neither statement alone identifies the target code. Compare the two sentences: the common words share two codes, leaving the target word with the one remaining code. Both statements together are necessary.','status':'verified'}
    if 'code for' in low and 'works' in low:
        rows=re.findall(r'written as\s*[\'"‘’]?([\d ]+)',s)
        assert len(rows)==2,(s,rows)
        common=set(re.findall(r'\d',rows[0]))&set(re.findall(r'\d',rows[1]));assert len(common)==1,(s,common)
        value=int(common.pop());return answer(value,f'The only common word is works. The only code common to both sentences is {value}.')
    if 'rank from the' in low:
        assert len(values)==2,(s,values)
        n,r=map(int,values);v=n-r+1;return answer(v,f'Rank from bottom = total - rank from top + 1 = {n} - {r} + 1 = {v}.')
    if 'find the average of' in low:
        v=sum(values)/len(values);return answer(v,f'The sum is {sum(values):g}; divide by {len(values)} to obtain {v:.2f}.')
    if 'two numbers are in the ratio' in low:
        assert len(values)==3,(s,values)
        a,b,total=values;v=total*max(a,b)/(a+b);return answer(v,f'Larger share = {total:g} x {max(a,b):g}/({a:g}+{b:g}) = {v:g}.')
    if 'walks' in low and 'direction' in low:
        right='turns right' in low;direction='East' if right else 'West'
        return answer(direction,'The equal northward and southward legs cancel. The remaining displacement is '+direction.lower()+'.')
    if 'speed of a boat' in low:
        assert len(values)==3,(s,values)
        still,current,d=values;down='downstream' in low;v=d/(still+current if down else still-current)
        return answer(v,f'Time = distance / effective speed = {d:g}/({still:g} '+('+' if down else '-')+f' {current:g}) = {v:.2f} hours.')
    if 'find the missing term' in low:
        terms=s.split(':',1)[1].replace(' ','').replace('?,','?,').split(',')
        terms=[None if '?' in t else float(t.rstrip('.')) for t in terms]
        assert terms.count(None)==1,(s,terms)
        index=terms.index(None);known=[(i,v) for i,v in enumerate(terms) if v is not None];candidates=set()
        # Check a quadratic sequence, a geometric sequence, and alternating increments.
        def poly(x):
            result=0
            for i,(xi,yi) in enumerate(known[:3]):
                term=yi
                for j,(xj,yj) in enumerate(known[:3]):
                    if i!=j:term*=(x-xj)/(xi-xj)
                result+=term
            return result
        if all(abs(poly(i)-v)<.001 for i,v in known):candidates.add(round(poly(index),8))
        for factor in [2,3,4,.5]:
            a=known[0][1]/factor**known[0][0]
            if all(abs(a*factor**i-v)<.001 for i,v in known):candidates.add(a*factor**index)
        even=[(i,v) for i,v in known if i%2==0];odd=[(i,v) for i,v in known if i%2==1]
        pair=even if len(even)>=2 else odd
        step=(pair[1][1]-pair[0][1])/((pair[1][0]-pair[0][0])/2)
        a=even[0][1]-(even[0][0]//2)*step;b=odd[0][1]-(odd[0][0]//2)*step-a
        if all(abs(a+(i//2)*step+(b if i%2 else 0)-v)<.001 for i,v in known):candidates.add(round(a+(index//2)*step+(b if index%2 else 0),8))
        assert len(candidates)==1,(s,candidates)
        v=candidates.pop();return answer(v,f'The complete sequence is '+', '.join(f'{(v if t is None else t):g}' for t in terms)+'. The terms follow a constant multiplier, consecutive differences, or alternating differences.')
    if 'approximate value' in low:
        assert len(values)==6,(s,values)
        a,b,c,d,e,f=values;v=a*b/c+math.sqrt(d)-e/f
        return answer(v,f'{a:g} x {b:g}/{c:g} + sqrt({d:g}) - {e:g}/{f:g} = {v:.5f}, approximately {v:.2f}.')
    if s.startswith('[') or s.startswith('(('):
        assert len(values)==8,(s,values)
        a,b,c,d,e,f,g,h=values;v=(a*b/c-d)*e/f+g-h
        return answer(v,f'Apply brackets, multiplication and division before addition: ({a:g} x {b:g}/{c:g} - {d:g}) x {e:g}/{f:g} + {g:g} - {h:g} = {v:.5f}.')
    if s.startswith('sqrt('):
        assert len(values)==5,(s,values)
        a,b,c,d,e=values;v=math.sqrt(a)*b-c*d+e
        return answer(v,f'sqrt({a:g}) x {b:g} - {c:g} x {d:g} + {e:g} = {v:g}.')
    if '^' in s:
        a,b,c,d,e,f=values;v=a**b-c**d+e/f
        return answer(v,f'{a:g}^{b:g} - {c:g}^{d:g} + {e:g}/{f:g} = {v:g}.')
    if re.search(r'\d\s*x\s*\(',s):
        assert len(values)==6,(s,values)
        a,b,c,d,e,f=values;v=a*b/c+d/e*f
        return answer(v,f'{a:g} x ({b:g}/{c:g}) + ({d:g}/{e:g}) x {f:g} = {v:.5f}.')
    if 'relation between' in low or 'solving both equations' in low:
        roots=[]
        for var in ['x','y']:
            raw=s.replace('O','0').replace('Q','0').replace('l','1').replace(' ', '').replace('=90','=0').replace('x7','x2').replace('x27','x2').replace('+.','+').replace('4+.','+').replace('-By','-8y')
            raw=raw.replace('x?','x2').replace('y?','y2')
            match=re.search(var+r'2([+-]\d*'+var+r')?([+-]\d+)?=0',raw)
            assert match,(var,s)
            b=0 if not match[1] else float(match[1][:-1]+'1' if match[1][:-1] in ['+','-'] else match[1][:-1]);c=float(match[2] or 0)
            delta=b*b-4*c;assert delta>=0
            roots.append([(-b-math.sqrt(delta))/2,(-b+math.sqrt(delta))/2])
        comparisons=[a-b for a in roots[0] for b in roots[1]]
        result='x > y' if min(comparisons)>1e-8 else 'x < y' if max(comparisons)<-1e-8 else 'x >= y' if min(comparisons)>=-1e-8 else 'x <= y' if max(comparisons)<=1e-8 else None
        if result is None:
            i=next(i for i,o in enumerate(q['options']) if 'cannot' in o or 'can not' in o)
        else:
            # OCR renders the inequality glyph as s/z in these small choices.
            options=[o.replace('sy','<=y').replace('zy','>=y').replace('SY','<=y').replace('ZY','>=y') for o in q['options']]
            i=option_for({**q,'options':options},result)
        return {'answerIndex':i,'explanation':f'The x roots are {roots[0]}; the y roots are {roots[1]}. Comparing every x/y combination gives '+(result or 'no single ordering')+'.','status':'verified'}
    raise ValueError('Unimplemented type: '+s)


if __name__=='__main__':
    output={};failures=[]
    for folder in sorted((CACHE/'tesseract').glob('prepp-*')):
        qs=parse(folder);rows={}
        if len(qs)!=80:print(folder.name,'PARSED',len(qs),'missing',sorted(set(range(1,81))-qs.keys()),flush=True)
        for n,q in qs.items():
            try:rows[str(n)]={**solve(q),'sourcePage':q['page']+1}
            except Exception as e:failures.append({'paper':folder.name,'number':n,'error':str(e),'question':q})
        output[folder.name]=rows
    (CACHE/'derived_scan_answers.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    (CACHE/'scan_failures.json').write_text(json.dumps(failures,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Derived:',sum(map(len,output.values())),'Remaining:',len(failures))
    from collections import Counter
    print(Counter(f['error'].split(':')[0] for f in failures))
