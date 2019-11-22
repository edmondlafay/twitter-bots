# -*- coding: utf-8 -*-
import tweepy, time, logging, requests, urllib.request
from bs4 import BeautifulSoup
from .bot import Bot


class ProperDeals(Bot):
  def __init__(self):
    self.name = 'proper_deals'
    super().__init__()
    self.shopping_list='shopping'
    self.shopping_author='seigneurcanard'

  def get_last_post_tweet_id(self):
    """Get last tweet we computed to avoid spam"""
    for tweet in self.api.user_timeline(count=1):
      if tweet.is_quote_status:
        return tweet.quoted_status_id
      if tweet.retweeted:
        return tweet.retweeted_status.id
    return 0

  def build_status(self, tweet):
    result = {'attachment_url': f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"}
    author = tweet.user.screen_name
    url = tweet.entities['urls'][0]['expanded_url']
    if author=='Dealabs' or author=='ClubicBonsPlans' or author=='bonreduc' or author=='bonsplansastuce' or author=='deal_france':
      response = requests.get(url, headers={'User-Agent': "PostmanRuntime/7.20.1"})
      if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        if author=='Dealabs':
          result['img'] = soup.find('img', 'thread-image')['src']
          result['text'] = soup.find('span', 'thread-price').string
        if author=='ClubicBonsPlans':
          result['img'] = soup.find('article').find('img')['src']
          result['text'] = soup.find('article').select("a > b")[0].string
        if author=='bonreduc':
          result['img'] = soup.find('img', 'odr_img')['src']
          result['text'] = soup.find('h1').string
        if author=='bonsplansastuce':
          result['text'] = soup.find('span', 'rh_regular_price').string
          result['img'] = soup.find('img', 'lazyimages')['data-src']
        if author=='deal_france':
          result['text'] = next(soup.find('div', 'offer-box-price').stripped_strings)
          result['img'] = soup.find('img', 'lazyimages')['data-src']
    if 'img' in result and 'text' in result:
      filename = f"{self.name}imgtmp"
      request = requests.get(result['img'], stream=True)
      if request.status_code == 200:
        with open(filename, 'wb') as image:
          for chunk in request:
            image.write(chunk)
        media = self.api.media_upload(filename)
        result['media_ids']=[media_id]
        result['status'] = f"{result['text']}! #promo #bonplan #reduc"
        self.post_tweet(**(result))
      else:
        self.api.retweet(tweet.id)
    else:
      self.api.retweet(tweet.id)
    
  def run(self):
    logging.info(f"{self.name} : starting OK")
    last_id = self.get_last_post_tweet_id()
    for tweet in self.limit_handled(tweepy.Cursor(self.api.list_timeline, owner_screen_name=self.shopping_author, slug=self.shopping_list, since_id=last_id).items(10)):
      # if the url has a link
      if len(tweet.entities['urls'])>0:
        logging.info(f"{self.name} : https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}")
        self.build_status(tweet)
