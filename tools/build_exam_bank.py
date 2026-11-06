"""Original RRB Scale I practice. Exact arithmetic and exhaustively solved arrangements.
Run this generator, then validate_questions.py. No third-party questions are copied.
"""
import json, random, itertools, math
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
R = random.Random(706112026)
PERMS = list(itertools.permutations(range(8)))
AUDIT = []

def fmt(v):
    if isinstance(v, F):
        return str(v.numerator) if v.denominator == 1 else f'{float(v):.2f}'.rstrip('0').rstrip('.')
    return str(v)

def question(topic, stem, answer, explanation, pool=None, stimulus=None):
    if isinstance(answer,F) and answer.denominator != 1 and 'decimal' not in stem.lower():
        stem += ' (Round to two decimal places if needed.)'
    answer = fmt(answer)
    opts = [answer]
    if pool:
        for x in pool:
            if fmt(x) not in opts: opts.append(fmt(x))
            if len(opts) == 5: break
    if len(opts) < 5:
        value = float(F(answer))
        step = max(1, round(abs(value) / 12))
        for k in [1, -1, 2, -2, 3, -3, 4, 5]:
            x = fmt(F(str(value + k * step)))
            if x not in opts: opts.append(x)
            if len(opts) == 5: break
    assert len(opts) == len(set(opts)) == 5
    R.shuffle(opts)
    q = dict(topic=topic, stem=stem, options=opts, answerIndex=opts.index(answer), explanation=explanation)
    if stimulus: q['stimulusId'] = stimulus
    return q

def arrangement(t, kind):
    names = R.sample(['Aditi','Bina','Charu','Deepa','Esha','Farah','Gita','Hema','Isha','Jaya','Kiran','Lata','Meera','Nisha','Ovi','Pia','Riya','Sana','Tara','Uma'],8)
    target = R.choice(PERMS)
    sid = f'T{t:02d}-{kind}'
    if kind == 'linear':
        labels = [f'position {i+1} from the left' for i in range(8)]
        title = f"{', '.join(names)} sit in a row, all facing north. Positions are counted from left to right."
        topic = 'Linear seating'
    elif kind == 'box':
        labels = [f'position {i+1} from the bottom' for i in range(8)]
        title = f"Eight boxes labelled {', '.join(names)} are stacked one above another. Position 1 is at the bottom and position 8 at the top."
        topic = 'Box puzzle'
    elif kind == 'schedule':
        labels = [f'{m} {d}' for m in ['March','April','May','June'] for d in [7,21]]
        title = f"{', '.join(names)} attend interviews, one per slot, on 7 and 21 March, April, May and June. Slots run in chronological order."
        topic = 'Month and date puzzle'
    elif kind == 'circular':
        labels = [f'seat {i+1}' for i in range(8)]
        title = f"{', '.join(names)} sit around a circular table, all facing the centre. For reference only, seats 1–8 run clockwise. For a centre-facing person, left is clockwise and right is anticlockwise."
        topic = 'Circular seating'
    elif kind == 'parallel':
        labels = [f'Row {i//4+1}, position {i%4+1} from the left of the diagram' for i in range(8)]
        title = f"{', '.join(names)} sit in two rows of four. Row 1 faces south, Row 2 faces north. The first four people listed sit in Row 1 and the remaining four in Row 2. Positions 1–4 in each row run from left to right of the diagram. People at the same position in different rows face each other."
        target = tuple(R.sample(range(4),4)+R.sample(range(4,8),4))
        topic = 'Parallel rows'
    else:
        labels = [f'floor {i//2+1}, flat {"A" if i%2==0 else "B"}' for i in range(8)]
        title = f"{', '.join(names)} occupy eight flats on floors 1 (bottom) to 4 (top). Each floor has Flat A to the west of Flat B. Each flat has one resident. For ordering only, count Floor 1 A, Floor 1 B, Floor 2 A, Floor 2 B, and so on."
        topic = 'Floor and flat puzzle'
    # Each predicate has exactly the semantics stated by its clue.
    candidates=[]
    for a,b in itertools.combinations(range(8),2):
        d=target[b]-target[a]
        gap=abs(d)-1
        candidates.append((lambda p,a=a,b=b,gap=gap: abs(p[a]-p[b])==gap+1,
            f'Exactly {gap} occupied positions separate {names[a]} and {names[b]} in the stated order.'))
        if abs(d)>1:
            candidates.append((lambda p,a=a,b=b,d=d: (p[b]>p[a])==(d>0),
                f'{names[a]} comes {"before" if d>0 else "after"} {names[b]} in the stated order.'))
    for a in range(8):
        candidates.append((lambda p,a=a,v=target[a]%2: p[a]%2==v,
            f'{names[a]} occupies an {"odd" if target[a]%2==0 else "even"}-numbered position in the stated order.'))
    if kind == 'circular':
        candidates=[]
        for a,b in itertools.combinations(range(8),2):
            d=(target[b]-target[a])%8
            candidates.append((lambda p,a=a,b=b,d=d:(p[b]-p[a])%8==d,
                f'{names[b]} sits {d} place(s) to the left of {names[a]}.'))
    if kind == 'parallel':
        candidates=[]
        for a,b in itertools.combinations(range(8),2):
            if a//4==b//4:
                delta=target[b]%4-target[a]%4
                direction='left' if (delta>0)==(a<4) else 'right'
                candidates.append((lambda p,a=a,b=b,delta=delta:p[b]%4-p[a]%4==delta,
                    f'{names[b]} sits {abs(delta)} place(s) to the {direction} of {names[a]}.'))
            elif target[a]%4==target[b]%4:
                candidates.append((lambda p,a=a,b=b:p[a]%4==p[b]%4,
                    f'{names[a]} faces {names[b]}.'))
            else:
                candidates.append((lambda p,a=a,b=b:p[a]%4!=p[b]%4,
                    f'{names[a]} does not face {names[b]}.'))
    if kind == 'floor':
        candidates=[]
        for a,b in itertools.combinations(range(8),2):
            fa,fb=target[a]//2,target[b]//2
            sameflat=target[a]%2==target[b]%2
            if fa!=fb:
                candidates.append((lambda p,a=a,b=b,g=abs(fa-fb): abs(p[a]//2-p[b]//2)==g,
                    f'The floor numbers of {names[a]} and {names[b]} differ by {abs(fa-fb)}.'))
                candidates.append((lambda p,a=a,b=b,d=fa>fb: (p[a]//2>p[b]//2)==d and p[a]//2!=p[b]//2,
                    f'{names[a]} lives {"above" if fa>fb else "below"} {names[b]}.'))
            else:
                candidates.append((lambda p,a=a,b=b: p[a]//2==p[b]//2,
                    f'{names[a]} and {names[b]} live on the same floor.'))
            candidates.append((lambda p,a=a,b=b,v=sameflat: (p[a]%2==p[b]%2)==v,
                f'{names[a]} and {names[b]} live in {"the same" if sameflat else "different"} flat letters.'))
        for a in range(8):
            candidates.append((lambda p,a=a,v=target[a]%2:p[a]%2==v,
                f'{names[a]} lives in Flat {"A" if target[a]%2==0 else "B"}.'))
    if kind == 'schedule':
        for a in range(8):
            candidates.append((lambda p,a=a,m=target[a]//2:p[a]//2==m,
                f'{names[a]} attends in {["March","April","May","June"][target[a]//2]}.'))
    R.shuffle(candidates)
    anchor=R.randrange(8)
    clues=[f'{names[anchor]} occupies {labels[target[anchor]]}.']
    valid=[p for p in PERMS if p[anchor]==target[anchor] and (kind!='parallel' or all((p[a]<4)==(a<4) for a in range(8)))]
    base=valid[:];selected=[]
    for pred, text in candidates:
        smaller=[p for p in valid if pred(p)]
        if len(smaller)<len(valid): valid=smaller;selected.append((pred,text))
        if len(valid)==1: break
    assert valid == [target]
    # Remove redundant clues; retain the anchor as the reference convention.
    for item in selected[:]:
        trial=[x for x in selected if x is not item]
        survivors=[]
        for p in base:
            if all(fn(p) for fn,_ in trial): survivors.append(p)
            if len(survivors)>1: break
        if survivors==[target]: selected=trial
    clues.extend(text for _,text in selected)
    AUDIT.append(dict(mock=t, stimulus=sid, solutions=len(valid)))
    solution='; '.join(f'{labels[i]}: {names[target.index(i)]}' for i in range(8))
    st=dict(id=sid,type='logic_puzzle',variant=kind,title=title,body='Use all the following clues:\n'+'\n'.join('• '+c for c in clues),solution=solution)
    qs=[]
    for i in R.sample([x for x in range(8) if x!=target[anchor]],3):
        qs.append(question(topic,f'Who occupies {labels[i]}?',names[target.index(i)],f'The unique arrangement is: {solution}. Therefore {names[target.index(i)]} occupies {labels[i]}.',names, sid))
    a,b=R.sample(range(8),2)
    if kind == 'circular':
        count=min(abs(target[a]-target[b]),8-abs(target[a]-target[b]))-1
        qs.append(question(topic,f'How many people sit between {names[a]} and {names[b]} along the shorter arc?',count,f'Use the shorter circular distance, then subtract 1. Arrangement: {solution}.',range(7),sid))
    elif kind == 'parallel':
        who=target.index((target[a]+4)%8)
        qs.append(question(topic,f'Who faces {names[a]}?',names[who],f'The person at the same diagram position in the opposite row is {names[who]}. Arrangement: {solution}.',names,sid))
    else:
        qs.append(question(topic,f'How many occupied positions lie between {names[a]} and {names[b]} in the stated order?',abs(target[a]-target[b])-1,f'Positions are {target[a]+1} and {target[b]+1}; the count between them is |{target[a]+1} − {target[b]+1}| − 1. Arrangement: {solution}.',range(7),sid))
    a=R.choice([x for x in range(8) if x!=anchor])
    qs.append(question(topic,f'Which position is occupied by {names[a]}?',labels[target[a]],f'The unique arrangement is: {solution}.',R.sample(labels,8),sid))
    return st,qs

def miscellaneous(t):
    qs=[]
    syllopts=['Only I follows','Only II follows','Both I and II follow','Neither I nor II follows','Either I or II follows']
    words=R.sample(['loans','cards','accounts','deposits','tokens','files','bonds','cheques','notes','coins','branches','lockers'],4)
    a,b,c,d=words
    patterns=[
      (f'Only a few {a} are {b}. All {b} are {c}. No {c} is a {d}.',f'I. Some {a} are not {b}.\nII. No {b} is a {d}.',2,'Only a few means some are and some are not. All B are C and no C is D excludes every B from D.'),
      (f'Some {a} are {b}. All {b} are {c}. No {c} is a {d}.',f'I. Some {a} are {c}.\nII. Some {b} are {d}.',0,'The stated A–B overlap lies in C. Since B is contained in C, no B can be D.'),
      (f'No {a} is a {b}. Some {b} are {c}. All {c} are {d}.',f'I. All {a} are {d}.\nII. Some {d} are {b}.',1,'The B–C overlap is inside D, proving II. No universal A–D relation is given.'),
      (f'Only a few {a} are {b}. Some {b} are {c}. All {c} are {d}.',f'I. All {a} are {d}.\nII. No {b} is a {d}.',3,'A need not be contained in D. Some B are C and therefore D, contradicting II.')]
    R.shuffle(patterns)
    for st,con,ans,why in patterns:
        qs.append(question('Syllogism',f'Statements: {st}\nConclusions:\n{con}',syllopts[ans],why,syllopts))
    # Enumerate all weak orderings of five variables to verify conclusions.
    for k in range(4):
        symbols=R.sample(list('PQRSTUVWX'),5)
        vals=[R.randrange(4) for _ in symbols]
        rels=['>' if vals[i]>vals[i+1] else '<' if vals[i]<vals[i+1] else '=' for i in range(4)]
        def test(x,op,y): return {'>':x>y,'<':x<y,'=':x==y,'≥':x>=y,'≤':x<=y}[op]
        worlds=[w for w in itertools.product(range(5),repeat=5) if all(test(w[i],rels[i],w[i+1]) for i in range(4))]
        conclusions=[];truth=[];con_tests=[]
        for _ in range(2):
            x,y=R.sample(range(5),2);op=R.choice(['>','<','≥','≤'])
            conclusions.append(f'{symbols[x]} {op} {symbols[y]}')
            truth.append(all(test(w[x],op,w[y]) for w in worlds))
            con_tests.append((x,op,y))
        ans=2 if all(truth) else 0 if truth[0] else 1 if truth[1] else 3
        if not any(truth) and all(any(test(w[x],op,w[y]) for x,op,y in con_tests) for w in worlds): ans=4
        chain=' '.join(symbols[i]+(' '+rels[i] if i<4 else '') for i in range(5))
        qs.append(question('Inequality',f'Statements: {chain}.\nConclusions: I. {conclusions[0]}   II. {conclusions[1]}.\nWhich conclusions follow? “Either” means at least one must hold, although neither is individually guaranteed.',syllopts[ans],f'Trace the chain, retaining strict and equal signs. I is {"definitely true" if truth[0] else "not guaranteed"}; II is {"definitely true" if truth[1] else "not guaranteed"}. '+('Together the alternatives cover every permissible ordering, so either I or II follows.' if ans==4 else 'The selected conclusion follows across every weak ordering consistent with the statements.'),syllopts))
    # Four explicit language rows distinguish every word (unique occurrence signatures).
    vocabulary=R.sample(['rural','credit','digital','secure','banking','growth','savings','access'],6)
    codes=R.sample(['ka','mi','to','re','su','pa','ni','vo','ze','lu'],6)
    groups=[[0,1,2],[0,3,4],[1,3,5],[2,4,5],[0,1,5]]
    lines=[]
    for g in groups:
        cc=[codes[i] for i in g];R.shuffle(cc)
        lines.append(' '.join(vocabulary[i] for i in g)+' = '+' '.join(cc))
    codebody='In a substitution language, each word has one distinct code. Code order is arbitrary.\n'+'\n'.join(lines)
    for i in R.sample(range(6),4):
        qs.append(question('Coding and decoding',codebody+f'\nWhat is the code for “{vocabulary[i]}”?',codes[i],'Compare the intersections of the coded lines. The complete consistent mapping is: '+', '.join(f'{w} = {c}' for w,c in zip(vocabulary,codes))+'.',codes))
    for k in range(3):
        scale=R.randrange(2,20);w=R.randrange(2,25);e=w+3*scale;n=4*scale
        qs.append(question('Direction sense',f'A surveyor walks {e} km east, turns left and walks {n} km, then turns left and walks {w} km. What is the shortest distance (km) from the starting point?',5*scale,f'Net displacement is {e-w} km east and {n} km north. By Pythagoras, √({e-w}² + {n}²) = {5*scale} km.'))
    rels=[('daughter','sister','female'),('son','brother','male')]
    for k in range(3):
        a,b,c,d=R.sample(['A','B','C','D','E','F','G','H'],4)
        child,sibling,sex=rels[(t+k)%2]
        if k==0:
            stem=f'{a} is the mother of {b}. {c} is the {child} of {b}. {d} is the father of {b}. How is {c} related to {d}?'
            ans='Granddaughter' if sex=='female' else 'Grandson';why=f'{d} is a parent of {b}, and {c} is {b}’s {child}. Hence {c} is {d}’s grandchild.'
        elif k==1:
            stem=f'{a} is the brother of {b}. {b} is the mother of {c}. {d} is the father of {a} and {b}. How is {a} related to {c}?'
            ans='Maternal uncle';why=f'{a} is the brother of {c}’s mother {b}. Therefore {a} is the maternal uncle.'
        else:
            stem=f'{a} is the only daughter of {b}. {b} is the father of {a}. {c} is the son of {a}. {d} is the sister of {b}. How is {b} related to {c}?'
            ans='Maternal grandfather';why=f'{b} is the father of {a}, and {a} is {c}’s mother. Thus {b} is the maternal grandfather.'
        qs.append(question('Blood relations',stem,ans,why,['Granddaughter','Grandson','Maternal uncle','Maternal grandfather','Paternal uncle','Father','Niece']))
    for k in range(2):
        total=R.randrange(35,65);left=R.randrange(8,23);right=total-left+1
        qs.append(question('Ranking',f'In a queue of {total} candidates, a candidate is {left}th from the front. After moving {k+3} places towards the back, what is the candidate’s rank from the back?',right-k-3,f'New front rank = {left}+{k+3} = {left+k+3}. Back rank = {total} − {left+k+3} + 1 = {right-k-3}.'))
    return qs

def quantitative(t):
    sts=[];qs=[]
    # Indirect table, paired bar graph, and prose caselet. Derived data stay in solutions.
    for kind in ['table','bar','caselet']:
        sid=f'T{t:02d}-{kind}'
        rows=[]
        for i in range(5):
            unit=R.randrange(6,20)*20
            m,f=R.choice([(2,3),(3,2),(4,3),(3,4),(5,3)])
            rows.append(dict(label=chr(65+i),a=unit*m,b=unit*f))
        a=[r['a'] for r in rows];b=[r['b'] for r in rows]
        if kind=='table':
            cols=['Branch','Applications','Approved : Rejected']
            cells=[[r['label'],r['a']+r['b'],f'{r["a"]//math.gcd(r["a"],r["b"])} : {r["b"]//math.gcd(r["a"],r["b"])}'] for r in rows]
            title='Applications at five bank branches. Each application is either approved or rejected. Use the total and ratio to derive each category.'
            st=dict(columns=cols,cells=cells,visualization='table')
        elif kind=='bar':
            title='The chart gives agricultural and business loans sanctioned at five branches. Values are numbers of loans.'
            st=dict(columns=['Branch','Agricultural','Business'],rows=rows,visualization='bar')
        else:
            title='Five training centres A–E have male and female trainees only.'
            st=dict(visualization='none')
        body='\n'.join(f'Centre {r["label"]} has {r["a"]+r["b"]} trainees. The male : female ratio is {r["a"]//math.gcd(r["a"],r["b"])} : {r["b"]//math.gcd(r["a"],r["b"])}.' for r in rows) if kind=='caselet' else 'Read the data and answer the following questions.'
        sol='; '.join(f'{r["label"]}: first category {r["a"]}, second category {r["b"]}' for r in rows)
        st.update(id=sid,type='data_interpretation',variant=kind,title=title,body=body,solution=sol)
        sts.append(st)
        first,second=('approved','rejected') if kind=='table' else ('agricultural','business') if kind=='bar' else ('male','female')
        common=f'Derived data: {sol}. '
        setqs=[
          question('Data interpretation',f'What is the total number in the {first} category at A and C together?',a[0]+a[2],common+f'{a[0]} + {a[2]} = {a[0]+a[2]}.',stimulus=sid),
          question('Data interpretation',f'What is the difference between the total at B and the total at E?',abs(a[1]+b[1]-a[4]-b[4]),common+f'Absolute difference = |{a[1]+b[1]} − {a[4]+b[4]}|.',stimulus=sid),
          question('Data interpretation',f'The {second} category at D is what percentage of the {first} category at B? (Round to two decimal places.)',F(b[3]*100,a[1]),common+f'{b[3]} ÷ {a[1]} × 100 = {fmt(F(b[3]*100,a[1]))}%.',stimulus=sid),
          question('Data interpretation',f'What is the average number in the {second} category across A, C and E?',F(b[0]+b[2]+b[4],3),common+f'({b[0]} + {b[2]} + {b[4]}) ÷ 3.',stimulus=sid),
          question('Data interpretation',f'If the {first} category at C increases by 20% and the {second} category there decreases by 10%, what is the new total?',F(a[2]*120+b[2]*90,100),common+f'{a[2]} × 1.20 + {b[2]} × 0.90.',stimulus=sid)]
        ratio=F(a[0]+a[1],b[3]+b[4]);rt=f'{ratio.numerator} : {ratio.denominator}'
        setqs.extend([
          question('Data interpretation',f'What is the ratio of the {first} category at A and B together to the {second} category at D and E together?',rt,common+f'Reduce {a[0]+a[1]} : {b[3]+b[4]} to lowest terms.',[f'{ratio.denominator} : {ratio.numerator}','2 : 3','3 : 5','5 : 7','7 : 9','9 : 11'],sid),
          question('Data interpretation',f'If 25% of the {second} category at E is transferred to the {first} category there, what is the new size of the {first} category at E?',F(a[4]*4+b[4],4),common+f'New first category = {a[4]} + 25% of {b[4]}.',stimulus=sid),
          question('Data interpretation',f'The combined total at A and D is what percentage more or less than the total at C? Give the absolute percentage difference, rounded to two decimals.',F(abs(a[0]+b[0]+a[3]+b[3]-a[2]-b[2])*100,a[2]+b[2]),common+'Percentage difference = |total(A)+total(D)−total(C)| ÷ total(C) × 100.',stimulus=sid),
          question('Data interpretation',f'A fee of ₹20 applies to each in the {first} category and ₹15 to each in the {second} category at B. What is the total fee collected (₹)?',a[1]*20+b[1]*15,common+f'Fee = {a[1]}×20 + {b[1]}×15.',stimulus=sid),
          question('Data interpretation',f'A new branch F has a total equal to the average total at A and E. Its categories are split in ratio 2:3. What is the number in its second category?',F((a[0]+b[0]+a[4]+b[4])*3,10),common+'Average total = (total A + total E)/2. The second category is 3/5 of that average.',stimulus=sid)])
        for q in setqs: q['stem']=f'[{kind.title()} set] '+q['stem']
        qs.extend(R.sample(setqs,5))
    for k in range(5):
        p=R.choice([15,25,35,45,65,75]);base=R.randrange(12,40)*20;n=R.randrange(13,32);v=R.randrange(12,24)
        answer=F(p*base,100)+n*n-v*v
        qs.append(question('Approximation',f'Find the approximate value of ?:\n{p}.02% of {base-0.18:.2f} + {n*n+0.12:.2f} − ({v-0.02:.2f})² = ?',answer,f'Round to {p}% of {base} + {n*n} − {v}² = {fmt(answer)}. All alternatives are separated by several units.'))
    quadopts=['x > y','x ≥ y','x < y','x ≤ y','x = y or relationship cannot be determined']
    for k in range(5):
        x=sorted(R.sample(range(1,16),2));y=sorted(R.sample(range(1,16),2))
        ans=0 if min(x)>max(y) else 1 if min(x)>=max(y) else 2 if max(x)<min(y) else 3 if max(x)<=min(y) else 4
        qs.append(question('Quadratic equations',f'I. x² − {sum(x)}x + {math.prod(x)} = 0\nII. y² − {sum(y)}y + {math.prod(y)} = 0\nChoose the strongest relationship that holds for all possible root pairings.',quadopts[ans],f'Factor I: roots {x[0]}, {x[1]}. Factor II: roots {y[0]}, {y[1]}. Compare all four pairings to obtain {quadopts[ans]}.',quadopts))
    for k in range(5):
        start=R.randrange(3,180);step=R.randrange(2,12)
        seq=[start];diff=[]
        mode=(k+t)%5
        for i in range(5):
            if mode==0: d=(i+step)**2; nxt=seq[-1]+d
            elif mode==1: d=(i+1)*step; nxt=seq[-1]+d
            elif mode==2: d=i+step; nxt=seq[-1]*2+d
            elif mode==3: d=step*2**i; nxt=seq[-1]+d
            else: d=(i+1)**3; nxt=seq[-1]+d
            diff.append(d);seq.append(nxt)
        rule=f'Consecutive increments are {", ".join(map(str,diff))}.' if mode!=2 else f'Multiply each term by 2 and add successive integers {step} through {step+4}.'
        qs.append(question('Number series',f'Find the missing number:\n'+', '.join(map(str,seq[:5]))+', ?',seq[5],rule+f' The next term is {seq[5]}.'))
    # Ten multi-step arithmetic questions, all exact before display rounding.
    cp=R.randrange(16,40)*50;discount=R.choice([10,20,25]);profit=R.choice([12,20,25]);mp=F(cp*(100+profit),100-discount)
    qs.append(question('Profit and loss',f'An item costs ₹{cp}. It is marked above cost and sold at a {discount}% discount on marked price, earning {profit}% profit. Find the marked price (₹, to two decimals).',mp,f'Selling price = {cp} × {100+profit}/100. Marked price = selling price ÷ {(100-discount)/100} = {fmt(mp)}.'))
    days=R.randrange(8,17);worked=R.randrange(2,5)
    qs.append(question('Time and work',f'A can finish a job in {days*2} days and B in {days*3} days. They work together for {worked} days, then B leaves. How many more days does A need?',F(days*6-worked*5,3),f'Use {days*6} work units. Rates: A = 3, B = 2 units/day. Remaining = {days*6} − {worked}×5. Divide by A’s rate 3.'))
    speed=R.randrange(10,19);stream=R.randrange(2,5);dist=(speed+stream)*(speed-stream)
    qs.append(question('Boats and streams',f'A boat travels {dist} km downstream and the same distance upstream. Its still-water speed is {speed} km/h and stream speed is {stream} km/h. Find the total time (hours).',2*speed,f'Time = {dist}/({speed}+{stream}) + {dist}/({speed}−{stream}) = {speed-stream}+{speed+stream} = {2*speed}.'))
    capital=R.randrange(15,40)*1000;ratio=R.choice([2,3,4]);months=R.randrange(4,10);share=R.randrange(15,40)*100
    qs.append(question('Partnership',f'A invests ₹{capital} for 12 months. B invests ₹{capital*ratio} for {months} months. Total profit is ₹{share*(12+ratio*months)}. Find B’s share (₹).',share*ratio*months,f'Capital-time ratio = 12 : {ratio*months}. B’s share = total × {ratio*months}/({12+ratio*months}) = {share*ratio*months}.'))
    principal=R.randrange(10,35)*1000;rate=R.choice([5,10,15,20])
    qs.append(question('Compound interest',f'What is the difference (₹) between compound interest and simple interest on ₹{principal} at {rate}% per annum for 2 years, compounded annually?',F(principal*rate*rate,10000),f'For 2 years, CI − SI = P(r/100)² = {principal} × ({rate}/100)².'))
    litres=R.randrange(8,20)*5
    qs.append(question('Mixtures',f'A vessel contains {litres} litres of milk and water in ratio 3:2. How many litres of pure milk must be added to make the ratio 2:1?',F(litres,5),f'Milk = 3V/5, water = 2V/5. Solve (3V/5 + x)/(2V/5) = 2; x = V/5 = {litres/5:g}.'))
    old=R.randrange(40,70);count=R.randrange(15,35);delta=R.randrange(3,9)
    qs.append(question('Average',f'The average of {count} numbers is {old}. One number, {old+12}, is replaced and the average rises by {delta}. What is the new number?',old+12+count*delta,f'Total increases by {count} × {delta}. New number = {old+12} + {count*delta}.'))
    age=R.randrange(12,25);years=R.randrange(3,9)
    qs.append(question('Ages',f'A father is three times as old as his daughter. After {years} years, their combined age will be {4*age+2*years} years. Find the father’s present age.',3*age,f'Let daughter’s age be x. Father is 3x. 4x + {2*years} = {4*age+2*years}; x = {age}, so father = {3*age}.'))
    length=R.randrange(12,25)*10;platform=R.randrange(10,20)*10;velocity=R.randrange(12,25)
    qs.append(question('Trains',f'A train of length {length} m crosses a {platform} m platform at {fmt(F(velocity*18,5))} km/h. Find crossing time in seconds (to two decimals).',F(length+platform,velocity),f'Speed = {fmt(F(velocity*18,5))} × 5/18 = {velocity} m/s. Time = ({length}+{platform})/{velocity}.'))
    base=R.randrange(20,50)*100;up=R.choice([10,20,25]);down=R.choice([10,20,30])
    qs.append(question('Percentage',f'A village has {base} registered customers. This increases by {up}% in year 1 and decreases by {down}% in year 2. What is the final number?',F(base*(100+up)*(100-down),10000),f'Apply successive factors: {base} × {100+up}/100 × {100-down}/100.'))
    if t%2==0:
        # Alternate paper families test different setups instead of reskinning every stem.
        alt=[]
        cost=R.randrange(15,35)*100;loss=R.choice([10,20,25]);gain=R.choice([10,20,25])
        alt.append(question('Profit and loss',f'Two articles are sold for ₹{cost} each. One earns {gain}% profit and the other incurs {loss}% loss. Find the combined cost price (₹, to two decimals).',F(cost*100,100+gain)+F(cost*100,100-loss),f'Recover each cost separately: {cost}×100/{100+gain} + {cost}×100/{100-loss}. Equal selling prices do not imply equal costs.'))
        fill=R.randrange(8,35);drain=fill*3
        alt.append(question('Pipes and cisterns',f'Two inlet pipes can fill a tank in {fill*2} and {fill*3} hours. An outlet empties it in {drain} hours. All three open together. Find the time (hours) to fill the empty tank.',fill*2,f'Net rate = 1/{fill*2} + 1/{fill*3} − 1/{drain} = 1/{fill*2}. Take the reciprocal.'))
        speed=R.randrange(12,24);stream=R.randrange(2,6);hours=R.randrange(2,6)
        alt.append(question('Boats and streams',f'A boat covers {2*speed*hours} km in still water in {hours*2} hours. If the stream flows at {stream} km/h, how far (km) can it travel upstream in {hours} hours?',(speed-stream)*hours,f'Still-water speed = {speed} km/h. Upstream speed = {speed} − {stream}. Distance = speed × {hours}.'))
        a=R.randrange(3,10);b=R.randrange(3,10);months=R.randrange(3,10);unit=R.randrange(10,30)*100
        alt.append(question('Partnership',f'A and B invest in ratio {a}:{b}. A invests for 12 months; B joins later and invests for {months} months. A receives ₹{12*a*unit} profit. What is the total profit (₹)?',(12*a+b*months)*unit,f'Profit ratio is {12*a}:{b*months}. Each ratio unit = ₹{unit}. Total = {12*a+b*months} × {unit}.'))
        p=R.randrange(10,30)*1000;rate=R.choice([5,10,15,20])
        alt.append(question('Simple interest',f'A sum of ₹{p} earns ₹{p*rate*3//100} simple interest in 3 years. At the same annual rate, what would be the amount (₹) after 2 years with annual compounding?',F(p*(100+rate)**2,10000),f'Rate = interest ×100/(principal ×3) = {rate}%. Compound amount = {p} × (1 + {rate}/100)².'))
        vol=R.randrange(8,20)*10;removed=vol//5
        alt.append(question('Replacement mixture',f'A container holds {vol} litres of pure milk. {removed} litres are removed and replaced with water. This process is repeated once more, mixing thoroughly each time. How many litres of milk remain?',F(vol*16,25),f'Each replacement retains 4/5 of the milk. Remaining milk = {vol} × (4/5)².'))
        count=R.randrange(12,30);avg=R.randrange(25,60);extra=R.randrange(5,15)
        alt.append(question('Average',f'The average weight of {count} people is {avg} kg. One person joins and the average rises by 1 kg. Find the new person’s weight (kg).',avg+count+1,f'New total minus old total = ({count}+1)×({avg}+1) − {count}×{avg} = {avg+count+1}.'))
        age=R.randrange(9,21);after=age
        alt.append(question('Ages',f'A is twice as old as B. After {after} years their ages will be in ratio 3:2. What is the present sum of their ages?',3*age,f'Let B = x, A = 2x. (2x+{after})/(x+{after}) = 3/2 gives x = {after}. Present sum = 3x.'))
        length=R.randrange(12,30)*10;v=R.randrange(12,25);person=R.randrange(2,5)
        alt.append(question('Relative speed',f'A {length} m train moving at {fmt(F((v+person)*18,5))} km/h overtakes a runner moving in the same direction at {fmt(F(person*18,5))} km/h. Find the time (seconds, to two decimals) to pass the runner.',F(length,v),f'Relative speed = ({fmt(F((v+person)*18,5))} − {fmt(F(person*18,5))}) ×5/18 = {v} m/s. Time = {length}/{v}.'))
        qty=R.randrange(15,35)*100;rise=R.choice([20,25,50])
        alt.append(question('Expenditure',f'The price of a commodity increases by {rise}%. A household keeps spending fixed at ₹{qty}. By what percentage must consumption decrease? (Round to two decimals.)',F(rise*100,100+rise),f'New quantity / old quantity = 100/{100+rise}. Reduction percentage = {rise}/{100+rise} ×100.'))
        qs[-10:]=alt
    return sts,qs

def build():
    tests=[];seen=set()
    def distinct(qq):
        stems=[q['stem'] for q in qq if not q.get('stimulusId')]
        return len(stems)==len(set(stems)) and not any(st in seen for st in stems)
    for t in range(1,21):
        stimuli=[];questions=[]
        kinds=['linear' if t%2 else 'parallel','box' if t%3 else 'circular','schedule','floor']
        R.shuffle(kinds)
        for kind in kinds:
            st,qq=arrangement(t,kind);stimuli.append(st);questions.extend(qq)
        for _ in range(100):
            misc=miscellaneous(t)
            if distinct(misc): break
        else: raise AssertionError('Could not create distinct standalone reasoning')
        questions.extend(misc)
        seen.update(q['stem'] for q in misc)
        assert len(questions)==40
        for _ in range(100):
            st,qq=quantitative(t)
            if distinct(qq): break
        else: raise AssertionError(f'Could not create distinct standalone quant for paper {t}: '+str([q['stem'] for q in qq if q['stem'] in seen]))
        seen.update(q['stem'] for q in qq if not q.get('stimulusId'))
        stimuli.extend(st);questions.extend(qq)
        assert len(questions)==80
        for n,q in enumerate(questions,1):
            q.update(id=f'M{t:02d}-Q{n:02d}',number=n,section='reasoning' if n<=40 else 'quant')
            q['explanation']='Answer: '+q['options'][q['answerIndex']]+'. '+q['explanation']
        tests.append(dict(id=f'MOCK-{t:02d}',number=t,title=f'RRB Officer Scale I · Mock {t:02d}',totalQuestions=80,durationSeconds=2700,sections=[dict(id='reasoning',name='Reasoning Ability',start=1,end=40,durationSeconds=1500),dict(id='quant',name='Quantitative Aptitude',start=41,end=80,durationSeconds=1200)],marking=dict(correct=1,incorrect=-0.25,unattempted=0),stimuli=stimuli,questions=questions))
    payload=dict(format='rrb-practice-v3',exam='IBPS RRB Officer Scale I Prelims',version='3.0.0',totalMocks=20,totalQuestions=1600,blueprint='Original practice informed by IBPS structure and 2025 candidate-reported topic trends; difficulty is not officially calibrated.',tests=tests)
    raw=json.dumps(payload,ensure_ascii=False,indent=2)
    (ROOT/'data/tests.json').write_text(raw,encoding='utf-8')
    (ROOT/'data/tests_data.js').write_text('window.__IBPS_MOCK_DATA__ = '+raw+';',encoding='utf-8')
    (ROOT/'data/solver_audit.json').write_text(json.dumps(AUDIT,indent=2),encoding='utf-8')
    print('Built 20 papers / 1,600 questions; 80 arrangements each have exactly one solution.')

if __name__=='__main__': build()
