#!/bin/bash
printf "\n=======> Tailing logs\n"
docker logs --follow $(docker container ls  | grep 'artisan-text-detector-core:latest' | awk '{print $1}')
