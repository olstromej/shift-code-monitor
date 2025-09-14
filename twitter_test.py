import tweepy
import requests
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Twitter API and Discord webhook
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# Test account and keywords
USERNAME = "ShiftCodesTK"
KEYWORDS = ["shift code", "golden key", "redeem code"]

def contains_keyword(text):
    """Check if tweet contains any keyword."""
    return any(keyword.lower() in text.lower() for keyword in KEYWORDS)

def send_to_discord(tweet):
    """Send tweet to Discord."""
    content = (
        f"**Test SHiFT Code Detected!**\n"
        f"Account: {USERNAME}\n"
        f"Tweet: {tweet.text}\n"
        f"Link: https://twitter.com/{USERNAME}/status/{tweet.id}"
    )
    response = requests.post(DISCORD_WEBHOOK_URL, json={"content": content})
    if response.status_code in (200, 204):
        print(f"✅ Sent to Discord: {tweet.text[:50]}...")
    else:
        print(f"❌ Failed to send: {tweet.id}, Status Code: {response.status_code}")

def fetch_test_tweets():
    """Fetch recent tweets from the test account."""
    client = tweepy.Client(bearer_token=BEARER_TOKEN)
    try:
        user = client.get_user(username=USERNAME)
        if not user.data:
            print(f"User {USERNAME} not found.")
            return

        tweets = client.get_users_tweets(user.data.id, max_results=5)
        if not tweets.data:
            print(f"No tweets found for {USERNAME}")
            return

        for tweet in tweets.data:
            print(f"- {tweet.text}\nLink: https://twitter.com/{USERNAME}/status/{tweet.id}\n")
            if contains_keyword(tweet.text):
                send_to_discord(tweet)

    except tweepy.TooManyRequests:
        print("⚠️ Rate limit hit. Try again later.")
    except Exception as e:
        print(f"Error fetching tweets: {e}")

if __name__ == "__main__":
    fetch_test_tweets()
