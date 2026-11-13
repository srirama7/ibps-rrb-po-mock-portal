import asyncio
import http.server
import socketserver
import threading
from playwright.async_api import async_playwright

PORT = 8093

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def start_server():
    try:
        with socketserver.TCPServer(("", PORT), QuietHandler) as httpd:
            httpd.serve_forever()
    except Exception:
        pass

async def test_answers_preserved():
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    await asyncio.sleep(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(f"http://localhost:8093/#adda-mocks")
        await page.wait_for_timeout(1000)

        # Start Adda Mock 03
        await page.locator('#tabAdda').click()
        await page.wait_for_timeout(500)
        await page.locator('[data-adda-start="adda-03"]').click()
        await page.wait_for_timeout(500)
        await page.locator('#addaBeginMock').click()
        await page.wait_for_timeout(800)

        # Switch to Quant (Q41)
        await page.locator('#addaSecQuant').click()
        await page.wait_for_timeout(500)

        # Select option B on Q41
        await page.locator('[data-opt="1"]').click()
        await page.wait_for_timeout(300)

        # Submit test
        page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))
        await page.locator('#addaSubmitBtn').click()
        await page.wait_for_timeout(1000)

        # Click continue attempt
        await page.locator('#addaContinueAttemptBtn').click()
        await page.wait_for_timeout(800)

        # Now navigate to Q41
        await page.locator('#addaSecQuant').click()
        await page.wait_for_timeout(500)

        # Check if option B is selected on Q41
        opt_b = page.locator('[data-opt="1"]')
        classes = await opt_b.get_attribute("class") or ""
        print("Classes on Q41 Option B after resuming:", classes)
        assert "selected" in classes, "Option B should be selected on Q41"
        print("PASS: Answer on Q41 was 100% PRESERVED!")

        await browser.close()

asyncio.run(test_answers_preserved())
