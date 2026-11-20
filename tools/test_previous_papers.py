"""Validate imports and exercise saved answers, grading, expiry and mobile layout."""
import argparse
from functools import partial
import http.server
import json
from pathlib import Path
import threading
import pymupdf
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
bank = json.loads((ROOT/'data/previous/catalog.json').read_text(encoding='utf-8'))
assert len(bank['papers']) == 12
assert bank['auditSummary']['verifiedAnswers'] == 960
assert bank['auditSummary']['excludedQuestions'] == 0
assert sum(len(p['preRepair']['excludedQuestions']) for p in bank['papers']) == 32
assert sum(len(p['questionRepairs']) for p in bank['papers']) == 37
assert sum(len(p['answers']) == 80 for p in bank['papers']) == 12
for paper in bank['papers']:
    assert len(paper['answers']) in (0, 80)
    assert all(a is None or isinstance(a,int) and 0 <= a <= 4 for a in paper['answers'].values())
    assert len(paper['answerDetails']) == 80
    assert all(r['explanation'] for r in paper['answerDetails'].values())
    assert len(paper['pages']) > 0 and all((ROOT / f).is_file() for f in paper['pages'])
    assert (ROOT/paper['pdf']).is_file()
    for file in paper['pages']:
        with Image.open(ROOT/file) as im: im.load()
    with pymupdf.open(ROOT/paper['pdf']) as doc:
        assert 'Correct Option' not in ''.join(page.get_text() for page in doc)
    assert all(0 <= page < len(paper['pages']) for page in paper['questionPages'].values())
    if paper['keyPdf']: assert (ROOT/paper['keyPdf']).is_file()


def run(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width':1440,'height':1000})
        errors=[]
        page.on('pageerror',lambda e: errors.append(str(e)))
        page.goto(url+'previous.html',wait_until='networkidle')
        assert page.locator('.py-card').count() == 12
        assert page.locator('[data-key]').count() == 12
        # Source-key corrections must re-evaluate saved attempts, preserving choices.
        page.evaluate('''() => {
          const rows=[
            {paperId:'prepp-2023-08-05-shift-1',answers:{6:1},marked:[6],visited:[6],score:1,completedAt:new Date().toISOString()},
            {paperId:'prepp-2023-08-05-shift-1',answers:{6:4},marked:[],visited:[6],score:-.25,completedAt:new Date().toISOString()},
            {paperId:'prepp-2021-08-01',answers:{1:3},marked:[],visited:[1],score:null,completedAt:new Date().toISOString()}
          ]; localStorage.setItem('rrbpo_previous_history_v1',JSON.stringify(rows));
        }''')
        page.reload(wait_until='networkidle')
        migrated=page.evaluate('PreviousPortal.history()')
        assert [r['score'] for r in migrated] == [-.25,1,1]
        assert migrated[0]['answers'] == {'6':1} and migrated[0]['marked'] == [6]
        assert all(r['reviewVersion']==bank['auditVersion'] for r in migrated)
        page.locator('[data-key="prepp-2023-08-05-shift-1"]').click()
        page.select_option('#pyKeyFilter','corrected')
        assert page.locator('tbody tr').count()==1
        assert page.locator('tbody tr').inner_text().startswith('Q6')
        assert 'Corrected from publisher B' in page.locator('tbody tr').inner_text()
        assert 'Both conclusions follow: E' in page.locator('tbody tr').inner_text()
        assert page.evaluate("localStorage.getItem('rrbpo_previous_active_v1')") is None
        (ROOT/'artifacts').mkdir(exist_ok=True)
        page.screenshot(path=str(ROOT/'artifacts/previous-corrected-key.png'),full_page=True)
        page.click('#pyKeyBack')
        page.locator('[data-key="prepp-2023-08-05-shift-2"]').click()
        page.select_option('#pyKeyFilter','corrected')
        assert 'Q22' in page.locator('tbody tr').inner_text()
        assert 'Corrected from publisher A' in page.locator('tbody tr').inner_text()
        page.select_option('#pyKeyFilter','repaired')
        assert page.locator('tbody tr').count()==6
        assert '6:5' in page.locator('tbody tr').last.inner_text()
        page.click('#pyKeyBack')
        for keyed in (t for t in bank['papers'] if t['answers']):
            scores = page.evaluate('''t => {
                const wrong=Object.fromEntries(Object.entries(t.answers).map(([n,a])=>[n,(a+1)%5]));
                return [PreviousPortal.grade(t,t.answers).score, PreviousPortal.grade(t,wrong).score, PreviousPortal.grade(t,{}).score];
            }''', keyed)
            maximum=80-len(keyed.get('excludedQuestions',{}))
            assert scores == [maximum,-maximum*.25,0], (keyed['id'],scores)
        page.select_option('#pyYear','2024')
        assert page.locator('.py-card:visible').count() == 4
        page.select_option('#pyYear','all')
        paper=bank['papers'][0]
        page.locator(f'[data-start="{paper["id"]}"]').click()
        page.click('#pyBegin')
        assert page.locator('[data-question]').count() == 80
        assert page.locator('#pyTimer').inner_text().startswith('44:') or page.locator('#pyTimer').inner_text()=='45:00'
        correct=paper['answers']['1']
        page.locator(f'[data-choice="{correct}"]').click()
        page.click('#pyMark')
        assert page.locator('[data-question="1"]').evaluate('(el)=>el.classList.contains("marked-answered")')
        page.click('#pyNext')
        page.locator(f'[data-choice="{(paper["answers"]["2"]+1)%5}"]').click()
        page.click('#pyNextPage')
        assert page.locator('#pyPage').input_value() == '2'
        page.reload(wait_until='networkidle')
        page.click('#pyResume')
        assert page.locator('#pyPage').input_value() == '2'
        page.click('[data-question="1"]')
        assert page.locator('[data-choice].selected').get_attribute('data-choice') == str(correct)
        page.click('[data-question="43"]')
        assert page.locator('[data-choice]:disabled').count()==0
        assert page.locator('[data-repair-choice]').count()==5
        assert 'A man' in page.locator('.py-repair h3').inner_text()
        assert 'therefore his son' not in page.locator('.py-repair').inner_text()
        page.click('#pySubmit');page.click('#pyCancel')
        assert page.locator('#pyTimer').count() == 1
        page.click('#pySubmit');page.click('#pyConfirm')
        assert page.locator('#pyScore').inner_text() == f'0.75/{80-len(paper["excludedQuestions"])}'
        page.select_option('#pyReviewFilter','wrong')
        assert page.locator('tbody tr').count() == 1
        assert page.locator('tbody tr').first.inner_text().startswith('Q2')
        page.click('#pyResultHome')
        ungraded=bank['papers'][-1]
        assert len(ungraded['answers']) == 80
        page.locator(f'[data-start="{ungraded["id"]}"]').click();page.click('#pyBegin')
        page.click('[data-choice="3"]');page.click('#pySubmit');page.click('#pyConfirm')
        assert page.locator('#pyScore').inner_text() == '1/80'
        assert page.locator('td.py-wrong').count() == 0
        page.click('#pyResultHome')
        page.locator('[data-start="prepp-2022-08-20-shift-1"]').click();page.click('#pyBegin')
        page.click('[data-question="9"]')
        assert page.locator('[data-choice]:disabled').count() == 0
        assert 'FALSE' in page.locator('.py-repair h3').inner_text()
        assert page.locator('[data-repair-choice]').count() == 5
        assert not page.locator('.py-original-source').evaluate('(el)=>el.open')
        page.click('[data-repair-choice="3"]')
        assert page.locator('#pyPage').input_value() == '3'
        page.click('#pySubmit');page.click('#pyConfirm')
        assert page.locator('#pyScore').inner_text() == '1/80'
        assert 'Correct (+1)' in page.locator('tbody tr').nth(8).inner_text()
        page.click('#pyResultHome')
        page.locator('[data-start="prepp-2023-08-05-shift-2"]').click();page.click('#pyBegin')
        page.click('[data-question="26"]')
        assert 'M is older than P' in page.locator('.py-repair-context').inner_text()
        assert page.locator('[data-repair-choice="3"]').inner_text().endswith('L')
        page.click('[data-repair-choice="3"]');page.click('#pySubmit');page.click('#pyConfirm')
        assert page.locator('#pyScore').inner_text() == '1/80'
        page.click('#pyResultHome')
        page.evaluate("localStorage.setItem('rrbpo_previous_active_v1',JSON.stringify({paperId:'prepp-2022-08-20-shift-1',endAt:Date.now()+600000,startedAt:Date.now(),number:9,pageIndex:2,answers:{},marked:[],visited:[9]}))")
        page.reload(wait_until='networkidle');page.click('#pyResume')
        assert page.locator('[data-choice]:disabled').count() == 5
        assert page.locator('.py-repair').count() == 0
        assert 'earlier source wording' in page.locator('#app').inner_text()
        page.click('#pySubmit');page.click('#pyConfirm')
        assert page.locator('#pyScore').inner_text() == '0/70'
        assert 'Not scored' in page.locator('tbody tr').nth(8).inner_text()
        page.click('#pyResultHome')
        page.locator(f'[data-start="{paper["id"]}"]').click();page.click('#pyBegin')
        page.evaluate("const a=JSON.parse(localStorage.getItem('rrbpo_previous_active_v1')); a.endAt=Date.now()-1000; localStorage.setItem('rrbpo_previous_active_v1',JSON.stringify(a));")
        page.reload(wait_until='networkidle')
        assert page.locator('#pyScore').inner_text() == f'0/{80-len(paper["excludedQuestions"])}'
        assert 'AUTOMATICALLY SUBMITTED' in page.locator('.py-label').first.inner_text()
        assert page.evaluate("localStorage.getItem('rrbpo_previous_active_v1')") is None
        page.click('#pyResultHome')
        page.set_viewport_size({'width':390,'height':844})
        page.locator(f'[data-start="{paper["id"]}"]').click();page.click('#pyBegin')
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth+1')
        assert page.locator('[data-choice]').count() == 5
        page.wait_for_function("document.querySelector('#pyPageImage').complete && document.querySelector('#pyPageImage').naturalWidth > 0")
        (ROOT/'artifacts').mkdir(exist_ok=True)
        page.screenshot(path=str(ROOT/'artifacts/previous-mobile.png'),full_page=True)
        page.click('[data-question="43"]')
        assert page.locator('[data-repair-choice]').count()==5
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth+1')
        page.screenshot(path=str(ROOT/'artifacts/previous-repaired-mobile.png'),full_page=True)
        page.set_viewport_size({'width':1440,'height':1000})
        page.screenshot(path=str(ROOT/'artifacts/previous-exam.png'),full_page=True)
        page.goto(url,wait_until='networkidle')
        page.wait_for_selector('#tabPrevious')
        assert page.locator('#tabPrevious').get_attribute('href')=='previous.html'
        assert page.locator('.mock-card').count()==20
        page.goto(url+'previous.html#answers=prepp-2023-08-05-shift-1',wait_until='networkidle')
        assert page.locator('#pyKeyFilter').count()==1
        page.set_viewport_size({'width':390,'height':844})
        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth+1')
        assert not errors,errors
        browser.close()
    print('PASS: 12 reviewed keys, 960 audit records, corrections, history regrading, key views, scoring, resume, 32 repairs, legacy attempt isolation, auto-submit, mobile and direct links.')


if __name__=='__main__':
    args=argparse.ArgumentParser();args.add_argument('--url');options=args.parse_args()
    if options.url: run(options.url.rstrip('/')+'/')
    else:
        class Handler(http.server.SimpleHTTPRequestHandler):
            def log_message(self,*args): pass
        with http.server.ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT))) as server:
            threading.Thread(target=server.serve_forever,daemon=True).start()
            try: run(f'http://127.0.0.1:{server.server_port}/')
            finally: server.shutdown()
