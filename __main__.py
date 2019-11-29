import argparse
from twitter_bots import app

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Tweet using bots.')
  parser.add_argument('--debug', action='store_true',
      help='activate debug logs and replace tweeting with logs')

  args = parser.parse_args()
  debug = args.debug
  app.run(debug=debug)
