import asyncio
from apply import apply_to_job
from notifier import send_email
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Ensure the required environment variables are loaded
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASS = os.getenv("SENDER_PASS")

# Check if environment variables are set correctly
if not SENDER_EMAIL or not SENDER_PASS:
    print("❌ Error: SENDER_EMAIL or SENDER_PASS is not set in the environment.")
    exit(1)

# Define a test job for applying to
test_job = {
    "job_id": "TEST123",
    "title": "Amazon Warehouse Associate",
    "location": "Cambridge, ON",
    "link": "https://hiring.amazon.ca/search/warehouse-jobs#/"  # Use a real job link for testing
}

# Function to send a test email
def test_send_email():
    try:
        print("🚀 Attempting to send a test email...")
        send_email("✅ Test Subject", "This is a test body message.")
        print("✅ Test email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")

# Main async function to apply to a job
async def main():
    try:
        print(f"🚀 Applying to job: {test_job['title']} in {test_job['location']}")
        await apply_to_job(test_job)
        print("✅ Job application process completed!")
    except Exception as e:
        print(f"❌ Failed to apply to the job: {e}")

# Test email sending first
test_send_email()

# Run the job application process
if __name__ == "__main__":
    asyncio.run(main())

# Print loaded email credentials for verification
print(f"SENDER_EMAIL: {SENDER_EMAIL}, SENDER_PASS: {SENDER_PASS}")  # Just for checking

