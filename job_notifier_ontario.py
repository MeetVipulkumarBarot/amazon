# job_notifier_ontario.py

import asyncio
import random
from dotenv import load_dotenv
from notifier import send_email
from playwright.async_api import async_playwright

load_dotenv()  # loads SENDER_EMAIL, SENDER_PASS, RECEIVER_EMAIL

async def apply_filters(page):
    # 1) Set Location to Ontario, Canada
    await page.wait_for_selector('button[data-test-id="navigationLocationButton"]', state="visible")
    await page.click('button[data-test-id="navigationLocationButton"]', force=True)
    await page.wait_for_selector('[data-test-id="zipcodeInputField"] input', state="visible")
    await page.fill('[data-test-id="zipcodeInputField"] input', "Ontario, Canada")
    await page.keyboard.press("Enter")
    await page.wait_for_timeout(1000)

    # 2) Set Job keyword to warehouse
    await page.wait_for_selector('button[aria-label="Focus search bar button"]', state="visible")
    await page.click('button[aria-label="Focus search bar button"]', force=True)
    await page.wait_for_selector('[data-test-id="navigationSearchField"] input', state="visible")
    await page.fill('[data-test-id="navigationSearchField"] input', "warehouse")
    await page.keyboard.press("Enter")
    await page.wait_for_timeout(1000)

async def monitor_jobs():
    seen = set()
    print("🔍 Monitoring Ontario warehouse jobs…")

    # SMTP sanity check
    try:
        send_email("🔥 TEST ALERT", "Confirming that SMTP works from this VM.")
        print("📧 Test alert sent.")
    except Exception as e:
        print("❌ Test alert failed:", e)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            locale="en-CA", timezone_id="America/Toronto"
        )
        page = await context.new_page()

        while True:
            try:
                # 1) Reload the search page
                await page.goto("https://hiring.amazon.ca/search/warehouse-jobs#/", timeout=60000)

                # 2) Apply the two filters
                await apply_filters(page)

                # 3) Let React render the results
                await page.wait_for_selector(
                            '[data-test-id="jobResultContainer"]',
                            state="visible",
                            timeout=15000
                )

                await page.wait_for_timeout(1000)

                # 4) Grab all job cards
                tiles = await page.query_selector_all('div.job-tile')

                if not tiles:
                    # no tiles → no jobs right now
                    print("⏳ No new jobs right now.")
                else:
                    for t in tiles:
                        # Title
                        title = await t.query_selector_eval('.job-title', 'el => el.textContent.trim()')
                        # Location
                        location = await t.query_selector_eval('.job-location', 'el => el.textContent.trim()')
                        # Link
                        link = await t.query_selector_eval('a', 'el => el.href')

                        # Dedupe
                        if link in seen:
                            continue
                        seen.add(link)

                        # Email body
                        body = "\n".join([
                            "-------------------------------",
                            f"Job:      {title}",
                            f"Location: {location}",
                            f"Link:     {link}",
                            "-------------------------------",
                        ])

                        # Send!
                        send_email(
                            subject=f"🔔 New Ontario Job: {title} @ {location}",
                            body=body
                        )
                        print(f"📧 Alert sent for: {title} @ {location}")

            except Exception as e:
                print("⚠️ Monitor loop error:", e)

            # 5) Pause 2–5 seconds, then repeat
            await asyncio.sleep(random.uniform(2, 5))

if __name__ == "__main__":
    asyncio.run(monitor_jobs())
