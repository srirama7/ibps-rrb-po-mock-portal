"""Checked deductions for the three searchable source papers (2022/2023).

Answer letters below are conclusions of the calculations and explicit clue
models, not imports from the publisher keys. Multiple-model questions are
excluded rather than resolved by assuming extra clues.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
from audit_previous_models import all_models
MODELS={model.name:model.solve() for model in all_models()}

def build():
    out={}
    def paper(stamp, letters, math_notes):
        pid='prepp-'+stamp;rows={}
        assert len(letters.split())==80,(stamp,len(letters.split()))
        for n,letter in enumerate(letters.split(),1):
            rows[str(n)]={'answerIndex':None if letter=='-' else 'ABCDE'.index(letter),'status':'excluded' if letter=='-' else 'verified','explanation':''}
        for n,text in enumerate(math_notes.split('|'),41):rows[str(n)]['explanation']=text.strip()
        assert len(math_notes.split('|'))==40,(stamp,len(math_notes.split('|')))
        out[pid]=rows
        return rows
    a=paper('2022-08-20-shift-1', '''A D D D D B E A - B C A B C A D C A B C E D D A A A - - - - D A - E B C - - - D
        C D - A D C B D A D D B D C E D C E C C B C A A D C E D B A C D A B C E A A C A''',
    '''Approximate sqrt(168.99) as 13, 10.01 as 10, 2.99 as 3 and 7.04 as 7. Then 130 - 3x = 49, so x = 27.
    |864/4 + (38/19)x110 = 216 + 220 = 436.
    |The publisher obtains 47 by rounding both 13.48 and 13.33 to 13 before multiplying. Direct evaluation gives 36.95243285, whose nearest listed choice is 32. Because the source does not specify a rounding method and these approaches select different choices, this item is excluded from scoring. The computed value is approximately 36.95.
    |Cube root of 64 is 4; 4x125 + 407/11 = 500+37 = 537.
    |Using nearby integers: (23+17)/2 x4 -48+644 = 676.
    |x roots: 4, 5. y roots: 6, 7. Every x is less than every y: x < y.
    |y roots: 2, 3. x roots: 1, -2.5. Every x is less than every y: x < y.
    |x roots: 1/5, 1/2. y roots: 1/7, 1/5. Thus x >= y; equality is possible.
    |x roots: 1/3, 2. y roots: 5/2, 3. Thus x < y.
    |x roots: 7, 12. y roots: 12, 13. Thus x <= y; equality is possible.
    |The graph gives demand P = 2000 and production R = 3000. 2000/3000 x100 = 66 2/3 percent.
    |Demand exceeds production at P and R (2 companies). Production exceeds demand at Q, S and T (3). Ratio 2:3.
    |Production Q = 3600; demand S = 2200. 3600/2200 x100 = 163.636 percent, approximately 164 percent.
    |Production values P through T are 1500, 3600, 3000, 4400, 4500. Sum 17000; average 3400.
    |Production P+T = 1500+4500=6000. Demand R+Q = 4500+2700=7200. The difference is 1200, which is absent: None of these.
    |Subtract 10, 15, 20, 25, 30, 35 successively. The final term should be -55; -50 is wrong.
    |Terms follow n^3+n^2-1 for n=1 through 6: 1,11,35,79,149,251. The wrong term is 124, which should be 149.
    |Terms follow n^3-n^2 for n=1 through 7: 0,4,18,48,100,180,294. The wrong term is 177.
    |Subtract successive prime squares 4,9,25,49,121. The second term should be 357, not 355.
    |Multiply by 7,6,5,4,3,2 and add their squares. 91x6+36 = 582, so 584 is the wrong term; the following terms then match.
    |For two years, CI-SI = P r^2 = 18000 x0.15^2 = 405 rupees.
    |Capital-months: Amit 20000x12=240000; Trisha 25000x7=175000. Ratio 48:35 divides 83000 into 48000 and 35000.
    |New area factor = 1.10x0.80 = 0.88. Area decreases by 12 percent.
    |Initially milk=50 L and water=10 L. After additions: milk=60 L, water=15 L. Ratio 4:1.
    |New total weight = 40x52 -3x20 +5x25 = 2145 kg. New count 42; average = 2145/42 = 51 3/42 kg.
    |Total students = 2800+2500+1900+3200 = 10400.
    |Bachelor students in D = 3200x40%=1280. Relative to all students in B: 1280/2500 x100 = 51.2 percent.
    |Bachelor counts B=875, C=950, D=1280. Total = 3105.
    |Masters B+C = 1625+950=2575. Bachelors A+C = 1540+950=2490. Difference = 85.
    |A+C = 4700; B+D = 5700. Ratio = 47:57.
    |Let current ages be 14k,17k. (14k+6)/(17k+6)=17/20 gives k=2. Ramesh is 34 years old.
    |Upstream speed=4, downstream speed=8 km/h. d/4-d/8=3 gives d=24 km each way; total distance=48 km.
    |Train A speed=270/30=9 m/s. Combined length=9x90=810 m, so B length=810-270=540 m.
    |C's filling rate=1/6-1/9=1/18 tank/h. Three hours fills half the tank; C fills the remaining half in 9 hours.
    |A works t-3 days, B t days, C 4 days. (t-3)/20+t/40+4/60=1 gives t=130/9=14 4/9 days.
    |IT: males 700, females 500. Finance: males 800, females 700. Medical: males 850, females 950. Ratio IT males:Medical females = 700:950 = 14:19.
    |Medical females + Finance males = 950+800 = 1750.
    |IT + Finance employees = 1200+1500 = 2700. 2700/4500 x100 = 60 percent.
    |Medical employees = 4500-1200-1500=1800. Difference from Finance = 1800-1500 = 300.
    |Medical employees : males in IT+Finance = 1800:(700+800) = 6:5.''')
    def notes(rows,mapping):
        for n,text in mapping.items():rows[str(n)]['explanation']=text
    def arrangement(rows,start,end,model):
        solutions=MODELS[model];assert len(solutions)==1,model
        text='Applying all the stated clues gives the unique arrangement: '+json.dumps(solutions[0],ensure_ascii=False)+'.'
        for n in range(start,end+1):rows[str(n)]['explanation']=text
    arrangement(a,1,5,'2022_circle');arrangement(a,8,12,'2022_meetings');arrangement(a,16,20,'2022_south_row')
    notes(a,{
        6:'The qualifying index pairs in REFRIGERATOR are (2,3), (5,11), (8,10), (8,11), (10,12), counting from 1. There are five pairs.',
        7:'The selected letters of REACTION are C, I, O, N. Both COIN and ICON can be made, so there is more than one word: Y.',
        9:'The supplied PDF omits the Q9 heading and question prompt. Page 3 contains options and a key only. Excluded from scoring.',
        10:'The date order is F,A,C,E,G,B,H,D (Jan13, Jan22, Apr13, Apr22, May13, May22, Jul13, Jul22). E-B is the only pair drawn from different months; the other four pairs share a month.',
        13:'A is the mother, C the father, E the maternal aunt, and F the only son. B is married to D, so F is D\'s brother-in-law.',
        14:'B is a daughter of A and is married to D. Under the family relationships in the question, D is A\'s son-in-law.',
        15:'A and G share the female gender; E is A\'s sister. G is E\'s niece.',
        16:'South-facing positions from physical left to right: T=1,S=6,P=8,Q=10,R=12,V=13,U=17, with 17 seats. A is midway between S and P at 7. R is five places to A\'s left as viewed facing south.',
        19:'U occupies position 17, the left end when viewed by the south-facing occupants; T occupies the other end.',
        21:'G > H does not establish F > H, since F <= G. G < E is false because E < F <= G. Neither conclusion follows.',
        22:'S <= L <= I=P gives P>=S. I=P>E>R gives I>R. Both conclusions follow.',
        23:'T=I<=S<=M, so T<=M. Exactly one of T<M and T=M holds. Either conclusion follows.',
        24:'D>E>F>G proves D>G. E=G is false. Only I follows.',
        25:'J>=L>A=N proves J>N. K and J are not ordered by the given chains. Only I follows.',
        26:'In every arrangement allowed by the literal box clues, U=1, Q=2, T=6, X=8, R=10. Thus U is definitely at the top.',
        31:'From Shaan to the house the displacement is 30 km east and 9 km south. Distance=sqrt(30^2+9^2)=3 sqrt(109) km.',
        32:'The market-to-Karan displacement is 24 km west and 10 km south. Distance=sqrt(24^2+10^2)=26 km.',
        33:'The statements say No Cup is Spoon but also Some Plates are Cup and spoon. On the literal shared-object reading these contradict each other. The source wording does not supply a consistent set model; excluded rather than treating a contradictory premise as a valid proof.',
        34:'Some White is Blue proves some Blue is White. Only-few Black is White includes some Black that are White, proving some White is Black. Both conclusions follow.',
        35:'Some Grapes are Oranges converts to some Oranges are Grapes. No link forces Apples and Mangoes to intersect. Only II follows.',
        36:'All five arrangements permitted by the literal colour clues give V the colour Pink. The answer is definite even though the whole arrangement is not unique.',
        40:'All five arrangements permitted by the literal colour clues place T in position 2 with Purple. Hence T-Purple is the true option.'})
    box_note='The source does not explicitly make P immediately between V and S, or Q immediately above V. The literal clues permit 12 arrangements. For example, top-to-bottom U,Q,V,P,S,T,W,X,Y,R and U,Q,V,P,W,T,S,X,Y,R both satisfy them, but give different answers. The publisher key selects one without a sufficient clue; excluded.'
    for n in [27,28,29,30]:a[str(n)]['explanation']=box_note
    colour_note='The source allows five arrangements. Two valid left-to-right examples are R(Yellow),T(Purple),U(Green),P(Blue),V(Pink),S(Orange),Q(Red), and R(Yellow),T(Purple),V(Pink),S(Blue),U(Green),P(Orange),Q(Red). The requested result differs between valid arrangements; excluded.'
    for n in [37,38,39]:a[str(n)]['explanation']=colour_note
    b=paper('2023-08-05-shift-1', '''A D C E D E D A B E C A C B B D A D A A C D C B D E E B E A D A C E C C D B C B
        E E E C A E A A D E D B E D A B D B E D C E D B A C A C E D D B C B A D E C C B''',
    '''1.25x120 +0.5x460 -21/7 -2.5x180 = 150+230-3-450 = -73.
    |(14x4+0.40x240-0.30x120)/10 = (56+96-36)/10 = 11.6.
    |sqrt(256)-sqrt(169)x7+18x10+140-12 = 16-91+180+140-12 = 233, absent from the numeric choices: None of these.
    |140+2x=600, so x=230.
    |0.42x550 +0.63x400 -15x7 = 231+252-105 = 378.
    |Payment shares are proportional to work rates 1/20:1/30 = 3:2. B gets 2/5 of 6300 = 2520 rupees.
    |Let ages 15 years ago be 4k and 5k. (4k+20)/(5k+20)=13/15 gives k=8. Present ages=47,55; sum:difference=102:8=51:4.
    |After additions, total=570 L and water=570x10/19=300 L. Initially water=300-53=247 L.
    |420=P x0.20^2 gives P=10500. Required SI=10500x0.25x3=7875 rupees.
    |y roots: 14,-8; x roots: 5,-8. Some comparisons are greater, some smaller, and equality is possible; no single relation.
    |x roots 12,13; y roots 11,12. Every x>=every y, with equality possible: x>=y.
    |x roots 4,5; y roots 12,15. Thus x<y.
    |x roots 11,-6; y roots -5,-7. The ordering changes between root combinations; no single relation.
    |x roots 5,9; y roots 5,-6. Thus x>=y, including possible equality.
    |Statement I gives speed=360/24=15 m/s. Statement II supplies neither train nor platform length. I alone is sufficient.
    |The area increase 0.4Lb=200 gives original area Lb=500, not its perimeter. Statement II adds L=1.4b, fixing both dimensions. II alone is sufficient with the stem; I merely repeats a rectangle property.
    |Together the statements determine speeds and the combined length 9x18=162 m, but do not separate the two train lengths. Their length difference remains unknown.
    |(244+232)/(108+120)x100 = 208.77193 percent, approximately 208.77 percent.
    |Occupied rooms A=72,D=96,E=84. Average=(72+96+84)/3=84.
    |Unoccupied A+C=198; B+D=280. Percentage less=(280-198)/280 x100=29.2857 percent. The listed 29.28 percent is the intended truncated approximation.
    |Occupied C+D=56+96=152. Total A+E=162+204=366. Ratio=152:366=76:183.
    |Weighted cost=(90x7200+72x9000)/162=8000 rupees per room.
    |The squares should be those of primes 23,29,31,37,41,43. 1089=33^2 is wrong; 37^2=1369 belongs there.
    |Successive multipliers are 0.5,1.5,2.5,3.5,4.5. 585x3.5=2047.5, not 2049.5; 2047.5x4.5=9213.75.
    |From the second term onward multiply by 2,3,4,5. The first multiplier is 1, so the first term should be 25, not 12.
    |Terms are 2^3+2, 3^3+4, 4^3+8, 5^3+16, 6^3+32, 7^3+64 = 10,31,72,141,248,407. Thus 412 is wrong.
    |Subtract 8,16,24,32,40,48. The fourth term should be 264 rather than 266.
    |A capital-months=72000; B=108000; C=6c. C receives 18900/50400=3/8, so 6c/(180000+6c)=3/8 gives c=18000.
    |Successive selling prices: 800x1.10=880 and 880x1.05=924 rupees.
    |Let ages be 9k,5k. 45k^2=1125 gives k=5. Five years later the ratio is 50:30=5:3.
    |Closing speed=(28+current)+(37-current)=65 km/h. Time=455/65=7 hours.
    |Combined length=790 m. Relative speeds=15 and 45 m/s. Time sum=790/15+790/45=70.2222 s; 70.23 is the closest listed option.
    |The chart gives veg P=45,Q=105,R=140,S=75,T=80 and non-veg P=125,Q=90,R=20,S=100,T=55. Required ratio=135:150=9:10.
    |Restaurants R=160, S=175. Difference percentage=15/175 x100=8.5714 percent less.
    |Veg X=80x0.60=48. X+S+T=48+75+80=203.
    |Non-veg Q+R+S=90+20+100=210. Average=70.
    |Cafes P=220-(45+125)=50; S=90. Their total 140 is below non-veg P+S=225 by 85/225 x100=37.7778 percent.
    |Correct total weight=60x46-44+28=2744 kg. Mean=2744/60=45.7333 kg.
    |h=2r gives curved surface=2 pi r h=4 pi r^2=4x154=616 cm^2.
    |Drain rate=1/25+1/30-1/25=1/30 reservoir per minute. Emptying time=30 minutes.''')
    for lo,hi,name in [(1,5,'2023s1_floors'),(10,14,'2023s1_countries'),(16,20,'2023s1_circle'),(36,40,'2023s1_births')]:arrangement(b,lo,hi,name)
    notes(b,{
        5:'Floors: F1,I2,C3,G4,A5,D6,H7,B8,E9. G-I, H-A, B-D and E-H all differ by two floors; A-G differs by one. Thus A-G is the odd pair.',
        6:'D=F and D<C give C>F, which implies C>=F: I follows. B>C>F proves II. Both conclusions follow: E. The publisher key B incorrectly omits I.',
        7:'E=Q=Y<=D and P<=D do not compare E with P. Q>D is not possible. Neither follows.',
        8:'Z>T>=U>=R=Q gives Q<Z, so I follows. U>=T is not guaranteed. Only I follows.',
        9:'F=A<=U<L gives F<L; D>=E>F=A gives D>A. Both conclusions follow.',
        12:'From bottom to top: J(Vietnam),P(Brazil),L(Poland),N(Hungary),M(Spain),K(Denmark),O(Finland). M-Denmark is separated by one position; the other named pairs are separated by two.',
        15:'The repeated words are are and mouse, and their shared codes are gu and du. Their individual mapping cannot be separated: either gu or du.',
        21:'The new number is 6957205. Only the digit 5 is repeated, so one distinct digit repeats.',
        22:'EHL, PSW, ILP and GJN use alphabet jumps +3,+4. RUX uses +3,+3 and is the odd group.',
        23:'Some actions are movies and every movie is drama, proving some actions are drama. Other actions may be fiction, so only I follows.',
        24:'Keyboards can overlap monitors outside the laptop set, so I is possible. Every laser is a keyboard and no keyboard is a laptop, proving II. Both follow.',
        25:'Some cylinders exist and no rich is a cylinder, so making all cylinders rich is impossible. No statement links rich with simple. Neither follows.',
        26:'Some pans are spoons, and no spoon is a plate, so all pans cannot be plates. Bowls need not intersect spoons. Neither follows.',
        27:'The unique named positions are A3,H8,D11,G13,F15,J19,B22,C25 in a 28-seat north-facing row. Five places right of A is H.',
        28:'There are 28 seats. K third from the right occupies 26; four places to its left is 22, occupied by B.',
        29:'H8,G13,D11,F15,B22,C25,J19,A3. Two sit between H and D, so three sit to the right of C25, giving 28 seats.',
        30:'Take D=(0,0); C=(6,0), E=(0,-8). Distance C-E=sqrt(6^2+8^2)=10 m.',
        31:'D=(0,0), E=(0,-8), F=(16,-8), G=(16,1), H=(23,1), I=(23,-1). I is southeast of D.',
        32:'respect=za, must=la, elders=sa, we=na, be=da. Hence da means be.',
        33:'we=na, must=la, respect=za, elders=sa. The listed code la na za sa is the matching set.',
        34:'After must=la and respect=za, the codes ga and ka remain for old and rules. Neither individual mapping is fixed.',
        35:'The added sentence gives old=ga, leaving rules=ka.',
        36:'The unique birth years are U1961,Q1966,S1969,P1972,V1977,R1979,W1985,T1994. T-1961 is the mismatched pair.'})
    c=paper('2023-08-05-shift-2', '''D E D C B A C A B C E A D B A A B C A A E E D - - - D D C E D D E E B B B A E C
        C B A B C C A C C B - C C D B A C D C B A B E E D E D B A B E C E A B A C E D B''',
    '''Females A=360,B=560,C=1080,D=880; average=720. E females=800; with M:F=17:16, E males=850 and total=1650.
    |Senior females in C=0.75x1080=810. Senior males=1170-810=360. Ratio=360:810=4:9.
    |D males=1320; females=880. Required sum=(5/6)x1320+(1/11)x880=1100+80=1180.
    |C males above 40=720/2=360. C females below 40=1080/8=135. Difference=225.
    |A male officers=(4/7)x840=480. A female officers=(5/6)x360=300. Total officers=780.
    |Successive differences should be 5,7,10,15,22,33, whose increases are successive primes 2,3,5,7,11. Thus 306 should be 304.
    |Multiply by 1,2,3,4,5,6 and add the same integer. The second term should be 33, not 30: 32x1+1=33, 33x2+2=68.
    |Alternate subsequences should be 56,47,38,29 and 35,26,17, decreasing by 9. The wrong term is 50, which should be 47.
    |Add squares of consecutive even integers 4,16,36,64,100,144. The second term should be 18, not 20.
    |Add 2^2,3^3,4^2,5^3,6^2,7^3 = 4,27,16,125,36,343. Thus 211 should be 212.
    |The source chart gives males Monday=280 and Thursday=200; females Tuesday=360-140=220 and Wednesday=500-320=180. The ratio is 480:400=6:5. No offered choice is 6:5; publisher choice C (8:5) is wrong. Excluded from scoring.
    |Thursday males=200, females=640-200=440. Friday males=250,females=500; difference=250.
    |30 percent of Wednesday total 500 is 150. Of these 40 are male, so 110 are female.
    |(5/7)x140=100; (6/9)x180=120. Difference=20.
    |Monday unmarried males=280x4/7=160. Tuesday unmarried females=220x3/11=60. Total=220.
    |A-8=3(B-8) and A+4=2(B+6) give A=56,B=24. C=(56+24)/2-6=34 years.
    |One man works 1/80 of the job daily; one woman 1/288. Ten men finish half in 4 days. Together with 12 women the rate is 1/8+1/24=1/6; the remaining half takes 3 days. Total=7 days.
    |Simple-interest amount=20500x(1+0.20x4)=36900. Two-year CI=36900x(1.10^2-1)=7749.
    |Relative speed=(90+144)/3.6=65 m/s. Combined length=65x9=585 m, so second train length=105 m. At 40 m/s, crossing a platform in 8 s covers 320 m, so platform=215 m.
    |Charged price factor=1.5x0.75x1.10=1.2375 of cost. Thus 0.2375xCP=85.5 and CP=360 rupees.
    |Treat 33.33 percent as the intended one-third. After removing 54 L, mixture=126 L and water=42 L. 42/(126+x)=1/4 gives x=42 L.
    |x roots:1,5. y roots:5,16. Thus x<=y, with equality possible.
    |x roots:-16,-23. y roots:-17,-25. Different combinations reverse the ordering; no single relation.
    |x roots:17,6/5. y roots:17,11/7. Different combinations reverse the ordering; no single relation.
    |x roots:3/10,3/5. y roots:3/5,4/5. Thus x<=y, with equality possible.
    |x roots:8,-5.5. y roots:7.5,-7. Different combinations reverse the ordering; no single relation.
    |Let savings be 5k and 3k. A income=5k/0.6=25k/3, expenditure=10k/3. B expenditure=20k/3, income=29k/3. Income ratio=25:29.
    |A-5=B+5 gives A=B+10; C+10=B+10 gives C=B. Hence 2B+10=450, so B=220.
    |Statement I gives 0.8V(1-10/V)(1-5/V)=28.8, or (V-50)(V-1)=0. Only V=50 L is physically possible. I alone determines capacity. Source caveat: replacing 45 percent twice in II leaves 0.8x0.55^2=24.2 percent alcohol, not its stated 51.5 percent; II is arithmetically defective and cannot determine capacity.
    |I leaves train B's length unknown, so its speed is unknown. II gives speeds 125 and 75, ratio 5:3. Thus II alone is sufficient. Source caveat: I's A speed 30 m/s conflicts with II's 125 m/s if both describe the same train.
    |Integer approximation: 80x[12x(25-16)]/(9x5)=192. As a percentage of 434 this is 44.24 percent, so the closest choice is 44.
    |Approximate 259/[25+4x(33/(22/2))]=259/37=7. Thus ?-65=7 and ?=72.
    |Integer approximation gives 455-230+?^2 = 15^2+27x180/21. Hence ?^2 about 231.43 and ? about 15.21, closest to 15.
    |Approximation: 75-3x(40/8/0.5)/(9/3)+16=81.
    |Approximation: (460/20)x9+7^2+25-15=266.
    |D/4=v-2 and (D-2)/3=v+2 give D=56 km, upstream speed=14 km/h. In 3 h the upstream distance is 42 km.
    |Raja capital-months=3kx4+1.5kx8=24k. Tulsi=5kx12=60k. Tulsi gets 5/7 of 16800 = 12000 rupees.
    |Probability=C(22,1)xC(12,3)/C(34,4)=4840/46376=55/527.
    |External gap gives R+r=15-4.5=10.5; R-r=3.5. Thus R=7 cm; using pi=22/7, area=154 cm^2.
    |Even sum=126; two largest total=90, so smallest even=36. Odd sum=117; two largest total=88, so smallest odd=29. Difference=7.''')
    arrangement(c,1,5,'2023s2_floors');arrangement(c,10,14,'2023s2_row');arrangement(c,36,40,'2023s2_seminars')
    notes(c,{
        6:'Y<=W<K<N proves Y<N; M<=K<N proves M<N. Both conclusions follow.',
        7:'Treat the numeric labels as relationship symbols, as the question instructs. 22>20>=12>15>13>6 proves 22>6, and 2>4>=20>=12>15>13 proves 2>13. Both follow.',
        8:'A=B>C=D proves A>D. C=D<F<G rules out C>G. Only I follows.',
        9:'W<X and W<V do not order X and V. O<=T<V<U<=S gives O<S. Only II follows.',
        15:'Intersect the three sentences containing good: st is their common code, so good=st.',
        16:'The two common words good/player share st/pu. Since good=st, player=pu.',
        17:'siya=gu and good=st, player=pu, so the remaining code ri means is.',
        18:'The last sentence identifies siya=gu but leaves sing, very, nice matched to vx, ym, nr in an unknown order. Nice can be vx, ym, or nr.',
        19:'Comparing the second and third sentences leaves time=jt after good=st is resolved.',
        20:'Some A are B and every B is C, so some C are A (II). There is no restriction preventing all D from being A (I is possible). No overlap between B and D is forced (III does not follow). I and II follow.',
        21:'Some Clerks can be Nurses is a permissible overlap. II (no Engineers are Doctors) and III (some Engineers are Doctors) are complementary, so exactly one holds. The best listed option E identifies that either/or pair; its wording omits the additional valid possibility in I.',
        22:'Only-few cinema are hall means some cinema are hall and some cinema are not hall. It does NOT say some hall are not cinema. Counterexample: Hall={a}, Cinema={a,b}, Movie={a}, TV={b}. All hall can be cinema, and TV can overlap cinema outside hall. Neither I nor II follows: E, correcting the publisher A.',
        23:'It is possible for every woman to be a man while some men are not women. Some police are women and no police is a thief, proving some women are not thieves. Both follow.',
        27:'All three arrangements satisfying the literal age clues give J age 53, born in 1970. This answer is definite despite the incomplete overall arrangement.',
        28:'All three arrangements satisfying the literal age clues give P age 40. Thus D is definite.',
        29:'Only the E-G pair at positions 1 and 3 in EAGERNESS has matching word/alphabet spacing. There is one pair.',
        30:'Letters 3,7,10 of GOVERNMENT are V,M,T. No ordinary 3-letter English word can be made: X.',
        31:'Coordinates: A=(0,0), B=(10,0), C=(10,-8), D=(4,-8), E=(4,-16), F=(10,-16). D lies southwest of B.',
        32:'A-to-C displacement=(10,-8). Shortest distance=sqrt(100+64)=sqrt(164) m.',
        33:'From C=(10,-8) to A=(0,0), travel west and north: northwest.',
        34:'CLIPBOARD becomes BKJOAPBQC. Q is at position 8; four places left is position 4, O.',
        35:'Increasing the prime digits 2,3,5,7 by 1 gives 88843649368. Only 9 appears once; the other digits repeat.'})
    age_note='The literal age clues allow three models. One has J53,K63,L37,M16,N27,O42,P40; another has J53,K37,L16,M42,N27,O63,P40. Both satisfy every stated age sum, difference and parity clue but give different requested answers. Excluded because the publisher key assumes an unstated restriction.'
    for n in [24,25,26]:c[str(n)]['explanation']=age_note
    assert all(len(rows)==80 and all(r['explanation'] for r in rows.values()) for rows in out.values())
    return out

if __name__=='__main__':
    result=build();(ROOT/'tools/prepp_cache/audit/derived_old_answers.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');print('Audited',sum(map(len,result.values())),'older-paper questions')
