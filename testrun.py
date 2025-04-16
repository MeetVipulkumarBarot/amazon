import asyncio
import logging
import time
from apply import apply_to_job
from notifier import send_email
from dotenv import load_dotenv
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables with explicit path if needed
env_path = '/.env'  # Update this
load_dotenv(env_path)

# Environment variables verification
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASS = os.getenv("SENDER_PASS")

if not SENDER_EMAIL or not SENDER_PASS:
    logger.error("❌ SENDER_EMAIL or SENDER_PASS not set")
    exit(1)

test_job = {
    "job_id": "TEST123",
    "title": "Amazon Warehouse Associate",
    "location": "Cambridge, ON",
    "link": "https://hiring.amazon.ca/search/warehouse-jobs#/"
}

def test_send_email():
    try:
        logger.info("🚀 Attempting to send test email...")
        send_email("✅ Test Subject", "This is a test body message.")
        logger.info("✅ Test email sent!")
    except Exception as e:
        logger.error(f"❌ Email failed: {e}", exc_info=True)

async def main():
    try:
        logger.info(f"🚀 Applying to {test_job['title']}")
        start_time = time.time()
        await apply_to_job(test_job)
        logger.info(f"✅ Application completed in {time.time()-start_time:.2f}s")
    except Exception as e:
        logger.error(f"❌ Application failed: {e}", exc_info=True)

if __name__ == "__main__":
    logger.info("=== Starting Tests ===")
    test_send_email()
    
    start_total = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    logger.info(f"=== Total execution: {time.time()-start_total:.2f}s ===")
    
    # Credentials verification
    logger.info(f"Credentials check - Email: {'set' if SENDER_EMAIL else 'not set'}")