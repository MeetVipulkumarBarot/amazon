import asyncio
import random
from datetime import datetime
from utils import get_browser, wait_random
from apply import apply_to_job
from notifier import send_email

PREFERRED_CITIES = ["Cambridge", "Hamilton", "Brampton", "Mississauga", "London", "St Thomas"]

def job_matches_location(job):
    for city in PREFERRED_CITIES:
        if city.lower() in job['location'].lower():
            return True
    return False

async def fetch_available_jobs(page):
    await page.goto("https://hiring.amazon.ca/search/warehouse-jobs#/")
    await page.wait_for_timeout(5000)  # Allow JS to load

    jobs = []

    try:
        # Try to get all job tiles
        job_elements = await page.query_selector_all('.job-tile')

        if not job_elements:
            print("🔄 No job postings available currently. Will check again...")
            return []

        for el in job_elements:
            title = await el.query_selector_eval('.job-title', 'el => el.textContent') if await el.query_selector('.job-title') else "No title"
            location = await el.query_selector_eval('.job-location', 'el => el.textContent') if await el.query_selector('.job-location') else "No location"
            link = await el.query_selector_eval('a', 'el => el.href') if await el.query_selector('a') else "No link"

            jobs.append({
                'title': title.strip(),
                'location': location.strip(),
                'link': link.strip(),
                'timestamp': str(datetime.now())
            })

    except Exception as e:
        print(f"⚠️ Scraping error (non-critical): {e}")
        return []

    return jobs

async def monitor_jobs():
    browser, context = await get_browser()
    page = await context.new_page()

    print("🔍 Bot started monitoring jobs...")

    seen_jobs = set()

    while True:
        try:
            jobs = await fetch_available_jobs(page)

            for job in jobs:
                title = job['title']
                location = job['location']
                link = job['link']

                if job_matches_location(job) and link not in seen_jobs:
                    print(f"✅ Found job at {location}: {title}")
                    seen_jobs.add(link)

                    try:
                        # Apply to the job
                        await apply_to_job(job)
                        print(f"🚀 Applied to job: {title} in {location}")

                        # Send Email Notification
                        send_email(
                            subject=f"✅ Job Applied: {title} in {location}",
                            body=f"Your bot applied to the job:\n\nTitle: {title}\nLocation: {location}\nLink: {link}\nTime: {job['timestamp']}"
                        )
                    except Exception as app_error:
                        print(f"⚠️ Failed to apply: {app_error}")
                        send_email(
                            subject="❗ Job Application Failed",
                            body=f"Bot found a job, but failed to apply:\n\n{app_error}"
                        )
                else:
                    print(f"❌ Job doesn't match preferred cities or already seen: {title} - {location}")

        except Exception as e:
            print(f"⚠️ Error occurred: {e}")
            try:
                send_email(
                    subject="❗ Bot Error Alert",
                    body=f"An error occurred:\n\n{e}"
                )
            except:
                print("❌ Failed to send error email.")

            await asyncio.sleep(5)  # wait before retry

        # 🔁 Wait between 0 to 3 seconds before checking again
        await wait_random(0, 3)

    await browser.close()

if __name__ == "__main__":
    asyncio.run(monitor_jobs())
