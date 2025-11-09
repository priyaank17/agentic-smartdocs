# Sending Container to ECR repository

Follow the steps below to upload container to AWS. It pushes container to ECR, in already
created repository.

aws ecr get-login-password --profile Artisan-DataScience-461906100116 --region us-west-2 | docker login --username AWS --password-stdin 461906100116.dkr.ecr.us-west-2.amazonaws.com

docker build -t artisan-text-detector-core .

docker tag artisan-text-detector-core:latest 461906100116.dkr.ecr.us-west-2.amazonaws.com/artisan-text-detector-core:test8

docker push 461906100116.dkr.ecr.us-west-2.amazonaws.com/artisan-text-detector-core:test8
