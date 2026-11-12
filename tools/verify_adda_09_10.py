import http.server, socketserver, threading, json, os, re
from pathlib import Path
from functools import partial
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(r"C:\Users\amogh\ibps-rrb-portal-upgrade")

class Server(socketserver.TCPServer):
    allow_reuse_address = True

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

def test_paper_json(pid):
    filepath = ROOT / f"data/licensed_adda/{pid}.json"
    assert filepath.exists(), f"File {filepath} not found"
    with open(filepath, encoding='utf-8') as f:
        data = json.load(f)

    questions = data.get('questions', [])
    assert len(questions) == 80, f"{pid}: Expected 80 questions, got {len(questions)}"

    devanagari_pattern = re.compile(r'[\u0900-\u097F]')
    for q in questions:
        qnum = q['number']
        # Check pure English
        texts = [q['stem'], q.get('explanation', '')] + q.get('options', [])
        for t in texts:
            assert not devanagari_pattern.search(t), f"{pid} Q{qnum} contains Devanagari: {t[:50]}"

        # Check options
        opts = q.get('options', [])
        assert len(opts) == 5, f"{pid} Q{qnum} has {len(opts)} options instead of 5"

        # Check answerIndex
        ans_idx = q.get('answerIndex')
        assert ans_idx in range(5), f"{pid} Q{qnum} invalid answerIndex {ans_idx}"

        # Check explanation
        expl = q.get('explanation', '').strip()
        assert len(expl) >= 15, f"{pid} Q{qnum} explanation too short: '{expl}'"

        # Check diagram existence on disk
        for d in q.get('diagrams', []):
            d_path = ROOT / d.replace('/', os.sep)
            assert d_path.exists(), f"{pid} Q{qnum} missing diagram file: {d}"
            assert d_path.stat().st_size > 0, f"{pid} Q{qnum} empty diagram file: {d}"
            with Image.open(d_path) as im:
                w, h = im.size
                assert w > 0 and h > 0, f"{pid} Q{qnum} invalid image dims: {w}x{h}"

    print(f"PASS: JSON data integrity for {pid} (80 Qs, 100% English, 5 options, answerIndex 0-4, explanations, valid image files).")

def run_browser_verification():
    print("=" * 70)
    print("CBT VERIFICATION: ADDA-09 & ADDA-10")
    print("=" * 70)

    test_paper_json('adda-09')
    test_paper_json('adda-10')

    server = Server(('127.0.0.1', 0), partial(Handler, directory=str(ROOT)))
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    port = server.server_address[1]
    url = f'http://127.0.0.1:{port}/'

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport=dict(width=1440, height=900))
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('dialog', lambda dialog: dialog.accept())

            # ======================== ADDA-09 ========================
            print("\n--- Verifying ADDA-09 in Browser CBT ---")
            page.goto(url, wait_until='networkidle')
            page.locator('#tabAdda').click()
            page.wait_for_timeout(200)

            # Start adda-09
            page.locator('[data-adda-start="adda-09"]').click()
            page.locator('#addaBeginMock').click()
            page.wait_for_selector('#addaTimerDisplay')

            # Jump to Quant section (Q41 -> index 40)
            page.evaluate("""() => {
                const s = JSON.parse(localStorage.getItem('rrbpo_adda_active_v1'));
                s.sectionIndex = 1;
                s.sectionEndAt = Date.now() + 1200000;
                s.currentIndex = 40;
                localStorage.setItem('rrbpo_adda_active_v1', JSON.stringify(s));
            }""")
            page.reload(wait_until='networkidle')
            if page.locator('#resumeAddaActiveBtn').count() == 1:
                page.locator('#resumeAddaActiveBtn').click()
            page.wait_for_selector('#addaTimerDisplay')

            # 1. Hotels table (Q51-55)
            for q_idx in range(50, 55): # Q51-55 (0-based 50-54)
                page.locator(f'[data-adda-jump="{q_idx}"]').click()
                page.wait_for_timeout(50)
                assert page.locator('.cbt-diagram-img').count() >= 1, f"ADDA-09 Q{q_idx+1}: Table diagram not found"
                src = page.locator('.cbt-diagram-img').first.get_attribute('src')
                assert 'adda-09_page27_Image136.png' in src, f"ADDA-09 Q{q_idx+1}: wrong diagram {src}"
                nw = page.evaluate("document.querySelector('.cbt-diagram-img').naturalWidth")
                assert nw > 100, f"ADDA-09 Q{q_idx+1}: naturalWidth {nw} not > 100"
            print("PASS: ADDA-09 Q51-Q55 Hotels Table diagram verified with naturalWidth > 0.")

            # 2. Formula images Q56-60
            expected_fimages = {
                55: 'adda-09_page30_Image149.png',
                56: 'adda-09_page30_Image150.png',
                57: 'adda-09_page30_Image151.png',
                58: 'adda-09_page31_Image156.png',
                59: 'adda-09_page31_Image157.png',
            }
            for q_idx, exp_img in expected_fimages.items():
                page.locator(f'[data-adda-jump="{q_idx}"]').click()
                page.wait_for_timeout(50)
                assert page.locator('.cbt-diagram-img').count() >= 1, f"ADDA-09 Q{q_idx+1}: Formula image not found"
                src = page.locator('.cbt-diagram-img').first.get_attribute('src')
                assert exp_img in src, f"ADDA-09 Q{q_idx+1}: expected {exp_img}, got {src}"
                nw = page.evaluate("document.querySelector('.cbt-diagram-img').naturalWidth")
                assert nw > 50, f"ADDA-09 Q{q_idx+1}: naturalWidth {nw} not > 50"
            print("PASS: ADDA-09 Q56-Q60 Approximation formula images verified with naturalWidth > 0.")

            # 3. Restaurant Bar Graph Q66-70
            for q_idx in range(65, 70): # Q66-70
                page.locator(f'[data-adda-jump="{q_idx}"]').click()
                page.wait_for_timeout(50)
                assert page.locator('.cbt-diagram-img').count() >= 1, f"ADDA-09 Q{q_idx+1}: Bar graph diagram not found"
                src = page.locator('.cbt-diagram-img').first.get_attribute('src')
                assert 'adda-09_page33_Image166.png' in src, f"ADDA-09 Q{q_idx+1}: wrong diagram {src}"
                nw = page.evaluate("document.querySelector('.cbt-diagram-img').naturalWidth")
                assert nw > 200, f"ADDA-09 Q{q_idx+1}: naturalWidth {nw} not > 200"
            print("PASS: ADDA-09 Q66-Q70 Restaurant Bar Graph verified with naturalWidth > 0.")

            # 4. Quadratic Equation Formula Images Q76-80
            expected_quad = {
                75: 'adda-09_page37_Image187.png',
                76: 'adda-09_page37_Image188.png',
                77: 'adda-09_page37_Image189.png',
                78: 'adda-09_page40_Image194.png',
                79: 'adda-09_page40_Image195.png',
            }
            for q_idx, exp_img in expected_quad.items():
                page.locator(f'[data-adda-jump="{q_idx}"]').click()
                page.wait_for_timeout(50)
                assert page.locator('.cbt-diagram-img').count() >= 1, f"ADDA-09 Q{q_idx+1}: Quadratic formula not found"
                src = page.locator('.cbt-diagram-img').first.get_attribute('src')
                assert exp_img in src, f"ADDA-09 Q{q_idx+1}: expected {exp_img}, got {src}"
                nw = page.evaluate("document.querySelector('.cbt-diagram-img').naturalWidth")
                assert nw > 50, f"ADDA-09 Q{q_idx+1}: naturalWidth {nw} not > 50"
            print("PASS: ADDA-09 Q76-Q80 Quadratic formula images verified with naturalWidth > 0.")

            # 5. Scoring & Submit Verification for ADDA-09
            with open(ROOT / "data/licensed_adda/adda-09.json", encoding='utf-8') as f:
                d9 = json.load(f)
            q80_ans = d9['questions'][79]['answerIndex']
            q79_ans = d9['questions'][78]['answerIndex']

            # Jump to Q80 (index 79) and answer correctly
            page.locator('[data-adda-jump="79"]').click()
            page.wait_for_timeout(50)
            page.locator(f'.option-item[data-opt="{q80_ans}"]').click()
            page.locator('#addaSaveNext').click()

            # Jump to Q79 (index 78) and answer incorrectly
            page.locator('[data-adda-jump="78"]').click()
            page.wait_for_timeout(50)
            wrong_idx = (q79_ans + 1) % 5
            page.locator(f'.option-item[data-opt="{wrong_idx}"]').click()
            page.locator('#addaSaveNext').click()

            # Submit
            page.locator('#addaSubmitBtn').click()
            page.wait_for_selector('.result-dashboard')

            # Verify score: 1 correct (+1.00), 1 wrong (-0.25) -> net 0.75
            score_text = page.locator('.hero-score-value').inner_text()
            assert '0.75' in score_text, f"Expected 0.75 score, got {score_text}"
            print("PASS: ADDA-09 Scoring (+1.00 / -0.25 = 0.75) verified.")

            # Verify Solutions Review rendered
            review_cards = page.locator('.solution-card').count()
            assert review_cards == 80, f"Expected 80 solution cards, got {review_cards}"
            print("PASS: ADDA-09 Step-by-step solutions (80 cards) rendered in review mode.")


            # ======================== ADDA-10 ========================
            print("\n--- Verifying ADDA-10 in Browser CBT ---")
            page.evaluate("localStorage.clear()")
            page.goto(url, wait_until='networkidle')
            page.locator('#tabAdda').click()
            page.wait_for_timeout(200)

            # Start adda-10
            page.locator('[data-adda-start="adda-10"]').click()
            page.locator('#addaBeginMock').click()
            page.wait_for_selector('#addaTimerDisplay')

            # Jump to Quant section (Q41 -> index 40)
            page.evaluate("""() => {
                const s = JSON.parse(localStorage.getItem('rrbpo_adda_active_v1'));
                s.sectionIndex = 1;
                s.sectionEndAt = Date.now() + 1200000;
                s.currentIndex = 40;
                localStorage.setItem('rrbpo_adda_active_v1', JSON.stringify(s));
            }""")
            page.reload(wait_until='networkidle')
            if page.locator('#resumeAddaActiveBtn').count() == 1:
                page.locator('#resumeAddaActiveBtn').click()
            page.wait_for_selector('#addaTimerDisplay')

            # 1. Stacked fractions in Q42 and Q43
            page.locator('[data-adda-jump="41"]').click() # Q42
            page.wait_for_timeout(50)
            assert page.locator('.cbt-frac').count() >= 1, "ADDA-10 Q42: .cbt-frac not rendered"
            q42_frac_num = page.locator('.cbt-frac .cbt-num').first.inner_text()
            q42_frac_den = page.locator('.cbt-frac .cbt-den').first.inner_text()
            assert q42_frac_num == '1' and q42_frac_den == '3', f"ADDA-10 Q42: fraction mismatch {q42_frac_num}/{q42_frac_den}"

            page.locator('[data-adda-jump="42"]').click() # Q43
            page.wait_for_timeout(50)
            assert page.locator('.cbt-frac').count() >= 1, "ADDA-10 Q43: .cbt-frac not rendered"
            q43_frac_num = page.locator('.cbt-frac .cbt-num').first.inner_text()
            q43_frac_den = page.locator('.cbt-frac .cbt-den').first.inner_text()
            assert q43_frac_num == '1' and q43_frac_den == '9', f"ADDA-10 Q43: fraction mismatch {q43_frac_num}/{q43_frac_den}"
            print("PASS: ADDA-10 Q42 (1/3) and Q43 (1/9) stacked fractions (.cbt-frac) rendered correctly.")

            # 2. Approximation formulas Q46-50
            expected_adda10_approx = {
                45: 'adda-10_page21_Image108.png',
                46: 'adda-10_page21_Image109.png',
                47: 'adda-10_page22_Image114.png',
                48: 'adda-10_page22_Image115.png',
                49: 'adda-10_page22_Image116.png',
            }
            for q_idx, exp_img in expected_adda10_approx.items():
                page.locator(f'[data-adda-jump="{q_idx}"]').click()
                page.wait_for_timeout(50)
                assert page.locator('.cbt-diagram-img').count() >= 1, f"ADDA-10 Q{q_idx+1}: Approximation formula not found"
                src = page.locator('.cbt-diagram-img').first.get_attribute('src')
                assert exp_img in src, f"ADDA-10 Q{q_idx+1}: expected {exp_img}, got {src}"
                nw = page.evaluate("document.querySelector('.cbt-diagram-img').naturalWidth")
                assert nw > 50, f"ADDA-10 Q{q_idx+1}: naturalWidth {nw} not > 50"
            print("PASS: ADDA-10 Q46-Q50 Approximation formula images verified with naturalWidth > 0.")

            # 3. Employee Table Q64-68
            for q_idx in range(63, 68): # Q64-68
                page.locator(f'[data-adda-jump="{q_idx}"]').click()
                page.wait_for_timeout(50)
                assert page.locator('.cbt-diagram-img').count() >= 1, f"ADDA-10 Q{q_idx+1}: Employee table not found"
                src = page.locator('.cbt-diagram-img').first.get_attribute('src')
                assert 'adda-10_page26_Image133.png' in src, f"ADDA-10 Q{q_idx+1}: wrong diagram {src}"
                nw = page.evaluate("document.querySelector('.cbt-diagram-img').naturalWidth")
                assert nw > 150, f"ADDA-10 Q{q_idx+1}: naturalWidth {nw} not > 150"
            print("PASS: ADDA-10 Q64-Q68 Company Employee Table diagram verified with naturalWidth > 0.")

            # 4. Cupboard Bar Graph Q71-75
            for q_idx in range(70, 75): # Q71-75
                page.locator(f'[data-adda-jump="{q_idx}"]').click()
                page.wait_for_timeout(50)
                assert page.locator('.cbt-diagram-img').count() >= 1, f"ADDA-10 Q{q_idx+1}: Bar graph diagram not found"
                src = page.locator('.cbt-diagram-img').first.get_attribute('src')
                assert 'adda-10_page28_Image142.png' in src, f"ADDA-10 Q{q_idx+1}: wrong diagram {src}"
                nw = page.evaluate("document.querySelector('.cbt-diagram-img').naturalWidth")
                assert nw > 200, f"ADDA-10 Q{q_idx+1}: naturalWidth {nw} not > 200"
            print("PASS: ADDA-10 Q71-Q75 Cupboard Bar Graph verified with naturalWidth > 0.")

            # 5. Export Chart & Quadratic Formulas Q76-80
            expected_adda10_quad = {
                75: ('adda-10_page31_Image155.png', 'adda-10_page31_Image156.png'),
                76: ('adda-10_page31_Image155.png', 'adda-10_page31_Image157.png'),
                77: ('adda-10_page31_Image155.png', 'adda-10_page34_Image162.png'),
                78: ('adda-10_page31_Image155.png', 'adda-10_page34_Image163.png'),
                79: ('adda-10_page31_Image155.png', 'adda-10_page34_Image164.png'),
            }
            for q_idx, (exp_chart, exp_eq) in expected_adda10_quad.items():
                page.locator(f'[data-adda-jump="{q_idx}"]').click()
                page.wait_for_timeout(50)
                imgs = page.locator('.cbt-diagram-img')
                assert imgs.count() == 2, f"ADDA-10 Q{q_idx+1}: expected 2 diagrams (chart + formula), got {imgs.count()}"
                src0 = imgs.nth(0).get_attribute('src')
                src1 = imgs.nth(1).get_attribute('src')
                assert exp_chart in src0, f"ADDA-10 Q{q_idx+1}: expected chart {exp_chart}, got {src0}"
                assert exp_eq in src1, f"ADDA-10 Q{q_idx+1}: expected equation {exp_eq}, got {src1}"
                nw0 = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[0].naturalWidth")
                nw1 = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[1].naturalWidth")
                assert nw0 > 200 and nw1 > 50, f"ADDA-10 Q{q_idx+1}: naturalWidth invalid: nw0={nw0}, nw1={nw1}"
            print("PASS: ADDA-10 Q76-Q80 Export Chart & Quadratic Formula images verified with naturalWidth > 0.")

            # 6. Scoring & Submit Verification for ADDA-10
            with open(ROOT / "data/licensed_adda/adda-10.json", encoding='utf-8') as f:
                d10 = json.load(f)
            q80_ans = d10['questions'][79]['answerIndex']
            q79_ans = d10['questions'][78]['answerIndex']

            # Jump to Q80 (index 79) and answer correctly
            page.locator('[data-adda-jump="79"]').click()
            page.wait_for_timeout(50)
            page.locator(f'.option-item[data-opt="{q80_ans}"]').click()
            page.locator('#addaSaveNext').click()

            # Jump to Q79 (index 78) and answer incorrectly
            page.locator('[data-adda-jump="78"]').click()
            page.wait_for_timeout(50)
            wrong_idx = (q79_ans + 1) % 5
            page.locator(f'.option-item[data-opt="{wrong_idx}"]').click()
            page.locator('#addaSaveNext').click()

            # Submit
            page.locator('#addaSubmitBtn').click()
            page.wait_for_selector('.result-dashboard')

            # Verify score: 1 correct (+1.00), 1 wrong (-0.25) -> net 0.75
            score_text = page.locator('.hero-score-value').inner_text()
            assert '0.75' in score_text, f"Expected 0.75 score, got {score_text}"
            print("PASS: ADDA-10 Scoring (+1.00 / -0.25 = 0.75) verified.")

            # Verify Solutions Review rendered
            review_cards = page.locator('.solution-card').count()
            assert review_cards == 80, f"Expected 80 solution cards, got {review_cards}"
            print("PASS: ADDA-10 Step-by-step solutions (80 cards) rendered in review mode.")

            assert len(errors) == 0, f"Browser console errors encountered: {errors}"
            browser.close()

    finally:
        server.shutdown()
        server.server_close()

    print("\n" + "=" * 70)
    print("ALL VERIFICATIONS FOR ADDA-09 AND ADDA-10 PASSED WITH 100% SUCCESS!")
    print("=" * 70)

if __name__ == '__main__':
    run_browser_verification()
