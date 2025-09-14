import tweepy
import requests
import os
import time
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Discord webhook and Twitter credentials
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Twitter accounts to monitor
ACCOUNTS = [
    "GearboxOfficial",
    "Borderlands",
    "BorderlandsScience",
    "BorderlandsFilm"
]

# Keywords to look for in tweets
KEYWORDS = [
    "shift code",
    "golden key",
    "diamond key",
    "vault code",
    "redeem code",
    "xp boost",
    "vault card",
    "heads",
    "skins"
]

# File to keep track of already seen tweets
SEEN_TWEETS_FILE = "seen_tweets.txt"

# File to log found SHiFT codes
SHIFT_LOG_FILE = "shift_codes_log.txt"

# Load seen tweets from file
if os.path.exists(SEEN_TWEETS_FILE):
    with open(SEEN_TWEETS_FILE, "r") as f:
        seen_tweets = set(line.strip() for line in f.readlines())
else:
    seen_tweets = set()

# Initialize Tweepy client
client = tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)

def save_seen_tweet(tweet_id):
    """Save a tweet ID to the seen_tweets set and file."""
    seen_tweets.add(str(tweet_id))
    with open(SEEN_TWEETS_FILE, "a") as f:
        f.write(f"{tweet_id}\n")

def log_shift_code(username, tweet):
    """Log SHiFT code tweet locally."""
    with open(SHIFT_LOG_FILE, "a") as f:
        f.write(f"{username}: {tweet.text}\nhttps://twitter.com/{username}/status/{tweet.id}\n\n")

def contains_keyword(text):
    """Check if a tweet contains any of the keywords."""
    return any(keyword.lower() in text.lower() for keyword in KEYWORDS)

def send_to_discord(username, tweet):
    """Send detected SHiFT code tweet to Discord."""
    content = (
        f"**New SHiFT Code Detected!**\n"
        f"Account: {username}\n"
        f"Tweet: {tweet.text}\n"
        f"Link: https://twitter.com/{username}/status/{tweet.id}"
    )
    response = requests.post(DISCORD_WEBHOOK_URL, json={"content": content})
    if response.status_code == 204:
        print(f"✅ Sent to Discord: {tweet.text[:50]}...")
    else:
        print(f"❌ Failed to send: {tweet.id}, Status Code: {response.status_code}")

def fetch_shift_codes():
    """Fetch latest tweets from monitored accounts and send new SHiFT codes to Discord."""
    for username in ACCOUNTS:
        try:
            user = client.get_user(username=username)
            if not user.data:
                continue

            tweets = client.get_users_tweets(user.data.id, max_results=10)
            if not tweets.data:
                continue

            for tweet in tweets.data:
                if str(tweet.id) not in seen_tweets and contains_keyword(tweet.text):
                    send_to_discord(username, tweet)
                    log_shift_code(username, tweet)
                    save_seen_tweet(tweet.id)

        except tweepy.TooManyRequests:
            print(f"⚠️ Rate limit hit for {username}. Skipping this run.")
            time.sleep(900)  # wait 15 minutes
        except Exception as e:
            print(f"Error fetching tweets for {username}: {e}")

if __name__ == "__main__":
    fetch_shift_codes()
