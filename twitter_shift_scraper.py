import tweepy
import requests
import os
from dotenv import load_dotenv

# Load .env file if present (for local testing)
load_dotenv()

# Grab secrets from environment variables
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN") or os.getenv("BEARER_TOKEN")

# Safety checks
if not BEARER_TOKEN:
    print("❌ Error: Twitter Bearer Token not found!")
    exit(1)

if not DISCORD_WEBHOOK_URL:
    print("❌ Error: Discord Webhook URL not found!")
    exit(1)

print(f"✅ Using Twitter Bearer Token from {'TWITTER_BEARER_TOKEN' if os.getenv('TWITTER_BEARER_TOKEN') else 'BEARER_TOKEN'}")

# Accounts to monitor
ACCOUNTS = ["GearboxOfficial", "Borderlands", "BorderlandsGame", "ShiftCodesTK", "DuvalMagic"]

# Keywords to search for
KEYWORDS = [
    "shift code", "SHiFT code", "golden key", "redeem code", "codes",
    "bonus loot", "loot code", "special code", "promo code", "free keys",
    "borderlands code", "unlock", "vault hunter", "key code",
    "gearbox code", "shift rewards", "redeemable"
]

# Connect to Twitter API v2
client = tweepy.Client(bearer_token=BEARER_TOKEN)

def contains_keyword(text):
    """Check if tweet contains any target keyword."""
    return any(keyword.lower() in text.lower() for keyword in KEYWORDS)

def send_to_discord(username, tweet, text):
    """Send a tweet to Discord webhook."""
    content = (
        f"**New SHiFT Code Detected!**\n"
        f"Account: {username}\n"
        f"Tweet: {text}\n"
        f"Link: https://twitter.com/{username}/status/{tweet.id}"
    )
    response = requests.post(DISCORD_WEBHOOK_URL, json={"content": content})
    if response.status_code in (200, 204):
        print(f"✅ Sent to Discord: {text[:50]}...")
    else:
        print(f"❌ Failed to send: {tweet.id}, Status Code: {response.status_code}, Response: {response.text}")

def fetch_shift_codes():
    """Fetch tweets and post any new SHiFT codes to Discord."""
    for username in ACCOUNTS:
        try:
            print(f"🔍 Checking {username}...")
            user = client.get_user(username=username)
            if not user.data:
                print(f"⚠️ User {username} not found.")
                continue

            tweets = client.get_users_tweets(user.data.id, max_results=5)
            if not tweets.data:
                print(f"ℹ️ No tweets found for {username}.")
                continue

            for tweet in tweets.data:
                if contains_keyword(tweet.text):
                    send_to_discord(username, tweet, tweet.text)

        except tweepy.TooManyRequests:
            print(f"⚠️ Rate limit hit for {username}. Skipping this run.")
        except tweepy.errors.Unauthorized:
            print(f"❌ Unauthorized access for {username}. Check your Bearer Token.")
        except Exception as e:
            print(f"⚠️ Error fetching tweets for {username}: {e}")

if __name__ == "__main__":
    fetch_shift_codes()
