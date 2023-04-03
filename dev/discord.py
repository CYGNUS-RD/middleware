#!/usr/bin/env python3

def del_m(webhook, dt):
     import time
     time.sleep(dt)
     webhook.delete()
     return

def main(mess, file_tf, dt, verbose=False):
     import os
     import threading
     import subprocess
     import sys
     from discord_webhook import DiscordWebhook
     discord_webhook_URL = os.getenv('discord_webhook_URL')
     if file_tf:
        webhook = DiscordWebhook(url=discord_webhook_URL, username=mess)
        with open(mess, "rb") as f:
             webhook.add_file(file=f.read(), filename=mess)
     else:
     	webhook = DiscordWebhook(url=discord_webhook_URL, content=mess)
     response = webhook.execute()
     if dt>0:
        thread = threading.Thread(target=del_m(webhook,dt))
        thread.daemon = True
        thread.start()
     sys.exit(0) 

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser(usage='usage: %prog\t [message]')
    parser.add_option('-a','--attach', dest='attach', action="store_true", default=False, help='verbose output;');
    parser.add_option('-d','--dt', dest='dt', type="string", default='0', help='second for deletation;');
    parser.add_option('-v','--verbose', dest='verbose', action="store_true", default=False, help='verbose output;');
    (options, args) = parser.parse_args()
    main(mess=args[0], file_tf=options.attach, dt=int(options.dt), verbose=options.verbose)
