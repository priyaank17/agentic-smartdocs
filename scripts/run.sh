#!/bin/bash
printf "\n=======> Running the container\n"
docker run -v ~/.aws-lambda-rie:/aws-lambda -p 9105:8080 artisan-text-detector-core:latest 
    --entrypoint /aws-lambda/aws-lambda-rie
