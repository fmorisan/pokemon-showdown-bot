import random
import json
import re
import os
import subprocess
import requests
from websocket import create_connection

from moderator import Moderator
from commands import Commands

#from battle import BattleParser
class ShowdownBot:

	def __init__(self, user, password, owner, server, rooms, debug, symbol):
		self.username = user
		self.password = password
		self.server = server
		self.owner = owner
		self.rooms = rooms.replace(' ','').split(',')
		if debug == 'True' or debug == '1':
			self.debug = True
		else: self.debug = False
		self.symbol = symbol
		self.base_url = "http://play.pokemonshowdown.com/action.php"
		
	def owner(self):
		return self.owner

	def login(self, message):
		key = message[2]
		challenge = message[3]

		if self.password == '':
			url_data = '?act=getassertion&userid=%s&challengekeyid=%s&challenge=%s' % (self.username, key,challenge)
			data = requests.get(self.base_url+url_data)
			self.ws.send("|/trn %s,0,%s" % (self.username, data))
		else:
			url_data = {'act': 'login', 'name': self.username, 'pass': self.password, 'challengekeyid': key, 'challenge': challenge}
			data = requests.post(self.base_url, data=url_data)
			data = json.loads(data.text.split(']')[1])
			self.ws.send("|/trn %s,0,%s" % (self.username, data['assertion']))

	def join_rooms(self):
		for x in self.rooms:
			self.ws.send("|/join %s" % x)

	def parse_and_send_command(self, message):
		user = message[3]
		room = message[0]
		content = message[4]
		if not self.debug: print "Received: {}".format(content)
		mod = self.moderator.parse(user,content,room)
		if mod:
			self.send(mod, room)
		if message[4][0] == self.symbol:
			command = message[4].split(self.symbol)[1].split(' ')[0]
			try:
				arguments = message[4].split("%s " % (command))[1]
				arguments = arguments.split(" ")
			except IndexError:
				arguments = ''
			try:
				if command == 'reload':
					pass
				else:
					if command == '8ball':
						self.commands.eightball(arguments,user,room)
					else:
						getattr(self.commands, command, None)(arguments,user,room)
			except TypeError:
				self.send("Invalid command.",room)




	
	def send(self, message, room):
		if not self.debug:
			self.ws.send("%s|%s" % (room, message))
			print("%s|%s" % (room, message))
		else: print("O>>" + message)
	
	def parse_challenge(self,message):
		self.challenges = json.loads(message[2])
		for item in self.challenges["challengesFrom"]:
			self.send("/accept {}".format(item),"")
	
	def run(self):
		if not self.debug: self.ws = create_connection("ws://%s:8000/showdown/websocket" % (self.server))
		self.moderator = Moderator(self.debug)
		self.commands = Commands(self,self.moderator)
		print "Connection established."
		while True:
			if not self.debug:
				#message_raw = self.ws.recv()
				message = str(self.ws.recv()).replace("\n", '').replace(">",'')
				message = str(message).split('|')
				print "|".join(message) + "\n"
				if len(message) > 1:
					if message[0].startswith("battle-"):
						pass
					elif message[1] == 'challstr':
						self.login(message)
						self.join_rooms()
					elif message[1] == 'updateuser':
						self.join_rooms()
					elif message[1] == 'c:':
						print(message)
						self.parse_and_send_command(message)
					elif message[1] == 'updatechallenges':
						self.parse_challenge(message)
				
						
			else:
				self.parse_and_send_command(('','c:','','~Debug',raw_input("I>>")))