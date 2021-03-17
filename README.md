
sudo docker-compose exec web python manage.py initial_deployment

sudo docker-compose exec web python manage.py shell_plus --ipython
sudo docker-compose exec web python manage.py createsuperuser
sudo docker-compose exec web python manage.py generateschema --file openapi-schema.yml
sudo docker-compose exec web python manage.py export route_registered_with_the_router

**ipython shell** <br>
sudo docker-compose exec web python manage.py shell


sudo docker-compose exec web sh

**clear data** <br>
sudo docker system prune -a
sudo docker volume prune
sudo docker-compose exec web python manage.py flush

https://linuxize.com/post/how-to-remove-docker-images-containers-volumes-and-networks/
For docker-compose the correct way to remove volumes would be docker-compose down --volumes or docker-compose down --rmi all --volumes

sudo docker-compose ps
sudo docker container ls -a
sudo docker container stop 2fe70c7c1839
sudo docker container rm 2fe70c7c1839
sudo docker system prune -a

sudo docker volume ls

**pg admin** <br>
https://towardsdatascience.com/how-to-run-postgresql-and-pgadmin-using-docker-3a6a8ae918b5


deployment on digital ocean:

(local) git archive --format tar --output ./project.tar main
(local) rsync ./project.tar root@$DIGITAL_OCEAN_IP_ADDRESS:/tmp/project.tar
(ssh) rm -rf /app/* && tar -xf /tmp/project.tar -C /app
(ssh) cd /app/
(ssh) docker-compose -f /app/docker-compose.prod.yml build
(ssh) docker-compose -f /app/docker-compose.prod.yml up


sudo kill $(sudo lsof -t -i:80)

ssh user@server -o ServerAliveInterval=15

