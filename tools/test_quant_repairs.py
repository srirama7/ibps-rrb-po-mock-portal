"""Regression coverage for merged questions, lost data, and rendered exam pages.

python tools/test_quant_repairs.py [--url https://.../]
Without --url, serve this checkout on an ephemeral loopback port.
"""
import argparse
import functools
import http.server
import json
from pathlib import Path
import re
import threading

from playwright.sync_api import sync_playwright
from repair_adda_quant import repair

ROOT = Path(__file__).resolve().parents[1]


def validate_data():
    bank = json.loads((ROOT / 'data/adda_tests.json').read_text(encoding='utf-8'))
    tests = bank['tests']
    bundled = (ROOT / 'data/adda_tests_data.js').read_text(encoding='utf-8')
    assert json.loads(bundled.split('=', 1)[1].strip().rstrip(';')) == bank
    keys = json.loads((ROOT / 'data/adda_answer_keys.json').read_text(encoding='utf-8'))
    for test in tests:
        assert test == json.loads((ROOT / 'data/licensed_adda' / (test['id'] + '.json')).read_text(encoding='utf-8'))
        assert len(test['questions']) == 80
        for question in test['questions']:
            assert len(question['options']) == 5
            assert keys[test['id']][str(question['number'])] == question['answerIndex']
            if question['section'] != 'quant':
                continue
            assert len(set(question['options'])) == 5, question['id']
            assert not re.search(r'Option [A-E]\b', question['explanation']), question['id']
            for image in question.get('diagrams', []):
                assert (ROOT / image).is_file(), image
            stem = question['stem']
            if 'approximate value' in stem.lower() or 'two equation' in stem.lower():
                assert re.search(r'\d', stem) or question.get('diagrams'), question['id']
            if '|---|' in stem:
                for line in stem.splitlines():
                    if '|' in line:
                        assert line.startswith('|') and line.endswith('|'), question['id']
    assert not repair(tests), 'Repair command must be idempotent'
    q = lambda paper, number: tests[paper - 1]['questions'][number - 1]
    for number in range(56, 65):
        assert not q(7, number)['diagrams'], ('Unexpected formula on', number)
    for number, page, image in [(65,34,164),(66,34,165),(67,35,170),
            (68,35,171),(69,35,172),(71,36,178),(72,36,179),
            (73,37,184),(74,37,185)]:
        assert q(7,number)['diagrams'] == [f'data/diagrams/adda-07_page{page}_Image{image}.png']
    assert '14.98%' in q(7,70)['stem'] and not q(7,70)['diagrams']
    assert q(7,63)['topic'] == 'Number Series'
    assert not q(3,60)['diagrams'] and not q(8,60)['diagrams']
    for number, page, image in [(61,32,160),(62,33,165),(63,33,166),(64,33,167)]:
        assert q(3,number)['diagrams'] == [f'data/diagrams/adda-03_page{page}_Image{image}.png']
    for number in range(46,51):
        assert 'females in each village is 80' in q(8,number)['stem']
    for number in range(64,69):
        assert 'females in company D is 500' in q(10,number)['stem']
    assert all(len(option) > 30 for option in q(8,80)['options'])
    print('PASS: all 800 records, answer-key stability, synchronized copies, and quant repair invariants', flush=True)


class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def validate_browser(url):
    artifacts = ROOT / 'artifacts/quant-repairs'
    artifacts.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('dialog', lambda dialog: dialog.accept())
        page.goto(url, wait_until='networkidle')
        page.wait_for_function('window.AddaPortal && window.__ADDA_TESTS_DATA__')
        page.evaluate("window.AddaPortal.switchTab('adda')")
        checked = []
        for paper in range(1,11):
            pid = f'adda-{paper:02}'
            results = page.evaluate('''async pid => {
                window.AddaPortal.startTest(pid);
                document.querySelector('#addaSecQuant').click();
                const test = window.AddaPortal.getAddaTest(pid);
                const results = [];
                for (let n = 41; n <= 80; n++) {
                    document.querySelector(`[data-adda-jump="${n-1}"]`).click();
                    const q = test.questions[n-1];
                    const box = document.querySelector('.question-body');
                    const images = [...box.querySelectorAll('.cbt-diagram-img')];
                    await Promise.all(images.map(img => img.decode().catch(() => {})));
                    results.push({id:q.id, number:n,
                        title:document.querySelector('.question-header h2').textContent.trim(),
                        options:box.querySelectorAll('.option-item').length,
                        imageCount:images.length, expectedImages:(q.diagrams||[]).length,
                        brokenImages:images.filter(img=>!img.complete||!img.naturalWidth).map(img=>img.src),
                        tables:[...box.querySelectorAll('table')].map(table=>({
                            headings:[...table.querySelectorAll('th')].map(cell=>cell.textContent.trim()),
                            rowSizes:[...table.querySelectorAll('tbody tr')].map(row=>row.children.length)
                        }))});
                }
                return results;
            }''', pid)
            for result in results:
                assert f'Question {result["number"]} of 80' in result['title'], result
                assert result['options'] == 5, result
                assert result['imageCount'] == result['expectedImages'], result
                assert not result['brokenImages'], result
                for table in result['tables']:
                    assert table['headings'] and all(h != '---' for h in table['headings']), result
                    assert all(size == len(table['headings']) for size in table['rowSizes']), result
            checked.extend(results)
            print(f'PASS: {pid}, all 40 quant questions rendered with intact options, images, and tables', flush=True)

        # Reproduce the user's exact question and verify answer persistence.
        page.evaluate("window.AddaPortal.startTest('adda-07')")
        page.locator('#addaSecQuant').click()
        page.locator('[data-adda-jump="62"]').click()
        assert page.locator('.q-topic').inner_text() == 'NUMBER SERIES'
        assert page.locator('.question-body .cbt-diagram-img').count() == 0
        page.locator('[data-opt="0"]').click()
        page.locator('#addaSaveNext').click()
        page.locator('[data-adda-jump="62"]').click()
        assert page.locator('[data-opt="0"]').get_attribute('class').find('selected') >= 0
        page.screenshot(path=str(artifacts / 'mock07-q63-fixed.png'), full_page=True)
        page.reload(wait_until='networkidle')
        page.wait_for_function('window.AddaPortal')
        page.evaluate("window.AddaPortal.switchTab('adda')")
        page.wait_for_selector('#resumeAddaActiveBtn')
        page.locator('#resumeAddaActiveBtn').click()
        assert page.locator('[data-opt="0"]').get_attribute('class').find('selected') >= 0
        page.locator('#addaSubmitBtn').click()
        page.wait_for_selector('.solution-card')
        review = page.locator('.solution-card').filter(has_text='1708, 1196, 853')
        assert review.count() == 1
        assert review.locator('.cbt-diagram-img').count() == 0
        assert '421' in review.inner_text()
        assert not errors, errors
        assert len(checked) == 400
        (artifacts / 'browser-results.json').write_text(json.dumps(checked, indent=2), encoding='utf-8')
        print('PASS: screenshot regression, answer save/resume, submission and solution review; no browser errors', flush=True)
        browser.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url')
    args = parser.parse_args()
    validate_data()
    if args.url:
        validate_browser(args.url)
    else:
        server = http.server.ThreadingHTTPServer(('127.0.0.1',0), functools.partial(Handler,directory=str(ROOT)))
        threading.Thread(target=server.serve_forever,daemon=True).start()
        try:
            validate_browser(f'http://127.0.0.1:{server.server_address[1]}/')
        finally:
            server.shutdown()
            server.server_close()
