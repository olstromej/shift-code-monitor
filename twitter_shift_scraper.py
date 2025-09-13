import snscrape.modules.twitter as sntwitter
import requests
import time
import os

DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
ACCOUNTS = ["GearboxOfficial", "Borderlands"]
KEYWORDS = ["shift code", "golden key", "redeem code"]
SEEN_TWEETS_FILE = "seen_tweets.txt"

# Load seen tweets
if os.path.exists(SEEN_TWEETS_FILE):
    with open(SEEN_TWEETS_FILE, "r") as f:
        seen_tweets = set(line.strip() for line in f.readlines())
else:
    seen_tweets = set()

def save_seen_tweet(tweet_id):
    seen_tweets.add(tweet_id)
    with open(SEEN_TWEETS_FILE, "a") as f:
        f.write(f"{tweet_id}\n")

def contains_keyword(text):
    return any(keyword.lower() in text.lower() for keyword in KEYWORDS)

def fetch_shift_codes():
    for username in ACCOUNTS:
        for tweet in sntwitter.TwitterUserScraper(username).get_items():
            if tweet.id not in seen_tweets and contains_keyword(tweet.content):
                send_to_discord(username, tweet)
                save_seen_tweet(tweet.id)
            break  # Only check the latest tweet per account

def send_to_discord(username, tweet):
    content = f"**New SHiFT Code Detected!**\nAccount: {username}\nTweet: {tweet.content}\nLink: https://twitter.com/{username}/status/{tweet.id}"
    response = requests.post(DISCORD_WEBHOOK_URL, json={"content": content})
    if response.status_code == 204:
        print(f"Sent to Discord: {tweet.content[:50]}...")
    else:
        print(f"Failed to send: {tweet.id}, Status Code: {response.status_code}")

if __name__ == "__main__":
    fetch_shift_codes()
