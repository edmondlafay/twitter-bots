# -*- coding: utf-8 -*-
import logging
import threading
from .bots import proper_deals

def run():
  format = "%(asctime)s: %(message)s"
  logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

  bot_list = [
    proper_deals.ProperDeals()
  ]

  # Launch bots
  for bot in bot_list:
    logging.info("Main : Starting %s", bot.name)
    bot.thread = threading.Thread(target=bot.run, args=())
    bot.thread.start()
