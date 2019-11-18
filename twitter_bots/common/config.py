from yaml import load, BaseLoader
from os import path

config = {}

configs_file = 'config.yml'
credentials_file = '.credentials.yml'

if path.isfile(configs_file):
  with open(configs_file, 'r') as yml_file:
      config = {**config, **load(yml_file, Loader=BaseLoader)}

if path.isfile(credentials_file):
  with open(credentials_file, 'r') as yml_file:
      config = {**config, **load(yml_file, Loader=BaseLoader)}
