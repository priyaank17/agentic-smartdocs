#!/bin/bash
printf "\n=======> Killing container\n"
docker kill $(docker container ls  | grep 'artisan-text-detector-core:latest' | awk '{print $1}')
