"""Check every reasoning exam page and explanation, locally or after deployment."""
import argparse
import functools
import http.server
import json
from pathlib import Path
import re
import threading

from playwright.sync_api import sync_playwright
from repair_adda_reasoning import repair_content,RESTORED_INEQUALITIES
from test_quant_repairs import validate_data

ROOT=Path(__file__).resolve().parents[1]


def validate_reasoning():
    bank=json.loads((ROOT/'data/adda_tests.json').read_text(encoding='utf-8'))
    tests=bank['tests']
    before=json.dumps(tests,sort_keys=True)
    repair_content(tests)
    assert json.dumps(tests,sort_keys=True)==before,'Content repairs must be idempotent'
    statuses={}
    for test in tests:
        for q in test['questions'][:40]:
            assert q['explanationStatus']!='source-key-only',q['id']
            assert q['sourcePdfPage']>0,q['id']
            assert len(q['explanation'])>80,q['id']
            assert len(set(q['options']))==5,q['id']
            assert not re.search(r'Option [A-E]\b|Following the positive constraints|Formulating the problem equation',q['explanation']),q['id']
            assert not re.search(r'[\u0900-\u097f]',q['stem']+q['explanation']+' '.join(q['options'])),q['id']
            assert not q.get('diagrams'),('Unexpected separate question image',q['id'])
            assert not re.search(r'\bQ\s*\d+\.',q['stem']),q['id']
            if q['topic']=='Inequalities':
                assert q['stem'].count('Statements:')==1,q['id']
                assert q['stem'].count('Conclusions:')==1,q['id']
                assert len(re.findall(r'(?m)^I\.',q['stem']))==1,q['id']
                assert len(re.findall(r'(?m)^II\.',q['stem']))==1,q['id']
            statuses[q['explanationStatus']]=statuses.get(q['explanationStatus'],0)+1
    for paper,number in RESTORED_INEQUALITIES:
        q=tests[paper-1]['questions'][number-1]
        assert 'Statements:' in q['stem'] and 'II.' in q['stem']
    for n in range(11,15):
        stem=tests[9]['questions'][n-1]['stem']
        assert stem.count('is coded as')==4
        assert 'sf gi yt cn' in stem
    assert all(f'{label}.' in tests[9]['questions'][8]['stem'] for label in ['I','II','III'])
    assert all(f'{label}.' in tests[9]['questions'][29]['stem'] for label in ['I','II','III'])
    print('PASS: 400 reasoning explanations, source references, complete options, and single-question boundaries',flush=True)
    print('Explanation coverage:',statuses,flush=True)
    return bank


class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*_args):pass


def browser_check(url,expected):
    artifacts=ROOT/'artifacts/reasoning-repair'
    artifacts.mkdir(parents=True,exist_ok=True)
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        page=browser.new_page(viewport={'width':1440,'height':1000})
        errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.on('dialog',lambda dialog:dialog.accept())
        page.goto(url,wait_until='networkidle')
        page.wait_for_function('window.AddaPortal')
        assert page.evaluate('window.__ADDA_TESTS_DATA__')==expected,'Published bank is stale or differs from tested bank'
        page.evaluate("window.AddaPortal.switchTab('adda')")
        all_results=[]
        for paper in range(1,11):
            pid=f'adda-{paper:02}'
            results=page.evaluate('''pid=>{
                window.AddaPortal.startTest(pid);
                const test=window.AddaPortal.getAddaTest(pid);
                const results=[];
                for(let n=1;n<=40;n++){
                    document.querySelector(`[data-adda-jump="${n-1}"]`).click();
                    const q=test.questions[n-1];
                    const stem=document.querySelector('.question-body .q-stem');
                    const pdf=[...document.querySelectorAll('.exam-topbar a,.exam-header a,a')].find(a=>a.href.includes(test.pdfUrl));
                    results.push({id:q.id,n,stemCount:document.querySelectorAll('.question-body .q-stem').length,
                        options:document.querySelectorAll('.question-body .option-item').length,
                        images:document.querySelectorAll('.question-body .cbt-diagram-img').length,
                        text:stem.textContent.trim()});
                }
                document.querySelector('#addaSubmitBtn').click();
                return results;
            }''',pid)
            page.wait_for_selector('.solution-card')
            review=page.evaluate('''()=>[...document.querySelectorAll('.solution-card')].slice(0,40).map(card=>({
                explanations:card.querySelectorAll('.expl-box').length,
                source:card.querySelector('.question-source-link')?.getAttribute('href'),
                text:card.querySelector('.expl-box').textContent,
                tables:[...card.querySelectorAll('.expl-box table')].map(table=>({
                    width:table.querySelectorAll('th').length,
                    rows:[...table.querySelectorAll('tbody tr')].map(row=>row.children.length)
                }))
            }))''')
            assert len(results)==len(review)==40
            for result,explanation,q in zip(results,review,expected['tests'][paper-1]['questions'][:40]):
                assert result['stemCount']==1 and result['options']==5 and result['images']==0,result
                assert re.sub(r'\s+',' ',result['text'])==re.sub(r'\s+',' ',q['stem'].strip()),result['id']
                assert explanation['explanations']==1,result['id']
                assert explanation['source'].endswith('#page='+str(q['sourcePdfPage'])),result['id']
                for table in explanation['tables']:
                    assert table['width']>0 and all(size==table['width'] for size in table['rows']),result['id']
            all_results.extend(results)
            print(f'PASS: {pid}, all 40 reasoning exam pages and explanation/source cards',flush=True)

        page.evaluate("window.AddaPortal.startTest('adda-10')")
        page.locator('[data-adda-jump="10"]').click()
        assert page.locator('.q-stem').inner_text().count('is coded as')==4
        page.locator('[data-opt="0"]').click()
        page.locator('#addaSaveNext').click()
        page.locator('[data-adda-jump="10"]').click()
        page.screenshot(path=str(artifacts/'mock10-q11-restored.png'),full_page=True)
        page.reload(wait_until='networkidle')
        page.wait_for_function('window.AddaPortal')
        page.evaluate("window.AddaPortal.switchTab('adda')")
        page.wait_for_selector('#resumeAddaActiveBtn')
        page.locator('#resumeAddaActiveBtn').click()
        assert 'selected' in page.locator('[data-opt="0"]').get_attribute('class')
        page.locator('#addaSubmitBtn').click()
        page.wait_for_selector('.solution-card')
        page.locator('.solution-card').filter(has_text='What is the code for “rain”').screenshot(path=str(artifacts/'mock10-q11-explanation.png'))
        page.set_viewport_size({'width':390,'height':844})
        assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth+1')
        assert not errors,errors
        assert len(all_results)==400
        (artifacts/'browser-results.json').write_text(json.dumps(all_results,indent=2),encoding='utf-8')
        print('PASS: reasoning answer save/resume, solution review, mobile layout and zero browser errors',flush=True)
        browser.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--url');args=parser.parse_args()
    validate_data()
    bank=validate_reasoning()
    if args.url:browser_check(args.url,bank)
    else:
        server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
        threading.Thread(target=server.serve_forever,daemon=True).start()
        try:browser_check(f'http://127.0.0.1:{server.server_address[1]}/',bank)
        finally:server.shutdown();server.server_close()
