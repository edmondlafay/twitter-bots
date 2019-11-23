# -*- coding: utf-8 -*-
import tweepy, time, logging, requests, urllib.request, re
from bs4 import BeautifulSoup
from .bot import Bot


class ProperDeals(Bot):
  def __init__(self):
    self.name = 'proper_deals'
    self.timeout_minutes=1
    self.shopping_list='shopping'
    self.shopping_author='seigneurcanard'
    super().__init__()

  def get_last_post_tweet_id(self):
    """Get last tweet we computed to avoid spam"""
    for tweet in self.api.user_timeline(count=1):
      if tweet.is_quote_status:
        return tweet.quoted_status_id
      if tweet.retweeted:
        return tweet.retweeted_status.id
    return 0

  def build_status(self, tweet):
    result = {
      'attachment_url': f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
    }
    author = tweet.user.screen_name
    url = tweet.entities['urls'][0]['expanded_url']
    if author in {'Dealabs', 'ClubicBonsPlans', 'bonreduc', 'bonsplansastuce', 'deal_france'}:
      response = requests.get(url, headers={'User-Agent': "PostmanRuntime/7.20.1"})
      if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tag = None
        price_tag= None
        if author=='Dealabs':
          img_tag = soup.find('img', 'thread-image')
          price_tag = soup.find('span', 'thread-price')
        if author=='ClubicBonsPlans':
          tmp_tag = soup.find('article')
          if tmp_tag:
            img_tag = tmp_tag.find('img')
            tmp_tag = soup.find('article')
            if tmp_tag:
              tmp_tag = tmp_tag.select("a > b")
              if tmp_tag:
                price_tag = tmp_tag[0]
        if author=='bonreduc':
          img_tag = soup.find('img', 'odr_img')
          price_tag = soup.find('h1')
        if img_tag and price_tag and 'src' in img_tag:
          result['img'] = img_tag['src']
          result['text'] = next(price_tag.stripped_strings)
        if author=='bonsplansastuce':
          img_tag = soup.find('img', 'lazyimages')
          price_tag = soup.find('span', 'rh_regular_price')
          if img_tag and price_tag and 'data-src' in img_tag:
            result['img'] = img_tag['data-src']
            result['text'] = next(price_tag.stripped_strings)
        if author=='deal_france':
          img_tag = soup.find('img', 'lazyimages')
          price_tag = soup.find('div', 'offer-box-price')
          if img_tag and price_tag and 'data-src' in img_tag:
            result['img'] = img_tag['data-src']
            result['text'] = next(price_tag.stripped_strings)
    if 'img' in result and 'text' in result:
      file_type = re.search(r"\.[a-zA-Z]*$", result['img'])
      if file_type:
        filename = f"{self.name}imgtmp{file_type.group()}"
        request = requests.get(result['img'], stream=True)
        if request.status_code == 200:
          with open(filename, 'wb') as image:
            for chunk in request:
              image.write(chunk)
          media = self.api.media_upload(filename)
          result['media_ids']=[media.media_id]
          result['status'] = f"{result['text']} #promo #bonplan #reduc #soldes #reduction #promotion"
          black_friday_tag = re.search(r"#blackfriday", tweet.text, flags=re.IGNORECASE)
          if black_friday_tag:
            result['status'] = result['status'] + ' #blackfriday'
          return self.post_tweet(**(result))
    return self.post_retweet(tweet)

  def run(self):
    logging.info(f"{self.name} : starting OK")
    while True:
      last_id = self.get_last_post_tweet_id()
      for tweet in self.limit_handled(tweepy.Cursor(self.api.list_timeline, owner_screen_name=self.shopping_author, slug=self.shopping_list, since_id=last_id).items(10)):
        # if the url has a link
        if len(tweet.entities['urls'])>0:
          logging.info(f"{self.name} - run : https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}")
          self.build_status(tweet)
