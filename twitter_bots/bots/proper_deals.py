# -*- coding: utf-8 -*-
import tweepy, time, logging, requests, urllib, re, imghdr, os
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from .bot import Bot


class ProperDeals(Bot):
  def __init__(self):
    self.name = 'proper_deals'
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

  def build_status(self, tweet):
    result = {'attachment_url': f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"}
    author = tweet.user.screen_name
    headers={'User-Agent': "PostmanRuntime/7.20.1"}
    if author not in {'deal_france', 'ClubicBonsPlans', 'Dealabs', 'bonsplansastuce'}:
      logging.info(f"{self.name} - build_status : not in parsed users")
    else:
      for tweet_url in tweet.entities['urls']:
        url = tweet_url['expanded_url']
        logging.info(f"{self.name} - build_status : url {url}")
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
          logging.info(f"{self.name} - build_status : url responded {response.status_code}")
        else:
          domain = urlparse(response.url).netloc
          if domain not in {'dealfrance.eu', 'www.bons-plans-bonnes-affaires.fr', 'dlbs.fr', 'www.clubic.com'}:
            logging.info(f"{self.name} - build_status : not in parsed domains")
          else:
            soup = BeautifulSoup(response.text, 'html.parser')
            img_tag = None
            price_tag= None
            if domain=='dlbs.fr':
              img_tag = soup.find('img', 'thread-image')
              price_tag = soup.find('span', 'thread-price')
              if img_tag and price_tag and 'src' in img_tag.attrs:
                result['img'] = img_tag['src']
                result['text'] = next(price_tag.stripped_strings)
              else:
                logging.info(f"{self.name} - build_status : tags error img '{img_tag}' text '{price_tag}'")
            if domain=='www.clubic.com':
              tmp_tag = soup.find('article')
              if tmp_tag:
                img_tag = tmp_tag.find('img')
                if tmp_tag:
                  price_tag = tmp_tag.find('div', 'row')
                  if img_tag and price_tag and 'src' in img_tag.attrs:
                    result['img'] = img_tag['src']
                    result['text'] = ' '.join(price_tag.stripped_strings)
                  else:
                    logging.info(f"{self.name} - build_status : tags error img '{img_tag}' text '{price_tag}'")
            if domain=='www.bons-plans-bonnes-affaires.fr':
              img_tag = soup.find('img', 'lazyimages')
              price_tag = soup.find('span', 'rh_regular_price')
              if img_tag and price_tag and 'data-src' in img_tag:
                result['img'] = img_tag['data-src']
                result['text'] = next(price_tag.stripped_strings)
              else:
                logging.info(f"{self.name} - build_status : tags error img '{img_tag}' text '{price_tag}'")
            if domain == 'dealfrance.eu':
              img_tag = soup.find('img', 'lazyimages')
              price_tag = soup.find('div', 'offer-box-price')
              if img_tag and price_tag and 'data-src' in img_tag.attrs:
                result['img'] = img_tag['data-src']
                result['text'] = next(price_tag.stripped_strings)
              else:
                logging.info(f"{self.name} - build_status : tags error img '{img_tag}' text '{price_tag}'")
        if 'img' not in result or 'text' not in result:
          logging.info(f"{self.name} - build_status : no img or text")
        else:
          filename = f"{self.name}_imgtmp"
          request = requests.get(result['img'], stream=True, headers=headers)
          if request.status_code != 200:
            logging.info(f"{self.name} - build_status : picture url responded {request.status_code}")
          else:
            with open(filename, 'wb') as image:
              for chunk in request:
                image.write(chunk)
            file_type = imghdr.what(filename)
            if not file_type:
              logging.info(f"{self.name} - build_status : no picture format {result['img']}")
            else:
              os.rename(filename, filename + '.' + file_type)
              media = self.api.media_upload(filename + '.' + file_type)
              result['media_ids']=[media.media_id]
              result['status'] = f"{result['text']} #promo #bonplan #reduc #soldes #reduction #promotion"
              black_friday_tag = re.search(r"#blackfriday", tweet.text, flags=re.IGNORECASE)
              if black_friday_tag:
                result['status'] = result['status'] + ' #blackfriday'
              return self.post_tweet(**(result))
    return self.post_retweet(tweet)

  def run(self):
    logging.info(f"{self.name} : starting OK")
    last_id = self.get_last_post_tweet_id()
    while True:
      for tweet in self.limit_handled(tweepy.Cursor(self.api.list_timeline, owner_screen_name=self.shopping_author, slug=self.shopping_list, since_id=last_id).items(60)):
        # if the url has a link
        if len(tweet.entities['urls'])>0:
          logging.info('***********************************************')
          logging.info(f"{self.name} - run : https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}")
          self.build_status(tweet)
      last_id = tweet.id
