FROM certbot/dns-digitalocean:latest

RUN echo 'dns_digitalocean_token = 191939a013dfd3a435fa8de7965ae49c5134426bfe7aae6694ed700631341809' > certbot-creds.ini
RUN chmod go-rwx certbot-creds.ini

#COPY ./compose/production/cert/start start
#RUN sed -i 's/\r$//g' /start
#RUN chmod +x start
#RUN certbot certonly -m kamil1marczak@gmail.com --force-interactive --no-eff-email --agree-tos --dns-digitalocean --dns-digitalocean-credentials certbot-creds.ini --dns-digitalocean-propagation-seconds 20 -d api.sit-messenger.com -d www.api.sit-messenger.com
#RUN certbot certonly -m kamil1marczak@gmail.com --force-interactive --no-eff-email --agree-tos --dns-digitalocean --dns-digitalocean-credentials certbot-creds.ini -d \*.sit-messenger.com