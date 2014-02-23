import balance
import config
import locale


class roulette(object):

    stage = False
    host = False
    pot = 0
    players = []

    def __call__(self, xmpp, message):
        self.xmpp = xmpp
        locale.setlocale(locale.LC_ALL, '')

        room = message['from'].user + "@" + message['from'].server
        nick = message['from'].resource
        user = xmpp.plugin['xep_0045'].rooms[room][nick]['jid']
        user = user.user + "@" + user.server

        if " " in message['body']:
            subcommand = message['body'].split(" ")[1]
            subs = {
                'new': self.new_game,
                'join': self.join_game,
                'withdraw': self.withdraw,
                'end': self.end,
                'kick': self.kick,
                'players': self.list_players,
                'pot' : self.view_pot
            }
            subs[subcommand](message, user)
        else:
            self.respond(
                message['from'], "Roulette Commnands (These are situational): new, join, withdraw")

    def respond(self, source, message):
        self.xmpp.send_message(
            mto=source.bare,
            mbody="%s: %s" % (source.resource, message),
            mtype="groupchat")

    def new_game(self, message, user):
        amt = locale.format("%d", config.roulette['entry'], grouping=True)
        if not self.stage and len(message['body'].split(" ")) < 3:
            self.respond(message['from'], "It will cost you %s to start a new game. To open a new game, please type %sroulette new confirm" % (amt, config.xmpp['trigger']))
        elif not self.stage and message['body'].split(" ")[2] == "confirm":
            if balance.get(user) > config.roulette['entry']:
                if balance.take(user, config.roulette['entry']):
                    self.pot += config.roulette['entry']
                    self.stage = "pregame"
                    self.players.append(user)
                    self.host = user
                    self.respond(
                        message['from'], "A new game has been started and you have been added to it. %s isk has been debited from your account [%d/%d]" % (amt, len(self.players), config.roulette['max_players']))
                else:
                    self.respond(message['from'], "An error occured debiting your account. Please ask an admin for assistance. You were not entered into the game.")
            else:
                self.respond(message['from'], "You do not have the funds to do that.")
        else:
            self.respond(
                message['from'], "A game is already active. Please wait until that game is finished before starting a new game.")

    def join_game(self, message, user):
        if self.stage == "pregame" and len(self.players) < config.roulette['max_players']:
            amt = locale.format(
                "%d", config.roulette['entry'], grouping=True)

            if user not in self.players and len(message['body'].split(" ")) < 3:
                self.respond(
                    message['from'], "To enter this game it will cost you %s isk. To confirm, please type %sroulette join confirm" % (amt, config.xmpp['trigger']))
            elif user not in self.players and message['body'].split(" ")[2] == "confirm":
                if balance.get(user) > config.roulette['entry']:
                    if balance.take(user, config.roulette['entry']):
                        self.pot += config.roulette['entry']
                        self.players.append(user)
                        self.respond(message['from'],
                                     "You have been added to the active game. %s isk has been debited from your account [%d/%d]" % (amt,len(self.players), config.roulette['max_players']))
                    else:
                        self.respond(message['from'], "An error occured debiting your account. Please ask an admin for assistance. You were not entered into the game.")
                else:
                    self.respond(message['from'], "You do not have the funds to do that.")
            else:
                self.respond(message['from'],
                             "You are already in the active game.")
        else:
            self.respond(
                message['from'], "You are not able to join a game at this time. Maybe one is already active/full?")

    def withdraw(self, message, user):
        if self.stage == "pregame" and user in self.players:
            if user != self.host:
                self.players.remove(user)
                self.respond(message['from'],
                             "You have withdrawn from the game. Chicken.")
            else:
                self.respond(message['from'],
                             "The host cannot withdraw from the game.")
        else:
            self.respond(message['from'],
                         "You may not withdraw from the game at this point")

    def end(self, message, user):
        if user == self.host and self.stage == "pregame":
            self.stage = False
            self.players = []
            self.host = False
            self.respond(message['from'], "Game Aborted")
        else:
            self.respond(message['from'], "Only the host may cancel a game.")

    def kick(self, message, user):
        if user == self.host and self.stage == "pregame" and message['body'].split(" ")[2]:
            targetNick = message['body'].split(" ")[2]
            room = message['from'].user + "@" + message['from'].server
            target = self.xmpp.plugin['xep_0045'].rooms[
                room][targetNick]['jid']
            target = target.user + "@" + target.server

            if target in self.players:
                self.players.remove(target)
                self.respond(
                    message['from'], "%s has been removed from the active game." % (targetNick,))
            else:
                self.respond(
                    message['from'], "Unable to find %s in the current game." % (target,))
        else:
            self.respond(
                message['from'], "Only a game host may use that command, and it may only be used in the pregame stage.\nUsage: \"%sroulette kick nickname\"" %
                (config.xmpp['trigger'],))

    def list_players(self, message, user):
        if self.stage:
            room = message['from'].user + "@" + message['from'].server
            output = "Current Players:"
            for player in self.players:
                person = []
                for nick in self.xmpp.plugin['xep_0045'].rooms[room]:
                    entry = self.xmpp.plugin['xep_0045'].rooms[room][nick]
                    if entry is not None and entry['jid'].user == player.split("@")[0] and entry['jid'].server == player.split("@")[1]:
                        person.append(nick)
                output += "\n" + " / ".join(person)
            self.respond(message['from'], output)

    def view_pot(self, message, user):
        if self.stage:
            amt = locale.format("%d", self.pot, grouping=True)
            self.respond(message['from'], "The pot currently stands at %s isk." % (amt,))
