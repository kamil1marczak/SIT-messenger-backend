

![alt text](sit-logo.png "Title" )

# SIT messenger - backend

> SIT Messenger is a fully encrypted chat application. SIT Messenger Frontend is Nuxt.js web client for backend Django Rest API service.

### 🏠 [Homepage](https://sit-messenger.com/)

### ✨ [Demo](https://sit-messenger.com/)

## Installation and usage in production
1. Clone repo
2. Install docker-compose
3. Build images
  ```
  docker-compose build
  ```
4. Run containers
  ```
  docker-compose up
  ```
5. application will be available on ports 80 (http) adn 443 (htpps)

## Installation and usage in production
1-2 ame a in production
3. Build images
  ```
  docker-compose -f docker-compose.dev.yml build
  ```
4. Run containers
  ```
  docker-compose -f docker-compose.dev.yml up
  ```
5. application will be available http://localhost:8000/


## Application structure

Application component are packed inside docker-compose. Inside docker there are several linked services as separate
containers:

- #### nginx
  A web server, used for the purpose of reverse proxy, load balancer (jointly with Gunicorn in "web" container, later in
  the text), and parse HTTPS protocol (jointly with "certbot" container )
- #### certbot
  A software tool for automatically using Let’s Encrypt certificates on manually-administrated websites to enable HTTPS
- #### web
  The Main container with Django Rest Framework application. This container is collection of application organised to
  manage encrypted data hosted in storage, data from a database, integrate applications n from other contenders and
  finally parse Rest API as entry point
- #### db
  A Postgres relational database.
- #### redis
  An in-memory data structure store used to store cache
- #### rabbitmq
  A message-broker used by celery_worker container.
- #### celery_worker
  An asynchronous task and job queue. Celery worker mange caches by distributed message passing. Celery worker use "
  redis" container ad storage and "rabbitmq" container as message-broker
- #### celery_beat
  A specific usage of celery to manage recurring job queue in given time intervals.
- flower. A web based tool for monitoring and administrating Celery clusters.

## Data encryption:

- chats (which contain messages) are store as models.FileField where chats are stored as encrypted binary files and
  database store location to file
- everytime messages are saved to/read from storage, data is encrypted / decrypted by individual (for each chat).
  Cryptography is held under Fernet protocol provided by Cryptography
  framework [Cryptography Framework](https://cryptography.io/en/latest/fernet.html).
- It is not completed in this version but there are complited snipets inside aplication to provide encryption by tokens
  that base on, individual uudi created and stored on client side and salt created and stored on Django application.
  Lack of implementation is caused by the limitation of "SIT Messenger Frontend" the JavaScript client of Rest
  API [SIT Messenger Frontend](https://github.com/kamil1marczak/SIT-messenger-frontend)

## Author

👤 **Kamil Marczak**

* Github: [@kamil1marczak](https://github.com/kamil1marczak)
* LinkedIn: [@kamil-marczak-71765b48](https://linkedin.com/in/kamil-marczak-71765b48)

## Show your support

Give a ⭐️ if this project helped you!