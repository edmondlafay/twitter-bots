# -*- coding: utf-8 -*-
import logging
import threading
from .bots import proper_deals, contest_bot

def run(debug=False):
  format = "%(asctime)s: %(message)s"
  log_level = logging.DEBUG if debug else logging.INFO
  logging.basicConfig(format=format, level=log_level, datefmt="%H:%M:%S")

  bot_list = [
    proper_deals.ProperDeals(debug),
    #contest_bot.ContestBot()
  ]

  # Launch bots
  for bot in bot_list:
    logging.info("Main : Starting %s", bot.name)
    bot.thread = threading.Thread(target=bot.run, kwargs={})
    bot.thread.start()
