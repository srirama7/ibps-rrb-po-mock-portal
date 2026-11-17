"""Exercise PDF import integrity, CBT behavior, timers, grading, and mobile layout."""
import argparse
from functools import partial
import http.server
import json
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
bank = json.loads((ROOT / 'data/karnataka/tests.json').read_text(encoding='utf-8'))
assert len(bank['tests']) == 10 and len(bank['paperLinks']) == 10
assert json.loads((ROOT / 'data/karnataka/tests.js').read_text(encoding='utf-8').split('=', 1)[1].strip().rstrip(';')) == bank
for t in bank['tests']:
    assert len(t['questions']) == 75 and t['durationMinutes'] == 60
    assert (ROOT / t['pdf']).is_file()
    assert [q['number'] for q in t['questions']] == list(range(1,76))
    for s in t['sections']:
        assert len([q for q in t['questions'] if q['section'] == s['id']]) == s['count']
    for q in t['questions']:
        assert q['stem'] and q['explanation'] and len(q['options']) == 5
        assert 0 <= q['answerIndex'] < 5
        assert 'independent practice material' not in str(q)
        assert bool(q['passage']) == (q['number'] <= 3)


def exercise(base):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width':1440, 'height':1000})
        errors=[]
        page.on('pageerror', lambda e:errors.append(str(e)))
        page.goto(base, wait_until='networkidle')
        assert page.locator('#tabKarnataka').count() == 1
        assert page.locator('.mock-card').count() == 20
        page.locator('#tabKarnataka').click()
        page.wait_for_selector('[data-start="KBL-01"]')
        assert page.locator('[data-start]').count() == 10
        assert page.locator('.kb-card').count() == 20
        page.locator('[data-start="KBL-01"]').click()
        page.locator('#kbBegin').click()
        assert page.locator('#kbClock').inner_text() in ('60:00','59:59')
        assert page.locator('.kb-pal').count() == 75
        assert page.locator('.kb-option').count() == 5
        assert page.locator('.kb-passage').count() == 1
        page.locator('.kb-option').nth(3).click()
        page.locator('#kbMark').click()
        assert page.locator('.kb-pal.marked-answered').count() == 1
        page.locator('[data-jump="0"]').click()
        assert page.locator('input:checked').input_value() == '3'
        page.reload(wait_until='networkidle')
        page.locator('#kbResume').click()
        assert page.locator('input:checked').input_value() == '3'
        page.locator('#kbClear').click()
        assert page.locator('input:checked').count() == 0
        page.locator('.kb-option input').first.focus()
        page.keyboard.press('Space')
        assert page.locator('input:checked').count() == 1
        page.locator('[data-section="sales"]').click()
        assert page.locator('.kb-stem').inner_text() == bank['tests'][0]['questions'][64]['stem']
        page.locator('#kbSaveExit').click()
        page.locator('[data-start="KBL-02"]').click()
        page.locator('#kbBegin').click()
        page.locator('#kbCancel').click()
        assert page.evaluate("JSON.parse(localStorage.getItem('karnataka_csa_active_v1')).testId") == 'KBL-01'
        page.locator('#kbHome').click()
        # Independently grade every imported mock, including wrong/unanswered distinctions.
        for t in bank['tests']:
            answers={q['id']:q['answerIndex'] for q in t['questions']}
            answers[t['questions'][1]['id']] = (t['questions'][1]['answerIndex']+1)%5
            del answers[t['questions'][2]['id']]
            state=dict(testId=t['id'],startedAt=0,endAt=0,index=0,answers=answers,marked=[],visited=[])
            page.evaluate("s=>{s.startedAt=Date.now();s.endAt=Date.now()+3600000;localStorage.setItem('karnataka_csa_active_v1',JSON.stringify(s));}", state)
            page.reload(wait_until='networkidle');page.locator('#kbResume').click()
            page.locator('#kbSubmit').click();page.locator('#kbConfirm').click()
            assert page.locator('.kb-score').inner_text().split() == ['73', '/', '75'], repr(page.locator('.kb-score').inner_text())
            assert page.locator('.kb-review').count() == 75
            page.locator('#kbFilter').select_option('wrong')
            assert page.locator('.kb-review').count() == 1
            page.locator('#kbFilter').select_option('skipped')
            assert page.locator('.kb-review').count() == 1
            page.locator('#kbFilter').select_option('correct')
            assert page.locator('.kb-review').count() == 73
        # Absolute deadlines survive refresh and auto-submit without clicking Resume.
        state=dict(testId='KBL-01',index=0,answers={},marked=[],visited=[])
        page.evaluate("s=>{s.startedAt=Date.now()-3600001;s.endAt=Date.now()-1;localStorage.setItem('karnataka_csa_active_v1',JSON.stringify(s));}",state)
        page.reload(wait_until='networkidle')
        assert page.locator('.kb-score').inner_text().split() == ['0', '/', '75'], repr(page.locator('.kb-score').inner_text())
        assert page.get_by_text('TIME COMPLETE · AUTO-SUBMITTED').count() == 1
        page.locator('#kbResultHome').click();page.locator('[data-start="KBL-01"]').click();page.locator('#kbBegin').click()
        page.clock.install()
        page.clock.fast_forward(3601000)
        assert page.locator('.kb-score').inner_text().split() == ['0', '/', '75'], repr(page.locator('.kb-score').inner_text())
        # Mobile library, test and review stay within the viewport.
        page.set_viewport_size({'width':390,'height':844})
        for stage in ['home','exam','result']:
            if stage=='home':page.locator('#kbHome').click()
            elif stage=='exam':page.locator('[data-start="KBL-01"]').click();page.locator('#kbBegin').click()
            else:page.locator('#kbSubmit').click();page.locator('#kbConfirm').click()
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), stage
            page.screenshot(path=str(ROOT / 'artifacts' / f'karnataka-mobile-{stage}.png'),full_page=True)
        # Main library remains responsive too.
        page.goto(base,wait_until='networkidle')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'RRB home'
        assert not errors, errors
        browser.close()
    print('PASS: 10 mocks, scoring, review filters, saved answers, replacement guard, keyboard, timers, mobile layout and main-library integration.')


if __name__ == '__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--url');args=parser.parse_args()
    (ROOT / 'artifacts').mkdir(exist_ok=True)
    if args.url: exercise(args.url)
    else:
        class Handler(http.server.SimpleHTTPRequestHandler):
            def log_message(self,*args):pass
        with http.server.ThreadingHTTPServer(('127.0.0.1',0),partial(Handler,directory=str(ROOT))) as server:
            threading.Thread(target=server.serve_forever,daemon=True).start()
            try:exercise(f'http://127.0.0.1:{server.server_port}/')
            finally:server.shutdown()
