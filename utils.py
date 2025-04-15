import asyncio
import random
from playwright.async_api import async_playwright, Page, BrowserContext
from config import USER_DETAILS

# Optional: List of user agents for rotating
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# Optional: Proxy settings (update with your real proxy credentials or comment out if not needed)
USE_PROXY = False
PROXY_CONFIG = {
    "server": "http://your-proxy-server:port",  # Example: "http://123.45.67.89:8080"
    "username": "your-proxy-username",
    "password": "your-proxy-password"
}

# --- Launch browser with stealth options ---
async def get_browser(headless=True) -> tuple:
    playwright = await async_playwright().start()

    launch_args = {
        "headless": headless
    }

    if USE_PROXY:
        launch_args["proxy"] = PROXY_CONFIG

    browser = await playwright.chromium.launch(**launch_args)

    context = await browser.new_context(
        user_agent=random.choice(USER_AGENTS),
        viewport={"width": 1280, "height": 800},
        java_script_enabled=True,
        bypass_csp=True,
        locale="en-US",
        timezone_id="America/Toronto"
    )

    return browser, context


# --- Simulate human-like typing ---
async def human_type(page: Page, selector: str, text: str, min_delay=50, max_delay=150):
    for char in text:
        await page.fill(selector, await page.input_value(selector) + char)
        await asyncio.sleep(random.uniform(min_delay / 1000, max_delay / 1000))


# --- Login Function (modify based on actual login flow) ---
async def login_amazon(page: Page, email: str, password: str):
    await page.goto("https://www.amazon.jobs/en/login")
    await page.wait_for_selector("#ap_email")

    await human_type(page, "#ap_email", email)
    await page.click("#continue")

    await page.wait_for_selector("#ap_password")
    await human_type(page, "#ap_password", password)

    await page.click("#signInSubmit")
    await page.wait_for_load_state("networkidle")

    print("🔐 Logged in successfully.")


# --- Reusable function to fill form fields safely ---
async def safe_fill(page: Page, selector: str, value: str):
    try:
        await page.fill(selector, value)
    except Exception:
        print(f"⚠️ Could not fill selector: {selector}")


# --- Simulate resume upload ---
async def upload_resume(page: Page, resume_path: str = "resume.pdf"):
    try:
        await page.set_input_files('input[type="file"]', resume_path)
        print("📎 Resume uploaded.")
    except Exception:
        print("⚠️ Resume upload field not found.")


# --- Reusable delay ---
async def wait_random(min_sec=1, max_sec=3):
    await asyncio.sleep(random.uniform(min_sec, max_sec))
