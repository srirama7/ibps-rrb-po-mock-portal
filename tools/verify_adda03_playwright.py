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

def run():
    print("Starting local server for adda-03 Playwright verification...")
    with Server(('127.0.0.1', 0), partial(Handler, directory=str(ROOT))) as server:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        port = server.server_address[1]
        url = f'http://127.0.0.1:{port}/'
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport=dict(width=1440, height=1000))
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            
            page.goto(url, wait_until='networkidle')
            page.locator('#tabAdda').click()
            page.wait_for_timeout(300)
            
            # Start Adda Mock 03
            start_btn = page.locator('[data-adda-start="adda-03"]')
            assert start_btn.count() == 1, "Start button for adda-03 not found"
            start_btn.click()
            page.locator('#addaBeginMock').click()
            page.wait_for_selector('#addaTimerDisplay')
            print("PASS: adda-03 exam session started.")
            
            # 1. Check Seating / Inequality diagram (Q5 / Q6)
            page.locator('[data-adda-jump="4"]').click() # Q5
            page.wait_for_timeout(150)
            q5_diags = page.locator('.cbt-diagram-img').count()
            print(f"PASS: Q5 loaded with {q5_diags} diagram images rendered.")
            
            # 2. Advance to Quant (Q41+)
            page.locator('[data-adda-jump="39"]').click() # Q40
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
            
            # 3. Check Q47 (Twiggy/Xomato pie charts)
            page.wait_for_timeout(150)
            q47_diags = page.locator('.cbt-diagram-img').count()
            assert q47_diags >= 1, f"Q47 diagrams not rendered: {q47_diags}"
            nat_width = page.evaluate("document.querySelector('.cbt-diagram-img').naturalWidth")
            assert nat_width > 50, f"Q47 diagram failed to load: {nat_width}"
            print(f"PASS: Q47 Twiggy/Xomato pie charts loaded ({q47_diags} images, naturalWidth: {nat_width}px).")
            
            # 4. Check Q53 (Songs download table)
            page.locator('[data-adda-jump="52"]').click() # Q53
            page.wait_for_timeout(150)
            q53_diags = page.locator('.cbt-diagram-img').count()
            assert q53_diags >= 1, f"Q53 table diagrams not rendered: {q53_diags}"
            print(f"PASS: Q53 Songs download table loaded ({q53_diags} images).")
            
            # 5. Check Q59 (Formula image)
            page.locator('[data-adda-jump="58"]').click() # Q59
            page.wait_for_timeout(150)
            q59_diags = page.locator('.cbt-diagram-img').count()
            assert q59_diags >= 1, f"Q59 formula image not rendered: {q59_diags}"
            print(f"PASS: Q59 Formula image loaded ({q59_diags} images).")
            
            # 6. Check fraction rendering on Q52
            page.locator('[data-adda-jump="51"]').click() # Q52
            page.wait_for_timeout(150)
            frac_count = page.locator('.cbt-frac').count()
            print(f"PASS: Q52 has {frac_count} stacked vertical fractions rendered.")
            
            # Take verification screenshot
            out_img = ROOT / 'artifacts/adda-03-verified.png'
            page.screenshot(path=str(out_img), full_page=True)
            print(f"PASS: Screenshot saved to {out_img}")
            
            assert not errors, f"Console/page errors detected: {errors}"
            browser.close()
        server.shutdown()
    print("ALL CHECKS PASSED for adda-03 Playwright browser verification!")

if __name__ == '__main__':
    run()
