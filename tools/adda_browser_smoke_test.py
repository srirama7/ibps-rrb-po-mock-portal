"""Exercise the Adda Mocks integration: tab switching, 10 cards, exam flow, right/wrong analysis, solutions and mobile responsiveness."""
import http.server, socketserver, threading, json, sys
from pathlib import Path
from functools import partial
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts'
OUT.mkdir(exist_ok=True)

class Server(socketserver.TCPServer):
    allow_reuse_address = True

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

def run_tests():
    with Server(('127.0.0.1', 0), partial(Handler, directory=str(ROOT))) as server:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f'http://127.0.0.1:{server.server_address[1]}/'
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport=dict(width=1440, height=1000), device_scale_factor=1)
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            page.on('dialog', lambda d: d.accept())
            
            # 1. Visit Home
            page.goto(url, wait_until='networkidle')
            assert page.locator('#tabOriginal').count() == 1, "Original tab missing"
            assert page.locator('#tabAdda').count() == 1, "Adda tab missing"
            assert page.locator('.mock-card').count() == 20, "20 original cards must be present"
            
            # Switch to Adda tab
            page.locator('#tabAdda').click()
            page.wait_for_timeout(300)
            assert page.locator('.adda-card').count() == 10, "10 Adda cards must be present"
            page.screenshot(path=str(OUT / 'adda-desktop-home.png'), full_page=True)
            
            # 2. Check catalog URLs
            catalog = json.loads((ROOT / 'data/adda_mocks_catalog.json').read_text(encoding='utf-8'))
            for paper in catalog['papers']:
                pdf_link = page.locator(f'a[href="{paper["pdfUrl"]}"]')
                assert pdf_link.count() >= 1, f"Missing link for {paper['id']}"
                
            # 3. Start Adda Mock 01
            page.locator('[data-adda-start="adda-01"]').click()
            page.wait_for_selector('#addaBeginMock')
            page.locator('#addaBeginMock').click()
            page.wait_for_selector('#addaTimerDisplay')
            
            # Section 1: Reasoning Ability (Q1-Q40)
            assert page.locator('button.pal-btn').count() == 40
            assert page.locator('.option-item').count() == 5
            
            # Answer Q1 with option D (index 3)
            page.locator('.option-item').nth(3).click()
            assert page.locator('.option-item.selected').count() == 1
            
            # Mark for review & next
            page.locator('#addaMarkNext').click()
            page.wait_for_timeout(100)
            assert page.locator('button.pal-btn.marked-answered').count() == 1
            
            # Go back to Q1
            page.locator('[data-adda-jump="0"]').click()
            assert page.locator('.option-item.selected').count() == 1
            
            # Clear response
            page.locator('#addaClear').click()
            assert page.locator('.option-item.selected').count() == 0
            
            # Reselect correct option D (index 3)
            page.locator('.option-item').nth(3).click()
            page.locator('#addaSaveNext').click()
            
            # On Q2, select option A (index 0) - intentionally incorrect to test right/wrong
            page.locator('.option-item').nth(0).click()
            page.locator('#addaSaveNext').click()
            
            page.screenshot(path=str(OUT / 'adda-desktop-exam.png'), full_page=True)
            
            # 4. Reload and resume persistence
            page.reload(wait_until='networkidle')
            page.wait_for_timeout(400)
            if page.locator('#resumeAddaActiveBtn').count() == 1:
                page.locator('#resumeAddaActiveBtn').click()
            page.wait_for_selector('#addaTimerDisplay')
            assert page.locator('#addaTimerDisplay').count() == 1
            
            # 5. Submit Test
            page.locator('#addaSubmitBtn').click()
            page.wait_for_selector('.result-dashboard')
            
            # Check Result Screen
            assert page.locator('.hero-score-value').count() == 1
            assert page.locator('.solution-card').count() == 80, "80 solution cards must be rendered"
            
            # Verify Right vs Wrong distinction
            assert page.locator('.sol-status-tag.correct').count() >= 1, "Should point out which is right (correct tag)"
            assert page.locator('.sol-status-tag.wrong').count() >= 1, "Should point out which is wrong (wrong tag)"
            assert page.locator('.sol-status-tag.skipped').count() >= 1, "Should point out unattempted questions"
            
            # Test filter buttons
            page.locator('[data-rf="wrong"]').click()
            assert page.locator('.solution-card').count() == 1
            
            page.locator('[data-rf="correct"]').click()
            assert page.locator('.solution-card').count() == 1
            
            page.locator('[data-rf="all"]').click()
            assert page.locator('.solution-card').count() == 80
            
            page.screenshot(path=str(OUT / 'adda-desktop-result.png'), full_page=True)
            
            # 6. Mobile Layout
            mobile = browser.new_page(viewport=dict(width=390, height=844), is_mobile=True, has_touch=True)
            mobile.on('pageerror', lambda e: errors.append(str(e)))
            mobile.goto(url, wait_until='networkidle')
            assert mobile.evaluate('document.documentElement.scrollWidth <= innerWidth'), "Mobile overflow on home"
            
            mobile.locator('#tabAdda').click()
            mobile.wait_for_timeout(200)
            assert mobile.evaluate('document.documentElement.scrollWidth <= innerWidth'), "Mobile overflow on Adda tab"
            mobile.screenshot(path=str(OUT / 'adda-mobile.png'), full_page=True)
            
            assert not errors, f"Page errors encountered: {errors}"
            browser.close()
            
        server.shutdown()
    print("PASS: Adda Mocks integration fully verified (tab switch, 10 cards, exam flow, right/wrong solution analysis, filters, mobile responsiveness).")

if __name__ == '__main__':
    run_tests()
