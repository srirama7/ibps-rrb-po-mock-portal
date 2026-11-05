"""Optional browser smoke test; run on an ordinary local machine with Playwright + Chromium.
This container blocks browser navigation via policy, so this test was not executed here.
"""
import http.server, socketserver, threading
from pathlib import Path
from functools import partial
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
Handler=partial(http.server.SimpleHTTPRequestHandler,directory=str(ROOT))
class ReusableTCPServer(socketserver.TCPServer):allow_reuse_address=True
with ReusableTCPServer(('127.0.0.1',0),Handler) as server:
    port=server.server_address[1]
    th=threading.Thread(target=server.serve_forever,daemon=True);th.start()
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True)
        page=browser.new_page()
        errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto(f'http://127.0.0.1:{port}/',wait_until='networkidle')
        assert page.locator('.cards .card').count()==20
        page.locator('[data-start="MOCK-01"]').click()
        page.locator('#start').click()
        assert page.locator('.palette button').count()==40
        assert page.locator('#timer').inner_text().startswith(('25:', '24:'))
        page.locator('[data-answer="2"]').click()
        assert page.locator('.option.selected').count()==1
        page.locator('#next').click()
        page.reload(wait_until='networkidle')
        page.locator('#resume').click()
        page.locator('[data-jump="1"]').click()
        assert page.locator('.option.selected').count()==1
        page.evaluate("""() => {let st=JSON.parse(localStorage.getItem('rrbpo_active_v1'));st.sectionEndAt=Date.now()-2000;localStorage.setItem('rrbpo_active_v1',JSON.stringify(st));}""")
        page.reload(wait_until='networkidle')
        page.locator('#resume').click()
        assert page.locator('.palette button').first.inner_text()=='41'
        assert page.locator('#prev').is_disabled()
        page.on('dialog',lambda d:d.accept())
        page.locator('#submitButton').click()
        assert 'Your exam analysis' in page.locator('#app').inner_text()
        assert page.locator('.review-card').count()==80
        assert not errors,errors
        browser.close()
        print('PASS: browser smoke test')
    server.shutdown()
