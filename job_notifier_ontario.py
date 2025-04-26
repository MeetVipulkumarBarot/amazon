import os
import time
import random
import requests
from dotenv import load_dotenv
from notifier import send_email

# ─── Load creds and token ──────────────────────────────────────────────────────
load_dotenv()
SENDER_EMAIL   = os.getenv("SENDER_EMAIL")
SENDER_PASS    = os.getenv("SENDER_PASS")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
AUTH_TOKEN     = os.getenv("AMAZON_AUTH_TOKEN")
GRAPHQL_URL    = os.getenv(
    "AMAZON_GRAPHQL_URL",
    "https://e5mquma77feepi2bdn4d6h3mpu.appsync-api.us-east-1.amazonaws.com/graphql"
)

if not (SENDER_EMAIL and SENDER_PASS and RECEIVER_EMAIL):
    raise RuntimeError("Missing SENDER_EMAIL, SENDER_PASS or RECEIVER_EMAIL in .env")
if not AUTH_TOKEN:
    raise RuntimeError("Missing AMAZON_AUTH_TOKEN in .env")

# ─── The exact query your browser sends ────────────────────────────────────────
SEARCH_QUERY = r"""
query searchJobCardsByLocation($searchJobRequest: SearchJobRequest!) {
  searchJobCardsByLocation(searchJobRequest: $searchJobRequest) {
    jobCards {
      jobId
      jobTitle
      locationName
      scheduleCount
      employmentTypeL10N
      totalPayRateMinL10N
      totalPayRateMaxL10N
    }
  }
}
"""

def fetch_jobs():
    payload = {
      "operationName": "searchJobCardsByLocation",
      "query": SEARCH_QUERY,
      "variables": {
        "searchJobRequest": {
          "locale":       "en-CA",
          "country":      "Canada",
          "keyWords":     "warehouse",
          "equalFilters": [],
          "offset":       0,
          "pageSize":     100,
          "distance":     None,
          "postalCode":   None,
          "sortBy":       None,
          "mapBounds":    None
        }
      }
    }
    headers = {
      "Content-Type":  "application/json",
      "Accept":        "*/*",
      "Origin":        "https://hiring.amazon.ca",
      "Referer":       "https://hiring.amazon.ca/",
      "authorization": f"Bearer {AUTH_TOKEN}",
      "country":       "Canada",
      "iscanary":      "false"
    }

    resp = requests.post(GRAPHQL_URL, json=payload, headers=headers)
    try:
        resp.raise_for_status()
    except Exception as e:
        print("❌ HTTP error:", e, resp.text)
        return []

    try:
        js = resp.json()
    except ValueError as e:
        print("❌ Failed to parse JSON:", e, resp.text)
        return []

    # drill down safely
    data = js.get("data")
    if not isinstance(data, dict):
        print("⚠️ No `data` in GraphQL response:", js)
        return []
    response = data.get("searchJobCardsByLocation")
    if not isinstance(response, dict):
        print("⚠️ No `searchJobCardsByLocation` in data:", js)
        return []
    cards = response.get("jobCards")
    if not isinstance(cards, list):
        print("⚠️ `jobCards` is not a list:", js)
        return []

    return cards

def main():
    seen = set()
    print("🔍 Monitoring Ontario warehouse jobs via GraphQL…")

    # SMTP smoke-test
    try:
        send_email("🔥 TEST ALERT", "GraphQL notifier is running.")
        print("📧 Test alert sent.")
    except Exception as e:
        print("❌ SMTP test failed:", e)

    while True:
        try:
            cards = fetch_jobs()
            if not cards:
                print("⏳ No new jobs right now.")
            else:
                for c in cards:
                    jid = c.get("jobId")
                    if not jid or jid in seen:
                        continue
                    seen.add(jid)

                    title    = c.get("jobTitle",            "N/A")
                    location = c.get("locationName",        "N/A")
                    shifts   = c.get("scheduleCount",       "N/A")
                    emp_type = c.get("employmentTypeL10N",  "N/A")
                    pm       = c.get("totalPayRateMinL10N", "")
                    px       = c.get("totalPayRateMaxL10N", "")
                    pay      = f"{pm} – {px}" if pm and px else (pm or px or "N/A")

                    link = (
                        f"https://hiring.amazon.ca/app#/jobSearch?"
                        f"jobId={jid}&locale=en-CA"
                    )

                    body = "\n".join([
                        "-------------------------------",
                        f"Shifts:   {shifts}",
                        f"Location: {location}",
                        f"Type:     {emp_type}",
                        f"Pay:      {pay}",
                        f"Job:      {title}",
                        f"Link:     {link}",
                        "-------------------------------",
                    ])
                    send_email(
                        subject=f"🔔 New Ontario Job: {title} @ {location}",
                        body=body
                    )
                    print(f"📧 Alert sent for: {title} @ {location}")

        except Exception as e:
            print("⚠️ Error fetching/sending:", e)

        time.sleep(random.uniform(30, 60))

if __name__ == "__main__":
    main()
