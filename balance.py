import shelve
import locale


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

    locale.setlocale(locale.LC_ALL, '')
    balance = locale.format("%d", users[key], grouping=True)

    # Now tell the user their balance
    output = "%s: Your Balance Is %s ISK" % (message['from'].resource, balance)
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

    # Tell user that increment has happened (this needs to be replaced with
    # 'deposit isk to this corporation, with this reason')
    output = "%s: Depositing %d ISK into %s's account" % (
        message['from'].resource, amt, user)
    self.send_message(mto=message['from'].bare,
                      mbody=output, mtype="groupchat")

    users.close()
