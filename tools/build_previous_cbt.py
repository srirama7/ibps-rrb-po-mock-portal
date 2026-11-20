"""Build typed, section-ordered CBT questions from the reviewed source papers."""
import json, re, ast
from pathlib import Path
import pymupdf
from audit_scanned_answers import parse, nums

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/previous'
catalog=json.loads((DATA/'catalog.json').read_text(encoding='utf-8'))

def tidy(s):
    for a,b in [('jetter','letter'),('enrotied','enrolled'),('Whe lives','Who lives'),('conctusions','conclusions'),('T arun','Tarun')]:s=s.replace(a,b)
    return re.sub(r'\s+',' ',s).strip()

def maths(s):
    s=re.sub(r'([xy?])\s*2\b',r'\1²',s)
    s=re.sub(r'\)\s*2\b',')²',s)
    s=re.sub(r'(\d+\.\d+)\s+2\b',r'\1²',s)
    return s.replace('4.982','4.98²').replace('3.982','3.98²').replace('33 1 3 %','33⅓%').replace('66 2 3 %','66⅔%')

GROUPS={
 '2022-08-20-shift-1':[(1,5),(8,12),(13,15),(16,20),(26,30),(31,32),(36,40),(51,55),(66,70),(76,80)],
 '2023-08-05-shift-1':[(1,5),(10,14),(16,20),(27,29),(30,31),(32,35),(36,40),(58,62),(73,77)],
 '2023-08-05-shift-2':[(1,5),(10,14),(15,19),(24,28),(31,33),(36,40),(41,45),(51,55)]}

def old_questions(p):
    suffix=p['id'][6:]; year,month,day,_,shift=suffix.split('-')
    f=ROOT/f'tools/prepp_cache/{year}-{month}-{day}_Shift-{shift}_RRB_PO_Prelims_Paper.pdf'
    text='\n'.join(page.get_text(sort=True) for page in pymupdf.open(f))
    text=re.sub(r'www\.prepp\.in','',text)
    # One source heading is absent from the searchable PDF layer.
    if year=='2022':text=text.replace('Correct Option - 1\n  1.  G attended','Correct Option - 1\nQue. 9 Which statement is false?\n  1.  G attended',1)
    parts=re.split(r'Que\.\s*(\d+)\s*',text); result={}; carry=''
    for i in range(1,len(parts),2):
        n=int(parts[i]); body=carry+'\n'+parts[i+1]
        key=re.search(r'Correct Option\s*-\s*\d',body)
        assert key,(p['id'],n)
        carry=body[key.end():]; body=body[:key.start()]
        options=list(re.finditer(r'(?m)^\s*([1-5])\.\s+',body))
        assert len(options)==5,(p['id'],n,len(options))
        stem=body[:options[0].start()].strip()
        opts=[body[m.end():options[j+1].start() if j<4 else len(body)].strip() for j,m in enumerate(options)]
        result[n]={'stem':stem,'options':opts,'shared':''}
    assert len(result)==80
    for start,end in GROUPS[suffix]:
        stem=result[start]['stem']
        matches=list(re.finditer(r'(?m)^\s*(?:Who|How|Which|What|Find|If |Four |On which|In which|The demand|The number|The ratio)',stem))
        if not matches and '\n\n' in stem:
            split=stem.rfind('\n\n');context=stem[:split].strip()
            result[start]['stem']=stem[split:].strip()
            for n in range(start,end+1):result[n]['shared']=context
        if matches:
            split=matches[-1].start(); context=stem[:split].strip()
            if context:
                result[start]['stem']=stem[split:].strip()
                for n in range(start,end+1):result[n]['shared']=context
    return result

TABLES={
 ('2022',51):(['Company','Production','Demand'],[['P',1500,2000],['Q',3600,2700],['R',3000,4500],['S',4400,2200],['T',4500,3600]]),
 ('2022',66):(['College','Total students',"Master's (%)"],[['A',2800,45],['B',2500,65],['C',1900,50],['D',3200,60]]),
 ('2023-08-05-shift-1',58):(['Building','Total rooms','Unoccupied rooms'],[['A',162,90],['B',244,144],['C',164,108],['D',232,136],['E',204,120]]),
 ('2023-08-05-shift-1',73):(['City','Vegetarian','Non-vegetarian'],[['P',45,125],['Q',105,90],['R',140,20],['S',75,100],['T',80,55]]),
 ('2023-08-05-shift-2',41):(['Company','Total employees','Female (%)'],[['A',1200,30],['B',1600,35],['C',1800,60],['D',2200,40]]),
 ('2023-08-05-shift-2',51):(['Day','Total employees','Male employees'],[['Monday',400,280],['Tuesday',360,140],['Wednesday',500,320],['Thursday',640,200]])}

def normalize_scan(q, detail):
    s=q['stem']; options=q['options'][:]
    if not options[0] and '(8)' in s:
        s,options[0]=s.rsplit('(8)',1)
    low=s.lower(); v=nums(s)
    def currency(text):
        value=re.sub(r'[^0-9.]','',text)
        return value[1:] if value[0] in '37' and len(value)>3 else value
    if 'interest on' in low:
        s=re.sub(r'(interest on )(.*?)( at)',lambda m:m[1]+'Rs. '+currency(m[2])+m[3],s,flags=re.I).replace('simpie','simple')
    elif 'shopkeeper bought' in low:
        s=re.sub(r'(for )(.*?)( and sold)',lambda m:m[1]+'Rs. '+currency(m[2])+m[3],s)
    elif 'a and b invest' in low:
        s=re.sub(r'(invest )(.*?)( and )(.*?)( respectively)',lambda m:m[1]+'Rs. '+currency(m[2])+m[3]+'Rs. '+currency(m[4])+m[5],s)
        s=re.sub(r'(year is )([^\s,]+)',lambda m:m[1]+'Rs. '+currency(m[2]),s)
        s=re.sub(r'[({]in [^)}]+[)}]','(in rupees)',s)
    elif 'rice costing' in low:
        def rice(m):
            a,b=[re.sub(r'^[^\d]+','',t) for t in [m[1],m[2]]]
            a=a[1:] if a.startswith('7') and len(a)>2 else a
            b=b[1:] if b.startswith('7') and len(b)>2 else b
            return 'costing Rs. '+a+'/kg and Rs. '+b+'/kg'
        s=re.sub(r'costing (.*?)\/kg and (.*?)\/kg',rice,s)
        s=re.sub(r'\(in [^)]+\)','(in rupees)',s)
    if 'approximate value' in low:
        a,b,c,d,e,f=v;s=f'Find the approximate value: {a:g} × {b:g} ÷ {c:g} + √{d:g} − {e:g} ÷ {f:g} = ?'
    elif s.startswith('[') or s.startswith('(('):
        a,b,c,d,e,f,g,h=v;s=f'[({a:g} × {b:g}) ÷ {c:g} − {d:g}] × {e:g} ÷ {f:g} + ({g:g} − {h:g}) = ?'
    elif s.startswith('sqrt('):
        a,b,c,d,e=v;s=f'√{a:g} × {b:g} − ({c:g} × {d:g}) + {e:g} = ?'
    elif '^' in s:
        a,b,c,d,e,f=v;s=f'({a:g}^{b:g}) − ({c:g}^{d:g}) + {e:g} ÷ {f:g} = ?'
    elif re.search(r'\d\s*x\s*\(',s):
        a,b,c,d,e,f=v;s=f'{a:g} × ({b:g}/{c:g}) + ({d:g}/{e:g}) × {f:g} = ?'
    elif 'relation between' in low or 'solving both equations' in low:
        roots=re.findall(r'roots are (\[[^]]+\])',detail['explanation'])
        assert len(roots)==2
        equations=[]
        for var,raw in zip('xy',roots):
            a,b=ast.literal_eval(raw); B=-(a+b); C=a*b
            equations.append(f'{var}² {B:+g}{var} {C:+g} = 0')
        s='Solve both equations and determine the relationship between x and y. I. '+equations[0]+'; II. '+equations[1]
        for i,o in enumerate(options):
            z=o.lower().replace(' ','').replace(chr(8804),'<=') .replace(chr(8805),'>=')
            if 'cannot' in z or 'cannot' in z.replace(' ',''):options[i]='x = y or the relationship cannot be established'
            elif 'sy' in z:options[i]='x ≤ y'
            elif 'zy' in z or '2y' in z:options[i]='x ≥ y'
            elif '<=' in z:options[i]='x '+chr(8804)+' y'
            elif '>=' in z:options[i]='x '+chr(8805)+' y'
            elif '<' in z:options[i]='x < y'
            elif '>' in z:options[i]='x > y'
        expected=['x > y','x < y','x ≥ y','x ≤ y','x = y or the relationship cannot be established']
        missing=[x for x in expected if x not in options]
        bad=[i for i,x in enumerate(options) if x not in expected]
        if len(missing)==len(bad)==1:options[bad[0]]=missing[0]
        assert set(options)==set(expected),(s,options)
    elif low.startswith('statement:'):
        left,right=re.split('Conclusions:',s,flags=re.I,maxsplit=1)
        left=left.replace('€','')
        relations=re.findall(r'([A-H])\s*([<>=≤≥])\s*([A-H])',right)
        if len(relations)==2:s=left.strip()+'\nConclusions:\n'+'\n'.join(f'{label}. '+ ' '.join(r) for label,r in zip(['I','II'],relations))
    if low.startswith('statements:'):
        left,right=s.replace('Ali ','All ').split('Conclusions:',1)
        sentences=re.findall(r'(?:All|No|Some)\b[^.]+',right)
        assert len(sentences)==3,(s,sentences)
        s=left+'\nConclusions:\n'+'\n'.join(f'{label}. {sentence}.' for label,sentence in zip(['I','II','III'],sentences))
        norm=lambda t:re.sub('[^a-z]','',t.lower().replace('|','i').replace('l','i').replace('u','ii').replace('j','i').replace('t','i'))
        for i,o in enumerate(options):
            z=norm(o)
            if 'all' in o.lower():options[i]='All I, II and III follow'
            elif 'none' in o.lower():options[i]='None of the conclusions follow'
            else:
                for marker,label in [('onlyiandii','Only I and II follow'),('onlyiandiii','Only I and III follow'),('onlyiiandiii','Only II and III follow')]:
                    if z.startswith(norm(marker+'follow')):options[i]=label;break
    if any(x in low for x in ['tallest among','even number','area of a rectangle']) or ('code for' in low and 'works' not in low):
        s=re.sub(r'(?<!\w)[|!1iIlJ]{1,2}[.,]\s*',lambda m:'\n'+('II' if len(m.group().rstrip(' ., '))>1 else 'I')+'. ',s)
        for i,o in enumerate(options):
            z=o.lower()
            if 'neither' in z:options[i]='Neither statement I nor statement II is sufficient'
            elif 'either' in z:options[i]='Either statement I or statement II alone is sufficient'
            elif 'both' in z:options[i]='Both statements I and II together are necessary'
            else:
                roman=re.search(r'statement\s+(.*?)\s+alone',o,re.I)
                assert roman,(s,o)
                label='II' if len(re.sub('[^a-zI|1]','',roman[1]))>=2 else 'I'
                options[i]=f'Only statement {label} alone is sufficient'
    if low.startswith('statement:'):
        for i,o in enumerate(options):
            z=o.lower()
            if 'both' in z:options[i]='Both conclusions I and II follow'
            elif 'neither' in z:options[i]='Neither conclusion I nor II follows'
            elif 'either' in z:options[i]='Either conclusion I or II follows'
            else:
                numeral=re.search(r'conclusion\s+(\S+)',o,re.I)[1]
                options[i]='Only conclusion '+('II' if len(numeral)>1 else 'I')+' follows'
    # Roman numeral glyphs in text choices, never touch alphanumeric sequences.
    for i,o in enumerate(options):
        if any(w in o.lower() for w in ['follow','statement','conclusion','sufficient']):
            o=o.replace('|','I');o=re.sub(r'\b(?:Il|il|ll|II\]|U|UI)\b','II',o);o=re.sub(r'\b(?:Ill|IlI|ilI)\b','III',o)
            o=re.sub(r'\bJ\b','I',o);options[i]=o
        if re.fullmatch(r'[^\d+-]*[+-]?\d+[.,]\d+\s*',o):options[i]=re.sub(r'^[^\d+-]+','',o).replace(',','.')
    options=[re.sub(r'^[})\],;]+\s*','',o) for o in options]
    s=s.replace('Whe sits','Who sits').replace('bottem','bottom').replace('tn which','In which')
    return s,options

papers=[]
for p in catalog['papers']:
    scanned='2022' not in p['id'] and '2023' not in p['id']
    qs=parse(ROOT/'tools/prepp_cache/audit/tesseract'/p['id']) if scanned else old_questions(p)
    records=[]
    for n,q in qs.items():
        detail=p['answerDetails'][str(n)]; s=q['stem'];opts=q['options'];context=q['shared']; table=None
        if scanned:s,opts=normalize_scan(q,detail)
        else:
            for (suffix,start),(columns,rows) in TABLES.items():
                if suffix in p['id'] and start<=n<=start+4:
                    table={'columns':columns,'rows':rows}
                    context='Study the following data and answer the question. '+('Number of students enrolled in Master’s and Bachelor’s degrees.' if start==66 else '')
                    if (suffix,start) in [('2022',51),('2023-08-05-shift-1',73),('2023-08-05-shift-2',51)]:table['chart']='bar'
            s=maths(tidy(s));opts=[maths(tidy(o)) for o in opts]
            if '2022' in p['id'] and n in [65,75]:opts=[re.sub(r'^(\d+) (\d+) (\d+)$',r'\1 \2/\3',o) for o in opts]
        if scanned and 'Company ' in context:
            text=context.replace('Company 8:','Company B:')
            bodies=re.findall(r'Company\s*[^:;]{1,3}[:;]+(.*?)(?=Company|$)',text)
            rows=[[letter]+[int(v) for v in re.findall(r'-\s*(\d+)',body)] for letter,body in zip('ABCDE',bodies)]
            assert len(rows)==5 and all(len(r)==6 for r in rows)
            table={'columns':['Company',2016,2017,2018,2019,2020],'rows':rows};context='Number of employees (in hundreds) in five companies over five years.'
        elif scanned and 'percentage distribution' in context.lower():
            rows=[[k.replace('8','B'),int(v)] for k,v in re.findall(r'([A-F8]):\s*(\d+)%',context)]
            assert len(rows)==6 and sum(r[1] for r in rows)==100
            total=re.search(r'distribution of\s*(\d+)',context)[1]
            table={'columns':['Stream','Percentage (%)'],'rows':rows,'chart':'pie'};context=f'Percentage distribution of {total} students enrolled across six streams.'
        elif scanned and 'Product P' in context:
            chunks=context.replace('jan','Jan').replace('fun','Jun').split('Product Q:')
            a=[int(v) for v in re.findall(r'-\s*(\d+)',chunks[0])];b=[int(v) for v in re.findall(r'-\s*(\d+)',chunks[1])]
            assert len(a)==len(b)==6,(p['id'],context)
            table={'columns':['Month','Product P','Product Q'],'rows':[[m,x,y] for m,x,y in zip(['Jan','Feb','Mar','Apr','May','Jun'],a,b)],'chart':'bar'};context='Units sold (in tens) of two products over six months.'
        repair=p.get('questionRepairs',{}).get(str(n))
        if repair:s=repair['stem'];opts=repair['options'];context=repair.get('context','')
        low=q['stem'].lower(); g=q['shared'].lower()
        quant= n>40 if not scanned else (any(x in low for x in ['equation','find the average of','approximate value','numbers are in the ratio','missing term','interest on','rice costing','train covers','shopkeeper','boat in','pipe a','a and b invest','area of a rectangle','even number']) or any(x in g for x in ['company','companies','percentage distribution','product p']) or ('=' in low and (' x ' in low or '^' in low or 'sqrt(' in low) and 'statement' not in low))
        records.append({'id':f'{p["id"]}-q{n}','sourceNumber':n,'section':'quant' if quant else 'reasoning','stem':'\n'.join(tidy(line) for line in s.splitlines() if line.strip()),'options':[tidy(o) for o in opts],'context':tidy(context),'table':table,'answerIndex':p['answers'][str(n)],'explanation':detail['explanation'],'amended':bool(repair)})
    records.sort(key=lambda q:(q['section']=='quant',q['sourceNumber']))
    assert sum(q['section']=='reasoning' for q in records)==40,(p['id'],sum(q['section']=='reasoning' for q in records))
    for i,q in enumerate(records):q['number']=i+1;assert q['stem'] and len(q['options'])==5 and all(q['options']),(p['id'],q)
    papers.append({'id':p['id'],'title':p['title'],'date':p['date'],'sourcePdf':p['pdf'],'questions':records})
bank={'version':'typed-cbt-v1','papers':papers}
(DATA/'cbt_bank.json').write_text(json.dumps(bank,ensure_ascii=False,indent=2),encoding='utf-8')
(DATA/'cbt_bank.js').write_text('window.PREVIOUS_CBT_BANK='+json.dumps(bank,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
print('Built',len(papers),'typed papers;',sum(len(p['questions']) for p in papers),'questions.')
