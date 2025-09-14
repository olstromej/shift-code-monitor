import tweepy
import requests
import os
from dotenv import load_dotenv
from tweepy.errors import TooManyRequests
from datetime import datetime

# Load environment variables
load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

ACCOUNTS = ["GearboxOfficial", "Borderlands"]
KEYWORDS = ["shift code", "golden key", "redeem code"]

SEEN_TWEETS_FILE = "seen_tweets.txt"
LOG_FILE = "shift_codes_log.txt"

# Ensure files exist
if not os.path.exists(SEEN_TWEETS_FILE):
    open(SEEN_TWEETS_FILE, 'w').close()

if not os.path.exists(LOG_FILE):
    open(LOG_FILE, 'w').close()

# Load seen tweets
with open(SEEN_TWEETS_FILE, "r") as f:
    seen_tweets = set(line.strip() for line in f.readlines())

# Initialize Tweepy client
client = tweepy.Client(bearer_token=BEARER_TOKEN)

def save_seen_tweet(tweet_id):
    seen_tweets.add(str(tweet_id))
    with open(SEEN_TWEETS_FILE, "a") as f:
        f.write(f"{tweet_id}\n")

def log_shift_code(username, tweet_id, tweet_text):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {username} ({tweet_id}): {tweet_text}\n")

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
    if response.status_code == 204:
        print(f"Sent to Discord: {tweet.text[:50]}...")
    else:
        print(f"Failed to send: {tweet.id}, Status Code: {response.status_code}")

def fetch_shift_codes():
    for username in ACCOUNTS:
        try:
            user = client.get_user(username=username)
            if not user.data:
                continue

            tweets = client.get_users_tweets(user.data.id, max_results=5)
            if not tweets.data:
                continue

            tweet = tweets.data[0]  # most recent tweet only
            tweet_id_str = str(tweet.id)

            if tweet_id_str not in seen_tweets:
                if contains_keyword(tweet.text):
                    send_to_discord(username, tweet)
                    log_shift_code(username, tweet.id, tweet.text)
                save_seen_tweet(tweet.id)

        except TooManyRequests:
            print(f"Rate limit hit for {username}. Skipping this run.")
        except Exception as e:
            print(f"Error fetching tweets for {username}: {e}")

if __name__ == "__main__":
    fetch_shift_codes()
