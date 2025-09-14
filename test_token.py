import tweepy
import os
from dotenv import load_dotenv

load_dotenv()
BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

client = tweepy.Client(bearer_token=BEARER_TOKEN)

try:
    user = client.get_user(username="GearboxOfficial")
    print(user.data)
except tweepy.TweepyException as e:
    print(f"Error: {e}")
