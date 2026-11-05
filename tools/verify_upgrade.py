from playwright.sync_api import sync_playwright
from pathlib import Path

desktop_file = Path(r"C:\Users\amogh\Desktop\IBPS_RRB_PO_20_Mock_Tests.html").resolve().as_uri()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(desktop_file)

    # 1. Verify 20 mocks
    card_count = page.locator(".mock-card").count()
    print("Cards rendered:", card_count)
    assert card_count == 20

    # 2. Start mock 1
    page.locator("[data-start='MOCK-01']").first.click()
    assert "Official Pattern Prelims Simulation" in page.content()
    page.locator("#beginMock").click()

    # 3. Check exam screen
    palette_count = page.locator(".pal-btn").count()
    print("Palette buttons in Reasoning:", palette_count)
    assert palette_count == 40
    assert page.locator("#examTimer").count() == 1

    # 4. Check option selection
    page.locator(".option-item").first.click()
    assert page.locator(".option-item.selected").count() == 1
    # Check palette status became answered
    assert page.locator(".pal-btn.answered").count() >= 1

    # 5. Save & next
    page.locator("#btnSaveNext").click()

    # 6. Mark for review
    page.locator(".option-item").nth(1).click()
    page.locator("#btnMarkNext").click()

    # 7. Submit exam
    page.on("dialog", lambda d: d.accept())
    page.locator("#submitExamBtn").click()

    # 8. Check results screen
    assert "Expected Cutoff Benchmark" in page.content()
    assert "Topic-Wise Performance Analysis" in page.content()
    assert page.locator(".solution-card").count() == 80
    print("Result analysis rendered with 80 full solution cards!")

    # 9. Test wrong/unanswered filter
    page.locator("#toggleOnlyWrong").click()
    filtered_count = page.locator(".solution-card").count()
    print(f"Filtered to incorrect/unanswered questions: {filtered_count} cards shown.")
    assert filtered_count > 0

    assert not errors, errors
    browser.close()
    print("ALL TESTS PASSED: UI & Exam Flow 100% Verified!")
