"""Validate imports and exercise saved answers, grading, expiry and mobile layout."""
import argparse
from functools import partial
import http.server
import json
from pathlib import Path
import threading
import pymupdf
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
bank = json.loads((ROOT/'data/previous/catalog.json').read_text(encoding='utf-8'))
assert len(bank['papers']) == 12
assert sum(len(p['answers']) == 80 for p in bank['papers']) == 11
for paper in bank['papers']:
    assert len(paper['answers']) in (0, 80)
    assert all(isinstance(a,int) and 0 <= a <= 4 for a in paper['answers'].values())
    assert len(paper['pages']) > 0 and all((ROOT / f).is_file() for f in paper['pages'])
    assert (ROOT/paper['pdf']).is_file()
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
        page.click('#pySubmit');page.click('#pyCancel')
        assert page.locator('#pyTimer').count() == 1
        page.click('#pySubmit');page.click('#pyConfirm')
        assert page.locator('#pyScore').inner_text() == '0.75/80'
        page.select_option('#pyReviewFilter','wrong')
        assert page.locator('tbody tr').count() == 1
        assert page.locator('tbody tr').first.inner_text().startswith('Q2')
        page.click('#pyResultHome')
        ungraded=bank['papers'][-1]
        assert ungraded['answers'] == {}
        page.locator(f'[data-start="{ungraded["id"]}"]').click();page.click('#pyBegin')
        page.click('[data-choice="0"]');page.click('#pySubmit');page.click('#pyConfirm')
        assert page.locator('#pyScore').inner_text() == 'Ungraded answer record'
        assert page.locator('td.py-wrong').count() == 0
        page.click('#pyResultHome')
        page.locator('[data-start="prepp-2022-08-20-shift-1"]').click();page.click('#pyBegin')
        page.click('[data-question="9"]')
        assert page.locator('[data-choice]:disabled').count() == 5
        assert 'excluded from scoring' in page.locator('.py-sheet').inner_text()
        assert page.locator('#pyPage').input_value() == '3'
        page.click('#pySubmit');page.click('#pyConfirm')
        assert page.locator('#pyScore').inner_text() == '0/79'
        assert 'Excluded: source prompt missing' in page.locator('tbody tr').nth(8).inner_text()
        page.click('#pyResultHome')
        page.locator(f'[data-start="{paper["id"]}"]').click();page.click('#pyBegin')
        page.evaluate("const a=JSON.parse(localStorage.getItem('rrbpo_previous_active_v1')); a.endAt=Date.now()-1000; localStorage.setItem('rrbpo_previous_active_v1',JSON.stringify(a));")
        page.reload(wait_until='networkidle')
        assert page.locator('#pyScore').inner_text() == '0/80'
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
        page.set_viewport_size({'width':1440,'height':1000})
        page.screenshot(path=str(ROOT/'artifacts/previous-exam.png'),full_page=True)
        page.goto(url,wait_until='networkidle')
        page.wait_for_selector('#tabPrevious')
        assert page.locator('#tabPrevious').get_attribute('href')=='previous.html'
        assert page.locator('.mock-card').count()==20
        assert not errors,errors
        browser.close()
    print('PASS: 12 papers, 11 keys, filtering, answer save/resume, review marking, source pages, scoring, ungraded mode, auto-submit, mobile and home integration.')


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
