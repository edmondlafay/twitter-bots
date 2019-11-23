# -*- coding: utf-8 -*-
import tweepy, time, logging, json
from ..common.config import config

class Bot:
  name = 'bot'
  timeout_minutes=60
  thread = None

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
      logging.debug(f"{self.name}: Authentication OK")
    except:
      logging.error(f"{self.name} : Error during authentication")

  def twitbot_timeout(self, log_level, message):
    """Timeout the bot and log the reason"""
    getattr(logging, log_level)(f"{self.name} : {message}, sleeping {self.timeout_minutes} mins")
    time.sleep(self.timeout_minutes * 60)

  def limit_handled(self, cursor):
    """Cursor handling"""
    tweets_left = True
    while tweets_left:
      try:
        yield cursor.next()
      except tweepy.RateLimitError:
        self.twitbot_timeout('warn', 'rate limit cursor exceeded')
      except StopIteration:
        self.twitbot_timeout('info', 'Up to date')
        tweets_left = False
  
  def post_tweet(self, retries=3, **kwargs):
    """Post tweet handling"""
    try:
      logging.info(f"{self.name} : tweeting {kwargs}")
      self.api.update_status(**kwargs)
    except tweepy.TweepError as tweep_error:
      logging.warn(f"{self.name} - post_tweet : {tweep_error}")
    except tweepy.RateLimitError:
      if retries>0:
        self.twitbot_timeout('warn', 'post_tweet rate limit exceeded')
        self.post_tweet(status, retries=retries-1)
      else:
        raise Exception(f"{self.name} - post_tweet : Max retries exceeded for post_tweet")
  
  def post_retweet(self, tweet, retries=3):
    """Post retweet handling"""
    try:
      self.api.retweet(tweet.id)
      logging.info(f"{self.name} - post_retweet : https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}")
    except tweepy.TweepError as tweep_error:
      logging.warn(f"{self.name} - post_retweet : tweet_id {tweet.id} - {tweep_error}")
    except tweepy.RateLimitError:
      if retries>0:
        self.twitbot_timeout('warn', 'post_retweet rate limit exceeded')
        self.post_retweet(status, retries=retries-1)
      else:
        raise Exception(f"{self.name} - post_retweet : Max retries exceeded for post_tweet")

  def run(self):
    """Run the bot"""
    logging.info(f"{self.name} : starting OK")
