# -*- coding: utf-8 -*-
import twitter, time, logging, json
from ..common.config import config

class Bot:
  name = 'bot'
  timeout_minutes=15
  thread = None

  def twitter_auth(self):
    """Authenticate to Twitter"""
    twitter_conf = config.get('twitter', {}).get(self.name, {})
    return twitter.Api(consumer_key=twitter_conf.get('api_key'),
      consumer_secret=twitter_conf.get('api_secret'),
      access_token_key=twitter_conf.get('access_token'),
      access_token_secret=twitter_conf.get('access_secret'),
      tweet_mode='extended')

  def __init__(self):
    self.api = self.twitter_auth()
    try:
      logging.info(f"{self.name} : {self.api.VerifyCredentials()}")
    except:
      raise Exception(f"{self.name} : Error during authentication")

  def twitbot_timeout(self, log_level, message):
    """Timeout the bot and log the reason"""
    getattr(logging, log_level)(f"{self.name} : {message}, sleeping {self.timeout_minutes} mins")
    time.sleep(self.timeout_minutes * 60)

  def post_tweet(self, retries=3, **kwargs):
    """Post tweet handling"""
    try:
      accepter_params = set(self.api.PostUpdate.__code__.co_varnames)
      accepter_params.discard('self')
      accepter_params.discard('status')
      args = {}
      for valid_key in accepter_params:
        if kwargs.get(valid_key):
          args[valid_key] = kwargs.get(valid_key)
      logging.info(f"{self.name} : tweeting {args}")
      self.api.PostUpdate(status=kwargs['status'], **args)
    except twitter.error.TwitterError as tweep_error:
      if tweep_error.message[0]['message'] == 'Rate limit exceeded' and retries > 0:
        self.twitbot_timeout('warn', 'post_tweet rate limit exceeded')
        self.post_tweet(retries=retries-1, **kwargs)
      else:
        logging.warn(f"{self.name} - post_tweet : tweet_id {tweet.id} - {tweep_error}")
        raise Exception(f"{self.name} - post_tweet")
    except requests.exceptions.ConnectionError:
      self.twitbot_timeout('warn', 'post_tweet connection error')
      self.post_tweet(retries=retries-1, **kwargs)
  
  def post_retweet(self, tweet, retries=3):
    """Post retweet handling"""
    try:
      self.api.PostRetweet(tweet.id)
      logging.info(f"{self.name} - post_retweet : https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}")
    except twitter.error.TwitterError as tweep_error:
      if tweep_error.message[0]['message'] == 'You have already retweeted this Tweet.':
        logging.info('already retweeted this Tweet')
      elif tweep_error.message[0]['message'] == 'Rate limit exceeded' and retries > 0:
        self.twitbot_timeout('warn', 'post_retweet rate limit exceeded')
        self.post_retweet(tweet, retries=retries-1)
      else:
        logging.warn(f"{self.name} - post_retweet : tweet_id {tweet.id} - {tweep_error}")
        raise Exception(f"{self.name} - post_retweet")
    except requests.exceptions.ConnectionError:
      self.twitbot_timeout('warn', 'post_retweet connection error')
      self.post_retweet(tweet, retries=retries-1)

  def run(self):
    """Run the bot"""
    logging.info(f"{self.name} : starting OK")
