# -*- coding: utf-8 -*-
import tweepy
from .config import config


def twitter_auth(bot_name):
    """Authenticate to Twitter"""
    twitter_conf = config.get('twitter', {}).get(bot_name, {})
    auth = tweepy.OAuthHandler(twitter_conf['api_key'], twitter_conf['api_secret'])
    auth.set_access_token(twitter_conf['access_token'], twitter_conf['access_secret'])
    return auth

