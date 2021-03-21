![GitHub release (latest by date)](https://img.shields.io/github/v/release/kamil1marczak/SIT-messenger-backend)
![GitHub language count](https://img.shields.io/github/languages/count/kamil1marczak/SIT-messenger-backend)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/kamil1marczak/SIT-messenger-backend)
![Website](https://img.shields.io/website?down_color=lightgrey&down_message=offline&up_color=blue&up_message=online&url=http%3A%2F%2Fsit-messenger.com%2F)
[![Maintainability](https://api.codeclimate.com/v1/badges/f3575e4a26896cdc9720/maintainability)](https://codeclimate.com/github/kamil1marczak/SIT-messenger-backend/maintainability)
![GitHub Release Date](https://img.shields.io/github/release-date/kamil1marczak/SIT-messenger-backend)


![alt text](sit-logo.png "Title" )

<img alt="Python" src="https://img.shields.io/badge/python%20-%2314354C.svg?&style=for-the-badge&logo=python&logoColor=white"/>
<img alt="Django" src="https://img.shields.io/badge/django%20-%23092E20.svg?&style=for-the-badge&logo=django&logoColor=white"/>
<img alt="Nginx" src="https://img.shields.io/badge/nginx%20-%23009639.svg?&style=for-the-badge&logo=nginx&logoColor=white"/>
<img alt="Postgres" src ="https://img.shields.io/badge/postgres-%23316192.svg?&style=for-the-badge&logo=postgresql&logoColor=white"/>
<img alt="Docker" src="https://img.shields.io/badge/docker%20-%230db7ed.svg?&style=for-the-badge&logo=docker&logoColor=white"/>

# SIT Messenger Backend

> SIT Messenger is a fully encrypted chat application. SIT Messenger Backed is Docker Compose application with Django Rest Framework. Api Client Application is SIT Messenger Frontend.

#### Project is deployed on page http://sit-messenger.com/

### 🏠 [Homepage](https://sit-messenger.com/)


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

[![ForTheBadge built-with-swag](http://ForTheBadge.com/images/badges/built-with-swag.svg)](https://GitHub.com/Naereen/)

## Show your support

Give a ⭐️ if this project helped you!