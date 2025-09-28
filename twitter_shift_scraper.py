import tweepy
import requests
import os
from dotenv import load_dotenv

# Load .env if running locally
load_dotenv()

# Grab secrets
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
API_KEY = os.getenv("TWITTER_API_KEY")
API_SECRET = os.getenv("TWITTER_API_SECRET")
ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")

# Safety checks
if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET]):
    print("❌ Error: Missing one or more Twitter API credentials!")
    exit(1)

if not DISCORD_WEBHOOK_URL:
    print("❌ Error: Discord Webhook URL not found!")
    exit(1)

# Accounts to monitor
ACCOUNTS = ["GearboxOfficial", "Borderlands", "BorderlandsGame", "ShiftCodesTK", "DuvalMagic"]

# Keywords to search for
KEYWORDS = [
    "shift code", "SHiFT code", "golden key", "redeem code", "codes",
    "bonus loot", "loot code", "special code", "promo code", "free keys",
    "borderlands code", "unlock", "vault hunter", "key code",
    "gearbox code", "shift rewards", "redeemable"
]

# Files to track seen tweets
SEEN_TWEETS_FILE = "seen_tweets.txt"
SEEN_TEXT_FILE = "seen_texts.txt"

seen_tweets = set()
if os.path.exists(SEEN_TWEETS_FILE):
    with open(SEEN_TWEETS_FILE, "r") as f:
        seen_tweets = set(line.strip() for line in f.readlines())

seen_texts = set()
if os.path.exists(SEEN_TEXT_FILE):
    with open(SEEN_TEXT_FILE, "r") as f:
        seen_texts = set(line.strip() for line in f.readlines())

# Authenticate with Twitter API v1.1
auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

def save_seen_tweet(tweet_id, tweet_text):
    """Save a tweet’s ID and text so we don’t process it again later."""
    seen_tweets.add(str(tweet_id))
    seen_texts.add(tweet_text)
    with open(SEEN_TWEETS_FILE, "a") as f:
        f.write(f"{tweet_id}\n")
    with open(SEEN_TEXT_FILE, "a") as f:
        f.write(f"{tweet_text}\n")

def contains_keyword(text):
    """Check if tweet contains any target keyword."""
    return any(keyword.lower() in text.lower() for keyword in KEYWORDS)

def send_to_discord(username, tweet, text):
    """Send tweet to Discord webhook."""
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
        print(f"❌ Discord error {response.status_code}: {response.text}")

def fetch_shift_codes():
    """Fetch tweets and send matches to Discord."""
    for username in ACCOUNTS:
        try:
            print(f"🔍 Checking {username}...")
            tweets = api.user_timeline(
                screen_name=username,
                count=5,
                tweet_mode="extended"
            )

            for tweet in tweets:
                text = tweet.full_text
                if (
                    str(tweet.id) not in seen_tweets
                    and text not in seen_texts
                    and contains_keyword(text)
                ):
                    send_to_discord(username, tweet, text)
                    save_seen_tweet(tweet.id, text)

        except tweepy.errors.Unauthorized:
            print(f"❌ Unauthorized for {username}. Check credentials.")
        except Exception as e:
            print(f"⚠️ Error fetching tweets for {username}: {e}")

if __name__ == "__main__":
    fetch_shift_codes()
