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
