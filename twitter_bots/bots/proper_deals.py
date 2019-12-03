# -*- coding: utf-8 -*-
import twitter, time, logging, requests, urllib, re, imghdr, os
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from .bot import Bot

newline_char = "\n"

class ProperDeals(Bot):
  def __init__(self, debug=False):
    self.name = 'proper_deals'
    self.shopping_list='shopping'
    self.shopping_author='seigneurcanard'
    self.last_post_tweet_ids = set()
    super().__init__(debug=debug)

  def get_last_post_tweet_ids(self, count):
    """Get last tweets ids we used to post"""
    homeTimeline = self.errorResilientCall(function=self.api.GetHomeTimeline, params={'count':count})
    for tweet in homeTimeline:
      if tweet.quoted_status_id:
        self.last_post_tweet_ids.add(tweet.quoted_status_id)
      if tweet.retweeted_status:
        self.last_post_tweet_ids.add(tweet.retweeted_status.id)
      self.last_post_tweet_ids.add(tweet.id)

  def external_request(self, url, stream=False):
    logging.debug(f"{self.name} - external_request : url {url}")
    domain = urlparse(url).netloc
    headers = {
      'User-Agent': "PostmanRuntime/7.20.1", 'Accept': "*/*",
      'Accept-Encoding': "gzip, deflate", 'Connection': "keep-alive"
    }
    if domain in {'www.bons-plans-bonnes-affaires.fr'}:
      headers['Host'] = domain
      response = self.errorResilientCall(function=requests.get, params={'url':url, 'headers':headers, 'stream':stream})
    elif domain in {'amzn.to'}:
      headers['Referer'] = url
      session = requests.session()
      response = self.errorResilientCall(function=session.get, params={'url':url, 'headers':headers, 'stream':stream})
    else:
      response = self.errorResilientCall(function=requests.get, params={'url':url, 'headers':headers, 'stream':stream})
    
    if response.status_code != 200:
      logging.warn(f"{self.name} - external_request : get url {url} responded {response.status_code}")
    return response
  
  def parse_tweet(self, tweet):
    author = tweet.user.screen_name
    for tweet_url in tweet.urls:
      result = {'attachment_url': f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"}
      response = self.external_request(tweet_url.expanded_url)
      if response.status_code == 200:
        result['domain'] = urlparse(response.url).netloc
        soup = BeautifulSoup(response.text, 'html.parser')
        if result['domain']=='www.dealabs.com':
          img_tag = soup.select_one(".threadItem img")
          result['img'] = img_tag.get('src') if img_tag else None
          price_tag = soup.select_one(".threadItem .thread-price")
          if price_tag:
            result['text'] = ' '.join(price_tag.stripped_strings)
            if img_tag:
                result['text'] = ' '.join(filter(None, [img_tag.get('alt'), result['text']]))
        if result['domain']=='www.clubic.com':
          img_tag = soup.select_one("article img")
          result['img'] = img_tag.get('src') if img_tag else None
          price_tag = soup.select_one("article div.row")
          result['text'] = ' '.join(price_tag.stripped_strings) if price_tag else None
        if result['domain'] in {'www.bonne-promo.com', 'www.bons-plans-astuces.com'}:
          img_tag = soup.select_one('img.lazyimages')
          result['img'] = img_tag.get('data-src') if img_tag else None
          price_tag = soup.find('div', 'offer-box-price')
          result['text'] = next(price_tag.stripped_strings) if price_tag else None
        if result['domain']=='www.bons-plans-bonnes-affaires.fr':
          img_tag = soup.select_one('img.lazyimages')
          result['img'] = img_tag.get('data-src') if img_tag else None
          price_tag = soup.select_one('.rh_regular_price')
          result['text'] = next(price_tag.stripped_strings) if price_tag else None
        if result['domain']=='dealfrance.eu':
          img_tag = soup.find('img', 'landingImage')
          result['img'] = img_tag.get('data-src') if img_tag else None
          price_tag = soup.select_one(".threadItem .thread-price")
          if price_tag:
            result['text'] = ' '.join(price_tag.stripped_strings)
            if img_tag:
              result['text'] = ' '.join(filter(None, [img_tag.get('alt'), result['text']]))
        if result['domain'] in {'www.amazon.fr', 'www.amazon.com'}:
          try:
            img_tag_approx_position = response.text.index('id="landingImage"')
            soup = BeautifulSoup(response.text[img_tag_approx_position-20000:img_tag_approx_position+1000], 'html.parser')
            img_tag = soup.find(id='landingImage')
            result['img'] = img_tag.get('data-old-hires') if img_tag else None
            price_tag_approx_position = response.text.index('id="price_inside_buybox"')
            soup = BeautifulSoup(response.text[price_tag_approx_position-200:price_tag_approx_position+200], 'html.parser')
            price_tag = soup.find(id='price_inside_buybox')
            result['text'] = ' '.join(price_tag.stripped_strings) if price_tag else None
          except ValueError:
            try:
              response.text.index('Sorry, this promotion has now expired.')
              logging.debug(f"{self.name} - build_status : amazon promotion has now expired")
              return
            except ValueError:
              pass
      self.build_status(self, tweet, result)
    logging.debug(f"{self.name} - build_status : build result {result}")
    self.last_post_tweet_ids.add(tweet.id)
    self.post_retweet(tweet)

  def build_status(self, tweet, parsed_site_info):
    if parsed_site_info.get('img') and parsed_site_info.get('text'):
      request = self.external_request(url=parsed_site_info['img'], stream=True)
      if request.status_code == 200:
        filename = f"{self.name}_imgtmp"
        with open(filename, 'wb') as image:
          for chunk in request:
            image.write(chunk)
        file_type = imghdr.what(filename)
        if not file_type:
          logging.debug(f"{self.name} - build_status : no picture format {result['img']}")
        else:
          os.rename(filename, filename + '.' + file_type)
          parsed_site_info['media']=[filename + '.' + file_type]
          parsed_site_info['status'] = f"{parsed_site_info['text']} #promo #bonplan #reduc #soldes #reduction #promotion"
          black_friday_tag = re.search(r"#blackfriday", tweet.full_text, flags=re.IGNORECASE)
          if black_friday_tag:
            parsed_site_info['status'] = parsed_site_info['status'] + ' #blackfriday'
          logging.debug(f"{self.name} - build_status : build result {parsed_site_info}")
          self.post_tweet(**(parsed_site_info))
    logging.debug(f"{self.name} - build_status : build result {parsed_site_info}")
    self.last_post_tweet_ids.add(tweet.id)
    return self.post_retweet(tweet)

  def run(self):
    self.get_last_post_tweet_ids(count=200)
    while True:
      listTimeline = self.errorResilientCall(function=self.api.GetListTimeline, params={'count':30, 'owner_screen_name': self.shopping_author, 'slug': self.shopping_list})
      for tweet in listTimeline:
        # if the url has a link and not handled yet
        if len(tweet.urls)>0 and tweet.id not in self.last_post_tweet_ids:
          logging.info(f"{self.name} - run : https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}")
          logging.debug(f"{self.name} - run : {tweet}")
          self.parse_tweet(tweet)
      self.twitbot_timeout('info', 'up to date')
