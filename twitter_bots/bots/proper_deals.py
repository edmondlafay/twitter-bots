# -*- coding: utf-8 -*-
import twitter, time, logging, requests, urllib, re, imghdr, os
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from .bot import Bot


class ProperDeals(Bot):
  def __init__(self):
    self.name = 'proper_deals'
    self.shopping_list='shopping'
    self.shopping_author='seigneurcanard'
    super().__init__()

  def get_last_post_tweet_ids(self, count, retries=3):
    """Get last tweets ids we used to post"""
    result = set()
    homeTimeline = self.errorResilientCall(function=self.api.GetHomeTimeline, params={'count':count})
    for tweet in homeTimeline:
      if tweet.quoted_status_id:
        result.add(tweet.quoted_status_id)
      elif tweet.retweeted_status:
        result.add(tweet.retweeted_status.id)
      else:
        result.add(tweet.id)
    return result

  def external_request(self, url, stream=False):
    logging.info(f"{self.name} - external_request : url {url}")
    domain = urlparse(url).netloc
    headers = {
        'User-Agent': "PostmanRuntime/7.20.1", 'Accept': "*/*",
        'Accept-Encoding': "gzip, deflate", 'Connection': "keep-alive"
      }
    if domain in {'www.bons-plans-bonnes-affaires.fr'}:
      headers['Host'] = domain
      response = requests.get(url, headers=headers, stream=stream)
    elif domain in {'amzn.to'}:
      headers['Referer'] = url
      session = requests.session()
      response = session.get("https://www.amazon.com/",headers=headers, stream=stream)
    else:
      response = requests.get(url, headers=headers, stream=stream)
    
    if response.status_code != 200:
      logging.info(f"{self.name} - build_status : url responded {response.status_code}")
    return response

  def build_status(self, tweet):
    result = {'attachment_url': f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"}
    author = tweet.user.screen_name
    for tweet_url in tweet.urls:
      response = self.external_request(tweet_url.expanded_url)
      if response.status_code == 200:
        domain = urlparse(response.url).netloc
        soup = BeautifulSoup(response.text, 'html.parser')
        img_tag, price_tag = None, None
        if domain=='www.dealabs.com':
          img_tag = soup.select_one(".threadItem img")
          result['img'] = img_tag.get('src') if img_tag else None
          price_tag = soup.select_one(".threadItem .thread-price")
          if price_tag:
            result['text'] = ' '.join(price_tag.stripped_strings)
            if img_tag:
                result['text'] = img_tag.get('alt', '') + ' ' + result['text']
        if domain=='www.clubic.com':
          img_tag = soup.select_one("article img")
          result['img'] = img_tag.get('src') if img_tag else None
          price_tag = soup.select_one("article div.row")
          result['text'] = ' '.join(price_tag.stripped_strings) if price_tag else None
        if domain in {'www.bons-plans-bonnes-affaires.fr', 'www.bonne-promo.com', 'www.bons-plans-astuces.com'}:
          img_tag = soup.select_one('img.lazyimages')
          result['img'] = img_tag.get('data-src') if img_tag else None
          price_tag = soup.find('div', 'offer-box-price')
          result['text'] = next(price_tag.stripped_strings) if price_tag else None
        if domain=='dealfrance.eu':
          img_tag = soup.find('img', 'landingImage')
          result['img'] = img_tag.get('data-src') if img_tag else None
          price_tag = soup.select_one(".threadItem .thread-price")
          if price_tag:
            result['text'] = ' '.join(price_tag.stripped_strings)
            if img_tag:
              result['text'] = img_tag.get('alt', '') + ' ' + result['text']
        if domain in {'www.amazon.fr', 'www.amazon.com'}:
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
            pass
      if result.get('img') and result.get('text'):
        request = self.external_request(url=result['img'], stream=True)
        if request.status_code == 200:
          filename = f"{self.name}_imgtmp"
          with open(filename, 'wb') as image:
            for chunk in request:
              image.write(chunk)
          file_type = imghdr.what(filename)
          if not file_type:
            logging.info(f"{self.name} - build_status : no picture format {result['img']}")
          else:
            os.rename(filename, filename + '.' + file_type)
            result['media']=[filename + '.' + file_type]
            result['status'] = f"{result['text']} #promo #bonplan #reduc #soldes #reduction #promotion"
            black_friday_tag = re.search(r"#blackfriday", tweet.full_text, flags=re.IGNORECASE)
            if black_friday_tag:
              result['status'] = result['status'] + ' #blackfriday'
            return self.post_tweet(**(result))
    return self.post_retweet(tweet)

  def run(self, retries=3):
    past_tweet_ids = self.get_last_post_tweet_ids(count=200)
    listTimeline = self.errorResilientCall(function=self.api.GetListTimeline, params={'count':60, 'owner_screen_name': self.shopping_author, 'slug': self.shopping_list})
    for tweet in listTimeline:
      # if the url has a link and not handled yet
      if len(tweet.urls)>0 and tweet.id not in past_tweet_ids:
        logging.info('***********************************************')
        logging.info(f"{self.name} - run : https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}")
        self.build_status(tweet)
    self.twitbot_timeout('info', 'up to date')
    self.run()
