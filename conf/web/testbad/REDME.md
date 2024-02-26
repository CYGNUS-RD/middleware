# miniserver apeche +php
docker build -t myapp .
docker container run -d --name myapp \
    -p 80:80 \
    -p 443:443 \
    -v ${PWD}/public/:/var/www/html/public \
    -v ${PWD}/apache2/000-default.conf/000-default.conf:/etc/apache2/sites-enabled/000-default.conf \
    -v /etc/letsencrypt/:/var/www/letsencrypt/ \
    myapp
