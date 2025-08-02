FROM php:8.3-apache
#FROM php:7.4-apache


RUN a2enmod ssl && a2enmod rewrite
RUN mkdir -p /etc/apache2/ssl
RUN mv "$PHP_INI_DIR/php.ini-development" "$PHP_INI_DIR/php.ini"

# RUN wget -q -O - https://dl.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL-7 | apt-key add -
# RUN add-apt-repository "deb https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm"
# RUN apt-get update && apt-get install -y epel-release 

RUN apt-get update \
   && apt-get install -y wget \
   && apt-get install -y libcurl4-openssl-dev pkg-config libssl-dev

RUN docker-php-ext-install mysqli
RUN pecl install mongodb \
    &&  echo "extension=mongodb.so" > $PHP_INI_DIR/conf.d/mongo.ini

#RUN apt-get install -y curl \
#	gpg \
#	nano \
#	git
	
#RUN apt-get update \
#  && apt-get install -y python3 \
#  && apt-get install -y python3-pip \
#  && rm -rf /var/lib/apt/lists/*

#RUN pip install --no-cache-dir -U \
#    boto3 \
#    pandas \
#    mysql-connector \
#    numpy \
#    Pyarrow \
#    pymongo \
#    git+https://github.com/DODAS-TS/boto3sts \
#    git+https://github.com/CYGNUS-RD/cygno.git



WORKDIR /tmp
ARG SIMPLE_SAML_PHP_VERSION=2.1.3
#ARG SIMPLE_SAML_PHP_VERSION=1.18.8
RUN wget https://github.com/simplesamlphp/simplesamlphp/releases/download/v${SIMPLE_SAML_PHP_VERSION}/simplesamlphp-${SIMPLE_SAML_PHP_VERSION}.tar.gz
RUN tar xzf simplesamlphp-${SIMPLE_SAML_PHP_VERSION}.tar.gz 
RUN mv simplesamlphp-${SIMPLE_SAML_PHP_VERSION} /var/simplesamlphp
RUN wget -O /var/simplesamlphp/metadata/saml20-idp-remote.php https://idp.infn.it/metadata/idp.infn.it-idp_saml20-prod-metadata.simplesamlphp.txt
 
# COPY ./ssl/orchestratore.crt /etc/apache2/ssl/
# COPY ./ssl/orchestratore.key /etc/apache2/ssl/
# COPY ./apache/000-default.conf /etc/apache2/sites-available/000-default.conf
# COPY ./ssl/ssl.conf /etc/apache2/mods-available/ssl.conf

# EXPOSE 80
EXPOSE 443
