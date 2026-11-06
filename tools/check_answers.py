"""Recompute quantitative keys from displayed inputs, independently of the generator."""
import json, re, math
from fractions import Fraction as F
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'data/tests.json').read_text(encoding='utf-8'))
count=0; fingerprints=set()
def numbers(s): return [F(x) for x in re.findall(r'(?<![A-Za-z])\d+(?:\.\d+)?',s)]
def verify(q,answer):
    global count
    given=q['options'][q['answerIndex']]
    if isinstance(answer,str): assert given==answer,(q['id'],given,answer)
    else: assert abs(F(given)-answer)<=F(51,10000),(q['id'],given,str(answer))
    count+=1

for t in data['tests']:
    stimuli={s['id']:s for s in t['stimuli']}
    for q in t['questions']:
        stim=stimuli.get(q.get('stimulusId'))
        fp=q['stem']+(json.dumps(stim,sort_keys=True,ensure_ascii=False) if stim else '')
        assert fp not in fingerprints,('Repeated question',q['id'])
        fingerprints.add(fp)
        if q['section']!='quant': continue
        s=q['stem'];topic=q['topic'];n=numbers(s)
        if topic=='Data interpretation':
            if stim['variant']=='bar': a=[F(r['a']) for r in stim['rows']];b=[F(r['b']) for r in stim['rows']]
            else:
                if stim['variant']=='table': rows=[(F(row[1]),*[F(x.strip()) for x in row[2].split(':')]) for row in stim['cells']]
                else: rows=[tuple(map(F,x)) for x in re.findall(r'has (\d+) trainees\. The male : female ratio is (\d+) : (\d+)',stim['body'])]
                a=[total*x/(x+y) for total,x,y in rows];b=[total*y/(x+y) for total,x,y in rows]
            if 'A and C together' in s: ans=a[0]+a[2]
            elif 'difference between the total' in s: ans=abs(a[1]+b[1]-a[4]-b[4])
            elif 'what percentage of' in s: ans=b[3]*100/a[1]
            elif 'average number' in s: ans=(b[0]+b[2]+b[4])/3
            elif 'increases by 20%' in s: ans=a[2]*F(6,5)+b[2]*F(9,10)
            elif 'What is the ratio' in s:
                ratio=(a[0]+a[1])/(b[3]+b[4]);ans=f'{ratio.numerator} : {ratio.denominator}'
            elif 'transferred' in s: ans=a[4]+b[4]/4
            elif 'percentage more or less' in s: ans=abs(a[0]+b[0]+a[3]+b[3]-a[2]-b[2])*100/(a[2]+b[2])
            elif 'fee' in s: ans=a[1]*20+b[1]*15
            elif 'new branch F' in s: ans=(a[0]+b[0]+a[4]+b[4])*F(3,10)
            else: raise AssertionError(s)
        elif topic=='Quadratic equations':
            coeff=[tuple(map(int,v)) for v in re.findall(r'[xy]² − (\d+)[xy] \+ (\d+)',s)]
            roots=[]
            for sm,prod in coeff:
                d=math.isqrt(sm*sm-4*prod);roots.append([F(sm-d,2),F(sm+d,2)])
            x,y=roots
            ans='x > y' if min(x)>max(y) else 'x ≥ y' if min(x)>=max(y) else 'x < y' if max(x)<min(y) else 'x ≤ y' if max(x)<=min(y) else 'x = y or relationship cannot be determined'
        elif topic=='Approximation':
            p,base,term,v=map(F,re.findall(r'(\d+\.\d+)',s))
            ans=F(round(p)*round(base),100)+round(term)-round(v)**2
        elif topic=='Number series':
            seq=list(map(int,re.findall(r'\d+',s)))
            dif=[y-x for x,y in zip(seq,seq[1:])]
            candidates=[]
            if len(set(dif[i+1]-dif[i] for i in range(3)))==1: candidates.append(seq[-1]+dif[-1]+dif[1]-dif[0])
            if dif[1]==2*dif[0] and dif[2]==2*dif[1] and dif[3]==2*dif[2]: candidates.append(seq[-1]+2*dif[-1])
            r=[seq[i+1]-2*seq[i] for i in range(4)]
            if r[1]-r[0]==r[2]-r[1]==r[3]-r[2]==1: candidates.append(seq[-1]*2+r[-1]+1)
            rt=[math.isqrt(d) if d>=0 else -1 for d in dif]
            if all(x*x==d for x,d in zip(rt,dif)) and all(rt[i+1]-rt[i]==1 for i in range(3)): candidates.append(seq[-1]+(rt[-1]+1)**2)
            if dif==[1,8,27,64]: candidates.append(seq[-1]+125)
            assert len(set(candidates))==1,(q['id'],candidates)
            ans=F(candidates[0])
        elif topic=='Profit and loss':
            if 'Two articles' in s: cost,gain,loss=n[:3];ans=cost*100/(100+gain)+cost*100/(100-loss)
            else: cost,discount,profit=n[:3];ans=cost*(100+profit)/(100-discount)
        elif topic=='Time and work':
            da,db,worked=n[:3];ans=(1-worked*(1/da+1/db))*da
        elif topic=='Pipes and cisterns':
            p1,p2,out=n[:3];ans=1/(1/p1+1/p2-1/out)
        elif topic=='Boats and streams':
            if 'still water in' in s: dist,h,stream,time=n[:4];ans=(dist/h-stream)*time
            else: dist,v,stream=n[:3];ans=dist/(v+stream)+dist/(v-stream)
        elif topic=='Partnership':
            if 'A and B invest' in s: a,b,ma,months,profit=n[:5];ans=profit*(ma*a+b*months)/(ma*a)
            else: ca,ma,cb,mb,profit=n[:5];ans=profit*cb*mb/(ca*ma+cb*mb)
        elif topic=='Compound interest':
            principal,rate,years=n[:3];ans=principal*(1+rate/100)**int(years)-principal-principal*rate*years/100
        elif topic=='Simple interest':
            principal,interest,years,term=n[:4];rate=interest/principal/years;ans=principal*(1+rate)**int(term)
        elif topic=='Mixtures':
            vol,a,b,c,d=n[:5];ans=vol*b/(a+b)*c/d-vol*a/(a+b)
        elif topic=='Replacement mixture':
            vol,remove=n[:2];ans=vol*(1-remove/vol)**2
        elif topic=='Average':
            if 'people' in s: cnt,avg=n[:2];ans=(cnt+1)*(avg+1)-cnt*avg
            else: cnt,avg,old,delta=n[:4];ans=old+cnt*delta
        elif topic=='Ages':
            if 'A is twice' in s: after=n[0];ans=after*3
            else: after,total=n[:2];ans=(total-2*after)*F(3,4)
        elif topic=='Trains':
            length,platform,speed=n[:3];ans=(length+platform)/(speed*F(5,18))
        elif topic=='Relative speed':
            length,train,runner=n[:3];ans=length/((train-runner)*F(5,18))
        elif topic=='Expenditure':
            rise=n[0];ans=rise*100/(100+rise)
        elif topic=='Percentage':
            base,up,year1,down=n[:4];ans=base*(100+up)*(100-down)/10000
        else: raise AssertionError(topic)
        verify(q,ans)
assert count==800
assert len(fingerprints)==1600
print(f'PASS: {count} quantitative keys independently recomputed; all 1,600 contextual questions are distinct.')
