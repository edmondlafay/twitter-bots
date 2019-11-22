# -*- coding: utf-8 -*-
import tweepy, time, logging
from .config import config


def twitter_auth(bot_name):
    """Authenticate to Twitter"""
    twitter_conf = config.get('twitter', {}).get(bot_name, {})
    auth = tweepy.OAuthHandler(twitter_conf['api_key'], twitter_conf['api_secret'])
    auth.set_access_token(twitter_conf['access_token'], twitter_conf['access_secret'])
    return auth

def twitbot_timeout(bot, log_level, message):
  getattr(logging, log_level)(message)
  time.sleep(bot.timeout * 60)

def limit_handled(bot, cursor):
  while True:
    try:
      yield cursor.next()
    except tweepy.RateLimitError:
      twitbot_timeout(bot, 'warn', f"{bot.name} : rate limit exceeded, sleeping {bot.timeout} mins")
    except StopIteration:
      twitbot_timeout(bot, 'info', f"{bot.name} : Up to date, sleeping {bot.timeout} mins")