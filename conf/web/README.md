# CYGNO data managment webserver
- docker apache-php 8.3 - mongo, sql module,
- simplesamlphp (2.1.3) (https://wiki.infn.it/cn/ccr/aai/howto/saml-sp-rhel7)
- saml conf, etuth, ecc backuped in private git repo "info"

# falure of certificate renewal
''' 
certbot -q renew; chmod -R a+r /etc/letsencrypt/archive/ 
cd middleware/conf/web/
docker compose down
docker compose up -d
'''
