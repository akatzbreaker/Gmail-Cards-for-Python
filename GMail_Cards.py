#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
# Python Wrapper for rendering Gmail Cards in Human Readable Format in Python
#
#    Coded by Akatzbreaker (@akatzbreaker)
#
#	Please note that ONLY JSON-LD Format is available right now, not Microdata Format!
#
#
#	Feel Free to comment on Github!
##

import email
import imaplib
import json
import hashlib
from getpass import getpass

authentication={'email':"",'password':""}

# Login Credentials
print("Enter your Email (Gmail Address): ")
email_address=raw_input(" > ")
password=getpass("\nEnter your Password:  (Hidden)")

authentication['email'] = email_address
authentication['password'] = password

class GMail(): # Class for Getting Inbox Messages and Checking if they have any Gmail Cards
	messages=[]
	schemas=[]

	def get_email_messages(self): # Store Inbox Messages to self.messages
		global authentication
		mail = imaplib.IMAP4_SSL('imap.gmail.com')
		mail.login(authentication['email'],authentication['password'])
		mail.select('inbox')
		typ, data = mail.search(None, 'ALL')
		ids = data[0]
		id_list = ids.split()
		latest_email_id = int( id_list[-1] )

		for i in range( latest_email_id, latest_email_id-15, -1 ):
		   typ, data = mail.fetch( i, '(RFC822)' )

		   for response_part in data:
			  if isinstance(response_part, tuple):
				  msg = email.message_from_string(response_part[1])
				  varSubject = msg['subject']
				  varFrom = msg['from']
				  for part in msg.walk():
						self.messages.append(part.as_string())
					

		   varFrom = varFrom.replace('<', '')
		   varFrom = varFrom.replace('>', '')

		   if len( varSubject ) > 35:
			  varSubject = varSubject[0:32] + '...'
		mail.logout()
	
	def does_have_schema(self,message): # Check if Message has a Schema
		if "\"application/ld+json\"" in message or "'application/ld+json'" in message:
			return True
		else:
			return False

	def get_schemas(self): # Get Schemas from Messages and store them to self.schemas
		if len(self.messages) == 0:
			self.get_email_messages()
		for message in self.messages:
			if self.does_have_schema(message):
				schemas_in_message=0
				schema=message.split("application/ld+json")[1].split(">")[1]
				if "list" in str(type(schema)):
					schema = ">".join(schema)
				schema=schema.split("</script")[0]
				schemas_in_message=len(schema)-1
				self.schemas.append(json.loads(schema))

class Schemas(): # Gmail Card Renderer
	identities=[]
	
	def human_readable_card(self,card={}): # Convert Dictionary with Gmail Card Details to a Human Readable String
		stringToReturn=""
		for key in card.keys():
			value=card[key]
			key=key[0].upper() + key[1:]
			for character in key:
				if character in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
					key=" " + character.join(key.split(character))				
			stringToReturn += key + ": " + value + "\n"
		return stringToReturn

	def parse_schema(self,schema):
		if "dict" in str(type(schema)):
			pass
		else:
			schema=json.loads(schema)
		schemabak=schema
		types={'lists':[],'dicts':[],'data':[]}
		data={}

		imported = []
		behold = ""

		for key in schema.keys():
			value=schema[key]
			if 'list' in str(type(value)):
				types['lists'].append({key:value})
			elif 'dict' in str(type(value)):
				types['dicts'].append({key:value})
			else:
					if key.startswith("@") == False or key == "@type":
						if key == "@type":
							behold = value
						elif key == "name":
							key=behold.lower() + "Name"
							behold=""
						if key not in imported:
							if key != "@type":
								data[key] = value
								imported.append(key)
						else:
							data[key + str(data.keys().count(key) + 1)] = value
		
		behold=""

		while len(types['dicts']) > 0:
			newdicts=[]
			for d in types['dicts']:
				for key in d.keys():
					value=d[key]
					if 'list' in str(type(value)):
						for tiem in value:
							types['lists'].append({key:tiem})
					elif 'dict' in str(type(value)):
						for k in value.keys():
							newdicts.append({k:value[k]})
					else:
						if key.startswith("@") == False or key == "@type":
							if key == "@type":
								behold = value
							elif key == "name":
								key = behold.lower() + "Name"
								behold = ""
							if key not in imported:
								if key != "@type":
									data[key] = value
									imported.append(key)
							else:
								data[key + str(data.keys().count(key) + 1)] = value
			types['dicts']=newdicts
			newdicts=[]
			behold=""

			newlists=[]
			for d in types['lists']:
				for key in d:
					if 'list' in str(type(value)):
						types['lists'].append({key:value})
					elif 'dict' in str(type(value)):
						newdicts.append({key:value})
					else:
						if key.startswith("@") == False or key == "@type":
							if key == "@type":
								behold=value
							elif key == "name":
								key = behold.lower() + "Name"
								behold=""
							if key not in imported:
								if key != "@type":
									data[key] = value
									imported.append(key)
							else:
								data[key + str(data.keys().count(key) + 1)] = value
			types['lists']=newlists
			newlists=[]
			behold=""

		return data

	def get_cards(self):
		mail=GMail()
		mail.get_email_messages()		
		mail.get_schemas()				
		gmail_cards=mail.schemas		
		rendered=[]
		toreturn=[]
		if len(gmail_cards) > 0: 
			schema_renderer=Schemas()
			for card in gmail_cards:
				rendered.append(schema_renderer.parse_schema(card))
			for Card in rendered:
				identity = hashlib.sha1(str(Card).strip()).hexdigest()
				if identity in self.identities:
					pass
				else:
					self.identities.append(identity)
					toreturn.append(self.human_readable_card(Card))
		return toreturn

if __name__ == "__main__":
	schema_renderer=Schemas()
	gmail_cards = schema_renderer.get_cards() 		# Get all Gmail Cards Available (Already Human Readable)

	if len(gmail_cards) > 0: 		# Render all Gmail Cards
		for Card in gmail_cards: 	# Print all Gmail Cards
			print(Card)				# Print the Card in Human Readable Form
			print("\n")
	else:
		print("\n--> No Cards Found! Sorry!\n\n")
		print("If you want to test the Gmail Cards, try going to these websites: [So as to be able to send Schemas in E-Mails]")
		print("	To get in the Schema Whitelist:")
		print("		https://developers.google.com/gmail/schemas/registering-with-google\n")
		print("	More Info about Schemas and how they work:")
		print("		https://developers.google.com/gmail/schemas/reference/index")
		print("		(Navigate from the Reference Guide Dropdown at the bottom left of the Sidebar)")
		print("\n\n  Happy Hacking!")
