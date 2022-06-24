import os
import tweepy
from dotenv import load_dotenv

def post_twitter_link(txt, link):

    load_dotenv()
    
    api_key = os.getenv("TWITTER_API_KEY")
    api_key_secret = os.getenv("TWITTER_API_SECRET")

    access_token = os.getenv("TWITTER_ACESSS_TOKEN")
    access_token_secret = os.getenv("TWITTER_ACCESS_SECRET")
    # bearer_token  = os.getenv("TWITTER_BEARER_TOKEN")

    print(api_key)
    print(api_key_secret)
    print(access_token)
    print(access_token_secret)

    client = tweepy.Client(consumer_key=api_key, consumer_secret=api_key_secret, access_token=access_token, access_token_secret=access_token_secret)

    response = client.create_tweet(
         text=txt + " " + link,
    )

    return response



post_twitter_link("Search with Bing!", "https://www.bing.com")