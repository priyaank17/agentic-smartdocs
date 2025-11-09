#!/bin/bash
printf "\n=======> Building\n"
docker build --platform linux/x86_64 -t artisan-text-detector-core .
