
import asyncio
from job_checker import get_new_jobs
from apply import apply_to_job

async def main():
    new_jobs = await get_new_jobs()
    if not new_jobs:
        print("🟡 No new jobs found.")
        return

    for job in new_jobs:
        await apply_to_job(job)

asyncio.run(main())
