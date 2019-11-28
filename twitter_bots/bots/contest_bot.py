# -*- coding: utf-8 -*-
import twitter, time, logging
from .bot import Bot

class ContestBot(Bot):
  def __init__(self):
    self.name = 'contest_bot'
    self.timeout_minutes=15
    super().__init__()

  def run(self):
    logging.info(f"{self.name} : starting OK")
    while True:
      last_id = self.get_last_post_tweet_id()
      for tweet in self.limit_handled(tweepy.Cursor(self.api.list_timeline, owner_screen_name=self.shopping_author, slug=self.shopping_list, since_id=last_id).items(10)):
        # if the url has a link
        if len(tweet.entities['urls'])>0:
          logging.info(f"{self.name} - run : https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}")
          self.build_status(tweet)
