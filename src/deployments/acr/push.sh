#!/usr/bin/env bash
set -euo pipefail
REGISTRY=${1:?"registry name"}
IMAGE=${2:?"image name"}
TAG=${3:-latest}

docker build -f src/deployments/docker/Dockerfile.api -t ${REGISTRY}.azurecr.io/${IMAGE}:${TAG} .
docker push ${REGISTRY}.azurecr.io/${IMAGE}:${TAG}
