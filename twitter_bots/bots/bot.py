# -*- coding: utf-8 -*-
import tweepy, time, logging, json
from ..common.config import config

class Bot:
  name = 'bot'
  thread = None
  timeout=60

  def twitter_auth(self):
    """Authenticate to Twitter"""
    twitter_conf = config.get('twitter', {}).get(self.name, {})
    auth = tweepy.OAuthHandler(twitter_conf.get('api_key'), twitter_conf.get('api_secret'))
    auth.set_access_token(twitter_conf.get('access_token'), twitter_conf.get('access_secret'))
    return auth

  def __init__(self):
    self.api = tweepy.API(self.twitter_auth(), wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    try:
      self.api.verify_credentials()
      logging.debug("%s : Authentication OK", self.name)
    except:
      logging.error("%s : Error during authentication", self.name)

  def twitbot_timeout(self, log_level, message):
    """Timeout the bot and log the reason"""
    getattr(logging, log_level)(f"{self.name} : {message}, sleeping {self.timeout} mins")
    time.sleep(self.timeout * 60)

  def limit_handled(self, cursor):
    """Cursor handling"""
    while True:
      try:
        yield cursor.next()
      except tweepy.RateLimitError:
        self.twitbot_timeout('warn', 'rate limit cursor exceeded')
      except StopIteration:
        self.twitbot_timeout('info', 'Up to date')
  
  def post_tweet(self, status='', attachment_url=None, retries=3, **kwargs):
    """Post tweet handling"""
    try:
      logging.info(f"{self.name} : tweeting {status}")
      self.api.update_status(status=status, attachment_url=attachment_url)
    except tweepy.RateLimitError:
      if retries>0:
        self.twitbot_timeout('warn', 'rate limit exceeded post_tweet')
        self.post_tweet(status, retries=retries-1)
      else:
        raise Exception('Max retries exceeded for post_tweet')

  def run(self):
    """Run the bot"""
    logging.info("%s : starting OK", self.name)
