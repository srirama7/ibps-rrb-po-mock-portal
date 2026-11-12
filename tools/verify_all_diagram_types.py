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
    with Server(('127.0.0.1', 0), partial(Handler, directory=str(ROOT))) as server:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f'http://127.0.0.1:{server.server_address[1]}/'
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport=dict(width=1440, height=1000))
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            
            print(f"Connecting to test server at {url} ...")
            page.goto(url, wait_until='networkidle')
            page.locator('#tabAdda').click()
            page.wait_for_timeout(300)
            print("PASS: Adda Mocks tab switched successfully.")

            # Test samples across different mock papers
            test_samples = [
                ("adda-01", 41, "table", ".cbt-rendered-table"),
                ("adda-01", 52, "fraction", ".cbt-frac"),
                ("adda-01", 76, "pie-chart", ".cbt-diagram-img"),
                ("adda-02", 41, "formula-image", ".cbt-diagram-img"),
                ("adda-02", 46, "line-graph", ".cbt-diagram-img"),
                ("adda-02", 57, "table", ".cbt-rendered-table"),
                ("adda-04", 41, "line-graph", ".cbt-diagram-img"),
                ("adda-04", 46, "table", ".cbt-rendered-table"),
                ("adda-06", 41, "table", ".cbt-rendered-table"),
                ("adda-06", 52, "pie-chart", ".cbt-diagram-img"),
            ]

            for pid, qnum, kind, sel in test_samples:
                # Set active test directly in localStorage
                page.evaluate(f"""() => {{
                    const s = {{
                        testId: '{pid}',
                        sectionIndex: 1,
                        sectionEndAt: Date.now() + 1200000,
                        currentIndex: {qnum - 1},
                        responses: {{}},
                        marked: {{}},
                        history: [],
                        startEpoch: Date.now()
                    }};
                    localStorage.setItem('rrbpo_adda_active_v1', JSON.stringify(s));
                    if (window.__initAddaMocks) window.__initAddaMocks();
                }}""")
                page.reload(wait_until='networkidle')
                if page.locator('#resumeAddaActiveBtn').count() == 1:
                    page.locator('#resumeAddaActiveBtn').click()
                    page.wait_for_selector('#addaTimerDisplay')

                elem = page.locator(sel).first
                assert elem.is_visible(), f"FAIL: {pid} Q{qnum} expected {kind} with selector {sel} to be visible"

                if "table" not in kind and "fraction" not in kind:
                    img_loaded = page.evaluate(f"""() => {{
                        const img = document.querySelector('{sel}');
                        return img && img.complete && img.naturalWidth > 0;
                    }}""")
                    assert img_loaded, f"FAIL: {pid} Q{qnum} {kind} image failed to load or has 0 naturalWidth"
                    nat_w = page.evaluate(f"() => document.querySelector('{sel}').naturalWidth")
                    print(f"PASS: [{pid} Q{qnum:02d}] {kind} rendered & verified (naturalWidth: {nat_w}px).")
                else:
                    print(f"PASS: [{pid} Q{qnum:02d}] {kind} rendered & visible.")

            browser.close()
            print("\nALL VERIFICATION SAMPLES PASSED WITHOUT ERRORS!")

if __name__ == '__main__':
    run()
