import asyncio
import http.server
import socketserver
import threading
from playwright.async_api import async_playwright

PORT = 8096

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def start_server():
    try:
        with socketserver.TCPServer(("", PORT), QuietHandler) as httpd:
            httpd.serve_forever()
    except Exception:
        pass

async def test_app_js():
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    await asyncio.sleep(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print("1. Loading original mocks...")
        await page.goto(f"http://localhost:8096/")
        await page.wait_for_timeout(1000)

        # Clear localStorage
        await page.evaluate("() => localStorage.clear()")
        await page.reload()
        await page.wait_for_timeout(1000)

        # Click Take Mock Exam on Mock 01
        await page.locator('[data-start="MOCK-01"]').click()
        await page.wait_for_timeout(500)
        await page.locator('#beginMock').click()
        await page.wait_for_timeout(800)

        q_num = await page.locator('.q-title').inner_text()
        print(f"   Original Mock Q: {q_num}")
        assert "Question No. 1" in q_num

        # 2. Test switching to Quant
        print("2. Switching to Section 2 (Quant)...")
        await page.locator('#tabQuant').click()
        await page.wait_for_timeout(500)

        q_num_quant = await page.locator('.q-title').inner_text()
        print(f"   Switched to: {q_num_quant}")
        assert "Question No. 41" in q_num_quant

        # 3. Test Previous button
        print("3. Clicking Previous from Q41...")
        await page.locator('#btnPrev').click()
        await page.wait_for_timeout(500)

        q_num_prev = await page.locator('.q-title').inner_text()
        print(f"   Back to: {q_num_prev}")
        assert "Question No. 40" in q_num_prev

        # 4. Test Pause
        print("4. Testing Pause on original mock...")
        await page.locator('#btnPauseExam').click()
        await page.wait_for_timeout(500)
        assert await page.locator('.cbt-pause-overlay').count() > 0

        # Resume
        await page.locator('#resumeFromPauseBtn').click()
        await page.wait_for_timeout(500)
        assert await page.locator('.cbt-pause-overlay').count() == 0
        print("   Pause & Resume working on original mock!")

        # 5. Submit & test Continue
        print("5. Submitting original mock...")
        page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))
        await page.locator('#submitExamBtn').click()
        await page.wait_for_timeout(1000)

        cont_btn = page.locator('#continueAttemptBtn')
        assert await cont_btn.count() > 0
        print(f"   Continue button present on original mock result: '{(await cont_btn.inner_text()).strip()}'")

        # 6. Test Clicking Continue
        print("6. Clicking Continue button on original mock...")
        await cont_btn.click()
        await page.wait_for_timeout(800)

        q_resumed = await page.locator('.q-title').inner_text()
        print(f"   Successfully resumed original mock! Current Q: {q_resumed}")

        await browser.close()
        print("\nALL ORIGINAL MOCK TESTS PASSED 100%!")

asyncio.run(test_app_js())
