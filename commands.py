import random
import json
import re
import os

class Commands:
	def __init__(self,bot,mod):
		self.bot = bot
		self.mod = mod
		self.eightball_strings = [
		"No.",
		"Yes.",
		"Ask again.",
		"Maybe.",
		"Ask someone else.",
		"I don't think so.",
		"Whatever, it doesn't matter.",
		"Concentrate and try again.",
		"Absolutely." 
		]
		
	def test(self, args, user ,room):
		self.bot.send('Yes, you are pregnant.',room)
		
	def pick(self, args, user, room):
		if args:
			self.bot.send(str(args[random.randint(0,len(args)-1)]),room)
		else:
			self.bot.send("Error, not enough arguments.",room)	
			
	def toggle(self, args, user, room):
		user = self.mod.userCreate(user,room)
		if user.auth_level < 3 and not self.bot.debug:
			self.bot.send("You are not authorized to do this.",room)
		else:
			if args[0] == "rant":
				if self.mod.rantControl_state:
					self.mod.rantControl_state = False
					self.bot.send("Rant control is now off.",room)
				else:
					self.mod.rantControl_state = True
					self.bot.send("Rant control is now on.",room)
			if args[0] == "flood":
				if self.mod.floodControl_state:
					self.mod.floodControl_state = False
					self.bot.send("Flood control is now off.",room)
				else:
					self.mod.floodControl_state = True
					self.bot.send("Flood control is now on.",room)
			if args[0] == "caps":
				if self.mod.capControl_state:
					self.mod.capControl_state = False
					self.bot.send("Caps control is now off.",room)
				else:
					self.mod.capControl_state = True
					self.bot.send("Caps control is now on.",room)
					
	def eightball(self, args, user, room):
		self.bot.send(str(self.eightball_strings[random.randint(0,len(self.eightball_strings)-1)]),room)
	
	def cointoss(self,args, user, room):
		t = random.randint(0,1)
		if t == 1:
			self.bot.send("The coin landed on Tails.",room)
		else:
			self.bot.send("The coin landed on Heads.",room)
	
	def echo(self,args, user, room):
		user = self.mod.userCreate(user,room)
		if user.auth_level > 1:
			self.bot.send(" ".join(args),room)
		else:
			self.bot.send("You are not authorized to use this command.",room)