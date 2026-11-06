"""Exercise the actual static portal: navigation, data, scoring, timers and mobile layout."""
import http.server, socketserver, threading, json
from pathlib import Path
from functools import partial
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts';OUT.mkdir(exist_ok=True)
class Server(socketserver.TCPServer): allow_reuse_address=True
class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args): pass

with Server(('127.0.0.1',0),partial(Handler,directory=str(ROOT))) as server:
    threading.Thread(target=server.serve_forever,daemon=True).start()
    url=f'http://127.0.0.1:{server.server_address[1]}/'
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page(viewport=dict(width=1440,height=1000),device_scale_factor=1)
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('dialog',lambda d:d.accept())
        page.goto(url,wait_until='networkidle')
        assert page.locator('.mock-card').count()==20
        assert page.locator('#practiceNotes').count()==1
        page.screenshot(path=str(OUT/'desktop-home.png'),full_page=True)
        page.locator('[data-start="MOCK-01"]').click();page.locator('#beginMock').click()
        assert page.locator('.pal-btn').count()==40
        assert page.locator('.option-item').count()==5
        page.locator('.option-item').nth(2).click()
        assert page.locator('.option-item.selected').count()==1
        page.locator('#btnMarkNext').click()
        assert page.locator('.pal-btn.marked-answered').count()==1
        page.locator('[data-jump="1"]').click()
        assert page.locator('.option-item.selected').count()==1
        page.locator('#btnClear').click()
        assert page.locator('.option-item.selected').count()==0
        page.locator('.option-item').first.focus();page.keyboard.press('Space')
        assert page.locator('.option-item.selected').count()==1
        page.screenshot(path=str(OUT/'desktop-exam.png'),full_page=True)
        page.reload(wait_until='networkidle');page.locator('#resumeActiveBtn').click()
        assert page.locator('.option-item.selected').count()==1
        page.evaluate("""() => { const s=JSON.parse(localStorage.getItem('rrbpo_active_v3')); s.sectionEndAt=Date.now()-1000; localStorage.setItem('rrbpo_active_v3',JSON.stringify(s)); }""")
        page.reload(wait_until='networkidle');page.locator('#resumeActiveBtn').click()
        assert page.locator('.pal-btn').first.inner_text().strip()=='41'
        assert page.locator('#btnPrev').is_disabled()
        assert page.locator('.cbt-table thead th').count()==3
        assert page.locator('.cbt-table tbody tr').first.locator('td').count()==3
        page.locator('[data-jump="46"]').click()
        assert page.locator('.bar-value').count()==10
        page.locator('[data-jump="51"]').click()
        assert 'ratio' in page.locator('.stimulus-card').inner_text()
        data=json.loads((ROOT/'data/tests.json').read_text(encoding='utf-8'))
        for test in data['tests']:
            page.evaluate("""t => {const s={testId:t.id,startedAt:Date.now(),sectionIndex:1,sectionEndAt:Date.now()+1200000,currentIndex:40,answers:Object.fromEntries(t.questions.map(q=>[q.id,q.answerIndex])),visited:t.questions.map(q=>q.id),marked:[t.questions[0].id]};localStorage.setItem('rrbpo_active_v3',JSON.stringify(s));}""",test)
            page.reload(wait_until='networkidle');page.locator('#resumeActiveBtn').click()
            page.locator('#submitExamBtn').click()
            assert page.locator('.hero-score-value').inner_text().strip().startswith('80.00')
            assert page.locator('.solution-card').count()==80
            page.locator('#toggleOnlyWrong').click()
            assert page.locator('.solution-card').count()==0
        t=data['tests'][0]
        page.evaluate("""t => {const q=t.questions;const s={testId:t.id,startedAt:Date.now(),sectionIndex:1,sectionEndAt:Date.now()+1200000,currentIndex:40,answers:{[q[0].id]:q[0].answerIndex,[q[1].id]:(q[1].answerIndex+1)%5},visited:[],marked:[]};localStorage.setItem('rrbpo_active_v3',JSON.stringify(s));}""",t)
        page.reload(wait_until='networkidle');page.locator('#resumeActiveBtn').click();page.locator('#submitExamBtn').click()
        assert page.locator('.hero-score-value').inner_text().strip().startswith('0.75')
        mobile=browser.new_page(viewport=dict(width=390,height=844),is_mobile=True,has_touch=True)
        mobile.on('pageerror',lambda e:errors.append(str(e)))
        mobile.goto(url,wait_until='networkidle')
        assert mobile.evaluate('document.documentElement.scrollWidth <= innerWidth')
        mobile.screenshot(path=str(OUT/'mobile-home.png'),full_page=True)
        mobile.locator('[data-start="MOCK-02"]').click()
        assert mobile.evaluate('document.documentElement.scrollWidth <= innerWidth')
        mobile.locator('#beginMock').click()
        assert mobile.evaluate('document.documentElement.scrollWidth <= innerWidth')
        assert mobile.locator('.option-item').count()==5
        mobile.locator('.option-item').first.click()
        assert mobile.locator('.option-item.selected').count()==1
        mobile.screenshot(path=str(OUT/'mobile-exam.png'),full_page=True)
        mobile.evaluate("""() => {const s=JSON.parse(localStorage.getItem('rrbpo_active_v3'));s.sectionIndex=1;s.sectionEndAt=Date.now()-1000;localStorage.setItem('rrbpo_active_v3',JSON.stringify(s));}""")
        mobile.reload(wait_until='networkidle')
        assert mobile.evaluate("localStorage.getItem('rrbpo_active_v3') === null")
        assert not errors,errors
        browser.close()
    server.shutdown()
print('PASS: desktop/mobile layout, answer selection, mark/clear, resume, sectional lock, DI, all 20 score reports, negative marking and automatic submission.')
