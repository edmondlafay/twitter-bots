# -*- coding: utf-8 -*-
import tweepy, time, logging
from ..common.utils import twitter_auth, limit_handled


class ProperDeals:
  name = 'proper_deals'
  shopping_list='shopping'
  shopping_author='seigneurcanard'
  timeout=60

  def __init__(self):
    self.thread = None
    self.api = tweepy.API(twitter_auth(self.name), wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    try:
      self.api.verify_credentials()
      logging.debug("%s : Authentication OK", self.name)
    except:
      logging.error("%s : Error during authentication", self.name)
  
  def get_last_retweet_id(self):
    for tweet in self.api.user_timeline(count=1):
      return tweet.retweeted_status.id
    return 0
  
  def post_tweet(self, text, retries=3):
    try:
      self.api.update_status()
    except tweepy.RateLimitError:
      if retries>0:
        twitbot_timeout(self, 'warn', f"{self.name} : rate limit exceeded post_tweet, sleeping {self.timeout} mins")
        self.post_tweet(text, retries=retries-1)
      else:
        raise Exception("Max retries exceeded for post_tweet")

  def run(self):
    logging.info("%s : starting OK", self.name)
    last_id = self.get_last_retweet_id()
    for tweet in limit_handled(self, tweepy.Cursor(self.api.list_timeline, owner_screen_name=self.shopping_author, slug=self.shopping_list, since_id=last_id).items(60)):
      if len(tweet.entities['urls'])>0:
        print(f"***********************************")
        print(f"{tweet.user.name} said ({tweet.id}) : {tweet.text}")
    print(f"***********************************")
