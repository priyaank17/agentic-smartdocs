#!/bin/bash
printf "\n=======> Entering Shell\n"
docker exec -it $(docker container ls  | grep 'artisan-text-detector-core:latest' | awk '{print $1}') bash
