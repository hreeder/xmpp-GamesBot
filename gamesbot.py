#!/usr/bin/env python
import config
import sleekxmpp
import logging
from optparse import OptionParser

# Command Modules
import balance
import rroulette as roulette

# Fill a dict of our commands
cmds = {
    'balance': balance.balance,
    'deposit': balance.deposit,
    'totals' : balance.totals,
    'roulette': roulette.roulette(),
}


class GamesBot(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("groupchat_message", self.msgHandler)

    def start(self, args):
        self.send_presence()
        self.get_roster()
        self.plugin['xep_0045'].joinMUC(
            config.xmpp['muc'], config.xmpp['nick'])

    def msgHandler(self, msg):
        # If the bot has been triggered
        if msg['body'][0] == config.xmpp['trigger']:
            # Grab the command
            if " " in msg['body']:
                firstWord = msg['body'][1:].split(' ')[0]
            else:
                firstWord = msg['body'][1:]
            # Look for Help Command
            if firstWord == "help":
                helptext = "Available Commands:"
                for cmd in cmds:
                    helptext += "\n" + cmd
                self.send_message(mto=msg['from'].bare,
                                  mbody=helptext, mtype="groupchat")
            # Run the command, if it exists
            elif firstWord in cmds:
                cmds[firstWord](self, msg)

if __name__ == '__main__':
    # Set up Optionparser and get our Debug options
    optp = OptionParser()

    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    opts, args = optp.parse_args()

    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    # Init the bot, Register Plugins
    xmpp = GamesBot(config.xmpp['jid'], config.xmpp['password'])
    xmpp.register_plugin('xep_0045')  # XMPP Mucs

    # Connect / Run
    if xmpp.connect():
        xmpp.process(block=True)
    else:
        print("Unable to connect.")
