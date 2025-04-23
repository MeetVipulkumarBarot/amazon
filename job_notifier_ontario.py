# job_notifier_ontario.py

import asyncio
import random
from dotenv import load_dotenv
from notifier import send_email
from playwright.async_api import async_playwright

load_dotenv()  # loads your SMTP creds

async def apply_filters(page):
    # 1) Set Location
    await page.wait_for_selector('button[data-test-id="navigationLocationButton"]', state="visible")
    await page.click('button[data-test-id="navigationLocationButton"]', force=True)
    await page.wait_for_selector('[data-test-id="zipcodeInputField"] input', state="visible")
    await page.fill('[data-test-id="zipcodeInputField"] input', "Ontario, Canada")
    await page.keyboard.press("Enter")
    await page.wait_for_timeout(1000)

    # 2) Set Job Keyword
    await page.wait_for_selector('button[aria-label="Focus search bar button"]', state="visible")
    await page.click('button[aria-label="Focus search bar button"]', force=True)
    await page.wait_for_selector('[data-test-id="navigationSearchField"] input', state="visible")
    await page.fill('[data-test-id="navigationSearchField"] input', "warehouse")
    await page.keyboard.press("Enter")
    await page.wait_for_timeout(1000)

async def monitor_jobs():
    seen = set()
    print("🔍 Monitoring Ontario warehouse jobs…")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(locale="en-CA", timezone_id="America/Toronto")
        page = await context.new_page()

        while True:
            try:
                # 1) Full reload
                await page.goto("https://hiring.amazon.ca/search/warehouse-jobs#/", timeout=60000)

                # 2) Apply filters
                await apply_filters(page)

                # 3) Wait for either job cards or “no jobs” message
                await page.wait_for_selector(
                    'div.job-tile, div.jobNotFoundContainer',
                    state="visible",
                    timeout=15000
                )

                # 4) Gather all job cards
                tiles = await page.query_selector_all('div.job-tile')
                if not tiles:
                    print("⏳ No new jobs right now.")
                else:
                    for t in tiles:
                        title    = await t.query_selector_eval('.job-title',    'el => el.textContent.trim()')
                        location = await t.query_selector_eval('.job-location', 'el => el.textContent.trim()')
                        link     = await t.query_selector_eval('a',             'el => el.href')

                        # Dedupe by link
                        if link in seen:
                            continue
                        seen.add(link)

                        # **Optionally** click into the card to grab shifts/type/pay fields,
                        # but Amazon’s summary card often has a “tagLine” or “bannerText”
                        # for bonus info. If you need more, you can page.goto(link) and scrape.

                        # Build a simple email body
                        body = "\n".join([
                            "-------------------------------",
                            f"Job:      {title}",
                            f"Location: {location}",
                            f"Link:     {link}",
                            "-------------------------------",
                        ])

                        send_email(
                            subject=f"🔔 New Ontario Job: {title} @ {location}",
                            body=body
                        )
                        print(f"📧 Alert sent for: {title} @ {location}")

            except Exception as e:
                print("⚠️ Monitor loop error:", e)

            # 5) Pause before next full refresh
            await asyncio.sleep(random.uniform(2, 5))

if __name__ == "__main__":
    asyncio.run(monitor_jobs())
