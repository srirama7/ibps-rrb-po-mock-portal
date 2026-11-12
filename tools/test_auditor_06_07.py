import http.server, socketserver, threading, json, sys, os
from pathlib import Path
from functools import partial
from playwright.sync_api import sync_playwright

ROOT = Path(r"C:\Users\amogh\ibps-rrb-portal-upgrade")

class Server(socketserver.TCPServer):
    allow_reuse_address = True

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

def test_adda_06_and_07():
    with Server(('127.0.0.1', 0), partial(Handler, directory=str(ROOT))) as server:
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        port = server.server_address[1]
        url = f'http://127.0.0.1:{port}/'
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport=dict(width=1440, height=1000))
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))

            # Load homepage
            page.goto(url, wait_until='networkidle')
            page.locator('#tabAdda').click()
            page.wait_for_timeout(200)

            print("=== VERIFYING ADDA-06 IN CBT ===")
            page.locator('[data-adda-start="adda-06"]').click()
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

            # 1. Q41 product export table
            assert page.locator('.cbt-rendered-table').count() >= 1, "ADDA-06 Q41: Markdown table not rendered"
            table_text = page.locator('.cbt-rendered-table').inner_text()
            assert "2010" in table_text and "56%" in table_text, f"Unexpected table text: {table_text}"
            print("PASS: ADDA-06 Q41 Product Export Table rendered correctly.")

            # 2. Q52 Office Pie Charts
            page.locator('[data-adda-jump="51"]').click()
            page.wait_for_timeout(100)
            assert page.locator('.cbt-diagram-img').count() >= 2, "ADDA-06 Q52: Pie chart diagrams not rendered"
            src0 = page.locator('.cbt-diagram-img').nth(0).get_attribute('src')
            src1 = page.locator('.cbt-diagram-img').nth(1).get_attribute('src')
            assert 'adda-06_page28_Image142.jpeg' in src0, f"Unexpected image: {src0}"
            assert 'adda-06_page28_Image143.jpeg' in src1, f"Unexpected image: {src1}"
            nw0 = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[0].naturalWidth")
            nw1 = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[1].naturalWidth")
            assert nw0 > 100 and nw1 > 100, f"Images failed to load: {nw0}, {nw1}"
            print(f"PASS: ADDA-06 Q52 Office Pie Charts loaded successfully ({nw0}x... and {nw1}x...).")

            print("\n=== VERIFYING ADDA-07 IN CBT ===")
            # Return home and start adda-07
            page.evaluate("localStorage.clear()")
            page.goto(url, wait_until='networkidle')
            page.locator('#tabAdda').click()
            page.wait_for_timeout(200)

            page.locator('[data-adda-start="adda-07"]').click()
            page.locator('#addaBeginMock').click()
            page.wait_for_selector('#addaTimerDisplay')

            # Advance to Quant section (Q41)
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

            # 3. ADDA-07 Q41 Villages Pie Charts
            assert page.locator('.cbt-diagram-img').count() >= 2, "ADDA-07 Q41: Pie charts not rendered"
            src_p0 = page.locator('.cbt-diagram-img').nth(0).get_attribute('src')
            src_p1 = page.locator('.cbt-diagram-img').nth(1).get_attribute('src')
            assert 'adda-07_page25_Image124.png' in src_p0, f"Unexpected: {src_p0}"
            assert 'adda-07_page26_Image129.png' in src_p1, f"Unexpected: {src_p1}"
            nw_p0 = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[0].naturalWidth")
            nw_p1 = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[1].naturalWidth")
            assert nw_p0 > 100 and nw_p1 > 100, f"Images not loaded: {nw_p0}, {nw_p1}"
            print(f"PASS: ADDA-07 Q41 Pie Charts loaded ({nw_p0}px, {nw_p1}px).")

            # 4. ADDA-07 Q51 Cities Bar Graph
            page.locator('[data-adda-jump="50"]').click()
            page.wait_for_timeout(100)
            assert page.locator('.cbt-diagram-img').count() >= 2, "ADDA-07 Q51: Bar graphs not rendered"
            src_b0 = page.locator('.cbt-diagram-img').nth(0).get_attribute('src')
            assert 'adda-07_page29_Image142.png' in src_b0, f"Unexpected: {src_b0}"
            nw_b0 = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[0].naturalWidth")
            assert nw_b0 > 100, f"Bar graph image not loaded: {nw_b0}"
            print(f"PASS: ADDA-07 Q51 Bar Graphs loaded ({nw_b0}px).")

            # 5. ADDA-07 Q56 Formula Image
            page.locator('[data-adda-jump="55"]').click()
            page.wait_for_timeout(100)
            assert page.locator('.cbt-diagram-img').count() >= 1, "ADDA-07 Q56: Formula image not rendered"
            src_f0 = page.locator('.cbt-diagram-img').nth(0).get_attribute('src')
            nw_f0 = page.evaluate("document.querySelectorAll('.cbt-diagram-img')[0].naturalWidth")
            assert nw_f0 > 50, f"Formula image failed: {nw_f0}"
            print(f"PASS: ADDA-07 Q56 Formula Image loaded ({nw_f0}px, src: {src_f0}).")

            # 6. Verify Scoring Logic (+1.00 / -0.25) by answering 1 correct, 1 wrong, then submitting
            # Answer Q56 option B
            page.locator('.option-item[data-opt="1"]').click()
            # Jump to Q57
            page.locator('[data-adda-jump="56"]').click()
            page.wait_for_timeout(100)
            page.locator('.option-item[data-opt="2"]').click()

            # Submit exam
            page.locator('#submitExamBtn').click()
            page.locator('#addaModalSubmitConfirm').click()
            page.wait_for_selector('.result-dashboard')

            # Verify score banner and +1.00 / -0.25 indicators
            summary_text = page.locator('.result-dashboard').inner_text()
            assert "Performance Summary" in summary_text, "Result dashboard not displayed"
            assert "+1.00" in summary_text and "-0.25" in summary_text, "Scoring indicators missing"
            print("PASS: Scoring engine (+1.00 / -0.25) and Result Analysis dashboard verified successfully.")

            assert not errors, f"Page errors: {errors}"
            browser.close()
        server.shutdown()
    print("\nALL AUDIT & VERIFICATION CHECKS PASSED FOR ADDA-06 & ADDA-07!")

if __name__ == '__main__':
    test_adda_06_and_07()
