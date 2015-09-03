import os
import sys
import arrow

levels = {
"+":1,
"=":2,
"%":3,
"@":4,
"#":5,
"&":6,
"~":9,
}

class Moderator:
	""" Main moderation class, contains routines for what consists an infraction, parsing messages, and creating Message and User objects"""
	
	def __init__(self,debug):
		""" Initialize the Moderator instance with the stuff that we'll need. """
		
		self.messageList = []
		self.userList = []
		
		self.flood_reason = "You have offended the gods of flood control!"
		self.caps_reason = "You have capitalized one too many letters.."
		self.rant_reason = "Please don't talk to yourself." #Maybe load these from the cfg.
		
		self.last_message = None
		
		self.debug = debug
		
		self.rantControl_state = True
		self.floodControl_state = True
		self.capControl_state = True
		
	def parse(self, user, message, room):
		""" Parse an incoming message for moderation stuff """
		
		user = self.userCreate(user, room)
			
		m = Message(user, message, room)
		
		self.messageList.append(m)
		user.sent_messages.append(m)
		
		
	
		if self.rantControl_state: 
			veredict = self.rantControl(m)
			
		if self.floodControl_state: 
			veredict = self.floodControl(m)
			
		if self.capControl_state: 
			veredict = self.capControl(m)
			
			
		self.last_message = m
		
		if veredict:
			return veredict
	
	def userCreate(self, user, room):
		""" Retrieve an user object given their username, or create a new one """
		
		usernamelist = []
		for item in self.userList:
			usernamelist.append(item.name)
		if user in usernamelist:
			for item in self.userList:
				if item.name == user:
					user = item
					#print "found user {}".format(user.name)
		else:
			user = User([room],user)
			self.userList.append(user)
			#print "created user {}".format(user.name)
		if room not in user.rooms:
			user.rooms.append(room)

		return user
		
	def floodControl(self, message):
		""" Detect flooding. """
		recent = []
		now = arrow.utcnow()
		now = now.timestamp
		
		for item in message.sender.sent_messages:
			if now - item.timestamp < 5:
				recent.append(item)
		#print recent
		if len(recent) > 5:
			return self.punish(message.sender, self.flood_reason)
	
		else:
			return None
	
	def capControl(self,message):
		""" Detect excessive usage of caps. """
		now = arrow.utcnow()
		now = now.timestamp
		upper = len([letter for letter in message.content if letter.isupper()])
		lower = len([letter for letter in message.content if letter.islower()])
		if upper > lower and len(message.content) > 4:
			return self.punish(message.sender,self.caps_reason)
	
	def rantControl(self,message):
		""" Detect when an user sends many messages in a row, regardless of time elapsed """
		if message.sender.messages_in_a_row > 11:
			return self.punish(message.sender,self.rant_reason)
		try:	
			if self.last_message.sender == message.sender:
				message.sender.messages_in_a_row += 1
		except AttributeError:
			pass
			
	def punish(self, user, reason):
		""" Warn/Mute/Kick users """
		#Maybe implement locking/banning at a later date
		now = arrow.utcnow()
		now = now.timestamp
		if user.auth_level < 2:
			if self.timeSince(user.last_warn, now) > 60:
				print "Warning {}".format(user.name)
				user.last_warn = now
				return "/warn {}, {}".format(user.name,reason)
			
			elif self.timeSince(user.last_mute, now) > 480 and self.timeSince(user.last_warn, now) > 5:
				print "Muting {}".format(user.name)
				user.last_mute = now
				return "/mute {}, {}".format(user.name,reason)
					
			elif self.timeSince(user.last_kick, now) > 60 and self.timeSince(user.last_warn, now) > 5:
				print "Kicking {}".format(user.name)
				user.last_kick = now
				return "/kick {}, {}".format(user.name,reason)
	

		
	def timeSince(self,then,now):
		""" Get the time between two timestamps """
		return now - then
		
class Message:
	""" A Message object contains it's sender, it's timestamp, it's content, and the room it was sent in """
	
	def __init__(self, user, message, room):
		t = arrow.utcnow()
		self.sender = user
		self.content = message
		self.timestamp = t.timestamp
		self.room = room
	
class User:
	""" A User object contains the rooms the user is in; their username; all the messages they've sent; the last time they were warned, kicked or muted; the amount of messages they've sent in a row and their auth level. """
	
	def __init__(self, rooms, username):
		self.rooms = rooms
		self.name = username
		self.sent_messages = []
		self.last_warn = 0
		self.last_kick = 0
		self.last_mute = 0
		self.messages_in_a_row = 0
		if username[0] in levels:
			self.auth_level = levels[username[0]]
		else:
			self.auth_level = 0
			
