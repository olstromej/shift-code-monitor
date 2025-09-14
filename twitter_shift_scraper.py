import tweepy
import requests
import os
from dotenv import load_dotenv

# Load variables from a .env file if present
load_dotenv()

# Grab secrets from environment variables (GitHub Actions or local .env)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN") or os.getenv("BEARER_TOKEN")

# Safety checks to make sure required credentials exist
if not BEARER_TOKEN:
    print("❌ Error: Twitter Bearer Token not found!")
    exit(1)

if not DISCORD_WEBHOOK_URL:
    print("❌ Error: Discord Webhook URL not found!")
    exit(1)

# Twitter accounts we’ll monitor for SHiFT codes
ACCOUNTS = ["GearboxOfficial", "Borderlands", "BorderlandsGame", "ShiftCodesTK", "DuvalMagic"]

# Keywords that we’ll search for in tweets
KEYWORDS = [
    "shift code", "SHiFT code", "golden key", "redeem code", "codes",
    "bonus loot", "loot code", "special code", "promo code", "free keys",
    "borderlands code", "unlock", "vault hunter", "key code",
    "gearbox code", "shift rewards", "redeemable"
]

# Files to track already-processed tweets (IDs and full text)
SEEN_TWEETS_FILE = "seen_tweets.txt"
SEEN_TEXT_FILE = "seen_texts.txt"

# Load tweet IDs we’ve already processed
seen_tweets = set()
if os.path.exists(SEEN_TWEETS_FILE):
    with open(SEEN_TWEETS_FILE, "r") as f:
        seen_tweets = set(line.strip() for line in f.readlines())

# Load tweet texts we’ve already processed (extra protection against duplicates)
seen_texts = set()
if os.path.exists(SEEN_TEXT_FILE):
    with open(SEEN_TEXT_FILE, "r") as f:
        seen_texts = set(line.strip() for line in f.readlines())

# Connect to Twitter API using Tweepy and Bearer Token
client = tweepy.Client(bearer_token=BEARER_TOKEN)

def save_seen_tweet(tweet_id, tweet_text):
    """Save a tweet’s ID and text so we don’t process it again later."""
    seen_tweets.add(str(tweet_id))
    seen_texts.add(tweet_text)
    with open(SEEN_TWEETS_FILE, "a") as f:
        f.write(f"{tweet_id}\n")
    with open(SEEN_TEXT_FILE, "a") as f:
        f.write(f"{tweet_text}\n")

def contains_keyword(text):
    """Check if tweet contains any of our target keywords."""
    return any(keyword.lower() in text.lower() for keyword in KEYWORDS)

def send_to_discord(username, tweet):
    """Send a tweet that looks like a SHiFT code to Discord via webhook."""
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
    """Main function: fetch tweets from accounts, filter by keyword, send to Discord."""
    for username in ACCOUNTS:
        try:
            # Get Twitter user by username
            user = client.get_user(username=username)
            if not user.data:
                print(f"⚠️ User {username} not found.")
                continue

            # Fetch up to 5 most recent tweets
            tweets = client.get_users_tweets(user.data.id, max_results=5)
            if not tweets.data:
                continue

            # Loop through tweets and check for new SHiFT codes
            for tweet in tweets.data:
                if (
                    str(tweet.id) not in seen_tweets  # not seen before
                    and tweet.text not in seen_texts  # text not seen before
                    and contains_keyword(tweet.text)  # matches keywords
                ):
                    send_to_discord(username, tweet)
                    save_seen_tweet(tweet.id, tweet.text)

        # Handle Twitter API rate limit (TooManyRequests error)
        except tweepy.TooManyRequests:
            print(f"⚠️ Rate limit hit for {username}. Skipping this run.")

        # Handle invalid credentials / permissions
        except tweepy.errors.Unauthorized:
            print(f"❌ Unauthorized access for {username}. Check your Bearer Token.")

        # Catch-all for other errors
        except Exception as e:
            print(f"⚠️ Error fetching tweets for {username}: {e}")

if __name__ == "__main__":
    # Run once each time the script is executed
    fetch_shift_codes()
