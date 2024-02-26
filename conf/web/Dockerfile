FROM php:8-apache

RUN a2enmod ssl && a2enmod rewrite
RUN mkdir -p /etc/apache2/ssl
RUN mv "$PHP_INI_DIR/php.ini-development" "$PHP_INI_DIR/php.ini"

# RUN wget -q -O - https://dl.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL-7 | apt-key add -
# RUN add-apt-repository "deb https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm"
# RUN apt-get update && apt-get install -y epel-release 

RUN docker-php-ext-install mysqli
RUN apt-get update && apt-get install -y wget

WORKDIR /tmp
ARG SIMPLE_SAML_PHP_VERSION=1.19.6
RUN wget https://github.com/simplesamlphp/simplesamlphp/releases/download/v${SIMPLE_SAML_PHP_VERSION}/simplesamlphp-${SIMPLE_SAML_PHP_VERSION}.tar.gz
RUN tar xzf simplesamlphp-${SIMPLE_SAML_PHP_VERSION}.tar.gz 
RUN mv simplesamlphp-${SIMPLE_SAML_PHP_VERSION} /var/simplesamlphp
RUN wget -o /var/simplesamlphp/metadata/saml20-idp-remote.php https://idp.infn.it/metadata/idp.infn.it-idp_saml20-prod-metadata.simplesamlphp.txt
 
# COPY ./ssl/orchestratore.crt /etc/apache2/ssl/
# COPY ./ssl/orchestratore.key /etc/apache2/ssl/
# COPY ./apache/000-default.conf /etc/apache2/sites-available/000-default.conf
# COPY ./ssl/ssl.conf /etc/apache2/mods-available/ssl.conf

# EXPOSE 80
EXPOSE 443
