import asyncio
import http.server
import socketserver
import threading
from playwright.async_api import async_playwright

PORT = 8091

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def start_server():
    try:
        with socketserver.TCPServer(("", PORT), QuietHandler) as httpd:
            httpd.serve_forever()
    except Exception:
        pass

async def inspect():
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    await asyncio.sleep(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        page.on("console", lambda msg: print(f"BROWSER LOG: {msg.text}"))
        page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))

        await page.goto(f"http://localhost:8091/")
        await page.wait_for_timeout(1000)

        # Check tab buttons
        tab_adda = page.locator('#tabAdda')
        count = await tab_adda.count()
        print(f"#tabAdda count: {count}")
        if count > 0:
            await tab_adda.click()
            await page.wait_for_timeout(1000)

        adda_btns = await page.locator('[data-adda-start]').all()
        print(f"Found {len(adda_btns)} adda start buttons")
        for b in adda_btns[:3]:
            print("Btn attr:", await b.get_attribute("data-adda-start"), "text:", (await b.inner_text()).strip())

        await browser.close()

asyncio.run(inspect())
