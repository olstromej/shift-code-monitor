#!/usr/bin/env python3
import os
import requests
import time
import re
from datetime import datetime

# ------------------------
# Configuration
# ------------------------
TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
if not TWITTER_BEARER_TOKEN:
    raise ValueError("TWITTER_BEARER_TOKEN environment variable not set.")

ACCOUNTS = [
    "GearboxOfficial",
    "Borderlands",
    "BorderlandsGame",
    "ShiftCodesTK",
    "DuvalMagic"
]

MAX_RESULTS = 10  # between 5 and 100
SLEEP_BETWEEN_ACCOUNTS = 31  # seconds

# Regex pattern for Shift Codes (example: XXXX-XXXX-XXXX-XXXX)
SHIFT_CODE_PATTERN = re.compile(r'\b[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}\b')

# ------------------------
# Helper functions
# ------------------------
def fetch_tweets(username):
    url = f"https://api.twitter.com/2/tweets/search/recent"
    headers = {"Authorization": f"Bearer {TWITTER_BEARER_TOKEN}"}
    query = {
        "query": f"from:{username}",
        "max_results": MAX_RESULTS,
        "tweet.fields": "created_at,text"
    }
    
    response = requests.get(url, headers=headers, params=query)
    
    if response.status_code == 429:
        raise Exception("RateLimitError")
    elif response.status_code != 200:
        raise Exception(f"Error {response.status_code}: {response.text}")
    
    return response.json()

def extract_shift_codes(text):
    return SHIFT_CODE_PATTERN.findall(text)

def log_shift_codes(account, tweets):
    found = False
    if "data" in tweets:
        for tweet in tweets["data"]:
            text = tweet["text"].replace("\n", " ")
            codes = extract_shift_codes(text)
            if codes:
                found = True
                created_at = tweet["created_at"]
                for code in codes:
                    print(f"[{created_at}] {account}: {code}")
    if not found:
        print(f"No shift codes found for {account}")

# ------------------------
# Main loop
# ------------------------
def main():
    print(f"✅ Using Twitter *** from TWITTER_BEARER_TOKEN")
    
    for account in ACCOUNTS:
        print(f"🔍 Checking {account}...")
        
        for attempt in range(3):  # retry up to 3 times if rate-limited
            try:
                tweets = fetch_tweets(account)
                log_shift_codes(account, tweets)
                break
            except Exception as e:
                if "RateLimitError" in str(e):
                    print(f"⚠️ Rate limit hit for {account}. Waiting {SLEEP_BETWEEN_ACCOUNTS} seconds before retry...")
                    time.sleep(SLEEP_BETWEEN_ACCOUNTS)
                else:
                    print(f"⚠️ Error fetching tweets for {account}: {e}")
                    break
        time.sleep(SLEEP_BETWEEN_ACCOUNTS)

if __name__ == "__main__":
    main()
