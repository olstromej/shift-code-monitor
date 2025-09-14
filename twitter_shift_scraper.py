import tweepy
import requests
import os
from dotenv import load_dotenv

# Load .env if exists
load_dotenv()

# Use env vars from GitHub Actions or .env
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN") or os.getenv("BEARER_TOKEN")

if not BEARER_TOKEN:
    print("❌ Error: Twitter Bearer Token not found!")
    exit(1)

if not DISCORD_WEBHOOK_URL:
    print("❌ Error: Discord Webhook URL not found!")
    exit(1)

ACCOUNTS = ["GearboxOfficial", "Borderlands", "BorderlandsGame", "ShiftCodesTK", "DuvalMagic"]
KEYWORDS = ["shift code", "golden key", "redeem code"]

SEEN_TWEETS_FILE = "seen_tweets.txt"
SEEN_TEXT_FILE = "seen_texts.txt"

# Load seen tweet IDs
seen_tweets = set()
if os.path.exists(SEEN_TWEETS_FILE):
    with open(SEEN_TWEETS_FILE, "r") as f:
        seen_tweets = set(line.strip() for line in f.readlines())

# Load seen tweet texts
seen_texts = set()
if os.path.exists(SEEN_TEXT_FILE):
    with open(SEEN_TEXT_FILE, "r") as f:
        seen_texts = set(line.strip() for line in f.readlines())

# Initialize Tweepy client
client = tweepy.Client(bearer_token=BEARER_TOKEN)

def save_seen_tweet(tweet_id, tweet_text):
    seen_tweets.add(str(tweet_id))
    seen_texts.add(tweet_text)
    with open(SEEN_TWEETS_FILE, "a") as f:
        f.write(f"{tweet_id}\n")
    with open(SEEN_TEXT_FILE, "a") as f:
        f.write(f"{tweet_text}\n")

def contains_keyword(text):
    return any(keyword.lower() in text.lower() for keyword in KEYWORDS)

def send_to_discord(username, tweet):
    content = (
        f"**New SHiFT Code Detected!**\n"
        f"Account: {username}\n"
        f"Tweet: {tweet.text}\n"
        f"Link: https://twitter.com/{username}/status/{tweet.id}"
    )
    response = requests.post(DISCORD_WEBHOOK_URL, json={"content": content})
    if response.status_code in (200, 204):
        print(f"✅ Sent to Discord: {tweet.text[:50]}...")
    else:
        print(f"❌ Failed to send: {tweet.id}, Status Code: {response.status_code}")

def fetch_shift_codes():
    for username in ACCOUNTS:
        try:
            user = client.get_user(username=username)
            if not user.data:
                print(f"⚠️ User {username} not found.")
                continue

            tweets = client.get_users_tweets(user.data.id, max_results=5)
            if not tweets.data:
                continue

            for tweet in tweets.data:
                if (str(tweet.id) not in seen_tweets) and (tweet.text not in seen_texts) and contains_keyword(tweet.text):
                    send_to_discord(username, tweet)
                    save_seen_tweet(tweet.id, tweet.text)

        except tweepy.TooManyRequests:
            print(f"⚠️ Rate limit hit for {username}. Skipping this run.")
        except tweepy.errors.Unauthorized:
            print(f"❌ Unauthorized access for {username}. Check your Bearer Token.")
        except Exception as e:
            print(f"⚠️ Error fetching tweets for {username}: {e}")

if __name__ == "__main__":
    fetch_shift_codes()
