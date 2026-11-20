"""Create explicit editorial practice repairs; never claim recovered source text."""
import json
from pathlib import Path
import re
from audit_scanned_answers import parse

ROOT=Path(__file__).resolve().parents[1]

def build():
    bank=json.loads((ROOT/'data/previous/catalog.json').read_text(encoding='utf-8'))
    papers={}
    def add(pid,n,stem,options,letter,explanation,change,context=''):
        assert len(options)==5
        papers.setdefault(pid,{})[str(n)]={'title':'Repaired practice question',
            'change':change,'context':context,'stem':stem,'options':options,
            'answerIndex':'ABCDE'.index(letter),'explanation':explanation}
    for paper in bank['papers']:
        if paper['id'].startswith(('prepp-2022','prepp-2023')):continue
        questions=parse(ROOT/'tools/prepp_cache/audit/tesseract'/paper['id'])
        old=paper.get('preRepair',paper)
        for n in old['excludedQuestions']:
            q=questions[int(n)];options=[re.sub(r'^[}\s]+','',o) for o in q['options']]
            male='only son' in q['stem']
            stem=('A man points to a photograph and says, "Arjun is the son of my father\'s only son." How is Arjun related to the man?' if male else
                  'A woman says, "Nisha\'s mother is the only daughter of my mother." How is the woman related to Nisha?')
            answer='Son' if male else 'Mother';index=next(i for i,v in enumerate(options) if v.lower()==answer.lower())
            proof=('The speaker is explicitly a man, so his father\'s only son is the speaker himself. Arjun is therefore his son.' if male else
                   'The speaker is explicitly a woman and her mother has only one daughter, so that daughter is the speaker. Nisha\'s mother is the speaker herself: Mother.')
            add(paper['id'],int(n),stem,options,'ABCDE'[index],proof,
                'Editorial rewrite: the speaker\'s gender is explicit and neutral example names replace the ambiguous source names. The relationship options stay in their original order.')
    pid='prepp-2022-08-20-shift-1'
    meeting='Eight people attend meetings on Jan 13, Jan 22, Apr 13, Apr 22, May 13, May 22, Jul 13 and Jul 22. Two people attend between A and G. The number before D equals the number after F. C attends on Apr 13. At least three people attend between C and H. A attends on an even-numbered date before G. Two people attend between F and E.'
    add(pid,9,'Which of the following statements is FALSE?',[
        'G attended the meeting in May.','Three people attended between A and B.',
        'D attended in a month with 31 days.','C attended exactly one month after F.',
        'G attended immediately before B.'],'D',
        'The chronological order is F,A,C,E,G,B,H,D. F attends Jan 13 and C Apr 13, which is three months later, not one. A, B, C and E are true, so D is the unique false statement.',
        'Editorial reconstruction: supplies the absent prompt and replaces the ambiguous meta-option "All are true" with a specific true statement. This is new practice wording, not recovered original text.',meeting)
    boxes='Ten boxes occupy positions 1 (top) to 10 (bottom). Two boxes are between Y and T. R is at the bottom. Three boxes are between Q and T. P is immediately between V and S. The number between R and X equals the number between X and T. X is at position 8. Q is immediately below U and immediately above V. W is not at an even position.'
    box_proof='The clarified clues give one top-to-bottom order: U,Q,V,P,S,T,W,X,Y,R. '
    box_questions={
      26:('Which box is at the top?',['U','T','W','V','Q'],'A','U is at position 1.'),
      27:('Which box is at position 5?',['U','T','Q','S','V'],'D','S is at position 5.'),
      28:('Which box is between T and X?',['Q','W','Y','P','S'],'B','T is at 6 and X at 8, so W at 7 is between them.'),
      29:('What is the position number of W?',['Five','Six','Four','Two','Seven'],'E','W is at position 7.'),
      30:('U is related to V and P is related to T by moving down two positions. In the same way, W is related to which box?',['S','R','T','X','Y'],'E','Moving two positions down from W at 7 reaches Y at 9.')}
    for n,(stem,options,key,proof) in box_questions.items():
        add(pid,n,stem,options,key,box_proof+proof,
            'Editorial clarification for Q26-Q30: P is immediately between V and S; Q is immediately above V. Q30 also states the analogy rule explicitly.',boxes)
    add(pid,33,'Which conclusions follow? Statements: No Cup is a Spoon. Some Spoons are Tiffin and some Spoons are not Tiffin. Some Plates are Cups. Some Plates are Spoons. Conclusions: I. All Plates are Tiffin. II. Some Tiffin are Spoons.',[
        'Only conclusion I follows.','Only conclusion II follows.','Either I or II follows.',
        'Neither conclusion follows.','Both conclusions follow.'],'B',
        'Some Spoons are Tiffin converts to some Tiffin are Spoons, proving II. Nothing makes every Plate a Tiffin. The two Some Plates statements may refer to different plates, so the premises are consistent.',
        'Editorial clarification: separates the contradictory "Some Plates are Cup and spoon" into two existential statements and expands "only few" explicitly.')
    colours='P,Q,R,S,T,U,V sit in a row facing north, each with a different colour: Blue, Red, Yellow, Pink, Green, Purple, Orange. Four people sit between T and Red, and Red is at an end. R likes Yellow and sits immediately left of T. Two people sit between R and Blue. Neither P nor Q is adjacent to Blue. P is not at an end. U likes Green and is adjacent to P. One person sits between U and Pink. S does not like Pink. T does not like Orange. Q does not like Blue. Additional clue: P does not like Blue.'
    colour_proof='The unique left-to-right order is R(Yellow), T(Purple), V(Pink), S(Blue), U(Green), P(Orange), Q(Red). '
    colour_questions={
      36:('Which colour does V like?',['Purple','Orange','Pink','Blue','None of these'],'C','V likes Pink.'),
      37:('Who likes Orange?',['T','Q','S','P','None of these'],'D','P likes Orange.'),
      38:('How many people sit between R and the person who likes Green?',['4','3','5','1','None of these'],'B','R is at 1 and U (Green) at 5; three people are between them.'),
      39:('Who sits immediately between S and P?',['U','R','V','T','None of these'],'A','S is at 4 and P at 6, with U at 5.'),
      40:('Which pairing is correct?',['Q - Orange','P - Red','S - Pink','T - Purple','None of these'],'D','T likes Purple.')}
    for n,(stem,options,key,proof) in colour_questions.items():
        add(pid,n,stem,options,key,colour_proof+proof,
            'Editorial addition for Q36-Q40: P does not like Blue. This removes the five-way ambiguity. Q39 explicitly asks for the person immediately between S and P.',colours)
    add(pid,43,'Round each decimal input to the nearest whole number FIRST, then evaluate: 936.43 / 13 / 3.99 x 12 - 13.48 x 13.33.',[
        '47','64','50','23','32'],'A',
        'The instruction fixes the rounding order: 936.43->936, 3.99->4, 13.48->13, 13.33->13. Evaluate left-to-right multiplication/division: 936/13/4 x12 -13x13 =216-169=47.',
        'Editorial clarification: explicitly requires integer rounding before calculation, making the intended answer uniquely reproducible.')
    pid='prepp-2023-08-05-shift-2'
    ages='J,K,L,M,N,O,P were born in 1960,1970,1981,1983,1986,1996,2007, in an unknown order. Calculate ages in 2023. L and O have a combined age of 79. The O-M age gap equals the L-K age gap. O is older than M. J and N have a combined age twice P\'s age. M\'s age is even. J is not younger than N. Additional clue: M is older than P.'
    age_proof='The unique ages are O63,J53,M42,P40,K37,N27,L16; birth years are O1960,J1970,M1981,P1983,K1986,N1996,L2007. '
    age_questions={
      24:('Which statement is true?',['Only two people are older than P.','N is younger than L.','O is the oldest person.','J was born in 1993.','K has an even age.'],'C','O is the oldest.'),
      25:('How many people are older than K?',['Four','One','Five','Two','Three'],'A','O,J,M,P are older than K: four.'),
      26:('Who is immediately younger than N?',['J','K','O','L','M'],'D','N is 27; L is the next younger person, at 16. This also corrects the publisher\'s K choice.'),
      27:('In which year was J born?',['2007','1960','1993','1970','1983'],'D','J was born in 1970.'),
      28:('What is P\'s age?',['43','16','27','40','37'],'D','P is 40.')}
    for n,(stem,options,key,proof) in age_questions.items():
        add(pid,n,stem,options,key,age_proof+proof,
            'Editorial addition for Q24-Q28: M is older than P. This selects one arrangement without assuming facts absent from the source.',ages)
    add(pid,51,'Find the ratio of males working on Monday and Thursday together to females working on Tuesday and Wednesday together.',[
        '6:7','4:5','6:5','3:4','2:1'],'C',
        'Males Monday+Thursday=280+200=480. Females Tuesday+Wednesday=(360-140)+(500-320)=220+180=400. Ratio 480:400=6:5, now included as option C.',
        'Editorial option repair: changes option C from 8:5 to 6:5. The chart data and option positions are retained.',
        'Chart data: Monday total 400, males 280; Tuesday total 360, males 140; Wednesday total 500, males 320; Thursday total 640, males 200.')
    record={'version':'2026-11-20-repaired-v2',
        'note':'Editorial practice amendments. Added wording is explicit; it is not claimed to be recovered or official source text.',
        'papers':papers}
    assert sum(map(len,papers.values()))==37
    (ROOT/'data/previous/question_repairs.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Prepared 37 amended question views, restoring all 32 excluded questions.')

if __name__=='__main__':build()
