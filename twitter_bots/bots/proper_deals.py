# -*- coding: utf-8 -*-
import tweepy
from ..common.utils import twitter_auth


class ProperDeals:
  name = 'proper_deals'
  def __init__(self):
    self.api = tweepy.API(twitter_auth('proper_deals'))
    self.api.verify_credentials()
    print("Authentication {} OK".format(self.name))
