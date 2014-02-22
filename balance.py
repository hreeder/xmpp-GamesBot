import shelve

def balance(self, message):
	# Get some details about the user
	room = message['from'].user + "@" + message['from'].server
	nick = message['from'].resource
	user = self.plugin['xep_0045'].rooms[room][nick]['jid']
	user = user.user + "@" + user.server
	key = user.encode("utf-8")

	# Open our shelf
	users = shelve.open("users.shelf")

	# If the user doesn't exist on the shelf, create it
	if key not in users:
		users[key] = 0

	# Now tell the user their balance
	output = "%s: Your Balance Is %d ISK" % (message['from'].resource, users[key])
	self.send_message(mto=message['from'].bare, mbody=output, mtype="groupchat")

	users.close()

def deposit(self, message):
	# Get some details about the user
	room = message['from'].user + "@" + message['from'].server
	nick = message['from'].resource
	user = self.plugin['xep_0045'].rooms[room][nick]['jid']
	user = user.user + "@" + user.server
	key = user.encode("utf-8")

	# Open our shelf
	users = shelve.open("users.shelf")

	# If the user doesn't exist on the shelf, create it
	if key not in users:
		users[key] = 0

	# Increment by 5. This is only temporary
	users[key] += 5

	# Tell user that increment has happened (this needs to be replaced with 'deposit isk to this corporation, with this reason')
	output = "%s: Depositing 5 ISK into %s's account" % (message['from'].resource, user)
	self.send_message(mto=message['from'].bare, mbody=output, mtype="groupchat")

	users.close()