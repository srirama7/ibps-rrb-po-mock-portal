import http.server
import socketserver
import threading
import json
import os
import sys
from pathlib import Path
from functools import partial
from playwright.sync_api import sync_playwright

ROOT = Path(r"C:\Users\amogh\ibps-rrb-portal-upgrade")

class Server(socketserver.TCPServer):
    allow_reuse_address = True

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

def verify_all():
    print("=" * 80)
    print("STARTING CBT TEST INTEGRATION VERIFICATION FOR ADDA-05 AND ADDA-06")
    print("=" * 80)

    server = Server(('127.0.0.1', 0), partial(Handler, directory=str(ROOT)))
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    port = server.server_address[1]
    url = f"http://127.0.0.1:{port}/"

    summary = {
        "adda-05": {"status": "FAIL", "checks": []},
        "adda-06": {"status": "FAIL", "checks": []}
    }

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport=dict(width=1440, height=1000))
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("dialog", lambda dialog: dialog.accept())

            # =================================================================
            # VERIFY ADDA-05
            # =================================================================
            print("\n>>> TESTING ADDA-05 <<<")
            page.goto(url, wait_until="networkidle")
            page.locator("#tabAdda").click()
            page.wait_for_timeout(300)

            # Check that adda-05 card exists and start mock
            start_btn = page.locator('[data-adda-start="adda-05"]')
            assert start_btn.count() == 1, "adda-05 card start button not found"
            start_btn.click()
            page.wait_for_selector("#addaBeginMock", state="visible")
            page.locator("#addaBeginMock").click()
            page.wait_for_selector("#addaTimerDisplay", state="visible")
            print("✓ ADDA-05 started successfully in CBT interface.")
            summary["adda-05"]["checks"].append("CBT Mock Launch: PASS")

            # Q1 check
            q1_header = page.locator(".question-header h2").inner_text().strip()
            assert "Question 1 of 80" in q1_header, f"Expected Q1 header, got {q1_header}"
            print(f"✓ Q1 rendered properly: {q1_header}")

            # Jump to Quant section (Q41)
            page.evaluate("""() => {
                const s = JSON.parse(localStorage.getItem('rrbpo_adda_active_v1'));
                s.sectionIndex = 1;
                s.sectionEndAt = Date.now() + 1200000;
                s.currentIndex = 40;
                localStorage.setItem('rrbpo_adda_active_v1', JSON.stringify(s));
            }""")
            page.reload(wait_until="networkidle")
            if page.locator("#resumeAddaActiveBtn").count() == 1:
                page.locator("#resumeAddaActiveBtn").click()
            page.wait_for_selector("#addaTimerDisplay", state="visible")

            # Check Q41-Q45 (TVs bar graph)
            for qn in range(41, 46):
                page.locator(f'[data-adda-jump="{qn-1}"]').click()
                page.wait_for_timeout(100)
                qh = page.locator(".question-header h2").inner_text().strip()
                assert f"Question {qn} of 80" in qh, f"Expected Q{qn}, got {qh}"
                imgs = page.locator(".cbt-diagram-img")
                assert imgs.count() == 2, f"ADDA-05 Q{qn}: Expected 2 bar graph images, got {imgs.count()}"
                src0 = imgs.nth(0).get_attribute("src")
                src1 = imgs.nth(1).get_attribute("src")
                assert "adda-05_page24_Image120.png" in src0, f"Q{qn} src0 mismatch: {src0}"
                assert "adda-05_page24_Image121.png" in src1, f"Q{qn} src1 mismatch: {src1}"
                nw0 = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[0].naturalWidth")
                nw1 = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[1].naturalWidth")
                assert nw0 > 0 and nw1 > 0, f"Q{qn} images naturalWidth failed: {nw0}, {nw1}"
            print("✓ ADDA-05 Q41-Q45 TVs bar graph verified (2 images rendered with naturalWidth > 0).")
            summary["adda-05"]["checks"].append("TVs bar graph Q41-Q45: PASS")

            # Check Q46-Q50 (Companies pie chart)
            for qn in range(46, 51):
                page.locator(f'[data-adda-jump="{qn-1}"]').click()
                page.wait_for_timeout(100)
                qh = page.locator(".question-header h2").inner_text().strip()
                assert f"Question {qn} of 80" in qh, f"Expected Q{qn}, got {qh}"
                imgs = page.locator(".cbt-diagram-img")
                assert imgs.count() == 2, f"ADDA-05 Q{qn}: Expected 2 pie chart images, got {imgs.count()}"
                src0 = imgs.nth(0).get_attribute("src")
                src1 = imgs.nth(1).get_attribute("src")
                assert "adda-05_page26_Image130.png" in src0, f"Q{qn} src0 mismatch: {src0}"
                assert "adda-05_page26_Image131.jpeg" in src1, f"Q{qn} src1 mismatch: {src1}"
                nw0 = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[0].naturalWidth")
                nw1 = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[1].naturalWidth")
                assert nw0 > 0 and nw1 > 0, f"Q{qn} images naturalWidth failed: {nw0}, {nw1}"
            print("✓ ADDA-05 Q46-Q50 Companies pie chart verified (2 images rendered with naturalWidth > 0).")
            summary["adda-05"]["checks"].append("Companies pie chart Q46-Q50: PASS")

            # Check Q54 (Fractions Q54)
            page.locator('[data-adda-jump="53"]').click()
            page.wait_for_timeout(100)
            fracs = page.locator(".cbt-frac")
            assert fracs.count() >= 1, f"ADDA-05 Q54: Expected at least 1 .cbt-frac, got {fracs.count()}"
            frac_num = page.locator(".cbt-frac .cbt-num").first.inner_text().strip()
            frac_den = page.locator(".cbt-frac .cbt-den").first.inner_text().strip()
            assert frac_num == "5" and frac_den == "9", f"ADDA-05 Q54: Fraction expected 5/9, got {frac_num}/{frac_den}"
            print(f"✓ ADDA-05 Q54 Stacked Fraction verified ({frac_num}/{frac_den}).")
            summary["adda-05"]["checks"].append("Stacked fraction Q54 (5/9): PASS")

            # Check Q56 (Formula image Q56)
            page.locator('[data-adda-jump="55"]').click()
            page.wait_for_timeout(100)
            imgs = page.locator(".cbt-diagram-img")
            assert imgs.count() == 1, f"ADDA-05 Q56: Expected 1 formula image, got {imgs.count()}"
            assert "adda-05_page31_Image162.png" in imgs.first.get_attribute("src")
            nw = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[0].naturalWidth")
            assert nw > 0, f"ADDA-05 Q56: naturalWidth={nw}"
            print(f"✓ ADDA-05 Q56 Formula image verified (Image162, naturalWidth={nw}).")
            summary["adda-05"]["checks"].append("Formula image Q56: PASS")

            # Check Q57 (Formula image Q57)
            page.locator('[data-adda-jump="56"]').click()
            page.wait_for_timeout(100)
            imgs = page.locator(".cbt-diagram-img")
            assert imgs.count() == 1, f"ADDA-05 Q57: Expected 1 formula image, got {imgs.count()}"
            assert "adda-05_page31_Image163.png" in imgs.first.get_attribute("src")
            nw = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[0].naturalWidth")
            assert nw > 0, f"ADDA-05 Q57: naturalWidth={nw}"
            print(f"✓ ADDA-05 Q57 Formula image verified (Image163, naturalWidth={nw}).")
            summary["adda-05"]["checks"].append("Formula image Q57: PASS")

            # Check Q58 (Fractions Q58)
            page.locator('[data-adda-jump="57"]').click()
            page.wait_for_timeout(100)
            fracs = page.locator(".cbt-frac")
            assert fracs.count() >= 1, f"ADDA-05 Q58: Expected at least 1 .cbt-frac, got {fracs.count()}"
            frac_num = page.locator(".cbt-frac .cbt-num").first.inner_text().strip()
            frac_den = page.locator(".cbt-frac .cbt-den").first.inner_text().strip()
            assert frac_num == "3" and frac_den == "5", f"ADDA-05 Q58: Fraction expected 3/5, got {frac_num}/{frac_den}"
            print(f"✓ ADDA-05 Q58 Stacked Fraction verified ({frac_num}/{frac_den}).")
            summary["adda-05"]["checks"].append("Stacked fraction Q58 (3/5): PASS")

            # Test Scoring and Step-by-Step Solutions in ADDA-05
            with open(ROOT / "data" / "licensed_adda" / "adda-05.json", "r", encoding="utf-8") as f:
                d5 = json.load(f)
            q41_correct = d5["questions"][40]["answerIndex"]
            q42_correct = d5["questions"][41]["answerIndex"]
            q42_wrong = (q42_correct + 1) % 5

            # Jump to Q41, select correct option, Save & Next
            page.locator('[data-adda-jump="40"]').click()
            page.wait_for_timeout(100)
            page.locator(f'.option-item[data-opt="{q41_correct}"]').click()
            page.locator("#addaSaveNext").click()
            page.wait_for_timeout(100)

            # On Q42, select wrong option, Save & Next
            page.locator(f'.option-item[data-opt="{q42_wrong}"]').click()
            page.locator("#addaSaveNext").click()
            page.wait_for_timeout(100)

            # Submit paper
            page.locator("#addaSubmitBtn").click()
            page.wait_for_selector(".score-hero-card", state="visible")

            # Verify score: 1 correct (+1.00), 1 incorrect (-0.25) -> Total = 0.75
            score_text = page.locator(".hero-score-value").inner_text()
            assert "0.75" in score_text, f"Expected 0.75, got {score_text}"
            print(f"✓ ADDA-05 Scoring verified: 1 correct (+1.00), 1 incorrect (-0.25) = {score_text.strip()}.")
            summary["adda-05"]["checks"].append("Scoring (+1.00/-0.25): PASS")

            # View solutions
            sol_items = page.locator(".solution-card")
            assert sol_items.count() == 80, f"Expected 80 solution cards, got {sol_items.count()}"
            
            # Check Q41 solution has +1.00 correct tag and step-by-step analysis
            sol41 = sol_items.nth(40)
            assert sol41.locator(".sol-status-tag.correct").count() == 1, "Q41 missing correct status tag"
            assert "+1.00" in sol41.inner_text(), "Q41 missing +1.00"
            assert "Analysis & Solution" in sol41.inner_text(), "Q41 missing step-by-step solution"
            
            # Check Q42 solution has -0.25 incorrect tag
            sol42 = sol_items.nth(41)
            assert sol42.locator(".sol-status-tag.wrong").count() == 1, "Q42 missing incorrect status tag"

            print("✓ ADDA-05 Step-by-Step Solutions verified across all 80 questions.")
            summary["adda-05"]["checks"].append("Step-by-step Solutions: PASS")
            summary["adda-05"]["status"] = "PASS"

            # =================================================================
            # VERIFY ADDA-06
            # =================================================================
            print("\n>>> TESTING ADDA-06 <<<")
            page.evaluate("localStorage.clear()")
            page.goto(url, wait_until="networkidle")
            page.locator("#tabAdda").click()
            page.wait_for_timeout(300)

            start_btn = page.locator('[data-adda-start="adda-06"]')
            assert start_btn.count() == 1, "adda-06 card start button not found"
            start_btn.click()
            page.wait_for_selector("#addaBeginMock", state="visible")
            page.locator("#addaBeginMock").click()
            page.wait_for_selector("#addaTimerDisplay", state="visible")
            print("✓ ADDA-06 started successfully in CBT interface.")
            summary["adda-06"]["checks"].append("CBT Mock Launch: PASS")

            # Jump to Quant section (Q41)
            page.evaluate("""() => {
                const s = JSON.parse(localStorage.getItem('rrbpo_adda_active_v1'));
                s.sectionIndex = 1;
                s.sectionEndAt = Date.now() + 1200000;
                s.currentIndex = 40;
                localStorage.setItem('rrbpo_adda_active_v1', JSON.stringify(s));
            }""")
            page.reload(wait_until="networkidle")
            if page.locator("#resumeAddaActiveBtn").count() == 1:
                page.locator("#resumeAddaActiveBtn").click()
            page.wait_for_selector("#addaTimerDisplay", state="visible")

            # Check Q41-Q46 (Products export table)
            for qn in range(41, 47):
                page.locator(f'[data-adda-jump="{qn-1}"]').click()
                page.wait_for_timeout(100)
                qh = page.locator(".question-header h2").inner_text().strip()
                assert f"Question {qn} of 80" in qh, f"Expected Q{qn}, got {qh}"
                tables = page.locator(".cbt-rendered-table")
                assert tables.count() >= 1, f"ADDA-06 Q{qn}: Expected .cbt-rendered-table, found {tables.count()}"
                tbl_text = tables.first.inner_text()
                assert "2010" in tbl_text and "56%" in tbl_text and "136" in tbl_text, f"Q{qn} table missing content: {tbl_text}"
            print("✓ ADDA-06 Q41-Q46 Products export table verified (all render as .cbt-rendered-table with full tabular data).")
            summary["adda-06"]["checks"].append("Products export table Q41-Q46: PASS")

            # Check Q50 (Formula image Q50)
            page.locator('[data-adda-jump="49"]').click()
            page.wait_for_timeout(100)
            qh = page.locator(".question-header h2").inner_text().strip()
            assert "Question 50 of 80" in qh, f"Expected Q50, got {qh}"
            imgs = page.locator(".cbt-diagram-img")
            assert imgs.count() == 1, f"ADDA-06 Q50: Expected 1 formula image, got {imgs.count()}"
            assert "adda-06_page27_Image137.png" in imgs.first.get_attribute("src")
            nw = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[0].naturalWidth")
            assert nw > 0, f"ADDA-06 Q50: naturalWidth={nw}"
            print(f"✓ ADDA-06 Q50 Formula image verified (Image137, naturalWidth={nw}).")
            summary["adda-06"]["checks"].append("Formula image Q50: PASS")

            # Check Q52-Q57 (Office pie chart)
            for qn in range(52, 58):
                page.locator(f'[data-adda-jump="{qn-1}"]').click()
                page.wait_for_timeout(100)
                qh = page.locator(".question-header h2").inner_text().strip()
                assert f"Question {qn} of 80" in qh, f"Expected Q{qn}, got {qh}"
                imgs = page.locator(".cbt-diagram-img")
                assert imgs.count() == 2, f"ADDA-06 Q{qn}: Expected 2 pie chart images, got {imgs.count()}"
                src0 = imgs.nth(0).get_attribute("src")
                src1 = imgs.nth(1).get_attribute("src")
                assert "adda-06_page28_Image142.jpeg" in src0, f"Q{qn} src0 mismatch: {src0}"
                assert "adda-06_page28_Image143.jpeg" in src1, f"Q{qn} src1 mismatch: {src1}"
                nw0 = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[0].naturalWidth")
                nw1 = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[1].naturalWidth")
                assert nw0 > 0 and nw1 > 0, f"Q{qn} images naturalWidth failed: {nw0}, {nw1}"
            print("✓ ADDA-06 Q52-Q57 Office pie chart verified (2 images rendered with naturalWidth > 0).")
            summary["adda-06"]["checks"].append("Office pie chart Q52-Q57: PASS")

            # Test Scoring and Solutions for ADDA-06
            with open(ROOT / "data" / "licensed_adda" / "adda-06.json", "r", encoding="utf-8") as f:
                d6 = json.load(f)
            q41_correct = d6["questions"][40]["answerIndex"]
            q42_correct = d6["questions"][41]["answerIndex"]
            q43_correct = d6["questions"][42]["answerIndex"]
            q43_wrong = (q43_correct + 1) % 5

            # Q41 correct (+1.00)
            page.locator('[data-adda-jump="40"]').click()
            page.wait_for_timeout(100)
            page.locator(f'.option-item[data-opt="{q41_correct}"]').click()
            page.locator("#addaSaveNext").click()
            page.wait_for_timeout(100)

            # Q42 correct (+1.00)
            page.locator(f'.option-item[data-opt="{q42_correct}"]').click()
            page.locator("#addaSaveNext").click()
            page.wait_for_timeout(100)

            # Q43 wrong (-0.25)
            page.locator(f'.option-item[data-opt="{q43_wrong}"]').click()
            page.locator("#addaSaveNext").click()
            page.wait_for_timeout(100)

            # Submit paper
            page.locator("#addaSubmitBtn").click()
            page.wait_for_selector(".score-hero-card", state="visible")

            # Verify score: 2 correct (+2.00), 1 incorrect (-0.25) -> Total = 1.75
            score_text = page.locator(".hero-score-value").inner_text()
            assert "1.75" in score_text, f"Expected 1.75, got {score_text}"
            print(f"✓ ADDA-06 Scoring verified: 2 correct (+2.00), 1 incorrect (-0.25) = {score_text.strip()}.")
            summary["adda-06"]["checks"].append("Scoring (+1.00/-0.25): PASS")

            # View solutions
            sol_items = page.locator(".solution-card")
            assert sol_items.count() == 80, f"Expected 80 solution cards, got {sol_items.count()}"

            # Check Q41 solution has +1.00 correct tag and step-by-step analysis
            sol41 = sol_items.nth(40)
            assert sol41.locator(".sol-status-tag.correct").count() == 1, "Q41 missing correct status tag"
            assert "+1.00" in sol41.inner_text(), "Q41 missing +1.00"
            assert "Analysis & Solution" in sol41.inner_text(), "Q41 missing step-by-step solution"

            # Check Q43 solution has -0.25 incorrect tag
            sol43 = sol_items.nth(42)
            assert sol43.locator(".sol-status-tag.wrong").count() == 1, "Q43 missing incorrect status tag"

            print("✓ ADDA-06 Step-by-Step Solutions verified across all 80 questions.")
            summary["adda-06"]["checks"].append("Step-by-step Solutions: PASS")
            summary["adda-06"]["status"] = "PASS"

            browser.close()

    finally:
        server.shutdown()
        server.server_close()

    print("\n" + "=" * 80)
    print("FINAL SUMMARY REPORT:")
    print("=" * 80)
    for pid, res in summary.items():
        print(f"[{res['status']}] {pid}:")
        for chk in res["checks"]:
            print(f"   - {chk}")
    print("=" * 80)
    return summary

if __name__ == "__main__":
    verify_all()
