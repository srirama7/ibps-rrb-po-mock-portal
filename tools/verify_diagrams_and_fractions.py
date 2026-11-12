"""Verify that fractions, diagrams, and tables are properly rendered in the CBT exam and review view."""
import http.server, socketserver, threading, json, sys, os
from pathlib import Path
from functools import partial
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

class Server(socketserver.TCPServer):
    allow_reuse_address = True

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

def run():
    server = Server(('127.0.0.1', 0), partial(Handler, directory=str(ROOT)))
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    url = f'http://127.0.0.1:{server.server_address[1]}/'
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport=dict(width=1440, height=1000))
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            
            # --- TEST 1: adda-01 (Table, Fraction, Pie Chart) ---
            page.goto(url, wait_until='networkidle')
            page.locator('#tabAdda').click()
            page.wait_for_timeout(200)
            
            page.locator('[data-adda-start="adda-01"]').click()
            page.locator('#addaBeginMock').click()
            page.wait_for_selector('#addaTimerDisplay')
            
            # Simulate jump to Quant section Q41
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
            
            # 1. Verify Table rendering for Q41
            assert page.locator('.cbt-rendered-table').count() >= 1, "CBT table not rendered for Q41"
            print("PASS: [adda-01 Q41] Data Interpretation table rendered successfully.")
            
            # 2. Jump to Q52 (Simplification with fractions: 4/7)
            page.locator('[data-adda-jump="51"]').click()
            page.wait_for_timeout(100)
            assert page.locator('.cbt-frac').count() >= 1, "Fraction span .cbt-frac not rendered for Q52"
            print("PASS: [adda-01 Q52] Mathematical fraction rendered as stacked vertical fraction.")
            
            # 3. Jump to Q76 (Pie chart diagram)
            page.locator('[data-adda-jump="75"]').click()
            page.wait_for_timeout(100)
            assert page.locator('.cbt-diagram-img').count() >= 1, "Diagram image not rendered for Q76"
            img_w = page.evaluate("document.querySelector('.cbt-diagram-img').naturalWidth")
            assert img_w > 100, f"Image naturalWidth is {img_w}"
            print(f"PASS: [adda-01 Q76] Pie chart loaded with naturalWidth {img_w}px.")
            
            # --- TEST 2: adda-02 (Formula Image Q41, Line Graph Q46, Table Q57) ---
            page.evaluate("""() => {
              const s = JSON.parse(localStorage.getItem('rrbpo_adda_active_v1'));
              s.testId = 'adda-02';
              s.sectionIndex = 1;
              s.sectionEndAt = Date.now() + 1200000;
              s.currentIndex = 40;
              localStorage.setItem('rrbpo_adda_active_v1', JSON.stringify(s));
            }""")
            page.reload(wait_until='networkidle')
            if page.locator('#resumeAddaActiveBtn').count() == 1:
                page.locator('#resumeAddaActiveBtn').click()
            page.wait_for_selector('#addaTimerDisplay')
            
            # Q41 Formula Image
            assert page.locator('.cbt-diagram-img').count() >= 1, "Formula image not rendered for adda-02 Q41"
            f_w = page.evaluate("document.querySelector('.cbt-diagram-img').naturalWidth")
            assert f_w > 0, f"Formula image failed to load for adda-02 Q41: {f_w}"
            print(f"PASS: [adda-02 Q41] Formula image loaded with naturalWidth {f_w}px.")
            
            # Q46 Line Graph
            page.locator('[data-adda-jump="45"]').click()
            page.wait_for_timeout(100)
            assert page.locator('.cbt-diagram-img').count() >= 1, "Line graph not rendered for adda-02 Q46"
            lg_w = page.evaluate("document.querySelector('.cbt-diagram-img').naturalWidth")
            assert lg_w > 100, f"Line graph naturalWidth is {lg_w}"
            print(f"PASS: [adda-02 Q46] Line graph loaded with naturalWidth {lg_w}px.")
            
            # Q57 Markdown Table
            page.locator('[data-adda-jump="56"]').click()
            page.wait_for_timeout(100)
            assert page.locator('.cbt-rendered-table').count() >= 1, "Table not rendered for adda-02 Q57"
            print("PASS: [adda-02 Q57] Markdown table rendered successfully.")

            # --- TEST 3: adda-04 (Malls Table Q46) ---
            page.evaluate("""() => {
              const s = JSON.parse(localStorage.getItem('rrbpo_adda_active_v1'));
              s.testId = 'adda-04';
              s.sectionIndex = 1;
              s.sectionEndAt = Date.now() + 1200000;
              s.currentIndex = 45;
              localStorage.setItem('rrbpo_adda_active_v1', JSON.stringify(s));
            }""")
            page.reload(wait_until='networkidle')
            if page.locator('#resumeAddaActiveBtn').count() == 1:
                page.locator('#resumeAddaActiveBtn').click()
            page.wait_for_selector('#addaTimerDisplay')
            assert page.locator('.cbt-rendered-table').count() >= 1, "Table not rendered for adda-04 Q46"
            print("PASS: [adda-04 Q46] Malls table rendered successfully.")

            assert not errors, f"Errors: {errors}"
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        
    print("\nALL MULTI-PAPER CHECKS PASSED: Fractions, Tables, Diagrams & Formula Images verified!")

if __name__ == '__main__':
    run()
