"""Constraint models built from the supplied source clues, with no key input."""
from z3 import Int, Solver, Distinct, Or, If, sat
import json
from pathlib import Path

def absolute(x): return If(x>=0,x,-x)

class Model:
    def __init__(self, name, n):
        self.name=name;self.n=n;self.s=Solver();self.groups={}
    def group(self,label,names,lower=1,upper=None):
        values={name:Int(self.name+'_'+label+'_'+name) for name in names}
        self.groups[label]=values;self.s.add(Distinct(*values.values()))
        for x in values.values():self.s.add(x>=lower,x<=(self.n if upper is None else upper))
        return values
    def solve(self):
        variables=[v for group in self.groups.values() for v in group.values()]
        out=[]
        while self.s.check()==sat and len(out)<1000:
            m=self.s.model();out.append({k:{name:m.eval(v).as_long() for name,v in g.items()} for k,g in self.groups.items()})
            self.s.add(Or(*[v!=m.eval(v) for v in variables]))
        return out

def all_models():
    out=[]
    m=Model('2023s1_floors',9);p=m.group('floor','ABCDEFGHI')
    m.s.add(p['H']<p['E'],p['G']>p['F'],absolute(p['I']-p['E'])!=1,absolute(p['B']-p['I'])==6,p['D']==p['H']-1,p['D']%2==0,p['D']!=2,absolute(p['D']-p['B'])==2,absolute(p['A']-p['C'])!=1,p['C']!=1,p['C']<p['A'],p['A']<p['E']);out.append(m)
    m=Model('2023s1_countries',7);p=m.group('box','JKLMNOP');c=m.group('country',['Brazil','Denmark','Finland','Poland','Spain','Vietnam','Hungary'])
    m.s.add(absolute(p['M']-p['J'])==4,p['J']!=c['Denmark'],p['M']==c['Brazil']+3,absolute(p['N']-c['Finland'])!=1,c['Finland']>p['M']+1,absolute(p['L']-c['Finland'])==4,c['Hungary']==p['L']+1,c['Poland']==p['P']+1,absolute(p['K']-p['N'])==2,p['K']!=c['Spain'],p['J']!=c['Spain']);out.append(m)
    m=Model('2023s1_circle',8);p=m.group('seat','MRSTHCBK',0,7);f={name:Int(m.name+'_face_'+name) for name in p};m.groups['facing']=f
    for v in f.values():m.s.add(Or(v==1,v==-1))
    def right(b,a,k):return (p[b]-p[a]-k*f[a])%8==0
    m.s.add(p['S']==0,f['S']==1,right('R','S',3),right('C','R',-2),right('T','C',3),right('K','C',-2),right('M','R',2),right('B','M',3),~right('B','S',2),f['K']==f['R'],f['R']==-f['B'],f['B']==-f['T'],right('H','B',2),f['M']==f['H'],f['M']==-f['T']);out.append(m)
    m=Model('2023s1_births',8);p=m.group('position','PQRSTUVW');years=[1961,1966,1969,1972,1977,1979,1985,1994]
    year=lambda x:sum(If(p[x]==i+1,v,0) for i,v in enumerate(years))
    m.s.add(Or(absolute(p['U']-2)==3,absolute(p['U']-4)==3,absolute(p['U']-8)==3),p['U']==p['Q']-1,p['Q']+p['W']==9,absolute(year('P')-year('V'))==5,absolute(p['V']-p['U'])==4,year('R')%2==1,p['R']>p['S'],p['T']!=p['R']+1);out.append(m)
    m=Model('2022_circle',8);p=m.group('seat','MNOPXYZR',0,7);f={name:Int(m.name+'_face_'+name) for name in p};m.groups['facing']=f
    for v in f.values():m.s.add(Or(v==1,v==-1))
    def right(b,a,k):return (p[b]-p[a]-k*f[a])%8==0
    m.s.add(p['M']==0,right('M','Z',-3),Or((p['O']-p['R'])%8==2,(p['R']-p['O'])%8==2),right('M','R',3),right('Y','M',2),right('N','P',1),(p['N']-p['Z'])%8!=1,(p['N']-p['Z'])%8!=7,right('O','N',2),f['O']==f['N'],f['Y']==-1,f['Y']==-f['Z'],f['X']==f['Z']);out.append(m)
    m=Model('2022_meetings',8);p=m.group('position','ABCDEFGH')
    m.s.add(absolute(p['A']-p['G'])==3,p['D']+p['F']==9,p['C']==3,absolute(p['C']-p['H'])>=4,p['A']%2==0,p['A']<p['G'],absolute(p['F']-p['E'])==3);out.append(m)
    m=Model('2022_south_row',18);p=m.group('position','PQRSTUV');total=Int('2022_south_total');m.groups['total']={'count':total}
    m.s.add(total<=18,total>=7)
    for x in p.values():m.s.add(x<=total)
    m.s.add(absolute(p['P']-p['Q'])==2,p['R']==p['P']+4,absolute(p['R']-p['S'])==6,absolute(p['S']-p['T'])==5,p['S']-1<=6,absolute(p['P']-p['T'])==absolute(p['Q']-p['U']),p['Q']<p['U'],absolute(p['U']-p['V'])==4,p['V']==p['R']+1,p['T']!=2,p['T']!=total-1,p['U']!=2,p['U']!=total-1);out.append(m)
    m=Model('2022_boxes',10);p=m.group('position','PQRSTUVWXY')
    m.s.add(absolute(p['Y']-p['T'])==3,p['R']==10,absolute(p['Q']-p['T'])==4,Or(p['V']<p['P'],p['S']<p['P']),Or(p['V']>p['P'],p['S']>p['P']),absolute(p['R']-p['X'])==absolute(p['X']-p['T']),p['X']==8,p['Q']==p['U']+1,p['Q']<p['V'],p['W']%2==1);out.append(m)
    m=Model('2022_colours',7);p=m.group('position','PQRSTUV');c=m.group('colour',['Blue','Red','Yellow','Pink','Green','Purple','Orange'])
    m.s.add(absolute(p['T']-c['Red'])==5,Or(c['Red']==1,c['Red']==7),p['R']==c['Yellow'],p['R']==p['T']-1,absolute(p['R']-c['Blue'])==3,absolute(p['P']-c['Blue'])!=1,absolute(p['Q']-c['Blue'])!=1,p['P']!=1,p['P']!=7,p['U']==c['Green'],absolute(p['U']-p['P'])==1,absolute(p['U']-c['Pink'])==2,p['S']!=c['Pink'],p['T']!=c['Orange'],p['Q']!=c['Blue']);out.append(m)
    m=Model('2023s2_floors',10);p=m.group('floor','PQRSTUVWYZ')
    m.s.add(p['Z']==6,absolute(p['Z']-p['U'])==4,p['P']==p['U']-1,absolute(p['P']-p['Q'])==6,p['V']%2==0,p['V']==p['R']+1,p['W']<p['R']-1,p['W']%2==0,p['W']>p['Q'],p['Y']>p['T'],p['Y']<p['S'],p['S']%2==1);out.append(m)
    m=Model('2023s2_row',8);p=m.group('position','ABCDEFGH');f={name:Int(m.name+'_face_'+name) for name in p};m.groups['facing']=f
    for v in f.values():m.s.add(Or(v==1,v==-1))
    m.s.add(sum(If(v==1,1,0) for v in f.values())>4,absolute(p['E']-p['C'])==5,p['E']!=1,p['E']!=8,p['C']!=1,p['C']!=8,f['E']==1,p['F']==p['E']+1,absolute(p['F']-p['D'])==2,absolute(p['D']-p['E'])==absolute(p['D']-p['G']),f['G']==1,p['B']==p['G']-2,f['E']==-f['D'],p['A']!=1,p['A']!=8,f['A']==-1,absolute(p['G']-p['A'])!=1)
    for a in p:
        for b in p:
            m.s.add(Or(p[a]!=1,p[b]!=8,f[a]==-f[b]))
            m.s.add(Or(p[a]!=p['E']-1,p[b]!=p['E']+1,f[a]==-f[b]))
    out.append(m)
    m=Model('2023s2_ages',7);p=m.group('position','JKLMNOP');ages=[63,53,42,40,37,27,16]
    age=lambda x:sum(If(p[x]==i+1,v,0) for i,v in enumerate(ages))
    m.s.add(age('L')+age('O')==79,absolute(age('O')-age('M'))==absolute(age('L')-age('K')),age('O')>age('M'),age('J')+age('N')==2*age('P'),age('M')%2==0,age('J')>=age('N'));out.append(m)
    m=Model('2023s2_seminars',7);p=m.group('month','ABCDEFG');c=m.group('subject',['Physiology','Biology','History','Sociology','Mathematics','Taxology','Cardiology'])
    m.s.add(p['C']==c['Mathematics'],Or(p['C']==4,p['C']==6),absolute(p['C']-c['Cardiology'])==3,c['Biology']==5,p['G']==c['Physiology'],absolute(c['Cardiology']-c['History'])==2,absolute(p['C']-p['B'])==3,p['B']==c['Sociology'],p['G']==p['D']-1,p['E']>p['A'],p['E']!=c['Biology'],p['A']!=c['Biology']);out.append(m)
    return out

if __name__=='__main__':
    results={}
    for model in all_models():
        solutions=model.solve();results[model.name]=solutions;print(model.name,len(solutions),json.dumps(solutions[:3]),flush=True)
    Path(__file__).with_name('prepp_cache').joinpath('audit/models.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
