import tweepy
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

# Twitter accounts to monitor (added ShiftCodesTK)
ACCOUNTS = ["GearboxOfficial", "Borderlands", "ShiftCodesTK"]
KEYWORDS = ["shift code", "golden key", "redeem code"]

SEEN_TWEETS_FILE = "seen_tweets.txt"
LOG_FILE = "shift_codes_log.txt"

# Load seen tweets
if os.path.exists(SEEN_TWEETS_FILE):
    with open(SEEN_TWEETS_FILE, "r") as f:
        seen_tweets = set(line.strip() for line in f.readlines())
else:
    seen_tweets = set()

client = tweepy.Client(bearer_token=BEARER_TOKEN)

def save_seen_tweet(tweet_id):
    seen_tweets.add(str(tweet_id))
    with open(SEEN_TWEETS_FILE, "a") as f:
        f.write(f"{tweet_id}\n")

def log_message(message):
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")

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
        print(f"✅ Sent to Discord: {tweet.text[:50]}...")
        log_message(f"Sent: {tweet.text[:100]}...")
    else:
        print(f"❌ Failed to send: {tweet.id}, Status Code: {response.status_code}")
        log_message(f"Failed to send tweet {tweet.id}, Status: {response.status_code}")

def fetch_shift_codes():
    for username in ACCOUNTS:
        try:
            user = client.get_user(username=username)
            if not user.data:
                continue

            tweets = client.get_users_tweets(user.data.id, max_results=5)
            if not tweets.data:
                continue

            for tweet in tweets.data:
                if str(tweet.id) not in seen_tweets and contains_keyword(tweet.text):
                    send_to_discord(username, tweet)
                    save_seen_tweet(tweet.id)
        except tweepy.TooManyRequests:
            print(f"⚠️ Rate limit hit for {username}. Skipping this run.")
            log_message(f"Rate limit hit for {username}")
        except Exception as e:
            print(f"Error fetching tweets for {username}: {e}")
            log_message(f"Error fetching tweets for {username}: {e}")

if __name__ == "__main__":
    fetch_shift_codes()
