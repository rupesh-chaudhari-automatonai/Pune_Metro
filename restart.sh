#!/bin/bash

# Stop and remove the Docker containers
docker compose down

docker stop mongo-example

# Remove Kafka data directory and all files in the frames directory
rm -rf Kafka/ frames/*

docker system prune

docker run -d -p 27017:27017 --name=mongo-example mongo:latest

# Start Docker containers in detached mode
docker compose up -d
