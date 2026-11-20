"""Check all typed questions and exercise the CBT lifecycle in a real browser."""
import argparse, json, threading, http.server
from functools import partial
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
bank=json.loads((ROOT/'data/previous/cbt_bank.json').read_text(encoding='utf-8'))
catalog=json.loads((ROOT/'data/previous/catalog.json').read_text(encoding='utf-8'))
assert len(bank['papers'])==12
for p,source in zip(bank['papers'],catalog['papers']):
    assert len(p['questions'])==80
    assert {q['sourceNumber'] for q in p['questions']}==set(range(1,81))
    assert [q['section'] for q in p['questions']]==['reasoning']*40+['quant']*40
    for q in p['questions']:
        assert q['stem'] and len(q['options'])==5 and all(q['options'])
        assert q['answerIndex']==source['answers'][str(q['sourceNumber'])]
        assert q['explanation'] and isinstance(q['answerIndex'],int) and 0<=q['answerIndex']<5
        assert '\ufffd' not in q['stem']+''.join(q['options'])
        if q['table']:assert all(len(row)==len(q['table']['columns']) for row in q['table']['rows'])

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass

def run(url):
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        page=browser.new_page(viewport={'width':1440,'height':1000})
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(url+'previous.html',wait_until='networkidle')
        assert page.locator('.cbt-card').count()==12
        page.locator('[data-action^="instructions:"]').first.click()
        assert page.locator('[data-action^="start:"]').is_disabled()
        page.locator('#ready').check();page.locator('[data-action^="start:"]').click()
        assert page.locator('.cbt-option').count()==5 and page.locator('.cbt-palette button').count()==40
        assert page.locator('iframe,object,embed,img').count()==0
        assert page.locator('#timer').inner_text().startswith('24:') or page.locator('#timer').inner_text()=='25:00'
        page.locator('input[value="2"]').check();page.locator('[data-action="mark"]').click()
        assert page.locator('[data-action="jump:0"]').get_attribute('class').find('answered-marked')>=0
        page.reload(wait_until='networkidle');page.locator('[data-action="resume"]').click()
        page.locator('[data-action="jump:0"]').click();assert page.locator('input[value="2"]').is_checked()
        page.locator('[data-action="clear"]').click();assert page.locator('input:checked').count()==0
        assert page.locator('.cbt-explanation').count()==0
        page.locator('[data-action="finish"]').click();page.locator('#cancelAction').click()
        assert page.locator('h1').inner_text()=='Reasoning Ability'
        page.locator('[data-action="finish"]').click();page.locator('#confirmAction').click()
        assert page.locator('h1').inner_text()=='Quantitative Aptitude'
        assert page.locator('[data-action="jump:0"]').count()==0
        assert page.locator('[data-action="jump:40"]').count()==1
        # Correct and incorrect choices, including an answered marked-for-review slot.
        page.evaluate('''() => { const a=JSON.parse(localStorage.getItem('rrbpo_previous_cbt_active_v1'));const qs=window.PREVIOUS_CBT_BANK.papers[0].questions;a.answers={0:qs[0].answerIndex,40:(qs[40].answerIndex+1)%5};a.marked=[0];localStorage.setItem('rrbpo_previous_cbt_active_v1',JSON.stringify(a)); }''')
        page.reload(wait_until='networkidle');page.locator('[data-action="resume"]').click()
        page.locator('[data-action="finish"]').click();page.locator('#confirmAction').click()
        assert '0.75' in page.locator('.cbt-score').inner_text()
        assert page.locator('.correct-option').count()==1 and page.locator('.cbt-explanation').count()==1
        assert page.evaluate("localStorage.getItem('rrbpo_previous_cbt_active_v1')") is None
        # Render all 960 typed questions in study review, including each shared dataset.
        page.locator('[data-action="home"]').click()
        for p in bank['papers']:
            page.locator(f'[data-action="study:{p["id"]}"]').click()
            page.evaluate("""id => {
                const paper=window.PREVIOUS_CBT_BANK.papers.find(p=>p.id===id);
                paper.questions.forEach((q,i)=>{
                    const select=document.querySelector('#reviewSelect');select.value=String(i);select.dispatchEvent(new Event('change'));
                    const choices=document.querySelectorAll('.cbt-option');
                    if(choices.length!==5 || document.querySelector('.cbt-stem').textContent!==q.stem)throw Error('Question rendering '+id+' '+i);
                    if(!document.querySelector('.correct-option').textContent.includes(q.options[q.answerIndex]))throw Error('Answer mismatch');
                    if(q.table && document.querySelectorAll('.cbt-table-wrap tbody tr').length!==q.table.rows.length)throw Error('Table mismatch');
                });
            }""",p['id'])
            page.locator('[data-action="home"]').click()
        # Time away carries through the sectional boundary and expires the whole test.
        def seed(section,deadline):
            page.evaluate('''([section,offset]) => localStorage.setItem('rrbpo_previous_cbt_active_v1',JSON.stringify({paperId:window.PREVIOUS_CBT_BANK.papers[0].id,section,index:section*40,deadline:Date.now()+offset,startedAt:Date.now()-3000000,answers:{},marked:[],visited:[]}))''',[section,deadline])
            page.reload(wait_until='networkidle')
        seed(0,-60000)
        page.locator('[data-action="resume"]').click()
        assert page.locator('h1').inner_text()=='Quantitative Aptitude'
        assert page.locator('#timer').inner_text().startswith('18:') or page.locator('#timer').inner_text().startswith('19:')
        seed(0,-21*60000)
        assert page.locator('.cbt-score').count()==1
        seed(1,-1000)
        assert page.locator('.cbt-score').count()==1
        page.locator('[data-action="home"]').click()
        page.locator('[data-action^="instructions:"]').first.click();page.locator('#ready').check();page.locator('[data-action^="start:"]').click()
        page.set_viewport_size({'width':390,'height':844})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
        page.screenshot(path=str(ROOT/'artifacts/previous-cbt-mobile.png'),full_page=True)
        page.set_viewport_size({'width':1440,'height':1000})
        page.screenshot(path=str(ROOT/'artifacts/previous-cbt-desktop.png'),full_page=True)
        assert not errors,errors
        browser.close()
    print('Passed: all 960 typed questions; choices, flags, clear, resume, sectional locks, time-away expiry, scoring, review and mobile layout.')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--url');args=parser.parse_args()
    if args.url:run(args.url.rstrip('/')+'/')
    else:
        server=http.server.ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
        threading.Thread(target=server.serve_forever,daemon=True).start()
        try:run(f'http://127.0.0.1:{server.server_port}/')
        finally:server.shutdown()
