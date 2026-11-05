"""Deterministic original practice content for the IBPS RRB Scale-I prelims suite.
This is an independent mock simulation, not an official or previously asked paper.
"""
import json, random, itertools, math, re
from pathlib import Path
from fractions import Fraction
from collections import Counter

OUT=Path(__file__).resolve().parents[1]/'data'/'tests.json'
R=random.Random(20261105)
MALE_NAMES='Aarav Dev Farhan Harish Jatin Lakshya Nikhil Ojas Rohan Uday Varun Yash Bharat Eshan Firoz Hemanth Jai Lalit Mohan Om Ravi Tarun Vikram Yuvraj'.split()
FEMALE_NAMES='Bhavna Chitra Esha Gauri Isha Kavya Meera Priya Sana Tanvi Wami Zara Anika Charu Deepa Geeta Ira Kriti Nisha Pooja Shreya Uma Zoya'.split()
NAMES='Aarav Bhavna Chitra Dev Esha Farhan Gauri Harish Isha Jatin Kavya Lakshya Meera Nikhil Ojas Priya Rohan Sana Tanvi Uday Varun Wami Yash Zara Anika Bharat Charu Deepa Eshan Firoz Geeta Hemanth Ira Jai Kriti Lalit Mohan Nisha Om Pooja Ravi Shreya Tarun Uma Vikram Yuvraj Zoya'.split()
WORDS='lotus river garden market timber yellow silver cotton bridge mango winter temple golden paper harvest candle velvet pearl forest travel basket ocean violet almond breeze window summer honest planet summit maple copper saffron honey violet meadow circle feather thunder cotton canvas inland'.split()
DI_LABELS=['Mysuru','Hubballi','Belagavi','Shivamogga','Tumakuru','Ballari','Mandya','Hassan','Udupi','Davangere','Bidar','Kolar','Raichur','Chitradurga','Bagalkot']
correct_letters='ABCDE'
seen_stems=set()
question_counts=Counter()


def fmt(x):
    if isinstance(x, Fraction):
        if x.denominator == 1:return str(x.numerator)
        return f'{x.numerator}/{x.denominator}'
    if isinstance(x,float):return f'{x:.2f}'.rstrip('0').rstrip('.')
    return str(x)

def opts(correct, distractors=None, unit='', integer=True):
    # Stable 5-option quantitative MCQs; each option's representation is distinct.
    v=float(correct)
    vals=[v]
    proposed=list(distractors or [])
    deltas=[1,2,3,4,5,6,7,8,10,12,15,20,25,30,35,40,50,60,75,100]
    R.shuffle(deltas)
    proposed += [v+d for d in deltas] + [v-d for d in deltas]
    for d in proposed:
        if len(vals)>=5:break
        d=float(d)
        if (not math.isfinite(d)) or d<0 or (integer and abs(d-round(d))>1e-8):continue
        if all(abs(d-a)>1e-8 for a in vals):vals.append(d)
    if len(vals)!=5:raise ValueError('options failure')
    R.shuffle(vals)
    texts=[fmt(round(x) if integer else x) + unit for x in vals]
    return texts, vals.index(v)

def letter_opts(answer, distractors):
    vals=[answer]+[x for x in distractors if x!=answer]
    vals=list(dict.fromkeys(vals))
    if len(vals)!=5:raise ValueError(('non5 names',vals))
    R.shuffle(vals)
    return vals, vals.index(answer)

def q(section,topic,stem,options,correct,explanation,stimulus_id=None,difficulty='moderate'):
    if stem in seen_stems:raise ValueError('duplicate stem: '+stem[:140])
    seen_stems.add(stem)
    if len(explanation.strip())<20:explanation='Working: '+explanation
    assert len(options)==5 and len(set(options))==5 and 0<=correct<5
    question_counts[topic]+=1
    return {'id':None,'section':section,'topic':topic,'difficulty':difficulty,'stem':stem,
            'options':options,'answerIndex':correct,'explanation':explanation,
            **({'stimulusId':stimulus_id} if stimulus_id else {})}

def Q(topic,stem,correct,exp,distractors=None,unit='',integer=True):
    options,ix=opts(correct,distractors,unit,integer)
    return q('quant',topic,stem,options,ix,exp)

# ---------- Puzzle generation, automatically solved for uniqueness ----------
PERMS=list(itertools.permutations(range(7)))

def puzzle_set(test_no,group_no):
    names=R.sample(NAMES,7)
    typ=['row','floor','boxes','months','designation','heights'][(test_no*3+group_no)%6]
    if typ=='row':title='Seven candidates sit in a straight row, all facing north.'; direction='to the right of'; top='leftmost'; levels=[f'seat {i+1} from the left' for i in range(7)]
    elif typ=='floor':title='Seven people live on different floors of a seven-storey building. Floor 1 is the bottom floor, and floor 7 is the top floor.';direction='above';top='bottom';levels=[f'floor {i+1}' for i in range(7)]
    elif typ=='boxes':title='Seven labelled boxes are stacked vertically, with one box in each position.';direction='above';top='bottom';levels=[f'position {i+1} from the bottom' for i in range(7)]
    elif typ=='months':title='Seven people have interviews in seven consecutive months from January to July, one per month.';direction='later than';top='first';levels=['January','February','March','April','May','June','July']
    elif typ=='designation':title='Seven employees hold seven distinct ranks (rank 1 is junior-most and rank 7 is senior-most).';direction='senior to';top='junior-most';levels=[f'rank {i+1}' for i in range(7)]
    else:title='Seven contestants finish at different positions in a race (position 1 is last and position 7 is first).';direction='ahead of';top='last';levels=[f'position {i+1} from last' for i in range(7)]
    order=names[:];R.shuffle(order)
    pos={nm:i for i,nm in enumerate(order)}
    constraints=[]
    def add(kind,ref,description):constraints.append((kind,ref,description))
    for person in names:
        p=pos[person]
        if p in (0,1,2,3,4,5,6):add('anchor',(person,p),f'{person} is at {levels[p]}.')
    for a,b in itertools.permutations(names,2):
        d=pos[a]-pos[b]
        if d==1:add('immediate',(a,b),f'{a} is immediately {direction} {b}.')
        if d in (2,3):add('exact',(a,b,d),f'{a} is exactly {d} positions {direction} {b}.')
        if abs(d) in (2,3):add('gap',(a,b,abs(d)-1),f'There are exactly {abs(d)-1} positions between {a} and {b}.')
        if d>0:add('later',(a,b),f'{a} is {direction} {b}.')
    for a,b,c in itertools.permutations(names,3):
        if pos[a]<pos[b]<pos[c] and pos[c]-pos[a] in (3,4):
            add('between',(a,b,c),f'In the stated ordering, {a} comes before {b}, and {b} comes before {c}.')
    # For each statement, candidate arrangements satisfying it are precomputed.
    name_idx={nm:i for i,nm in enumerate(names)}
    def test_constraint(t,arr):
        typ,ref,_=t
        def p(name):return arr[name_idx[name]]
        if typ=='anchor':a,k=ref;return p(a)==k
        if typ=='immediate':a,b=ref;return p(a)-p(b)==1
        if typ=='exact':a,b,d=ref;return p(a)-p(b)==d
        if typ=='gap':a,b,n=ref;return abs(p(a)-p(b))==n+1
        if typ=='later':a,b=ref;return p(a)>p(b)
        if typ=='between':a,b,c=ref;return p(a)<p(b)<p(c)
        raise ValueError(typ)
    # Represent permutations as positions by person index (not order index).
    candidates=PERMS[:]
    picked=[]; anchors=0
    # Exactly one anchor, then non-anchor clues. An anchor makes questions solvable without a hidden orientation.
    anchor_pool=[c for c in constraints if c[0]=='anchor' and c[1][1] in (0,1,2,3,4,5,6)]
    selected_anchor=R.choice(anchor_pool)
    picked.append(selected_anchor);anchors+=1
    candidates=[v for v in candidates if test_constraint(selected_anchor,v)]
    available=[x for x in constraints if x!=selected_anchor and x[0]!='anchor']
    R.shuffle(available)
    while len(candidates)>1 and len(picked)<13:
        sample=R.sample(available, min(len(available), 38))
        best=None;surv=None;small=len(candidates)
        for c in sample:
            subset=[a for a in candidates if test_constraint(c,a)]
            if len(subset)<small and len(subset)>0:
                small=len(subset);best=c;surv=subset
        if best is None:raise RuntimeError('no solver progress')
        picked.append(best);available.remove(best);candidates=surv
    if len(candidates)!=1:raise RuntimeError('puzzle not unique')
    R.shuffle(picked)
    sid=f'T{test_no:02d}-P{group_no}'
    layout='; '.join(f'{levels[i]}: {nm}' for i,nm in enumerate(order))
    s={'id':sid,'type':'logic_puzzle','variant':typ,'title':title,'body':'Clues:\n'+'\n'.join(f'{i+1}. {clue[2]}' for i,clue in enumerate(picked)),
       'solution':layout,'uniquenessVerified':True}
    questions=[]
    # Ask a deliberate mix of location, occupant, next neighbour and between.
    for j in range(5):
        if j==0:
            idx=R.choice([0,1,3,5,6]);ans=order[idx];occupant_from_q1=ans
            options,ci=letter_opts(ans,R.sample([nm for nm in names if nm!=ans],4))
            stem=f'Based on arrangement {sid}, who occupies {levels[idx]}?'
        elif j==1:
            person=R.choice([nm for nm in names if nm!=occupant_from_q1]);idx=pos[person];ans=levels[idx]
            options,ci=letter_opts(ans,R.sample([x for x in levels if x!=ans],4))
            stem=f'Based on arrangement {sid}, which position does {person} occupy?'
        elif j==2:
            idx=R.choice(list(range(6)));person=order[idx];ans=order[idx+1]
            options,ci=letter_opts(ans,R.sample([nm for nm in names if nm!=ans],4))
            stem=f'Based on arrangement {sid}, who is immediately {direction} {person}?'
        elif j==3:
            a,b=R.sample(names,2);ans=abs(pos[a]-pos[b])-1
            options,ci=opts(ans,list(range(7)))
            stem=f'Based on arrangement {sid}, how many positions are between {a} and {b}?'
        else:
            idx=R.choice(list(range(1,6)));person=order[idx];ans=order[idx-1]
            options,ci=letter_opts(ans,R.sample([nm for nm in names if nm!=ans],4))
            stem=f'Based on arrangement {sid}, who is immediately before {person} in the order defined in the passage?'
        questions.append(q('reasoning','Puzzle & Seating Arrangement',stem,options,ci,'Unique arrangement: '+layout,sid))
    return s, questions

SYL_TEMPLATES=[
 ('Some {a} are {b}. All {b} are {c}.','Some {a} are {c}.','All {a} are {c}.',True,False,'Some A–B members must be C; not all A need be C.'),
 ('No {a} are {b}. Some {b} are {c}.','Some {c} are not {a}.','No {c} are {a}.',True,False,'The B∩C members are outside A; other C members remain unrestricted.'),
 ('All {a} are {b}. No {b} are {c}.','No {a} are {c}.','Some {a} are {c}.',True,False,'A is contained in B, while B and C are disjoint.'),
 ('Some {a} are {b}. No {b} are {c}.','Some {a} are not {c}.','All {a} are {c}.',True,False,'The A∩B members cannot be C.'),
 ('Some {a} are {b}. Some {b} are {c}.','Some {a} are {c}.','Some {b} are {a}.',False,True,'The two Some overlaps need not coincide; Some A are B converts to Some B are A.'),
 ('All {a} are {b}. Some {c} are {a}.','Some {c} are {b}.','Some {b} are {c}.',True,True,'The existing C∩A members must lie in B, proving both conclusions.'),
 ('No {a} are {b}. All {c} are {b}. Some {c} are {b}.','No {a} are {c}.','Some {c} are not {a}.',True,True,'All C members belong to B, disjoint from A; some C are explicitly given.'),
 ('Some {a} are {b}. Some {b} are {c}.','Some {a} are {c}.','All {c} are {a}.',False,False,'The specified intersections do not force A and C to overlap or include one another.'),
]
SYL_OPTIONS=['Only conclusion I follows','Only conclusion II follows','Both conclusions I and II follow','Neither conclusion follows','Either conclusion I or II follows']

def reasoning_short(t):
    qs=[];stimuli=[]
    # 5 inequality implications, verified by exhaustive numeric counterexamples.
    for j in range(5):
        letters=R.sample('PQRSTUVWXZ',5)
        rel=R.choices(['>','<','≥','≤','='],[3,3,2,2,1],k=4)
        chain=' '.join(f'{letters[k]} {rel[k]}' for k in range(4))+' '+letters[4]
        def ok(x,op,y):return {'>':x>y,'<':x<y,'≥':x>=y,'≤':x<=y,'=':x==y}[op]
        valid=[v for v in itertools.product(range(5),repeat=5) if all(ok(v[k],rel[k],v[k+1]) for k in range(4))]
        if not valid: # construct a valid ordering if random signs incompatible
            rel=['>','≥','>','<'];valid=[v for v in itertools.product(range(5),repeat=5) if all(ok(v[k],rel[k],v[k+1]) for k in range(4))]
            chain=' '.join(f'{letters[k]} {rel[k]}' for k in range(4))+' '+letters[4]
        conclusions=[]
        for a,b in itertools.combinations(range(5),2):
            for op in ['>','<','≥','≤','=']:
                truth=all(ok(v[a],op,v[b]) for v in valid)
                conclusions.append((f'{letters[a]} {op} {letters[b]}',truth))
        true_cons=[x for x in conclusions if x[1]];false_cons=[x for x in conclusions if not x[1]]
        combo=R.choice([(True,False),(False,True),(True,True),(False,False)])
        if (not true_cons) and (True in combo):combo=(False,False)
        choices=[R.choice(true_cons if v else false_cons) for v in combo]
        if choices[0][0]==choices[1][0]:choices[1]=R.choice([v for v in (true_cons if combo[1] else false_cons) if v[0]!=choices[0][0]])
        correct={ (True,False):0,(False,True):1,(True,True):2,(False,False):3}[combo]
        stem=f'Given the inequality chain {chain}, decide which conclusions follow. I: {choices[0][0]}. II: {choices[1][0]}.'
        explanation=f'Exhaustive valid-order checking confirms: I is {"always" if combo[0] else "not necessarily"} true and II is {"always" if combo[1] else "not necessarily"} true.'
        qs.append(q('reasoning','Inequality',stem,SYL_OPTIONS,correct,explanation))
    # 5 syllogism with correct conclusion logic from vetted logical forms.
    for j in range(5):
        template=SYL_TEMPLATES[(t*5+j)%len(SYL_TEMPLATES)]
        a,b,c=R.sample(['poets','runners','artists','farmers','pilots','singers','teachers','bakers','coders','dancers','readers','sailors','painters','workers','drivers'],3)
        d={'a':a,'b':b,'c':c};stat,co1,co2,v1,v2,expl=template
        stat=stat.format(**d);co1=co1.format(**d);co2=co2.format(**d)
        correct={(True,False):0,(False,True):1,(True,True):2,(False,False):3}[(v1,v2)]
        stem=f'Statements: {stat} Conclusions: I. {co1} II. {co2} Which conclusion follows?'
        qs.append(q('reasoning','Syllogism',stem,SYL_OPTIONS,correct,expl))
    # Four coding/decoding questions using a shared and fully identifiable word-code mapping.
    words=R.sample(list(dict.fromkeys(WORDS)),6)
    codes=R.sample(['ka','ni','ro','te','mu','sa','li','ve','po','di','zu','fa','no','bi','qa','xe','ju','fi'],6)
    pairs=list(zip(words,codes));R.shuffle(pairs);dic=dict(pairs)
    phrases=[(0,1,2),(0,3,4),(1,3,5),(2,4,5)]
    lines=[]
    for inds in phrases:
        w=[words[i] for i in inds];c=[dic[x] for x in w];R.shuffle(w);R.shuffle(c)
        lines.append(' '.join(w)+' = '+' '.join(c))
    sid=f'T{t:02d}-CODE'
    stimuli.append({'id':sid,'type':'coding','title':'In a certain coded language, each word has one unique code.','body':'\n'.join(lines), 'solution':', '.join(f'{w}={dic[w]}' for w in words)})
    for j in range(4):
        word=words[j];ans=dic[word]
        options,ix=letter_opts(ans,R.sample([x for x in codes if x!=ans],4))
        qs.append(q('reasoning','Coding-Decoding',f'Based on coding set {sid}, what is the code for "{word}"?',options,ix,f'Common-word intersections identify {word} as {ans}.',sid))
    # 3 self-contained direction-and-distance questions.
    for j in range(3):
        k=t+1
        if j==0:
            n,s,e,w=5*k,k,4*k,k
            answer=5*k; distractors=[7*k,3*k,4*k,6*k]
            stem=f'Ritu walks {n} km north, then {e} km east, then {s} km south and finally {w} km west. What is her shortest distance from the starting point?'
            options,ci=opts(answer,distractors,' km')
            explanation=f'Net north = {n-s} km and east = {e-w} km. Distance = √({n-s}²+{e-w}²) = {answer} km.'
        elif j==1:
            n,s,e,w=k,3*k,6*k,k
            answer='South-East';others=['North','South-West','North-West','North-East']
            stem=f'Kiran moves {n} km north, {e} km east, {s} km south and {w} km west. In which direction is Kiran from the start?'
            options,ci=letter_opts(answer,others)
            explanation=f'Net {s-n} km south and {e-w} km east: South-East.'
        else:
            n,s,e,w=9*k,5*k,4*k,k
            answer=n+e+s+w;shortest=5*k
            stem=f'A cyclist travels {n} km north, {e} km east, {s} km south and {w} km west. What total distance did the cyclist travel?'
            options,ci=opts(answer,[shortest,n+e,s+w,answer-k],' km')
            explanation=f'Total path length = {n}+{e}+{s}+{w}={answer} km (not displacement).'
        qs.append(q('reasoning','Direction & Distance',stem,options,ci,explanation))
    # 3 blood-relation word problems from explicit gender/family statements.
    blood=[
     ('{a} is the father of {b}. {b} is the sister of {c}. {c} is the mother of {d}. How is {a} related to {d}?','Maternal grandfather','As C is the mother of D and A is C’s father, A is D’s maternal grandfather.'),
     ('{a} is the mother of {b}. {b} is the father of {c}. How is {a} related to {c}?','Paternal grandmother','A is the mother of C’s father B.'),
     ('{a} is the brother of {b}. {b} is the mother of {c}. How is {a} related to {c}?','Maternal uncle','A is the brother of C’s mother.'),
     ('{a} is the sister of {b}. {b} is the father of {c}. How is {a} related to {c}?','Paternal aunt','A is the sister of C’s father.'),
     ('{a} is the daughter of {b}. {b} is the brother of {c}. {c} is the mother of {d}. How is {a} related to {d}?','Cousin','A and D are children of siblings B and C, so they are cousins.'),
    ]
    allrels=['Maternal grandfather','Paternal grandmother','Maternal uncle','Paternal aunt','Cousin','Paternal grandfather','Maternal aunt','Niece','Brother','Mother','Nephew','Sister']
    for j in range(3):
        temp,ans,ex=blood[(t*3+j)%len(blood)]
        if ans=='Maternal grandfather': d={'a':R.choice(MALE_NAMES),'b':R.choice(FEMALE_NAMES),'c':R.choice(FEMALE_NAMES),'d':R.choice(NAMES)}
        elif ans=='Paternal grandmother': d={'a':R.choice(FEMALE_NAMES),'b':R.choice(MALE_NAMES),'c':R.choice(NAMES),'d':R.choice(NAMES)}
        elif ans=='Maternal uncle': d={'a':R.choice(MALE_NAMES),'b':R.choice(FEMALE_NAMES),'c':R.choice(NAMES),'d':R.choice(NAMES)}
        elif ans=='Paternal aunt': d={'a':R.choice(FEMALE_NAMES),'b':R.choice(MALE_NAMES),'c':R.choice(NAMES),'d':R.choice(NAMES)}
        else: d={'a':R.choice(FEMALE_NAMES),'b':R.choice(MALE_NAMES),'c':R.choice(FEMALE_NAMES),'d':R.choice(NAMES)}
        # A family cannot contain two distinct roles with the same name.
        while len(set(d.values()))<4:
            for key in 'abcd':
                if sum(v==d[key] for v in d.values())>1:
                    pool=MALE_NAMES if (key=='a' and ans in ('Maternal grandfather','Maternal uncle') or key=='b' and ans in ('Paternal grandmother','Paternal aunt','Cousin')) else FEMALE_NAMES if (key=='a' and ans in ('Paternal grandmother','Paternal aunt','Cousin') or key=='b' and ans in ('Maternal grandfather','Maternal uncle') or key=='c' and ans in ('Maternal grandfather','Cousin')) else NAMES
                    d[key]=R.choice([n for n in pool if n not in [v for k,v in d.items() if k!=key]])
        options,ci=letter_opts(ans,R.sample([x for x in allrels if x!=ans],4))
        qs.append(q('reasoning','Blood Relations',temp.format(**d),options,ci,ex))
    assert len(qs)==20
    return stimuli,qs

# ------------------------- Quantitative sets -------------------------------
def di_set(t,k):
    types=['table','bar','line','caselet','pie'];typ=types[(t+2*k)%5]
    labels=R.sample(DI_LABELS,5)
    base1=[20*R.randint(5,20) for _ in range(5)]
    base2=[20*R.randint(5,20) for _ in range(5)]
    first,second=R.choice([('rice','wheat'),('books','notebooks'),('buses','vans'),('shirts','trousers'),('mobile phones','headphones'),('tickets A','tickets B')])
    sid=f'T{t:02d}-DI{k}'
    rows=[{'label':lab,'a':a,'b':b} for lab,a,b in zip(labels,base1,base2)]
    title=f'A regional survey records {first} and {second} across five locations.'
    if typ=='caselet':
        body=f'The survey reported the following figures ({first}, {second}): '+ '; '.join(f'{lab} ({a}, {b})' for lab,a,b in zip(labels,base1,base2))+'.'
    else:
        body=f'{"Location":<15} {first:<18} {second}\n'+'\n'.join(f'{lab:<15} {a:<18} {b}' for lab,a,b in zip(labels,base1,base2))
    if typ=='pie':
        title='Two pie charts show the regional distribution of the two item categories, with exact counts in the accompanying table.'
    stim={'id':sid,'type':'data_interpretation','variant':typ,'title':title,'body':body,
          'columns':['Location',first,second],'rows':rows, 'visualization':('table' if typ in ('table','caselet') else typ)}
    qs=[]
    i,j=R.sample(range(5),2)
    answer=base1[i]+base1[j]
    qs.append(Q('Data Interpretation',f'Using data set {sid}, what is the combined number of {first} in {labels[i]} and {labels[j]}?',answer,f'{base1[i]} + {base1[j]} = {answer}.'))
    i,j=R.sample(range(5),2)
    answer=abs((base1[i]+base2[i])-(base1[j]+base2[j]))
    qs.append(Q('Data Interpretation',f'Using data set {sid}, what is the absolute difference between the total of both categories in {labels[i]} and {labels[j]}?',answer,f'Absolute difference between {base1[i]+base2[i]} and {base1[j]+base2[j]} = {answer}.'))
    i=R.randrange(5)
    g=math.gcd(base1[i],base2[i]);ratio=f'{base1[i]//g}:{base2[i]//g}'
    other=[]
    for a,b in [(1,1),(2,3),(3,2),(3,4),(4,3),(5,4),(4,5),(2,5),(5,2),(1,2),(2,1)]:
        r=f'{a}:{b}'
        if r!=ratio:other.append(r)
    options,ci=letter_opts(ratio,R.sample(other,4))
    qs.append(q('quant','Data Interpretation',f'Using data set {sid}, find the simplest ratio of {first} to {second} in {labels[i]}.',options,ci,f'Ratio {base1[i]}:{base2[i]} reduces to {ratio}.',sid))
    answer=sum(base2)//5
    qs.append(Q('Data Interpretation',f'Using data set {sid}, what is the average number of {second} across all five locations?',answer,f'({" + ".join(map(str,base2))}) / 5 = {answer}.'))
    i,j=R.sample(range(5),2)
    answer=(base1[i]+base2[j])//4
    qs.append(Q('Data Interpretation',f'Using data set {sid}, what is 25% of the sum of {first} in {labels[i]} and {second} in {labels[j]}?',answer,f'({base1[i]} + {base2[j]}) × 25/100 = {answer}.'))
    for question in qs:question['stimulusId']=sid
    return stim,qs

def simplification(t,j):
    typ=(t+j)%5
    if typ==0:
        a=(5+t)*40; b=R.randint(5,20)*5;ans=a//4+b//5
        stem=f'What is the exact value of 25% of {a} + {b} ÷ 5?';expl=f'{a}/4 + {b}/5 = {ans}.'
    elif typ==1:
        a=15+t;b=R.randint(2,8);ans=a+b**3
        stem=f'Calculate √{a*a} + {b}³.';expl=f'{a} + {b*b*b} = {ans}.'
    elif typ==2:
        a=15+2*t;b=R.randint(5,18);c=R.randint(2,9);ans=a*b-c*c
        stem=f'Simplify ({a} × {b}) − {c}².';expl=f'{a*b} − {c*c} = {ans}.'
    elif typ==3:
        a=20+t;b=R.randint(3,12);c=R.randint(4,20)*20;ans=a*b+c//4
        stem=f'Find ({a*b*b} ÷ {b}) + 25% of {c}.';expl=f'{a*b} + {c//4} = {ans}.'
    else:
        a=30+t;b=R.randint(2,18);ans=a*a-b*b
        stem=f'Evaluate {a}² − {b}².';expl=f'({a}−{b})({a}+{b}) = {ans}.'
    return Q('Simplification',stem,ans,expl)

def series(t,j):
    kind=(t+j*3)%8
    a=R.randint(2,20)+t*25;d=R.randint(2,12)
    if kind==0:seq=[a+i*d for i in range(6)];ans=a+6*d;exp=f'Add {d} each time.'
    elif kind==1:seq=[i*i+a for i in range(1,7)];ans=49+a;exp=f'Terms are n²+{a} for n=1,2,...'
    elif kind==2:seq=[a];
    elif kind==3:seq=[a];
    elif kind==4:seq=[a+i*i*d for i in range(6)];ans=a+36*d;exp=f'Terms are {a} + {d}n² with n starting from zero.'
    elif kind==5:seq=[a+i*(i+1)//2*d for i in range(6)];ans=a+21*d;exp=f'Increment by {d} × 1, {d} × 2, ...'
    elif kind==6:seq=[a*2**i+d for i in range(6)];ans=a*64+d;exp=f'Subtract {d}, double the result, add {d} back.'
    else:seq=[a+i*2*d for i in range(6)];ans=a+12*d;exp=f'Add {2*d} to each term.'
    if kind==2:
        for _ in range(5):seq.append(seq[-1]*2+d)
        ans=seq[-1]*2+d;exp=f'Each term is twice its predecessor plus {d}.'
    if kind==3:
        for i in range(5):seq.append(seq[-1]+(d if i%2==0 else d+3))
        ans=seq[-1]+(d if 5%2==0 else d+3);exp=f'Alternate additions of {d} and {d+3}.'
    return Q('Number Series',f'Find the next term in the series: {", ".join(map(str,seq))}, ?',ans,exp)

def quadratic(t,j):
    mode=(t+j)%5;offset=t-12
    schemes=[([7,8],[2,3]),([5,8],[3,5]),([1,2],[5,6]),([3,5],[5,8]),([1,8],[3,6])]
    xs,ys=schemes[mode]
    xs=[x+offset for x in xs];ys=[x+offset for x in ys]
    def poly(r):
        b=-(r[0]+r[1]);c=r[0]*r[1]
        return f'v² {"−" if b<0 else "+"} {abs(b)}v {"−" if c<0 else "+"} {abs(c)} = 0'
    left=poly(xs).replace('v','x');right=poly(ys).replace('v','y')
    answers=['x > y','x ≥ y','x < y','x ≤ y','Relationship cannot be established']
    stem=f'Compare x and y. Equation I: {left}. Equation II: {right}. Which option is always correct?'
    exp=f'Roots of x are {xs[0]} and {xs[1]}; roots of y are {ys[0]} and {ys[1]}. Hence {answers[mode]}.'
    return q('quant','Quadratic Comparison',stem,answers,mode,exp)

ARITH_TOPICS=['Percentage','Ratio & Proportion','Profit & Loss','Discount','Simple Interest','Compound Interest','Time & Work','Time, Speed & Distance','Averages','Ages','Mixture','Partnership','Pipes & Cisterns','Boats & Streams','Mensuration']

def arithmetic(t,j):
    topic=ARITH_TOPICS[(t*7+j*11)%len(ARITH_TOPICS)]
    k=3+question_counts[topic];r=R.choice([10,20,25,30,40]);
    if topic=='Percentage':
        n=(5+question_counts[topic])*40;ans=n*(100+r)//100
        return Q(topic,f'A village had {n} residents. Its population grew by {r}%. What is the new population?',ans,f'{n} × (100+{r})/100 = {ans}.')
    if topic=='Ratio & Proportion':
        a,b=R.sample(range(2,12),2);n=R.randint(8,35);total=(a+b)*n;ans=a*n
        return Q(topic,f'Two savings amounts are in ratio {a}:{b}. Their combined amount is ₹{total}. Find the first amount.',ans,f'{a}/({a}+{b}) × {total} = ₹{ans}.')
    if topic=='Profit & Loss':
        cp=k*100;ans=cp*(100+r)//100
        return Q(topic,f'A shop bought an item for ₹{cp} and sold it at {r}% profit. Find the selling price.',ans,f'{cp} × (100+{r})/100 = ₹{ans}.')
    if topic=='Discount':
        mp=k*100;ans=mp*(100-r)//100
        return Q(topic,f'An article marked ₹{mp} has a discount of {r}%. What is its selling price?',ans,f'{mp} × (100−{r})/100 = ₹{ans}.')
    if topic=='Simple Interest':
        p=k*1000;rate=R.randint(4,12);years=R.randint(2,5);ans=p*rate*years//100
        return Q(topic,f'Find simple interest on ₹{p} at {rate}% per annum for {years} years.',ans,f'SI = P×R×T/100 = {p}×{rate}×{years}/100 = ₹{ans}.')
    if topic=='Compound Interest':
        p=(k+30*question_counts[topic])*1000;rate=10;ans=p*21//100
        return Q(topic,f'Find compound interest on ₹{p} at {rate}% annually for 2 years.',ans,f'CI = {p}×[(1.1)²−1] = ₹{ans}.')
    if topic=='Time & Work':
        c=question_counts[topic]+1;a=12+2*c;b=18+3*c
        val=Fraction(a*b,a+b);ans=float(val);integer=val.denominator==1
        return Q(topic,f'A can finish a task in {a} days and B in {b} days. In how many days can they finish it together?',ans,f'Combined time = ({a}×{b})/({a}+{b}) = {fmt(val)} days.',integer=integer)
    if topic=='Time, Speed & Distance':
        sp=40+5*question_counts[topic];hours=R.randint(2,8);dist=sp*hours
        return Q(topic,f'A bus covers {dist} km in {hours} hours at constant speed. What is its speed?',sp,f'Speed = {dist} ÷ {hours} = {sp} km/h.',unit=' km/h')
    if topic=='Averages':
        n=22+2*question_counts[topic];diff=R.randint(2,10);old_total=n*5;new_avg=n+diff;ans=new_avg*6-old_total
        return Q(topic,f'The average of five test scores is {n}. What sixth score raises the average of six scores to {new_avg}?',ans,f'6×{new_avg} − 5×{n} = {ans}.')
    if topic=='Ages':
        son=R.randint(8,18);father=son+R.randint(20,30);n=R.randint(3,10);ans=father+n
        return Q(topic,f'A father is {father} years old and his son is {son}. How old will the father be after {n} years?',ans,f'{father}+{n}={ans}.')
    if topic=='Mixture':
        x=(2+question_counts[topic])*10;y=R.randint(2,6)*10;ans=(x*20+y*40)//(x+y)
        # Guarantee integer result by asking liters of substance, rather than resulting percent.
        ans=(x*20+y*40)//100
        return Q(topic,f'{x} litres of 20% juice is mixed with {y} litres of 40% juice. How many litres of pure juice does the mixture contain?',ans,f'{x}×0.20 + {y}×0.40 = {ans} litres.',unit=' L')
    if topic=='Partnership':
        a,b=R.randint(3,15),R.randint(3,15);m,n=R.randint(4,12),R.randint(4,12);profit=(a*m+b*n)*R.randint(10,20)
        ans=profit*a*m//(a*m+b*n)
        return Q(topic,f'A and B invest ₹{a*1000} for {m} months and ₹{b*1000} for {n} months. They earn ₹{profit} profit. What is A’s share?',ans,f'Capital-time ratio {a*m}:{b*n}; A gets {a*m}/{a*m+b*n} × {profit} = ₹{ans}.')
    if topic=='Pipes & Cisterns':
        c=question_counts[topic]+1;a=10+2*c;b=15+3*c
        val=Fraction(a*b,a+b);ans=float(val)
        return Q(topic,f'Pipe A fills a tank in {a} hours and pipe B in {b} hours. How many hours if both pipes work together?',ans,f'Time = {a}×{b}/({a}+{b}) = {fmt(val)} hours.',integer=(val.denominator==1))
    if topic=='Boats & Streams':
        boat=R.randint(10,30);stream=R.randint(2,8);hours=R.randint(2,6);distance=(boat+stream)*hours
        return Q(topic,f'A boat moves at {boat} km/h in still water while the stream runs at {stream} km/h. How long does it take to cover {distance} km downstream?',hours,f'Downstream speed = {boat}+{stream}={boat+stream}; time = {distance}/{boat+stream} = {hours} hours.',unit=' h')
    if topic=='Mensuration':
        l,b=R.randint(12,45),R.randint(8,32);ans=l*b
        return Q(topic,f'Find the area of a rectangular field of length {l} m and breadth {b} m.',ans,f'Area = {l}×{b}={ans} m².',unit=' m²')
    raise AssertionError(topic)


def generate():
    tests=[]
    for t in range(1,21):
        s=[];rq=[]
        for g in range(1,5):
            ss,qq=puzzle_set(t,g);s.append(ss);rq.extend(qq)
        ssh,short=reasoning_short(t);s.extend(ssh);rq.extend(short)
        assert len(rq)==40,(t,len(rq))
        di=[]
        for k in range(1,4):
            ss,qq=di_set(t,k);s.append(ss);di.extend(qq)
        quant=di + [simplification(t,j) for j in range(5)]+[series(t,j) for j in range(5)]+[quadratic(t,j) for j in range(5)]+[arithmetic(t,j) for j in range(10)]
        assert len(quant)==40,(t,len(quant))
        for n,item in enumerate(rq+quant,1):item['id']=f'M{t:02d}-Q{n:02d}';item['number']=n
        tests.append({'id':f'MOCK-{t:02d}','number':t,'title':f'RRB PO Prelims Mock {t:02d}',
                      'totalQuestions':80,'durationSeconds':2700,
                      'sectionOrder':['reasoning','quant'],'sections':[{'id':'reasoning','name':'Reasoning Ability','start':1,'end':40,'durationSeconds':1500},{'id':'quant','name':'Quantitative Aptitude','start':41,'end':80,'durationSeconds':1200}],
                      'marking':{'correct':1,'incorrect':-0.25,'unattempted':0},'stimuli':s,'questions':rq+quant})
        print('completed',t,'questions',len(rq+quant),'puzzle clues', [len(st['body'].splitlines()) for st in s if st['type']=='logic_puzzle'],flush=True)
    data={'format':'rrb-po-prelims-original-mock-v1','generatedFor':'Independent practice; not official IBPS content','locale':'en-IN','version':'1.0.0',
          'exam':'IBPS RRB Officer Scale I Preliminary Examination','totalMocks':20,'totalQuestions':1600,'tests':tests}
    OUT.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Saved',OUT,OUT.stat().st_size,'bytes')
    print('Topic counts:',dict(question_counts))

if __name__=='__main__':generate()
