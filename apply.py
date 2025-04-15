# apply.py

import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
import pymongo
from config import USER_DETAILS, MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME
from utils import human_type, safe_fill, upload_resume, wait_random

async def apply_to_job(job):
    print(f"🚀 Applying to: {job['title']} in {job['location']}")

    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION_NAME]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Set to False to see the browser
        page = await browser.new_page()

        try:
            await page.goto(job["link"], timeout=30000)
            await page.wait_for_load_state("networkidle")
            await wait_random()

            # Check if "Apply Now" or similar button exists
            apply_button = await page.query_selector("text='Apply Now'") or await page.query_selector("text='Start application'")
            if apply_button:
                await apply_button.click()
                await page.wait_for_timeout(2000)

                # Fill out application fields (example only)
                await safe_fill(page, 'input[name="email"]', USER_DETAILS["email"])
                await wait_random()
                await safe_fill(page, 'input[name="phone"]', USER_DETAILS["phone"])
                await wait_random()

                # Upload resume
                await upload_resume(page, "resume.pdf")
                await wait_random()

                # Submit form
                submit_button = await page.query_selector("text='Submit Application'") or await page.query_selector("text='Continue'")
                if submit_button:
                    await submit_button.click()
                    await page.wait_for_timeout(2000)
                    print(f"✅ Application submitted for: {job['title']}")
                else:
                    print("⚠️ No Submit button found.")

                # Save application to MongoDB
                collection.insert_one({
                    "user_email": USER_DETAILS["email"],
                    "job_id": job.get("job_id") or job["link"],
                    "title": job["title"],
                    "location": job["location"],
                    "applied_at": job.get("timestamp") or "now"
                })
            else:
                print("❌ No 'Apply Now' button found on page.")

        except PlaywrightTimeout:
            print("⏱️ Timeout while loading the page.")
        except Exception as e:
            print(f"🔥 Unexpected error during application: {e}")
        finally:
            await browser.close()
