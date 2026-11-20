"""Apply the reviewed answers without changing option order, IDs or saved choices."""
import csv
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/previous'

def apply():
    bank=json.loads((DATA/'catalog.json').read_text(encoding='utf-8'))
    audit=json.loads((DATA/'answer_audit.json').read_text(encoding='utf-8'))
    changes=[];export=[]
    for paper in bank['papers']:
        source=paper.setdefault('sourceAnswers',dict(paper['answers']))
        rows=audit['papers'][paper['id']]
        assert set(rows)=={str(n) for n in range(1,81)}
        paper['answerDetails']=rows
        paper['answers']={n:r['answerIndex'] for n,r in rows.items()}
        paper['excludedQuestions']={n:r['explanation'] for n,r in rows.items() if r['status']=='excluded'}
        paper['auditVersion']=audit['version']
        for n,row in rows.items():
            assert row['status'] in ['verified','excluded'] and row['explanation']
            if row['status']=='verified':assert isinstance(row['answerIndex'],int) and 0<=row['answerIndex']<5
            else:assert row['answerIndex'] is None
            page=row.get('sourcePage')
            if page is not None:paper['questionPages'][n]=page-1
            old=source.get(n);new=row['answerIndex']
            corrected=new is not None and old is not None and old!=new
            if corrected:changes.append({'paper':paper['id'],'question':int(n),'publisher':'ABCDE'[old],'reviewed':'ABCDE'[new]})
            row['correctedPublisherKey']=corrected
            export.append([paper['title'],n,'' if new is None else 'ABCDE'[new],row['status'],'' if old is None else 'ABCDE'[old],row['explanation']])
    bank['auditVersion']=audit['version'];bank['auditSummary']=audit['summary'];bank['auditSummary']['correctedKeys']=changes
    (DATA/'catalog.json').write_text(json.dumps(bank,ensure_ascii=False,indent=2),encoding='utf-8')
    (DATA/'catalog.js').write_text('window.PREVIOUS_PAPERS = '+json.dumps(bank,ensure_ascii=False)+';\n',encoding='utf-8')
    with (DATA/'reviewed_answers.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f);writer.writerow(['Paper','Question','Reviewed answer','Status','Publisher answer','Explanation']);writer.writerows(export)
    print(json.dumps(bank['auditSummary'],indent=2))

if __name__=='__main__':apply()
