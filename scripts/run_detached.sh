#!/bin/bash
printf "\n=======> Running the container\n"
docker run -d -v ~/.aws-lambda-rie:/aws-lambda -p 9000:8080 artisan-text-detector-core:latest --entrypoint /aws-lambda/aws-lambda-rie
