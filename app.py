import configparser
from module_parser import ShowdownBot
import sys

config=configparser.RawConfigParser()
config.read('config.cfg')

if __name__=="__main__":
	try:
		bot = ShowdownBot(
		config.get('bot','user'),
		config.get('bot','pass'),
		config.get('bot','owner'),
		config.get('bot','server'),
		config.get('bot','rooms'),
		config.get('bot','debug'),
		config.get('bot','symbol'),
		

		)
	
		bot.run()
	except KeyboardInterrupt:
		sys.exit()