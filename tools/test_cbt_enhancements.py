import asyncio
import http.server
import socketserver
import threading
from playwright.async_api import async_playwright

PORT = 8092

class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def start_server():
    try:
        with socketserver.TCPServer(("", PORT), QuietHandler) as httpd:
            httpd.serve_forever()
    except Exception:
        pass

async def run_tests():
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    await asyncio.sleep(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))
        page.on("pageerror", lambda err: print(f"PAGE ERROR: {err}"))

        print("1. Loading portal on http://localhost:8092/#adda-mocks ...")
        await page.goto(f"http://localhost:8092/#adda-mocks")
        await page.wait_for_timeout(1000)

        # Clear localStorage for clean test run
        await page.evaluate("() => localStorage.clear()")
        await page.reload()
        await page.wait_for_timeout(1000)

        # Switch to Adda tab if not active
        tab_adda = page.locator('#tabAdda')
        if await tab_adda.count() > 0:
            await tab_adda.click()
            await page.wait_for_timeout(500)

        print("2. Starting Adda Mock 03 ...")
        start_btn = page.locator('[data-adda-start="adda-03"]')
        await start_btn.click()
        await page.wait_for_timeout(500)

        # Click "I am Ready to Begin"
        ready_btn = page.locator('#addaBeginMock')
        await ready_btn.click()
        await page.wait_for_timeout(800)

        # We should be on Question 1 (Reasoning)
        q_heading = await page.locator('.question-header h2').inner_text()
        print(f"   Current Question: {q_heading}")
        assert "Question 1 of 80" in q_heading
        assert "Reasoning" in q_heading

        # Check TCS iON Timer widget in Reasoning
        timer_text = await page.locator('#addaTimerDisplay').inner_text()
        sec_label = await page.locator('#addaTimerSecLabel').inner_text()
        print(f"   Reasoning Timer: {timer_text} | Label: {sec_label}")
        assert "2" in timer_text and ":" in timer_text # e.g. 24:59 or 25:00
        assert "Reasoning" in sec_label

        # 3. Test Direct Section Switching to Quant
        print("3. Clicking '2. Quantitative (Q41–Q80)' section tab button...")
        sec_quant_btn = page.locator('#addaSecQuant')
        await sec_quant_btn.click()
        await page.wait_for_timeout(500)

        q_heading_quant = await page.locator('.question-header h2').inner_text()
        print(f"   Switched! Current Question: {q_heading_quant}")
        assert "Question 41 of 80" in q_heading_quant
        assert "Quantitative Aptitude" in q_heading_quant

        # Check TCS iON Timer widget switched to Quant
        timer_quant = await page.locator('#addaTimerDisplay').inner_text()
        sec_quant_label = await page.locator('#addaTimerSecLabel').inner_text()
        print(f"   Quant Timer: {timer_quant} | Label: {sec_quant_label}")
        assert ("19:" in timer_quant or "20:" in timer_quant)
        assert "Quantitative" in sec_quant_label

        # 4. Answer Question 41 (Quant)
        print("4. Answering Question 41...")
        opt_b = page.locator('[data-opt="1"]')
        await opt_b.click()
        await page.wait_for_timeout(300)

        # 5. Test 'Previous' button crossing section boundary back to Reasoning (Q40)
        print("5. Clicking 'Previous' from Question 41...")
        prev_btn = page.locator('#addaPrev')
        await prev_btn.click()
        await page.wait_for_timeout(500)

        q_heading_prev = await page.locator('.question-header h2').inner_text()
        print(f"   Back to previous question: {q_heading_prev}")
        assert "Question 40 of 80" in q_heading_prev
        assert "Reasoning Ability" in q_heading_prev

        # 6. Test 'Save & Next' crossing section boundary to Quant (Q41)
        print("6. Clicking 'Save & Next' from Question 40...")
        next_btn = page.locator('#addaSaveNext')
        await next_btn.click()
        await page.wait_for_timeout(500)

        q_heading_next = await page.locator('.question-header h2').inner_text()
        print(f"   Next question: {q_heading_next}")
        assert "Question 41 of 80" in q_heading_next
        assert "Quantitative Aptitude" in q_heading_next

        # 7. Test Pause & Break Modal
        print("7. Testing '⏸ Pause / Take Break' button...")
        pause_btn = page.locator('#addaPauseBtn')
        await pause_btn.click()
        await page.wait_for_timeout(500)

        pause_modal = page.locator('.cbt-pause-overlay')
        assert await pause_modal.count() > 0
        pause_title = await page.locator('.cbt-pause-card h2').inner_text()
        print(f"   Pause Modal visible: '{pause_title}'")

        # Resume from pause
        resume_btn = page.locator('#resumeFromPauseBtn')
        await resume_btn.click()
        await page.wait_for_timeout(500)
        assert await page.locator('.cbt-pause-overlay').count() == 0
        print("   Resumed from pause successfully!")

        # 8. Submit Test and verify Result page & Continue button
        print("8. Submitting test to test Result & Continue options...")
        # Handle JS confirm dialog automatically
        page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))
        submit_btn = page.locator('#addaSubmitBtn')
        await submit_btn.click()
        await page.wait_for_timeout(1000)

        hero_score = await page.locator('.hero-score-value').inner_text()
        print(f"   Scorecard rendered with score: {hero_score.strip()}")

        cont_btn = page.locator('#addaContinueAttemptBtn')
        assert await cont_btn.count() > 0
        btn_text = await cont_btn.inner_text()
        print(f"   Continue Button present: '{btn_text}'")

        # 9. Test Clicking Continue Attempt
        print("9. Clicking 'Continue Test & Complete Quant' from Result page...")
        await cont_btn.click()
        await page.wait_for_timeout(800)

        q_resumed = await page.locator('.question-header h2').inner_text()
        print(f"   Successfully resumed into exam mode! Question: {q_resumed}")
        assert "Quantitative Aptitude" in q_resumed

        # Check that Quant timer has official 20:00 (or remaining)
        timer_resumed = await page.locator('#addaTimerDisplay').inner_text()
        print(f"   Resumed Timer: {timer_resumed}")
        assert ("19:" in timer_resumed or "20:" in timer_resumed)

        # Question 41 was answered earlier; navigate to Q41 to verify answer preserved
        await page.locator('#addaPrev').click()
        await page.wait_for_timeout(500)
        q_41_heading = await page.locator('.question-header h2').inner_text()
        print(f"   Navigated back to: {q_41_heading}")
        assert "Question 41 of 80" in q_41_heading

        opt_b_resumed = page.locator('[data-opt="1"]')
        is_selected = "selected" in (await opt_b_resumed.get_attribute("class") or "")
        print(f"   Previous answer preserved on Q41: {is_selected}")
        assert is_selected == True, "Expected Q41 answer to be preserved"

        await browser.close()
        print("\nALL VERIFICATION TESTS PASSED 100% SUCCESSFULLY!")

asyncio.run(run_tests())
