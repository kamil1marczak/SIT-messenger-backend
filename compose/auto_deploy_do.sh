#! /bin/bash

# This shell scripts show you how to quickly deploy your project to your
# Digital Ocean Droplet

# generate TAR file from git
git archive --format tar --output ./project.tar main
echo 'start uploading project'
# upload the file to Digital Ocean Droplet
rsync ./project.tar root@$DIGITAL_OCEAN_IP_ADDRESS:/tmp/project.tar
echo 'project uploaded, start building image'

echo 'Building image...'
ssh -o StrictHostKeyChecking=no root@$DIGITAL_OCEAN_IP_ADDRESS << 'ENDSSH'
    mkdir -p /app
    rm -rf /app/* && tar -xf /tmp/project.tar -C /app
    docker-compose -f /app/docker-compose.prod.yml build
ENDSSH
echo 'Build complete.'
