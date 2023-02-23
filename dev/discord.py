#!/usr/bin/env python3
def main(mess, verbose=False):
     import os
     from discord_webhook import DiscordWebhook
     discord_webhook_URL = os.getenv('discord_webhook_URL')
     webhook = DiscordWebhook(url=discord_webhook_URL, content=mess)
     response = webhook.execute()

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog\t [message]')
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
    (options, args) = parser.parse_args()
    main(mess=args[0], verbose=options.verbose)
