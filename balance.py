import shelve
import config
import locale


def balance(self, message):
    # Get some details about the user
    room = message['from'].user + "@" + message['from'].server
    nick = message['from'].resource
    user = self.plugin['xep_0045'].rooms[room][nick]['jid']
    user = user.user + "@" + user.server

    # If we're dealing with an admin who wants to see someone else's account
    if user in config.xmpp['admins'] and " " in message['body']:
        target = message['body'].split(" ")[1]
        if "@" in target:
            key = target.encode("utf-8")
        elif target == "house":
            key = target.encode("utf-8")
        elif self.plugin['xep_0045'].rooms[room][target]:
            key = self.plugin['xep_0045'].rooms[room][target]['jid']
            key = key.user + "@" + key.server
            key = key.encode("utf-8")
    else:
        key = target = user.encode("utf-8")

    # Open our shelf
    users = shelve.open("users.shelf")

    # If the user doesn't exist on the shelf, create it
    if key not in users:
        users[key] = 0

    locale.setlocale(locale.LC_ALL, '')
    balance = locale.format("%d", users[key], grouping=True)

    # Now tell the user their balance
    output = "%s: The Balance of %s's account is %s ISK" % (message['from'].resource, target, balance)
    self.send_message(mto=message['from'].bare,
                      mbody=output, mtype="groupchat")

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

    # For debug purposes, allow inputting of ISK amount to deposit. This all
    # needs to be replaced by eve API support.
    if " " in message['body'] and int(message['body'].split(" ")[1]):
        amt = int(message['body'].split(" ")[1])
        users[key] += amt
    else:
        amt = 5
        # Increment by 5. This is only temporary
        users[key] += amt

    locale.setlocale(locale.LC_ALL, '')
    amt = locale.format("%d", amt, grouping=True)

    # Tell user that increment has happened (this needs to be replaced with
    # 'deposit isk to this corporation, with this reason')
    output = "%s: Depositing %s ISK into %s's account" % (
        message['from'].resource, amt, user)
    self.send_message(mto=message['from'].bare,
                      mbody=output, mtype="groupchat")

    users.close()

def get(user):
    user = user.encode("utf-8")

    users = shelve.open("users.shelf")

    if user not in users:
        users.close()
        return "No User Found"

    value = users[user]
    users.close()
    return value

def take(user, amount):
    user = user.encode("utf-8")

    users = shelve.open("users.shelf")

    if user not in users:
        users.close()
        return False

    if get(user) < amount:
        users.close()
        return False
    users[user] = users[user] - amount
    if user != "house":
        give("house".encode("utf-8"), amount)

    users.close()
    return True

def give(user, amount):
    if user == "house":
        print "OPENING SHELF TO GIVE TO HOUSE MATR: " + str(amount)
    user = user.encode("utf-8")

    users = shelve.open("users.shelf")

    if take("house".encode("utf-8"), amount) and user != "house":
        users[user] = users[user] + amount
        users.close()
        return True
    elif user == "house":
        users[user] = users[user] + amount
        users.close()
        return True
    users.close()
    return False

def totals(self, message):
    users = shelve.open("users.shelf")

    total = 0

    for user in users:
        total += users[user]
        
    users.close()

    locale.setlocale(locale.LC_ALL, '')
    total = locale.format("%d", total, grouping=True)
    output = "%s: Total Isk In System: %s" % (
        message['from'].resource, total)
    self.send_message(mto=message['from'].bare,
                      mbody=output, mtype="groupchat")