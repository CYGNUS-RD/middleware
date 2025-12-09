FROM php:8.3-apache

RUN a2enmod ssl && a2enmod rewrite
RUN mkdir -p /etc/apache2/ssl
RUN mv "$PHP_INI_DIR/php.ini-development" "$PHP_INI_DIR/php.ini"

RUN apt-get update \
   && apt-get install -y wget libcurl4-openssl-dev pkg-config libssl-dev git unzip curl \
   && rm -rf /var/lib/apt/lists/*

RUN docker-php-ext-install mysqli
RUN pecl install mongodb \
    && echo "extension=mongodb.so" > $PHP_INI_DIR/conf.d/mongo.ini

# Installa Composer e libreria WebSocket PHP
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer \
  && cd /var/www/html \
  && composer require textalk/websocket:^1.5

# --- (resto del tuo Dockerfile invariato) ---
WORKDIR /tmp
ARG SIMPLE_SAML_PHP_VERSION=2.1.3
RUN wget https://github.com/simplesamlphp/simplesamlphp/releases/download/v${SIMPLE_SAML_PHP_VERSION}/simplesamlphp-${SIMPLE_SAML_PHP_VERSION}.tar.gz \
 && tar xzf simplesamlphp-${SIMPLE_SAML_PHP_VERSION}.tar.gz \
 && mv simplesamlphp-${SIMPLE_SAML_PHP_VERSION} /var/simplesamlphp \
 && wget -O /var/simplesamlphp/metadata/saml20-idp-remote.php https://idp.infn.it/metadata/idp.infn.it-idp_saml20-prod-metadata.simplesamlphp.txt

EXPOSE 443
