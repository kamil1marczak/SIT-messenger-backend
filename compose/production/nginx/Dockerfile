FROM nginx:1-alpine as production
#WORKDIR /app

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
#COPY nginx.conf /etc/nginx/nginx.conf
ADD ./certbot/conf /etc/letsencrypt
ADD ./certbot/www /var/www/certbot

EXPOSE 80
#CMD ["nginx", "-g", "daemon off;"]
