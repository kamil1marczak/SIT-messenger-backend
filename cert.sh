#!/bin/bash

domain=api.sit-messenger.com
rsa_key_size=4096
data_path="./data/certbot"
email="kamil1marczak@gmail.com" # Adding a valid address is strongly recommended
staging=1

#docker-compose build cert

if [ -d "$data_path" ]; then
    read -p "Existing data found for $domain. Continue and replace existing certificate? (y/N) " decision
    if [ "$decision" != "Y" ] && [ "$decision" != "y" ]; then
        exit
    fi
fi

if [ ! -e "$data_path/conf/options-ssl-nginx.conf" ] || [ ! -e "$data_path/conf/ssl-dhparams.pem" ]; then
    echo "### Downloading recommended TLS parameters ..."
    mkdir -p "$data_path/conf"
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf >"$data_path/conf/options-ssl-nginx.conf"
    curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem >"$data_path/conf/ssl-dhparams.pem"
    echo
fi


echo "### Removing old certificate for $domain ..."
docker-compose run --rm --entrypoint "\
rm -Rf /etc/letsencrypt/live/$domain && \
rm -Rf /etc/letsencrypt/archive/$domain && \
rm -Rf /etc/letsencrypt/renewal/$domain.conf" cert
echo


if [ $staging != "0" ]; then staging_arg="--staging"; fi

#docker-compose run --rm --entrypoint "
#  echo 'dns_digitalocean_token = 191939a013dfd3a435fa8de7965ae49c5134426bfe7aae6694ed700631341809' > certbot-creds.ini \
#  chmod go-rwx certbot-creds.ini
#"

docker-compose run --rm --entrypoint "\
  certbot certonly\
    -m kamil1marczak@gmail.com \
    --staging \
    --force-interactive \
    --expand \
    --no-eff-email \
    --agree-tos \
    --dns-digitalocean \
    --dns-digitalocean-credentials certbot-creds.ini \
    --dns-digitalocean-propagation-seconds 20 \
    -d api.sit-messenger.com" cert
echo

docker-compose run --rm --entrypoint "\
  certbot certonly\
  -m kamil1marczak@gmail.com \
  --force-interactive \
  --no-eff-email \
  --agree-tos \
  --dns-digitalocean \
  --dns-digitalocean-credentials certbot-creds.ini \
  -d \*.sit-messenger.com" cert
echo


echo "### Starting nginx ..."
docker-compose up --force-recreate -d
echo


