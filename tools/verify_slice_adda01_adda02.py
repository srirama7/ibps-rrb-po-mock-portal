import json
import re
import os
import sys
import http.server
import socketserver
import threading
from pathlib import Path
from functools import partial
from playwright.sync_api import sync_playwright

ROOT = Path(r"C:\Users\amogh\ibps-rrb-portal-upgrade")

class Server(socketserver.TCPServer):
    allow_reuse_address = True

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

def audit_json(paper_id):
    path = ROOT / "data" / "licensed_adda" / f"{paper_id}.json"
    with open(path, encoding='utf-8') as f:
        data = json.load(f)

    questions = data['questions']
    assert len(questions) == 80, f"{paper_id}: Expected 80 questions, found {len(questions)}"

    # 1. Clean English check
    hindi_errors = []
    option_errors = []
    index_errors = []
    solution_errors = []

    for q in questions:
        qnum = q['number']
        texts = [q.get('stem', ''), q.get('explanation', '')] + q.get('options', [])
        for t in texts:
            if re.findall(r'[\u0900-\u097F]', t):
                hindi_errors.append((qnum, t[:50]))

        opts = q.get('options', [])
        if len(opts) != 5:
            option_errors.append((qnum, len(opts)))

        ans_idx = q.get('answerIndex')
        if ans_idx is None or not (0 <= ans_idx <= 4):
            index_errors.append((qnum, ans_idx))

        exp = q.get('explanation', '')
        if not exp or len(exp.strip()) < 10:
            solution_errors.append((qnum, "empty or too short"))

    print(f"[{paper_id}] JSON Audit:")
    print(f"  - Questions count: {len(questions)} (PASS)")
    print(f"  - Clean English (No Devanagari): {len(hindi_errors)} errors")
    assert not hindi_errors, f"Hindi text found: {hindi_errors}"
    print(f"  - Option count == 5: {len(option_errors)} errors")
    assert not option_errors, f"Invalid options: {option_errors}"
    print(f"  - Valid answerIndex (0-4): {len(index_errors)} errors")
    assert not index_errors, f"Invalid answer indices: {index_errors}"
    print(f"  - Step-by-step solutions present: {len(solution_errors)} errors")
    assert not solution_errors, f"Invalid explanations: {solution_errors}"

    return data

def run_browser_verification():
    server = Server(('127.0.0.1', 0), partial(Handler, directory=str(ROOT)))
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    url = f'http://127.0.0.1:{server.server_address[1]}/'
    print(f"Local server started at {url}")

    results = {}

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport=dict(width=1440, height=900))
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))

            # ----------------------------------------------------
            # VERIFY ADDA-01
            # ----------------------------------------------------
            print("\n================== TESTING ADDA-01 ==================")
            page.goto(url, wait_until='networkidle')
            page.locator('#tabAdda').click()
            page.wait_for_timeout(200)

            # Start adda-01
            page.locator('[data-adda-start="adda-01"]').click()
            page.wait_for_selector('#addaBeginMock')
            page.locator('#addaBeginMock').click()
            page.wait_for_selector('#addaTimerDisplay')

            # Jump to Quant Section (Q41)
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

            # (4) Check Mangoes markdown table for Q41-Q46
            print("Checking adda-01 Mangoes table (Q41-Q46)...")
            for q_idx in range(40, 46):
                page.locator(f'[data-adda-jump="{q_idx}"]').click()
                page.wait_for_timeout(80)
                tbl_count = page.locator('.cbt-rendered-table').count()
                assert tbl_count >= 1, f"adda-01 Q{q_idx+1}: .cbt-rendered-table missing!"
                # Check table headers and content
                th_text = page.locator('.cbt-rendered-table th').all_inner_texts()
                assert len(th_text) >= 2, f"adda-01 Q{q_idx+1}: Table headers empty!"
            print("  -> PASS: Mangoes markdown table rendered as .cbt-rendered-table on Q41-Q46")

            # (2) Check Fractions on Simplification questions (e.g. Q52)
            print("Checking adda-01 Fractions...")
            page.locator('[data-adda-jump="51"]').click() # Q52
            page.wait_for_timeout(80)
            frac_count = page.locator('.cbt-frac').count()
            assert frac_count >= 1, f"adda-01 Q52: .cbt-frac missing! Found {frac_count}"
            num_text = page.locator('.cbt-frac .cbt-num').first.inner_text()
            den_text = page.locator('.cbt-frac .cbt-den').first.inner_text()
            print(f"  -> PASS: Fraction span rendered properly (.cbt-frac with {num_text}/{den_text}) on Q52")

            # (3) Check Pie Chart diagram for Q76-Q80
            print("Checking adda-01 College Pie Chart (Q76-Q80)...")
            for q_idx in range(75, 80):
                page.locator(f'[data-adda-jump="{q_idx}"]').click()
                page.wait_for_timeout(80)
                img_count = page.locator('.cbt-diagram-img').count()
                assert img_count >= 1, f"adda-01 Q{q_idx+1}: .cbt-diagram-img missing!"
                nw = page.evaluate("document.querySelector('.cbt-diagram-img').naturalWidth")
                nh = page.evaluate("document.querySelector('.cbt-diagram-img').naturalHeight")
                assert nw > 0 and nh > 0, f"adda-01 Q{q_idx+1}: Diagram naturalWidth={nw}, naturalHeight={nh}"
            print(f"  -> PASS: College Pie Chart rendered with naturalWidth={nw}px, naturalHeight={nh}px across Q76-Q80")

            # (5) Test Scoring (+1.00 / -0.25) and Step-by-Step Solutions
            print("Testing adda-01 Scoring (+1.00 / -0.25) and Solutions...")
            # We will answer Q41 correctly and Q42 incorrectly, then submit
            # First check answerIndex of Q41 and Q42 in adda-01
            with open(ROOT / "data" / "licensed_adda" / "adda-01.json", encoding='utf-8') as f:
                p1 = json.load(f)
            q41_ans = p1['questions'][40]['answerIndex'] # 0-based
            q42_ans = p1['questions'][41]['answerIndex']
            q42_wrong = (q42_ans + 1) % 5

            # Jump to Q41 and select correct
            page.locator('[data-adda-jump="40"]').click()
            page.wait_for_timeout(80)
            page.locator('.option-item').nth(q41_ans).click()
            page.locator('#addaSaveNext').click()
            page.wait_for_timeout(80)

            # Now on Q42, select wrong
            page.locator('.option-item').nth(q42_wrong).click()
            page.locator('#addaSaveNext').click()
            page.wait_for_timeout(80)

            # Submit Test
            page.on('dialog', lambda d: d.accept())
            page.locator('#addaSubmitBtn').click()
            page.wait_for_selector('.result-dashboard')

            # Verify score: 1 correct (+1.00), 1 wrong (-0.25), 78 skipped (0) => 0.75 / 80.00
            score_text = page.locator('.hero-score-value').inner_text()
            print(f"  Total score rendered: '{score_text}'")
            assert "0.75" in score_text, f"Expected score 0.75, got {score_text}"

            # Verify solutions rendered (all 80 solution cards)
            sol_cards = page.locator('.solution-card').count()
            assert sol_cards == 80, f"Expected 80 solution cards, found {sol_cards}"
            print(f"  -> PASS: 80 solution cards rendered with step-by-step analysis")

            # Verify right/wrong tags
            assert page.locator('.sol-status-tag.correct').count() == 1
            assert page.locator('.sol-status-tag.wrong').count() == 1
            assert page.locator('.sol-status-tag.skipped').count() == 78
            print("  -> PASS: Scoring (+1.00 / -0.25 / 0.00) fully verified on adda-01")


            # ----------------------------------------------------
            # VERIFY ADDA-02
            # ----------------------------------------------------
            print("\n================== TESTING ADDA-02 ==================")
            # Clear storage and start fresh with adda-02
            page.goto(url, wait_until='networkidle')
            page.evaluate("""() => {
                localStorage.removeItem('rrbpo_adda_active_v1');
            }""")
            page.reload(wait_until='networkidle')
            page.locator('#tabAdda').click()
            page.wait_for_timeout(200)

            page.locator('[data-adda-start="adda-02"]').click()
            page.wait_for_selector('#addaBeginMock')
            page.locator('#addaBeginMock').click()
            page.wait_for_selector('#addaTimerDisplay')

            # Jump to Quant Section (Q41)
            page.evaluate("""() => {
                const s = JSON.parse(localStorage.getItem('rrbpo_adda_active_v1'));
                s.sectionIndex = 1;
                s.sectionEndAt = Date.now() + 1200000;
                s.currentIndex = 40;
                localStorage.setItem('rrbpo_adda_active_v1', JSON.stringify(s));
            }""")
            page.reload(wait_until='networkidle')
            if page.locator('#tabAdda').count() == 1:
                page.locator('#tabAdda').click()
            if page.locator('#resumeAddaActiveBtn').count() == 1:
                page.locator('#resumeAddaActiveBtn').click()
            page.wait_for_selector('#addaTimerDisplay')

            # (3) Formula images Q41-Q45
            print("Checking adda-02 Formula images (Q41-Q45)...")
            for q_idx in range(40, 45):
                page.locator(f'[data-adda-jump="{q_idx}"]').click()
                page.wait_for_timeout(80)
                img_count = page.locator('.cbt-diagram-img').count()
                assert img_count >= 1, f"adda-02 Q{q_idx+1}: .cbt-diagram-img missing!"
                nw = page.evaluate("document.querySelector('.cbt-diagram-img').naturalWidth")
                nh = page.evaluate("document.querySelector('.cbt-diagram-img').naturalHeight")
                assert nw > 0 and nh > 0, f"adda-02 Q{q_idx+1}: Formula naturalWidth={nw}, naturalHeight={nh}"
            print(f"  -> PASS: Formula images rendered with naturalWidth={nw}px across Q41-Q45")

            # (3) Cupboard line graph Q46-Q51
            print("Checking adda-02 Cupboard Line Graph (Q46-Q51)...")
            for q_idx in range(45, 51):
                page.locator(f'[data-adda-jump="{q_idx}"]').click()
                page.wait_for_timeout(80)
                img_count = page.locator('.cbt-diagram-img').count()
                assert img_count >= 1, f"adda-02 Q{q_idx+1}: .cbt-diagram-img missing!"
                nw = page.evaluate("document.querySelector('.cbt-diagram-img').naturalWidth")
                nh = page.evaluate("document.querySelector('.cbt-diagram-img').naturalHeight")
                assert nw > 0 and nh > 0, f"adda-02 Q{q_idx+1}: Line graph naturalWidth={nw}, naturalHeight={nh}"
            print(f"  -> PASS: Cupboard line graph rendered with naturalWidth={nw}px across Q46-Q51")

            # (4) Companies table Q57-Q62
            print("Checking adda-02 Companies Markdown Table (Q57-Q62)...")
            for q_idx in range(56, 62):
                page.locator(f'[data-adda-jump="{q_idx}"]').click()
                page.wait_for_timeout(80)
                tbl_count = page.locator('.cbt-rendered-table').count()
                assert tbl_count >= 1, f"adda-02 Q{q_idx+1}: .cbt-rendered-table missing!"
                th_text = page.locator('.cbt-rendered-table th').all_inner_texts()
                assert len(th_text) >= 2, f"adda-02 Q{q_idx+1}: Table headers empty!"
            print("  -> PASS: Companies table rendered as .cbt-rendered-table across Q57-Q62")

            # (2) Check Fractions on adda-02
            print("Checking adda-02 Fractions...")
            # Let's find questions with fractions in adda-02
            with open(ROOT / "data" / "licensed_adda" / "adda-02.json", encoding='utf-8') as f:
                p2 = json.load(f)
            frac_q_indices = []
            for idx, q in enumerate(p2['questions']):
                if re.search(r'\d+\s*/\s*\d+', q['stem']):
                    frac_q_indices.append(idx)
            print(f"  Questions with fractions in adda-02: {[i+1 for i in frac_q_indices]}")
            if frac_q_indices:
                test_q_idx = frac_q_indices[0]
                page.locator(f'[data-adda-jump="{test_q_idx}"]').click()
                page.wait_for_timeout(80)
                frac_count = page.locator('.cbt-frac').count()
                assert frac_count >= 1, f"adda-02 Q{test_q_idx+1}: .cbt-frac missing!"
                print(f"  -> PASS: Stacked fraction (.cbt-frac) verified on Q{test_q_idx+1}")

            # (5) Scoring and Solutions verification on adda-02
            print("Testing adda-02 Scoring (+1.00 / -0.25) and Solutions...")
            q41_ans = p2['questions'][40]['answerIndex']
            q42_ans = p2['questions'][41]['answerIndex']
            q43_ans = p2['questions'][42]['answerIndex']
            q42_wrong = (q42_ans + 1) % 5
            q43_wrong = (q43_ans + 2) % 5

            # 2 correct (Q41, Q44), 2 wrong (Q42, Q43)
            # Correct: Q41
            page.locator('[data-adda-jump="40"]').click()
            page.wait_for_timeout(80)
            page.locator('.option-item').nth(q41_ans).click()
            page.locator('#addaSaveNext').click()

            # Wrong: Q42
            page.locator('.option-item').nth(q42_wrong).click()
            page.locator('#addaSaveNext').click()

            # Wrong: Q43
            page.locator('.option-item').nth(q43_wrong).click()
            page.locator('#addaSaveNext').click()

            # Correct: Q44
            q44_ans = p2['questions'][43]['answerIndex']
            page.locator('.option-item').nth(q44_ans).click()
            page.locator('#addaSaveNext').click()

            # Submit
            page.locator('#addaSubmitBtn').click()
            page.wait_for_selector('.result-dashboard')

            # Expected score: 2 * 1.00 - 2 * 0.25 = 1.50
            score_text = page.locator('.hero-score-value').inner_text()
            print(f"  Total score rendered: '{score_text}'")
            assert "1.50" in score_text, f"Expected score 1.50, got {score_text}"

            # Solution cards count
            sol_cards = page.locator('.solution-card').count()
            assert sol_cards == 80, f"Expected 80 solution cards, found {sol_cards}"
            assert page.locator('.sol-status-tag.correct').count() == 2
            assert page.locator('.sol-status-tag.wrong').count() == 2
            assert page.locator('.sol-status-tag.skipped').count() == 76
            print("  -> PASS: Scoring (+1.00 / -0.25 / 0.00) and step-by-step solutions verified on adda-02")

            assert not errors, f"Browser errors logged: {errors}"
            browser.close()

    finally:
        server.shutdown()
        server.server_close()

    print("\n========================================================")
    print("ALL VERIFICATION CHECKS PASSED FOR ADDA-01 AND ADDA-02!!")
    print("========================================================")

if __name__ == "__main__":
    audit_json("adda-01")
    audit_json("adda-02")
    run_browser_verification()
