import json, os, re, sys, threading, http.server, socketserver
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

def test_static_data():
    print("=" * 60)
    print("STEP 1: STATIC DATA VALIDATION (adda-07 & adda-08)")
    print("=" * 60)

    for pid in ['adda-07', 'adda-08']:
        filepath = ROOT / f"data/licensed_adda/{pid}.json"
        assert filepath.exists(), f"File {filepath} not found!"
        with open(filepath, encoding='utf-8') as f:
            data = json.load(f)

        assert len(data['questions']) == 80, f"{pid}: expected 80 questions, got {len(data['questions'])}"
        print(f"[{pid}] 80 questions present.")

        devanagari_pattern = re.compile(r'[\u0900-\u097F]')
        for q in data['questions']:
            qnum = q['number']
            assert qnum >= 1 and qnum <= 80, f"Invalid qnum: {qnum}"
            assert len(q['options']) == 5, f"{pid} Q{qnum}: Options count {len(q['options'])} != 5"
            assert q['answerIndex'] in range(5), f"{pid} Q{qnum}: Invalid answerIndex {q['answerIndex']}"
            assert len(q.get('explanation', '').strip()) >= 15, f"{pid} Q{qnum}: Solution too short (<15 chars)"

            # Check clean English (no Devanagari)
            all_text = q['stem'] + " " + " ".join(q['options']) + " " + q.get('explanation', '')
            match = devanagari_pattern.search(all_text)
            assert not match, f"{pid} Q{qnum}: Devanagari text detected: {match.group()}"

            # Check diagram files exist on disk
            for d in q.get('diagrams', []):
                d_path = ROOT / d.replace('/', os.sep)
                assert d_path.exists(), f"{pid} Q{qnum}: Image not found on disk: {d_path}"
                assert d_path.stat().st_size > 0, f"{pid} Q{qnum}: Empty image file: {d_path}"
                with Image.open(d_path) as im:
                    w, h = im.size
                    assert w > 0 and h > 0, f"{pid} Q{qnum}: Corrupted image dimensions: {w}x{h}"

        print(f"[{pid}] All 80 questions 100% clean English, 5 options, answerIndex 0-4, solutions verified, diagrams verified on disk.")

def test_browser():
    print("\n" + "=" * 60)
    print("STEP 2: CBT PLAYWRIGHT BROWSER VERIFICATION (adda-07 & adda-08)")
    print("=" * 60)

    server = Server(('127.0.0.1', 0), partial(Handler, directory=str(ROOT)))
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    port = server.server_address[1]
    url = f'http://127.0.0.1:{port}/'

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport=dict(width=1440, height=1000))
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('dialog', lambda dialog: dialog.accept())

            # ==================== VERIFY ADDA-07 ====================
            print("\n---> VERIFYING ADDA-07 IN CBT UI")
            page.goto(url, wait_until='networkidle')
            page.locator('#tabAdda').click()
            page.wait_for_timeout(200)

            # Start adda-07
            page.locator('[data-adda-start="adda-07"]').click()
            page.locator('#addaBeginMock').click()
            page.wait_for_selector('#addaTimerDisplay')

            # Jump to Quant section (Q41)
            page.evaluate("""() => {
              const s = JSON.parse(localStorage.getItem('rrbpo_adda_active_v1'));
              s.sectionIndex = 1;
              s.sectionEndAt = Date.now() + 1200000;
              s.currentIndex = 40; // 0-based Q41
              localStorage.setItem('rrbpo_adda_active_v1', JSON.stringify(s));
            }""")
            page.reload(wait_until='networkidle')
            if page.locator('#resumeAddaActiveBtn').count() == 1:
                page.locator('#resumeAddaActiveBtn').click()
            page.wait_for_selector('#addaTimerDisplay')

            # Check Q41-46 Villages Pie Charts
            for q_idx in range(40, 46):
                page.locator(f'[data-adda-jump="{q_idx}"]').click()
                page.wait_for_timeout(80)
                imgs = page.locator('.cbt-diagram-img')
                assert imgs.count() == 2, f"adda-07 Q{q_idx+1}: Expected 2 pie charts, found {imgs.count()}"
                nw0 = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[0].naturalWidth")
                nw1 = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[1].naturalWidth")
                assert nw0 > 100 and nw1 > 100, f"adda-07 Q{q_idx+1}: naturalWidth failed: {nw0}, {nw1}"
            print("PASS: adda-07 Q41-46 Villages Pie Charts verified (naturalWidth > 100px).")

            # Check Q51-55 Cities Bar Graphs
            for q_idx in range(50, 55):
                page.locator(f'[data-adda-jump="{q_idx}"]').click()
                page.wait_for_timeout(80)
                imgs = page.locator('.cbt-diagram-img')
                assert imgs.count() == 2, f"adda-07 Q{q_idx+1}: Expected 2 bar graphs, found {imgs.count()}"
                nw0 = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[0].naturalWidth")
                nw1 = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[1].naturalWidth")
                assert nw0 > 100 and nw1 > 100, f"adda-07 Q{q_idx+1}: naturalWidth failed: {nw0}, {nw1}"
            print("PASS: adda-07 Q51-55 Cities Bar Graphs verified (naturalWidth > 100px).")

            # Check Q53 Stacked Fractions (.cbt-frac, .cbt-num, .cbt-den)
            page.locator('[data-adda-jump="52"]').click()
            page.wait_for_timeout(80)
            frac_count = page.locator('.cbt-frac').count()
            assert frac_count >= 1, f"adda-07 Q53: .cbt-frac not rendered (found {frac_count})"
            num_text = page.locator('.cbt-frac .cbt-num').first.inner_text()
            den_text = page.locator('.cbt-frac .cbt-den').first.inner_text()
            assert num_text == '3' and den_text == '4', f"adda-07 Q53: fraction content mismatch ({num_text}/{den_text})"
            print("PASS: adda-07 Q53 Stacked Fraction rendered properly (.cbt-frac with 3/4).")

            # Check Q56-65 Quadratic & Approx formula images
            for q_idx in range(55, 65):
                page.locator(f'[data-adda-jump="{q_idx}"]').click()
                page.wait_for_timeout(80)
                imgs = page.locator('.cbt-diagram-img')
                assert imgs.count() >= 1, f"adda-07 Q{q_idx+1}: Formula image not rendered"
                nw = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[0].naturalWidth")
                assert nw > 50, f"adda-07 Q{q_idx+1}: Formula image naturalWidth failed: {nw}"
            print("PASS: adda-07 Q56-65 Quadratic & Approx formula images verified (naturalWidth > 50px).")

            # Test Scoring and Solution Review for adda-07
            # Answer Q56 correctly, Q57 incorrectly
            with open(ROOT / "data/licensed_adda/adda-07.json", encoding='utf-8') as f:
                d07 = json.load(f)
            q56_ans = d07['questions'][55]['answerIndex']
            q57_ans = d07['questions'][56]['answerIndex']

            # Answer Q56 correctly
            page.locator(f'[data-adda-jump="55"]').click()
            page.wait_for_timeout(80)
            page.locator(f'.option-item[data-opt="{q56_ans}"]').click()
            page.locator('#addaSaveNext').click()
            page.wait_for_timeout(80)

            # Answer Q57 incorrectly (different option)
            wrong_opt = (q57_ans + 1) % 5
            page.locator(f'.option-item[data-opt="{wrong_opt}"]').click()
            page.locator('#addaSaveNext').click()
            page.wait_for_timeout(80)

            # Submit exam
            page.locator('#addaSubmitBtn').click()
            page.wait_for_selector('.result-dashboard')

            # Verify score breakdown: 1 correct (+1.00), 1 incorrect (-0.25) -> net 0.75
            summary_text = page.locator('.result-dashboard').inner_text()
            assert "0.75" in summary_text, f"Expected net score 0.75 in summary, got: {summary_text[:300]}"
            assert "+1.00" in summary_text and ("-0.25" in summary_text or "−0.25" in summary_text or "0.25" in summary_text), "Scoring indicators missing in summary"

            # Verify solution review screen
            rev_cards = page.locator('.solution-card')
            assert rev_cards.count() == 80, f"Expected 80 solution cards, got {rev_cards.count()}"
            expl_56 = page.locator('.solution-card').nth(55).inner_text()
            assert "Step-by-Step Analysis & Solution" in expl_56 or "Explanation" in expl_56, "Solution card missing solution text"
            print("PASS: adda-07 Scoring (+1.00/-0.25 = 0.75 net) and 80 solution cards verified.")

            # ==================== VERIFY ADDA-08 ====================
            print("\n---> VERIFYING ADDA-08 IN CBT UI")
            page.evaluate("localStorage.clear()")
            page.goto(url, wait_until='networkidle')
            page.locator('#tabAdda').click()
            page.wait_for_timeout(200)

            # Start adda-08
            page.locator('[data-adda-start="adda-08"]').click()
            page.locator('#addaBeginMock').click()
            page.wait_for_selector('#addaTimerDisplay')

            # Advance to Quant (Q41)
            page.evaluate("""() => {
              const s = JSON.parse(localStorage.getItem('rrbpo_adda_active_v1'));
              s.sectionIndex = 1;
              s.sectionEndAt = Date.now() + 1200000;
              s.currentIndex = 40; // 0-based Q41
              localStorage.setItem('rrbpo_adda_active_v1', JSON.stringify(s));
            }""")
            page.reload(wait_until='networkidle')
            if page.locator('#resumeAddaActiveBtn').count() == 1:
                page.locator('#resumeAddaActiveBtn').click()
            page.wait_for_selector('#addaTimerDisplay')

            # Check Q41-45 Physics Table images
            for q_idx in range(40, 45):
                page.locator(f'[data-adda-jump="{q_idx}"]').click()
                page.wait_for_timeout(80)
                imgs = page.locator('.cbt-diagram-img')
                assert imgs.count() == 2, f"adda-08 Q{q_idx+1}: Expected 2 table images, found {imgs.count()}"
                nw0 = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[0].naturalWidth")
                nw1 = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[1].naturalWidth")
                assert nw0 > 100 and nw1 > 100, f"adda-08 Q{q_idx+1}: naturalWidth failed: {nw0}, {nw1}"
            print("PASS: adda-08 Q41-45 Physics Table images verified (naturalWidth > 100px).")

            # Check Q46-50 Villages Pie Charts
            for q_idx in range(45, 50):
                page.locator(f'[data-adda-jump="{q_idx}"]').click()
                page.wait_for_timeout(80)
                imgs = page.locator('.cbt-diagram-img')
                assert imgs.count() == 2, f"adda-08 Q{q_idx+1}: Expected 2 pie charts, found {imgs.count()}"
                nw0 = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[0].naturalWidth")
                nw1 = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[1].naturalWidth")
                assert nw0 > 100 and nw1 > 100, f"adda-08 Q{q_idx+1}: naturalWidth failed: {nw0}, {nw1}"
            print("PASS: adda-08 Q46-50 Villages Pie Charts verified (naturalWidth > 100px).")

            # Check Q48 and Q49 Stacked Fractions
            page.locator('[data-adda-jump="47"]').click() # Q48
            page.wait_for_timeout(80)
            frac_count = page.locator('.cbt-frac').count()
            assert frac_count >= 1, f"adda-08 Q48: .cbt-frac not rendered (found {frac_count})"
            print("PASS: adda-08 Q48 Stacked Fractions verified.")

            # Check Q51-60 Quadratic & Approx formula images
            for q_idx in range(50, 60):
                page.locator(f'[data-adda-jump="{q_idx}"]').click()
                page.wait_for_timeout(80)
                imgs = page.locator('.cbt-diagram-img')
                assert imgs.count() >= 1, f"adda-08 Q{q_idx+1}: Formula image not rendered"
                nw = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[0].naturalWidth")
                assert nw > 50, f"adda-08 Q{q_idx+1}: Formula image naturalWidth failed: {nw}"
            print("PASS: adda-08 Q51-60 Quadratic & Approx formula images verified (naturalWidth > 50px).")

            # Test Scoring and Solution Review for adda-08
            with open(ROOT / "data/licensed_adda/adda-08.json", encoding='utf-8') as f:
                d08 = json.load(f)
            q51_ans = d08['questions'][50]['answerIndex']
            q52_ans = d08['questions'][51]['answerIndex']

            # Answer Q51 correctly
            page.locator(f'[data-adda-jump="50"]').click()
            page.wait_for_timeout(80)
            page.locator(f'.option-item[data-opt="{q51_ans}"]').click()
            page.locator('#addaSaveNext').click()
            page.wait_for_timeout(80)

            # Answer Q52 incorrectly
            wrong_opt2 = (q52_ans + 1) % 5
            page.locator(f'.option-item[data-opt="{wrong_opt2}"]').click()
            page.locator('#addaSaveNext').click()
            page.wait_for_timeout(80)

            # Submit exam
            page.locator('#addaSubmitBtn').click()
            page.wait_for_selector('.result-dashboard')

            # Verify score breakdown: 1 correct (+1.00), 1 incorrect (-0.25) -> net 0.75
            summary_text2 = page.locator('.result-dashboard').inner_text()
            assert "0.75" in summary_text2, f"Expected net score 0.75 in summary, got: {summary_text2[:300]}"
            assert "+1.00" in summary_text2 and ("-0.25" in summary_text2 or "−0.25" in summary_text2 or "0.25" in summary_text2), "Scoring indicators missing in summary"

            # Verify solution review screen
            rev_cards2 = page.locator('.solution-card')
            assert rev_cards2.count() == 80, f"Expected 80 solution cards, got {rev_cards2.count()}"
            expl_51 = page.locator('.solution-card').nth(50).inner_text()
            assert "Step-by-Step Analysis & Solution" in expl_51 or "Explanation" in expl_51, "Solution card missing solution text"
            print("PASS: adda-08 Scoring (+1.00/-0.25 = 0.75 net) and 80 solution cards verified.")

            # ==================== VERIFY MARKDOWN TABLE RENDERING ====================
            print("\n---> VERIFYING MARKDOWN TABLE RENDERING IN CBT ENGINE")
            page.evaluate("localStorage.clear()")
            page.goto(url, wait_until='networkidle')
            page.locator('#tabAdda').click()
            page.wait_for_timeout(200)
            page.locator('[data-adda-start="adda-01"]').click()
            page.locator('#addaBeginMock').click()
            page.wait_for_selector('#addaTimerDisplay')
            # Jump to Q41
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
            tbl = page.locator('.cbt-rendered-table')
            assert tbl.count() >= 1, "Markdown table not rendered as .cbt-rendered-table"
            tbl_text = tbl.inner_text()
            assert "480" in tbl_text and "75%" in tbl_text, f"Unexpected table content: {tbl_text}"
            print("PASS: Markdown tables verified rendering as .cbt-rendered-table.")

            assert not errors, f"Page errors encountered: {errors}"
            browser.close()
    finally:
        server.shutdown()
        server.server_close()

    print("\n" + "=" * 60)
    print("ALL VERIFICATIONS COMPLETED AND PASSED FOR ADDA-07 & ADDA-08!")
    print("=" * 60)

if __name__ == '__main__':
    test_static_data()
    test_browser()
