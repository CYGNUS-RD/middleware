#!/usr/bin/env python3
def main(mess, file_tf, verbose=False):
    import os
    from discord_webhook import DiscordWebhook
    discord_webhook_URL = os.getenv('discord_webhook_URL')
    if file_tf:
        webhook = DiscordWebhook(url=discord_webhook_URL, username=mess)
        with open(mess, "rb") as f:
             webhook.add_file(file=f.read(), filename=mess)
    else:
        webhook = DiscordWebhook(url=discord_webhook_URL, content=mess)
    response = webhook.execute()

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog\t [message]')
    parser.add_option('-a','--attach', dest='attach', action="store_true", default=False, help='verbose output;');
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
    (options, args) = parser.parse_args()
    main(mess=args[0], file_tf=options.attach, verbose=options.verbose)
