# job_notifier_ontario.py

import asyncio
import random
from dotenv import load_dotenv
from notifier import send_email
from playwright.async_api import async_playwright

load_dotenv()  # loads SENDER_EMAIL, SENDER_PASS, RECEIVER_EMAIL

async def apply_filters(page):
    # 1) Set Location → Ontario, Canada
    await page.wait_for_selector(
        'button[data-test-id="navigationLocationButton"]',
        state="visible"
    )
    await page.click(
        'button[data-test-id="navigationLocationButton"]',
        force=True
    )
    await page.wait_for_selector(
        '[data-test-id="zipcodeInputField"] input',
        state="visible"
    )
    await page.fill(
        '[data-test-id="zipcodeInputField"] input',
        "Ontario, Canada"
    )
    await page.keyboard.press("Enter")
    await page.wait_for_timeout(1000)

    # 2) Set Job keyword → warehouse
    await page.wait_for_selector(
        'button[aria-label="Focus search bar button"]',
        state="visible"
    )
    await page.click(
        'button[aria-label="Focus search bar button"]',
        force=True
    )
    await page.wait_for_selector(
        '[data-test-id="navigationSearchField"] input',
        state="visible"
    )
    await page.fill(
        '[data-test-id="navigationSearchField"] input',
        "warehouse"
    )
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
                await page.goto(
                    "https://hiring.amazon.ca/search/warehouse-jobs#/",
                    timeout=60000
                )

                # 2) Apply filters
                await apply_filters(page)

                # 3) Let the UI settle
                await page.wait_for_timeout(2000)

                # 4) Pull all job cards via JS
                jobs = await page.evaluate("""() => {
                    const cards = Array.from(document.querySelectorAll('div.job-tile'));
                    return cards.map(c => {
                        const t = c.querySelector('.job-title');
                        const l = c.querySelector('.job-location');
                        const a = c.querySelector('a');
                        return {
                            title:    t    ? t.textContent.trim()    : 'N/A',
                            location: l    ? l.textContent.trim()    : 'N/A',
                            link:     a    ? a.href                  : '',
                        };
                    });
                }""")

                if not jobs:
                    print("⏳ No new jobs right now.")
                else:
                    for job in jobs:
                        link = job["link"]
                        if not link or link in seen:
                            continue
                        seen.add(link)

                        body = "\n".join([
                            "-------------------------------",
                            f"Job:      {job['title']}",
                            f"Location: {job['location']}",
                            f"Link:     {job['link']}",
                            "-------------------------------",
                        ])
                        send_email(
                            subject=f"🔔 New Ontario Job: {job['title']} @ {job['location']}",
                            body=body
                        )
                        print(f"📧 Alert sent for: {job['title']} @ {job['location']}")

            except Exception as e:
                print("⚠️ Monitor loop error:", e)

            # 5) Pause before next cycle
            await asyncio.sleep(random.uniform(2, 5))

if __name__ == "__main__":
    asyncio.run(monitor_jobs())
