# job_checker.py

import asyncio
from playwright.async_api import async_playwright
import pymongo
from config import USER_DETAILS, MONGO_URI, MONGO_DB_NAME, MONGO_COLLECTION_NAME

async def get_new_jobs():
    # Setup MongoDB
    client = pymongo.MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    collection = db[MONGO_COLLECTION_NAME]

    new_jobs = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for city in USER_DETAILS["preferred_cities"]:
            print(f"🔍 Checking jobs in: {city}")
            search_url = f"https://www.amazon.jobs/en/search?base_query=warehouse&loc_query={city},%20Ontario,%20Canada"
            await page.goto(search_url)
            await page.wait_for_load_state("networkidle")

            job_cards = await page.query_selector_all("div.job-tile")

            for job in job_cards:
                title = await job.query_selector_eval("h3", "el => el.textContent.trim()")
                location = await job.query_selector_eval("p.location-and-id", "el => el.textContent.trim()")
                link = await job.query_selector_eval("a", "el => el.href")

                job_id = link.split("/")[-1]

                # Check if already applied
                if collection.find_one({"job_id": job_id}):
                    continue

                # Save job temporarily for applying
                new_jobs.append({
                    "job_id": job_id,
                    "title": title,
                    "location": location,
                    "link": link
                })

        await browser.close()

    return new_jobs
