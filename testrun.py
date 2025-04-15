# test_run.py

import asyncio
from apply import apply_to_job
from notifier import send_email
from dotenv import load_dotenv
import os


test_job = {
    "job_id": "TEST123",
    "title": "Amazon Warehouse Associate",
    "location": "Cambridge, ON",
    "link": "https://hiring.amazon.ca/search/warehouse-jobs#/"  # Use a real job link for testing
}

send_email("✅ Test Subject", "This is a test body message.")
async def main():
    await apply_to_job(test_job)

if __name__ == "__main__":
    asyncio.run(main())

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASS = os.getenv("SENDER_PASS")

print(SENDER_EMAIL, SENDER_PASS)  # Just for checking
