"""Explicit constraint models for source reasoning puzzles; no answer-key input.

Positions are one-based, left-to-right, bottom-to-top, or chronological as labelled.
Only arrangements proved unique are added as worked explanations.
"""
from z3 import Int, Solver, Distinct, Or, If, And, sat, unsat

def ab(x):return If(x>=0,x,-x)

class Puzzle:
    def __init__(self,paper,questions,size,labels=None,orientation='Position'):
        self.paper=paper;self.questions=questions;self.n=size;self.s=Solver();self.groups=[]
        self.labels=labels or list(range(1,size+1));self.orientation=orientation;self.total=None;self.facings={};self.circular=False
    def group(self,names,title='Person'):
        names=list(names) if isinstance(names,str) else names
        group={name:Int(f'p{self.paper}q{self.questions[0]}_{len(self.groups)}_{name}') for name in names}
        self.s.add(Distinct(*group.values()))
        for x in group.values():self.s.add(x>=1,x<=self.n)
        self.groups.append((title,group));return group
    def add(self,*constraints):self.s.add(*constraints)
    def end(self,x):return Or(x==1,x==self.n)
    def solve(self):
        if self.s.check()!=sat:
            print('MODEL NEEDS REVIEW',self.paper,self.questions,flush=True)
            return None
        m=self.s.model();variables=[x for _,g in self.groups for x in g.values()]+list(self.facings.values())+([self.total] if self.total is not None else [])
        self.s.push();self.s.add(Or(*[x!=m[x] for x in variables]));unique=self.s.check()==unsat;self.s.pop()
        if not unique:
            alternatives=[m]
            self.s.push()
            while len(alternatives)<=8:
                last=alternatives[-1]
                self.s.add(Or(*[x!=last[x] for x in variables]))
                if self.s.check()==unsat:break
                alternatives.append(self.s.model())
            complete=self.s.check()==unsat
            self.s.pop()
            if not complete:return None
            tables=[]
            for candidate in alternatives:
                rows=[]
                for i,label in enumerate(self.labels,1):
                    row=[str(label)]+[', '.join(name for name,x in g.items() if candidate[x].as_long()==i) or 'Unspecified' for _,g in self.groups]
                    if self.facings:
                        occupant=next(name for name,x in self.groups[0][1].items() if candidate[x].as_long()==i)
                        facing=candidate[self.facings[occupant]].as_long()==1
                        row.append(('Inside' if facing else 'Outside') if self.circular else ('North' if facing else 'South'))
                    rows.append(row)
                headers=[self.orientation]+[title for title,_ in self.groups]+(['Facing'] if self.facings else [])
                tables.append('| '+' | '.join(headers)+' |\n| '+' | '.join('---' for _ in headers)+' |\n'+'\n'.join('| '+' | '.join(row)+' |' for row in rows))
            return {'text':f'The stated clues allow {len(alternatives)} arrangements. '
                'The alternatives below are found by applying every ordering and position constraint. '
                'A conclusion is definite only when it holds in every arrangement; a publisher key '
                'does not resolve information absent from the clues.\n\n'+'\n\n'.join('Arrangement '+str(i+1)+':\n\n'+table for i,table in enumerate(tables)),
                'status':'constraint-verified-alternatives'}
        rows=[]
        labels=list(range(1,m[self.total].as_long()+1)) if self.total is not None else self.labels
        for i,label in enumerate(labels,1):
            row=[str(label)]
            for _,g in self.groups:row.append(', '.join(name for name,x in g.items() if m[x].as_long()==i) or 'Unspecified')
            if self.facings:
                occupant=next(name for name,x in self.groups[0][1].items() if m[x].as_long()==i)
                inward=m[self.facings[occupant]].as_long()==1
                row.append(('Inside' if inward else 'Outside') if self.circular else ('North' if inward else 'South'))
            rows.append(row)
        headers=[self.orientation]+[title for title,_ in self.groups]
        if self.facings:headers.append('Facing')
        table='| '+' | '.join(headers)+' |\n| '+' | '.join('---' for _ in headers)+' |\n'+'\n'.join('| '+' | '.join(row)+' |' for row in rows)
        return {'text':'Place each person/item once and apply all the positional and ordering clues together. '
            'Checking all assignments leaves the following unique arrangement:\n\n'+table+
            '\n\nRead the required position, gap, matching item, or true statement from this arrangement. '
            'A gap count excludes the two endpoints. This arrangement is derived from the displayed clues, '
            'not supplied as a worked solution in the publisher PDF.', 'status':'constraint-verified-arrangement'}


def build_models():
    models=[]
    def new(paper,lo,hi,n,**kw):
        model=Puzzle(paper,list(range(lo,hi+1)),n,**kw);models.append(model);return model
    def variable_row(paper,lo,hi,names):
        p=new(paper,lo,hi,40,orientation='Left-to-right position')
        d=p.group(names);p.total=Int(f'rowSize_{paper}_{lo}')
        p.add(p.total>=len(names),p.total<=40,*[x<=p.total for x in d.values()])
        return p,d,p.total
    def facing_group(p,names,circular=True,inside_count=None):
        d=p.group(names);p.circular=circular
        p.facings={name:Int(f'face_{p.paper}_{p.questions[0]}_{name}') for name in names}
        p.add(*[Or(x==0,x==1) for x in p.facings.values()])
        if inside_count is not None:p.add(sum(p.facings.values())==inside_count)
        def right(a,b,k=1):
            offset=If(p.facings[b]==1,-k,k) if circular else If(p.facings[b]==1,k,-k)
            return (d[a]-d[b]-offset)%p.n==0 if circular else d[a]==d[b]+offset
        def near(a,b):return Or((d[a]-d[b])%p.n==1,(d[b]-d[a])%p.n==1) if circular else ab(d[a]-d[b])==1
        return d,p.facings,right,near
    def circle(paper,lo,hi,names,inside_count=None,square=False):
        p=new(paper,lo,hi,len(names),orientation='Clockwise seat (starting seat arbitrary)')
        d,f,r,near=facing_group(p,names,inside_count=inside_count)
        p.add(Or(d[names[0]]==1,d[names[0]]==2) if square else d[names[0]]==1)
        return p,d,f,r,near
    p=new(1,1,5,9,orientation='Left-to-right position');d=p.group('ABCDEFGHI')
    A,B,C,D,E,F,G,H,I=[d[x] for x in 'ABCDEFGHI']
    p.add(ab(B-G)==4,C==G+2,H==C-3,ab(E-H)==1,ab(E-A)==2,F==D-2)
    p=new(1,6,8,6,orientation='Rank, tallest first');d=p.group('ABCDEF');A,B,C,D,E,F=[d[x] for x in 'ABCDEF']
    p.add(C<A,A<B,ab(C-D)==3,6-A==E-1,F>=5)
    p=new(1,13,17,9,orientation='Box position, bottom to top');d=p.group('ABCDEFGHI','Box');A,B,C,D,E,F,G,H,I=[d[x] for x in 'ABCDEFGHI']
    p.add(A==C+4,ab(G-A)==1,ab(G-B)==3,E==B+1,E<D,E<=4,I==F+2)
    ranks=['CEO','COO','AM','GM','AGM','Manager','Clerk']
    p=new(1,18,22,7,labels=ranks,orientation='Designation, senior to junior');d=p.group('KLMNOPQ');f=p.group(['pencil','fruit','rubber','paper','color','cutlery','brush'],'Item');K,L,M,N,O,P,Q=[d[x] for x in 'KLMNOPQ']
    p.add(P==f['paper']+4,K<4,K!=f['paper'],K!=f['cutlery'],ab(K-Q)==3,Q-1==7-f['pencil'],M==f['cutlery']+1,M!=7,ab(N-f['brush'])==3,O==f['color']-1,f['rubber']!=1)
    p,d,f,r,near=circle(1,35,39,'ABCDEFGH')
    p.add(Or((d['B']-d['C'])%8==2,(d['C']-d['B'])%8==2),r('H','C',2),Or((d['H']-d['A'])%8==3,(d['A']-d['H'])%8==3),r('D','A',-1),ab(d['G']-d['E'])==4,f['G']==f['B'],~near('G','B'),sum(f.values())>5)
    for name in d:p.add(If(near(name,'A'),f[name]!=f['A'],True))

    p,d,f,r,near=circle(2,6,10,'ABCDEFGHI',inside_count=9)
    p.add(r('G','B',4),Or((d['G']-d['E'])%9==3,(d['E']-d['G'])%9==3),r('H','E',-5),Or((d['H']-d['A'])%9==2,(d['A']-d['H'])%9==2),r('D','F'),r('F','C',3))
    p=new(2,29,33,8,orientation='Left-to-right position');d,f,r,near=facing_group(p,'ABCDEFGH',circular=False);A,B,C,D,E,F,G,H=[d[x] for x in 'ABCDEFGH']
    p.add(r('A','F',2),f['A']==f['F'],r('B','F',-1),r('F','B',-1),ab(A-B)-1==If(f['A']==1,8-A,A-1),ab(D-H)==4,f['D']!=f['H'],r('G','D'),f['C']==0,sum(f.values())>4)
    for name in d:p.add(If(near(name,'C'),f[name]==1,True))

    p=new(2,19,23,7,labels=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],orientation='Day');d=p.group('ABCDEFG');f=p.group(['Operation','History','Sociology','Urdu','Math','Zoology','Physics'],'Subject');A,B,C,D,E,F,G=[d[x] for x in 'ABCDEFG']
    p.add(F==f['History']-3,ab(F-C)>4,C==f['Sociology']+1,f['Urdu']==B+2,B!=5,B-1==7-A,ab(A-f['Math'])==4,D==f['Zoology'],E==f['Operation']+1)
    p=new(2,26,28,6,orientation='Rank, lightest first');d=p.group('ABCDEF');A,B,C,D,E,F=[d[x] for x in 'ABCDEF'];p.add(C>E,A>F,B>C,ab(B-C)>1,A<=2)
    years=[1957,1963,1970,1976,1985,1991,2000,2010]
    p=new(2,36,40,8,labels=years,orientation='Birth year, oldest first');d=p.group('PQRSTUVW');P,Q,R,S,T,U,V,W=[d[x] for x in 'PQRSTUVW']
    def year(x):return sum(If(x==i,y,0) for i,y in enumerate(years,1))
    p.add(year(P)-year(V)==9,P-1==8-Q+2,Q==S-1,ab(S-W)==4,U<R,R<T,U!=1)

    p=new(3,1,5,7,orientation='Column, observer left to right');a=p.group('ABCDEFG','North-facing row');b=p.group('PQRSTUV','South-facing row');A,B,C,D,E,F,G=[a[x] for x in 'ABCDEFG'];P,Q,R,S,T,U,V=[b[x] for x in 'PQRSTUV']
    p.add(p.end(S),ab(V-S)==1,T==V+2,ab(T-F)==3,2*A==B+C,Or(And(C==1,R==7),And(C==7,R==1)),A!=V,P==D,G==U-1,E!=T)
    p=new(3,13,17,10,labels=[f'Floor {floor}, Flat {flat}' for floor in range(1,6) for flat in ['X','Y']],orientation='Flat, bottom to top');d=p.group('NOPQRSTUVW');N,O,P,Q,R,S,T,U,V,W=[d[x] for x in 'NOPQRSTUVW']
    fl=lambda x:(x-1)/2+1
    side=lambda x:(x-1)%2
    p.add(ab(fl(S)-fl(O))==3,side(S)!=side(O),fl(P)==fl(S)+1,side(S)!=side(P),fl(O)!=4,fl(O)!=5,fl(V)==fl(T),side(V)==0,side(T)==1,fl(T)==fl(N)-1,side(N)==0,fl(U)==fl(W)+1,side(U)==side(W),fl(Q)>fl(R),side(Q)==side(R))
    p=new(3,27,31,9,labels=['January','March','April','May','July','August','September','October','December'],orientation='Birth month');d=p.group('ABCDEFGHI');A,B,C,D,E,F,G,H,I=[d[x] for x in 'ABCDEFGHI']
    months=[1,3,4,5,7,8,9,10,12]
    def month(x):return sum(If(x==i,v,0) for i,v in enumerate(months,1))
    p.add(Or(C==3,C==7),ab(C-I)==3,Or(I==3,I==6,I==7,I==8,I==9),Or(B==3,B==7),B==H-1,D==F+3,F!=1,month(E)==month(A)+4)
    p=new(3,33,35,7,orientation='Rank, shortest first');d=p.group('ABCDEFG');A,B,C,D,E,F,G=[d[x] for x in 'ABCDEFG']
    p.add(D<B,B<C,F>B,F!=7,G==5,G<C,E<B,E!=1,D!=1,D!=3)
    p=new(3,36,40,7,orientation='Left-to-right position');d=p.group('MNOPQRS');f=p.group(['Apple','Banana','Mango','Orange','Grapes','Pineapple','Watermelon'],'Fruit');M,N,O,P,Q,R,S=[d[x] for x in 'MNOPQRS']
    p.add(R==O+3,O==f['Mango'],R==Q-2,p.end(f['Banana']),P==f['Grapes']+3,ab(N-Q)==3,R!=f['Watermelon'],S==R-4,f['Apple']==N+2,N!=f['Watermelon'],N!=f['Pineapple'],Q<=f['Banana'])

    p=new(4,1,5,7,labels=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],orientation='Day');d=p.group('ABCDEFG');f=p.group(['Daffodil','Peony','Bluebell','Lavender','Hibiscus','Lotus','Dahlia'],'Flower');A,B,C,D,E,F,G=[d[x] for x in 'ABCDEFG']
    p.add(f['Lotus']==5,G==6,G==f['Dahlia'],ab(f['Lotus']-f['Daffodil'])==2,ab(f['Hibiscus']-f['Daffodil'])==4,E==f['Hibiscus'],E==f['Lavender']+2,A==E-1,D==f['Bluebell'],F==D+1,B<E)
    p=new(4,12,16,10,orientation='Box position, bottom to top');d=p.group('ABCDEFGHIJ','Box');A,B,C,D,E,F,G,H,I,J=[d[x] for x in 'ABCDEFGHIJ']
    p.add(ab(C-G)==4,A==C-2,I==C+1,ab(I-B)==2,J==B+3,ab(A-E)==3,F==H+1,F<A,F>E)
    p,d,f,r,near=circle(4,18,22,'JKLMNOPQ',inside_count=4)
    p.add(r('J','M',2),f['M']==0,r('L','J',-3),f['L']==f['J'],ab(d['L']-d['Q'])==4,~near('K','Q'),~near('K','L'),f['K']==0,r('O','K',3),r('N','P',-3),f['P']==1,f['N']==0)
    for a in d:
        for b in d:
            if a<b:p.add(If(And(near(a,'M'),near(b,'M')),f[a]!=f[b],True))
    p,d,total=variable_row(4,23,25,'PQRSTW');P,Q,R,S,T,W=[d[x] for x in 'PQRSTW']
    p.add(ab(P-T)==4,R==P+3,ab(S-R)==3,W==Q-2,ab(S-Q)==2,total-R==P,total-S<=2)
    p=new(4,35,39,8,labels=[f'Floor {floor}, Flat {flat}' for floor in range(1,5) for flat in ['A','B']],orientation='Flat, bottom to top');d=p.group('RSTUVWXZ');R,S,T,U,V,W,X,Z=[d[x] for x in 'RSTUVWXZ']
    fl=lambda x:(x-1)/2+1
    side=lambda x:(x-1)%2
    p.add(fl(W)==3,side(W)==1,fl(V)==fl(W)-2,side(Z)==1,fl(R)==fl(X),side(T)==0,fl(T)==fl(R)-1,fl(T)>fl(Z),fl(S)%2==1,side(S)==1)

    p=new(5,1,5,10,orientation='Box position, bottom to top');d=p.group('ABCDEFGHIJ','Box');A,B,C,D,E,F,G,H,I,J=[d[x] for x in 'ABCDEFGHIJ']
    p.add(ab(D-I)==4,B==D-1,ab(B-E)==4,E==A+1,A>I,ab(J-E)==2,C>E,2*H==C+E,10-F==H-2)
    p=new(5,11,15,7,orientation='Left-to-right position');d=p.group('JKLMNOP');f=p.group(['Papaya','Watermelon','Kiwi','Strawberry','Pear','Plum','Avocado'],'Fruit');J,K,L,M,N,O,P=[d[x] for x in 'JKLMNOP']
    p.add(p.end(O),f['Kiwi']==5,ab(N-f['Kiwi'])==2,P==f['Avocado'],ab(P-O)==3,M==N+3,N==f['Pear'],J==f['Watermelon'],J>M,ab(K-J)>3,ab(M-f['Papaya'])==4,f['Plum']!=1,f['Plum']!=7)
    dates=[f'{m} {day}' for m in ['May','June','July','August'] for day in [12,21]]
    p=new(5,35,39,8,labels=dates,orientation='Visit date');d=p.group('PQRSTUVW');P,Q,R,S,T,U,V,W=[d[x] for x in 'PQRSTUVW']
    p.add(R==6,ab(T-R)==1,ab(P-W)==3,T==W-1,Q==S-1,(Q-1)/2!=(S-1)/2,U<V)
    p,d,f,r,near=circle(5,24,28,'PQRSTUVW',inside_count=4,square=True)
    for name in d:p.add((d[name]%2==1)==(f[name]==1))
    p.add(r('R','P',2),r('T','R',2),near('P','U'),~near('Q','R'),r('W','U'),(d['S']-d['W'])%8==3,d['S']%2==0)

    p,d,f,r,near=circle(6,10,14,'JKLMNOPQ',inside_count=4,square=True)
    p.add(ab(d['J']-d['P'])==4,f['J']==1,f['P']==1,Or((d['P']-d['Q'])%8==3,(d['Q']-d['P'])%8==3),r('L','Q',3),~near('O','Q'),~near('O','L'),r('K','J',-1),d['M']%2==0,r('N','M',3),f['N']==1)
    def right_distance(a,b):return If(f[b]==1,(d[b]-d[a])%8,(d[a]-d[b])%8)
    p.add(right_distance('L','M')==right_distance('O','K'))

    p=new(6,20,24,10,orientation='Box position, bottom to top');d=p.group('PQRSTUVWXY','Box');P,Q,R,S,T,U,V,W,X,Y=[d[x] for x in 'PQRSTUVWXY']
    p.add(P==S+3,ab(P-R)==4,Q==P-2,R==U+2,V==W+4,W==Q-3,W<U,Y>V,Y<U,ab(Y-X)>3)
    p=new(6,26,30,7,orientation='Left-to-right position');d=p.group('PQRSTUV');f=p.group(['Lily','Orchid','Rose','Poppy','Daisy','Tulip','Jasmine'],'Flower');P,Q,R,S,T,U,V=[d[x] for x in 'PQRSTUV']
    p.add(P==f['Rose'],p.end(P),ab(T-P)==3,R==T-1,T==f['Jasmine'],Q==f['Poppy'],2*Q==R+U,S==Q-3,ab(U-f['Daisy'])==1,ab(V-f['Lily'])==3,f['Orchid']!=1,f['Orchid']!=7)
    dates=[f'{m} {day}' for m in ['May','June','July','August'] for day in [12,13]]
    p=new(6,35,39,8,labels=dates,orientation='Birth date');d=p.group('PQRSTUVW');P,Q,R,S,T,U,V,W=[d[x] for x in 'PQRSTUVW']
    p.add(Or(R==1,R==5),ab(R-Q)==3,Q<=6,V-1==8-R,T==P+1,(T-1)/2==(P-1)/2,ab(U-S)==4,U<S)

    p,d,total=variable_row(7,1,5,'BD FGHMPQ'.replace(' ',''));B,D,F,G,H,M,P,Q=[d[x] for x in 'BDFGHMPQ']
    p.add(ab(P-Q)==6,M==Q+3,Or(M==4,M==total-3),ab(H-M)==3,ab(B-H)==5,D==B-6,Or(D==3,D==total-2),G==F+4,Or(And(D<F,F<Q),And(Q<F,F<D)))
    p=new(7,8,12,8,labels=[f'{m} {day}' for m in ['January','April','July','September'] for day in [15,22]],orientation='Birth date');d=p.group('MNOPQRST');M,N,O,P,Q,R,S,T=[d[x] for x in 'MNOPQRST']
    p.add(Or(R==2,R==6),ab(R-N)==5,N<S,Q==S-3,M!=5,M!=6,S!=5,S!=6,M-1==8-Q,ab(M-T)==2,T<O,O<P)
    p=new(7,16,20,9,orientation='Box position, bottom to top');d=p.group('ABCDEFGHI','Box');A,B,C,D,E,F,G,H,I=[d[x] for x in 'ABCDEFGHI']
    p.add(ab(B-G)==6,E==G-1,ab(E-H)==4,I==H-1,I>D,Or(D==2,D==3,D==5,D==7),C>A,C!=9)
    p,d,f,r,near=circle(7,24,28,'ABCDEFGH',inside_count=4)
    p.add(r('E','A',2),f['A']==1,Or((d['E']-d['F'])%8==3,(d['F']-d['E'])%8==3),f['F']==0,ab(d['G']-d['C'])==4,~near('C','A'),r('H','D',3),f['D']==1,f['B']==f['E'],~near('B','F'))
    for a in d:
        for b in d:
            if a<b:p.add(If(And(near(a,'G'),near(b,'G')),f[a]==f[b],True))
    p=new(7,33,37,7,orientation='Left-to-right position');d=p.group('BCDEFGH');f=p.group(['Pink','Green','Red','Yellow','White','Blue','Grey'],'Colour');B,C,D,E,F,G,H=[d[x] for x in 'BCDEFGH']
    p.add(F==f['Yellow']+3,ab(f['Yellow']-f['White'])==4,ab(f['White']-D)==2,G==D-4,G==f['Red'],ab(f['Grey']-G)==1,F!=f['Grey'],ab(f['Grey']-H)==4,f['Green']==H-2,ab(f['Green']-B)==3,H!=f['Blue'],ab(C-G)!=1)

    p=new(8,1,5,6,orientation='Column, observer left to right');a=p.group('ABCDEF','North-facing row');b=p.group('PQRSTU','South-facing row');A,B,C,D,E,F=[a[x] for x in 'ABCDEF'];P,Q,R,S,T,U=[b[x] for x in 'PQRSTU']
    p.add(p.end(F),F==T,ab(C-F)==2,C==E-1,ab(R-C)==1,R==Q+2,Q!=1,Q!=6,B==A+2,B==P-1,2*S==Q+U,ab(Q-U)==2)
    p=new(8,6,10,10,orientation='Floor, bottom to top');d=p.group('JKLMNOPQRS');J,K,L,M,N,O,P,Q,R,S=[d[x] for x in 'JKLMNOPQRS']
    p.add(K%2==0,K!=2,K!=10,ab(K-J)==4,ab(O-K)==3,J>=8,P==O+1,M==S+1,N>K,N<M,M!=10,ab(R-Q)>3,Q%2==0)
    p,d,total=variable_row(8,12,14,'LOPQRSTU');L,O,P,Q,R,S,T,U=[d[x] for x in 'LOPQRSTU']
    p.add(P==Q+5,P==R-2,ab(R-T)==5,ab(T-U)==5,ab(O-R)==1,O==S+3,S>U,L==O+5,total-L==Q-2,total-O<=7)
    p,d,f,r,near=circle(8,15,19,'ABCDEFG',inside_count=7);items=p.group(['Car','Bike','Bus','Truck','Scooter','Bicycle','Jeep'],'Vehicle')
    p.add((d['C']-items['Truck']+3)%7==0,near('A','C'),r('A','E',-2),d['E']==items['Bus'],(items['Bicycle']-d['A']-1)%7==0,(d['D']-items['Bicycle']-2)%7==0,d['F']==items['Scooter'],r('F','B',-2),(items['Jeep']-d['G']-1)%7==0,d['G']!=items['Bike'])
    p=new(8,21,23,7,orientation='Competition rank, best first');d=p.group('LMNOPQR');L,M,N,O,P,Q,R=[d[x] for x in 'LMNOPQR']
    p.add(N==M-1,N>L,ab(L-Q)==3,O<P,P<L,Q<O,M!=7)
    years=[1988,1991,1993,1995,1999,2002,2007,2011]
    p=new(8,24,28,8,labels=years,orientation='Birth year, oldest first');d=p.group('JKLMNOPQ');J,K,L,M,N,O,P,Q=[d[x] for x in 'JKLMNOPQ']
    def yr8(x):return sum(If(x==i,y,0) for i,y in enumerate(years,1))
    p.add(yr8(Q)-yr8(P)==6,ab(Q-K)==3,yr8(J)-yr8(P)==2,ab(yr8(J)-yr8(O))==7,N<M,M<O)
    years=[1994,1996,1998,1999,2001,2002,2004,2005]
    p=new(9,1,5,8,labels=years,orientation='Birth year, oldest first');d=p.group('PQRSTUVW');P,Q,R,S,T,U,V,W=[d[x] for x in 'PQRSTUVW']
    def yr9(x):return sum(If(x==i,y,0) for i,y in enumerate(years,1))
    p.add(P<=2,ab(P-V)==3,Q==V-1,yr9(Q)%2==1,yr9(T)-yr9(R)==4,W<U,W==S+1)
    p=new(9,9,13,9,orientation='Box position, bottom to top');d=p.group('ABCDEFGHI','Box');A,B,C,D,E,F,G,H,I=[d[x] for x in 'ABCDEFGHI']
    p.add(G>=6,ab(G-H)==4,9-H==C-1,A==E+2,E==I+1,ab(F-H)!=1,B>D,B<E)
    p,d,total=variable_row(9,17,20,'ABCDFNQRUV');A,B,C,D,F,N,Q,R,U,V=[d[x] for x in 'ABCDFNQRUV']
    p.add(A==F-3,ab(F-R)==4,R==C-2,C==V-1,ab(U-V)==2,U>C,B==N-2,B==U+3,Q==D-3,D==A+1,ab(Q-R)-1==total-N+1,Q==1)
    p=new(9,27,31,7,orientation='Floor, bottom to top');d=p.group('MNOPQRS');f=p.group(['Italy','Canada','Germany','China','Spain','India','Brazil'],'Country');M,N,O,P,Q,R,S=[d[x] for x in 'MNOPQRS']
    p.add(S==f['Brazil']+2,Or(S==2,S==3,S==5,S==7),ab(S-f['Canada'])>3,N==f['Spain'],N==f['Canada']-3,O==f['Italy']+1,M-1==7-R,R==P-1,f['China']==f['India']+1)
    p,d,f,r,near=circle(9,36,40,'DEFGHIKL')
    p.add(r('H','K',3),f['H']==f['K'],ab(d['I']-d['K'])==4,f['I']!=f['K'],r('L','I',2),ab(d['F']-d['D'])==4,r('D','E',-2),r('G','D',3),~near('G','I'),~near('G','K'),f['L']==1,f['E']==1,f['G']==f['F'])
    for name in d:p.add(If(near(name,'E'),f[name]!=f['E'],True))
    p=new(10,6,10,8,orientation='Left-to-right position');d,f,r,near=facing_group(p,'BFGHKLMN',circular=False,inside_count=5)
    p.add(Or(d['M']==2,d['M']==7),r('G','M',3),r('G','H',-1),r('H','G',-1),ab(d['H']-d['N'])==4,f['N']==1,r('B','N',2),r('K','F',-4))
    for a in d:
        for b in d:
            if a<b:p.add(If(And(near(a,'F'),near(b,'F')),f[a]==f[b],True))
    months=['January','February','March','April','May','June','July']
    p=new(10,16,20,7,labels=months,orientation='Teaching month');d=p.group('ABCDEFG');f=p.group(['philosophy','humanities','science','medicine','commerce','journalism','pharmacy'],'Subject');A,B,C,D,E,F,G=[d[x] for x in 'ABCDEFG']
    p.add(f['science']==5,Or(B==2,B==4),B<f['science'],F==f['journalism']-4,ab(F-A)==3,A!=6,D==f['medicine'],D==G+1,f['humanities']<f['pharmacy'],f['pharmacy']<C,Or(f['commerce']==1,f['commerce']==3,f['commerce']==5,f['commerce']==7))
    p=new(10,27,31,10,orientation='Floor, bottom to top');d=p.group('ABE MOPQSUW'.replace(' ',''));A,B,E,M,O,P,Q,S,U,W=[d[x] for x in 'ABEMOPQSUW']
    p.add(P>=8,ab(P-B)==6,S==B+1,10-E==S-1,M==A+3,ab(M-W)==3,U>O,U<Q)
    years=[1990,1996,1998,2002,2006,2008,2014]
    p=new(10,36,40,7,labels=years,orientation='Birth year, oldest first');d=p.group('MNOPQRT');M,N,O,P,Q,R,T=[d[x] for x in 'MNOPQRT']
    def yr(x):return sum(If(x==i,y,0) for i,y in enumerate(years,1))
    p.add(yr(R)-yr(T)==4,yr(Q)-yr(P)==2,ab(Q-M)==3,2023-yr(N)!=9,2023-yr(N)!=25)
    return models


def solve_all():
    explanations={}
    for puzzle in build_models():
        result=puzzle.solve()
        print('Puzzle',puzzle.paper,puzzle.questions,result['status'] if result else 'unresolved',flush=True)
        if result:
            orientation=puzzle.orientation.lower()
            result['topic']=('Puzzle (Box / Stack)' if 'box' in orientation else
                'Puzzle (Floor / Flat)' if 'floor' in orientation or 'flat' in orientation else
                'Seating Arrangement (Circular)' if 'clockwise' in orientation else
                'Seating Arrangement (Linear / Parallel)' if 'left-to-right' in orientation or 'column' in orientation else
                'Order & Ranking' if 'rank' in orientation else 'Puzzles & Seating Arrangement')
            for number in puzzle.questions:
                explanations[f'adda-{puzzle.paper:02}-q{number:03}']=result
    return explanations


if __name__=='__main__':
    import json
    from pathlib import Path
    output=solve_all()
    p=Path(__file__).resolve().parents[1]/'artifacts/reasoning-repair'
    p.mkdir(parents=True,exist_ok=True)
    (p/'puzzle-explanations.json').write_text(json.dumps(output,indent=2),encoding='utf-8')
    print('Verified arrangement explanations:',len(output))
