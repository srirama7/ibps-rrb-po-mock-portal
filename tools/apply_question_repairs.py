"""Apply labelled editorial repairs while preserving the pre-repair exam version."""
import copy
import json
from pathlib import Path
import pymupdf

ROOT=Path(__file__).resolve().parents[1]

def apply_repairs(bank):
    path=ROOT/'data/previous/question_repairs.json'
    if not path.is_file():return
    manifest=json.loads(path.read_text(encoding='utf-8'))
    restored=0;amended=0
    for paper in bank['papers']:
        paper['preRepair']=copy.deepcopy({key:paper[key] for key in ['answers','answerDetails','excludedQuestions','auditVersion']})
        paper['preRepair']['questionVersion']=paper['auditVersion']
        paper['questionVersion']=manifest['version']
        paper['questionRepairs']=manifest['papers'].get(paper['id'],{})
        for n,repair in paper['questionRepairs'].items():
            amended+=1
            was_excluded=n in paper['excludedQuestions']
            restored+=was_excluded
            detail=paper['answerDetails'][n]
            detail.update(answerIndex=repair['answerIndex'],explanation=repair['explanation'],status='verified',
                repair=repair,restoredFromExclusion=was_excluded,correctedPublisherKey=False)
            paper['answers'][n]=repair['answerIndex']
            paper['excludedQuestions'].pop(n,None)
        assert not paper['excludedQuestions'],paper['id']
        assert all(isinstance(x,int) and 0<=x<5 for x in paper['answers'].values())
    assert restored==32 and amended==37,(restored,amended)
    bank['sourceAuditSummary']=copy.deepcopy(bank['auditSummary'])
    bank['auditVersion']=manifest['version'];bank['questionVersion']=manifest['version']
    bank['auditSummary'].update(verifiedAnswers=960,excludedQuestions=0,repairedQuestions=restored,amendedQuestions=amended,
        method='Original questions were reviewed, then 32 defective questions were restored with labelled editorial practice amendments. Shared clue repairs appear on 37 question views. Original PDF text and the earlier attempt version are retained.')
    bank['repairNote']=manifest['note']
    export_pdf(bank)

def export_pdf(bank):
    doc=pymupdf.open()
    def page(text,title):
        p=doc.new_page(width=595,height=842)
        p.insert_text((45,42),title,fontsize=14,fontname='hebo')
        fit=p.insert_textbox(pymupdf.Rect(45,65,550,795),text,fontsize=11,fontname='helv',lineheight=1.3)
        assert fit>=0,('Repair PDF overflow',title,fit)
    page('Companion to the supplied RRB PO memory-based papers.\n\n32 formerly excluded questions have been repaired. Shared clues are repeated across 37 affected question views so each revised question can be read on its own.\n\nThese are clearly labelled editorial practice amendments, not recovered original or official IBPS text. Use the amended wording and options here instead of the corresponding question in the source PDF.\n\nEvery new online attempt has 80 scorable questions. Earlier attempts retain their prior wording and scoring context. Answers and explanations are available in the portal and reviewed-answers CSV.\n\nQuestion version: '+bank['questionVersion'], 'Repaired practice questions')
    for paper in bank['papers']:
        for n,repair in sorted(paper['questionRepairs'].items(),key=lambda r:int(r[0])):
            text=paper['title']+'\n\nEDITORIAL PRACTICE REPAIR\n'+repair['change']+'\n\n'
            if repair['context']:text+='Shared information:\n'+repair['context']+'\n\n'
            text+=repair['stem']+'\n\n'+'\n'.join(f'({"ABCDE"[i]}) {option}' for i,option in enumerate(repair['options']))
            page(text,f'Question {n} - amended practice wording')
    doc.set_metadata({'title':'RRB PO - Repaired practice questions','subject':'Labelled editorial amendments; no answers shown','creationDate':'D:20261120000000Z'})
    doc.save(ROOT/'data/previous/repaired_questions.pdf',garbage=4,deflate=True,no_new_id=True)
