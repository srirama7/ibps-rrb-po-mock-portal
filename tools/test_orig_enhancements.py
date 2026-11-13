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

        # Check TCS iON Timer in Reasoning
        timer_text = await page.locator('#examTimer').inner_text()
        sec_label = await page.locator('#examTimerSecLabel').inner_text()
        print(f"   Original Mock Reasoning Timer: {timer_text} | Label: {sec_label}")
        assert "2" in timer_text and ":" in timer_text
        assert "Reasoning" in sec_label

        # 2. Test switching to Quant
        print("2. Switching to Section 2 (Quant)...")
        await page.locator('#tabQuant').click()
        await page.wait_for_timeout(500)

        q_num_quant = await page.locator('.q-title').inner_text()
        print(f"   Switched to: {q_num_quant}")
        assert "Question No. 41" in q_num_quant

        # Check TCS iON Timer switched to Quant (20:00)
        timer_quant = await page.locator('#examTimer').inner_text()
        sec_quant_label = await page.locator('#examTimerSecLabel').inner_text()
        print(f"   Original Mock Quant Timer: {timer_quant} | Label: {sec_quant_label}")
        assert ("19:" in timer_quant or "20:" in timer_quant)
        assert "Quantitative" in sec_quant_label

        # Answer Question 41
        print("   Answering Question 41...")
        await page.locator('[data-ans="2"]').click()
        await page.wait_for_timeout(300)

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
        assert "Question No. 42" in q_resumed

        # Check Timer after resuming into Quant
        timer_res = await page.locator('#examTimer').inner_text()
        print(f"   Resumed Timer: {timer_res}")
        assert ("19:" in timer_res or "20:" in timer_res)

        # Go back to Question 41 and verify answer is preserved
        await page.locator('#btnPrev').click()
        await page.wait_for_timeout(500)
        q_back = await page.locator('.q-title').inner_text()
        print(f"   Back to: {q_back}")
        assert "Question No. 41" in q_back

        opt_c = page.locator('[data-ans="2"]')
        is_sel = "selected" in (await opt_c.get_attribute("class") or "")
        print(f"   Question 41 preserved selected answer: {is_sel}")
        assert is_sel == True

        await browser.close()
        print("\nALL ORIGINAL MOCK TESTS PASSED 100%!")

asyncio.run(test_app_js())
