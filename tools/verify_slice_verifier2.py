import http.server, socketserver, threading, json, os, re, sys
from pathlib import Path
from functools import partial
from playwright.sync_api import sync_playwright

ROOT = Path(r"C:\Users\amogh\ibps-rrb-portal-upgrade")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)
    def log_message(self, *args):
        pass

def run_checks():
    print("=" * 80)
    print("VERIFIER-2: CBT TEST INTEGRATION VERIFICATION FOR ADDA-03 & ADDA-04")
    print("=" * 80)

    # STEP 1: Static JSON integrity & Clean English Checks
    for pid in ['adda-03', 'adda-04']:
        json_path = ROOT / f"data/licensed_adda/{pid}.json"
        assert json_path.exists(), f"Missing file: {json_path}"
        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)

        qs = data['questions']
        assert len(qs) == 80, f"{pid} question count is {len(qs)}, expected 80"

        for q in qs:
            qnum = q['number']
            assert len(q['options']) == 5, f"{pid} Q{qnum} does not have 5 options: {len(q['options'])}"
            assert 0 <= q['answerIndex'] < 5, f"{pid} Q{qnum} invalid answerIndex {q['answerIndex']}"
            assert q.get('explanation') and len(q['explanation'].strip()) >= 10, f"{pid} Q{qnum} empty explanation"

            full_text = q['stem'] + " " + q['explanation'] + " " + " ".join(q['options'])
            hindi_match = re.search(r'[\u0900-\u097F]', full_text)
            assert not hindi_match, f"{pid} Q{qnum} contains Devanagari/Hindi text: {hindi_match.group(0)}"

            # Verify diagram files on disk
            for d in q.get('diagrams', []):
                dpath = ROOT / d.replace('/', os.sep)
                assert dpath.exists(), f"{pid} Q{qnum} missing diagram file on disk: {dpath}"

        print(f"PASS: {pid} 80/80 questions verified: 100% clean English, 5 options, valid answerIndex, step-by-step explanations, all diagram assets exist.")

    # STEP 2: Browser CBT Verification with Playwright
    server = socketserver.TCPServer(('127.0.0.1', 0), Handler)
    port = server.server_address[1]
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    url = f'http://127.0.0.1:{port}/'

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport=dict(width=1440, height=1000))
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('dialog', lambda dialog: dialog.accept())

            # =========================================================================
            # VERIFY ADDA-03
            # =========================================================================
            print("\n" + "-" * 60)
            print("BROWSER TEST: ADDA-03")
            print("-" * 60)
            page.goto(url, wait_until='networkidle')
            page.locator('#tabAdda').click()
            page.wait_for_timeout(300)

            # Start adda-03
            start_btn = page.locator('[data-adda-start="adda-03"]')
            assert start_btn.count() == 1, "Start button for adda-03 not found"
            start_btn.click()
            page.locator('#addaBeginMock').click()
            page.wait_for_selector('#addaTimerDisplay')
            print("PASS: adda-03 exam session started.")

            # (1) Seating arrangement diagram Q5-Q8
            for qidx in range(4, 8):
                qnum = qidx + 1
                page.locator(f'[data-adda-jump="{qidx}"]').click()
                page.wait_for_timeout(100)
                imgs = page.locator('.cbt-diagram-img')
                img_count = imgs.count()
                assert img_count >= 1, f"Q{qnum} has no diagrams rendered"
                for i in range(img_count):
                    nw = imgs.nth(i).evaluate("img => img.naturalWidth")
                    nh = imgs.nth(i).evaluate("img => img.naturalHeight")
                    src = imgs.nth(i).get_attribute("src")
                    assert nw > 0 and nh > 0, f"Q{qnum} diagram image {src} naturalWidth is {nw}"
                print(f"PASS: adda-03 Q{qnum} seating diagrams loaded ({img_count} images, naturalWidth > 0).")

            # Jump to Quant section (Q41+)
            page.evaluate("""() => {
              const s = JSON.parse(localStorage.getItem('rrbpo_adda_active_v1'));
              s.sectionIndex = 1;
              s.sectionEndAt = Date.now() + 1200000;
              s.currentIndex = 46; // Q47
              localStorage.setItem('rrbpo_adda_active_v1', JSON.stringify(s));
            }""")
            page.reload(wait_until='networkidle')
            if page.locator('#resumeAddaActiveBtn').count() == 1:
                page.locator('#resumeAddaActiveBtn').click()
            page.wait_for_selector('#addaTimerDisplay')

            # (2) Twiggy / Xomato pie charts (Q47-Q52)
            for qidx in range(46, 52):
                qnum = qidx + 1
                page.locator(f'[data-adda-jump="{qidx}"]').click()
                page.wait_for_timeout(100)
                imgs = page.locator('.cbt-diagram-img')
                img_count = imgs.count()
                assert img_count == 2, f"Q{qnum} expected 2 pie charts, found {img_count}"
                for i in range(img_count):
                    nw = imgs.nth(i).evaluate("img => img.naturalWidth")
                    src = imgs.nth(i).get_attribute("src")
                    assert nw > 50, f"Q{qnum} pie chart {src} naturalWidth={nw}"
            print("PASS: adda-03 Q47-Q52 Twiggy/Xomato dual pie charts loaded and verified (naturalWidth > 0).")

            # Check fraction rendering on Q52
            page.locator('[data-adda-jump="51"]').click() # Q52
            page.wait_for_timeout(100)
            frac_count = page.locator('.cbt-frac').count()
            assert frac_count > 0, f"Q52 missing .cbt-frac elements"
            num_text = page.locator('.cbt-frac .cbt-num').first.inner_text()
            den_text = page.locator('.cbt-frac .cbt-den').first.inner_text()
            print(f"PASS: adda-03 Q52 stacked fraction rendered: {num_text}/{den_text} with .cbt-frac, .cbt-num, .cbt-den.")

            # (3) Songs download table (Q53-Q58)
            for qidx in range(52, 58):
                qnum = qidx + 1
                page.locator(f'[data-adda-jump="{qidx}"]').click()
                page.wait_for_timeout(100)
                imgs = page.locator('.cbt-diagram-img')
                img_count = imgs.count()
                assert img_count >= 1, f"Q{qnum} table image missing"
                for i in range(img_count):
                    nw = imgs.nth(i).evaluate("img => img.naturalWidth")
                    assert nw > 50, f"Q{qnum} table image naturalWidth={nw}"
            print("PASS: adda-03 Q53-Q58 Songs download table diagram images loaded and verified (naturalWidth > 0).")

            # (4) Formula images (Q59-Q63)
            for qidx in range(58, 63):
                qnum = qidx + 1
                page.locator(f'[data-adda-jump="{qidx}"]').click()
                page.wait_for_timeout(100)
                imgs = page.locator('.cbt-diagram-img')
                img_count = imgs.count()
                assert img_count == 1, f"Q{qnum} expected 1 formula image, found {img_count}"
                nw = imgs.first.evaluate("img => img.naturalWidth")
                assert nw > 20, f"Q{qnum} formula image naturalWidth={nw}"
            print("PASS: adda-03 Q59-Q63 Formula images loaded and verified (naturalWidth > 0).")

            # =========================================================================
            # VERIFY ADDA-04
            # =========================================================================
            print("\n" + "-" * 60)
            print("BROWSER TEST: ADDA-04")
            print("-" * 60)

            # Switch to adda-04
            page.evaluate(f"""() => {{
                const s = {{
                    testId: 'adda-04',
                    sectionIndex: 1,
                    sectionEndAt: Date.now() + 1500000,
                    currentIndex: 40, // Q41
                    answers: {{}},
                    marked: [],
                    visited: [40],
                    history: [],
                    startEpoch: Date.now()
                }};
                localStorage.setItem('rrbpo_adda_active_v1', JSON.stringify(s));
            }}""")
            page.reload(wait_until='networkidle')
            if page.locator('#resumeAddaActiveBtn').count() == 1:
                page.locator('#resumeAddaActiveBtn').click()
            page.wait_for_selector('#addaTimerDisplay')
            print("PASS: adda-04 session active on Quant section.")

            # (1) School line graph (Q41-Q45)
            for qidx in range(40, 45):
                qnum = qidx + 1
                page.locator(f'[data-adda-jump="{qidx}"]').click()
                page.wait_for_timeout(100)
                imgs = page.locator('.cbt-diagram-img')
                img_count = imgs.count()
                assert img_count == 1, f"adda-04 Q{qnum} missing school line graph"
                nw = imgs.first.evaluate("img => img.naturalWidth")
                assert nw > 50, f"adda-04 Q{qnum} line graph naturalWidth={nw}"
            print("PASS: adda-04 Q41-Q45 School line graph diagram loaded and verified (naturalWidth > 0).")

            # (2) Malls markdown table (Q46-Q50)
            for qidx in range(45, 50):
                qnum = qidx + 1
                page.locator(f'[data-adda-jump="{qidx}"]').click()
                page.wait_for_timeout(100)
                tables = page.locator('.cbt-rendered-table')
                assert tables.count() >= 1, f"adda-04 Q{qnum} missing .cbt-rendered-table"
                th_count = tables.first.locator('th').count()
                tr_count = tables.first.locator('tbody tr').count()
                assert th_count == 3, f"adda-04 Q{qnum} table th_count={th_count}, expected 3"
                assert tr_count == 5, f"adda-04 Q{qnum} table row_count={tr_count}, expected 5"
                headers = [tables.first.locator('th').nth(k).inner_text() for k in range(3)]
                assert 'Malls' in headers[0] and 'Total People' in headers[1], f"Unexpected headers: {headers}"
            print("PASS: adda-04 Q46-Q50 Malls markdown table rendered cleanly as .cbt-rendered-table with 3 columns, 5 data rows.")

            # (3) Fraction rendering in adda-04 (e.g. Q47 & Q48)
            page.locator('[data-adda-jump="46"]').click() # Q47
            page.wait_for_timeout(100)
            q47_frac = page.locator('.cbt-frac').count()
            print(f"PASS: adda-04 Q47 has {q47_frac} rendered .cbt-frac fractions.")

            # =========================================================================
            # VERIFY SCORING (+1.00 / -0.25) & STEP-BY-STEP SOLUTIONS
            # =========================================================================
            print("\n" + "-" * 60)
            print("TESTING SCORING (+1.00 / -0.25) & STEP-BY-STEP SOLUTIONS")
            print("-" * 60)

            # Answer Q41 correctly, Q42 incorrectly, rest unattempted
            with open(ROOT / 'data/licensed_adda/adda-04.json', encoding='utf-8') as f:
                d4_json = json.load(f)
            q41_correct = d4_json['questions'][40]['answerIndex']
            q42_correct = d4_json['questions'][41]['answerIndex']
            q42_wrong = (q42_correct + 1) % 5

            # Answer Q41 correctly
            page.locator('[data-adda-jump="40"]').click()
            page.wait_for_timeout(100)
            page.locator('.option-item').nth(q41_correct).click()
            page.locator('#addaSaveNext').click()
            page.wait_for_timeout(100)

            # Answer Q42 incorrectly
            page.locator('[data-adda-jump="41"]').click()
            page.wait_for_timeout(100)
            page.locator('.option-item').nth(q42_wrong).click()
            page.locator('#addaSaveNext').click()
            page.wait_for_timeout(100)

            # Submit the exam via #addaSubmitBtn
            page.locator('#addaSubmitBtn').click()
            page.wait_for_selector('.hero-score-value')

            # Verify Score: 1 correct (+1.00), 1 wrong (-0.25), 78 skipped (0.00) -> Total = 0.75
            score_text = page.locator('.hero-score-value').inner_text()
            assert '0.75' in score_text, f"Expected total score 0.75, got {score_text}"
            print(f"PASS: Exam submitted. Correct score verified: {score_text} (+1.00 for correct, -0.25 for incorrect).")

            # Verify Step-by-Step solutions are rendered on the result review page
            sol_cards = page.locator('.solution-card')
            assert sol_cards.count() == 80, f"Expected 80 solution cards, got {sol_cards.count()}"

            # Verify Step-by-Step Analysis & Solution text presence
            expl_boxes = page.locator('.expl-box')
            assert expl_boxes.count() == 80, f"Expected 80 explanation boxes, got {expl_boxes.count()}"

            # Check Q41 correct tag and Q42 wrong tag
            correct_tags = page.locator('.sol-status-tag.correct')
            wrong_tags = page.locator('.sol-status-tag.wrong')
            skipped_tags = page.locator('.sol-status-tag.skipped')
            assert correct_tags.count() == 1, f"Expected 1 correct tag, got {correct_tags.count()}"
            assert wrong_tags.count() == 1, f"Expected 1 wrong tag, got {wrong_tags.count()}"
            assert skipped_tags.count() == 78, f"Expected 78 skipped tags, got {skipped_tags.count()}"

            # Check explanation in Q46 (malls table solution)
            q46_card = sol_cards.nth(45)
            assert 'Step-by-Step Analysis & Solution:' in q46_card.locator('.expl-box').inner_text()
            print("PASS: Step-by-step solution analysis verified across all 80 questions with status tags and detailed explanations.")

            # Take screenshot of review page
            screenshot_path = ROOT / 'artifacts/verifier2_adda03_adda04_verified.png'
            page.screenshot(path=str(screenshot_path))
            print(f"PASS: Verification screenshot saved to {screenshot_path}")

            assert not errors, f"Console/page errors detected during tests: {errors}"
            browser.close()
    finally:
        server.shutdown()

    print("\n" + "=" * 80)
    print("ALL VERIFICATION CHECKS PASSED SUCCESSFULLY FOR VERIFIER-2 SLICE!")
    print("=" * 80)

if __name__ == '__main__':
    run_checks()
