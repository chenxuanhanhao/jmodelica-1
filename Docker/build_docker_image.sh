#!/bin/bash

# This script is used with generate_dockerfile because it builds what generate_dockerfile
# generated. Before running docker build it also checks for the hash corresponding to given
# config and, if it already exists locally it will not build the docker image.

BASE_DIR=$(dirname "$0")
CONFIG=$1
USER_CONFIG=$2
TAG_NAME=$3
DOCKERFILE_DIR=$4
OVERRIDE_TARGET=$5

echo "\tbuild_docker_image: Building docker image..."
echo -e "\tbuild_docker_image: using CONFIG $CONFIG USER_CONFIG $USER_CONFIG and TAG_NAME $TAG_NAME"
echo -e "\tbuild_docker_image: Current working directory is ${PWD}"

[[ -e "$CONFIG" ]] && source $CONFIG || echo "build_docker_image: No such config $CONFIG"
[[ -e "$USER_CONFIG" ]] && source $USER_CONFIG || echo "build_docker_image: No such user config $USER_CONFIG"

echo -e "\tbuild_docker_image: Generating hash..."
# check if docker image with given config already exists
HASH_GEN_TAG="$(echo -n $PLATFORM $DIST_VERSION $BUILD_TARGET $PYTHON_VERSION $OVERRIDE_TARGET | md5sum | awk '{print $1}')"

# build image if not found among images
if ! docker images | grep -q "$HASH_GEN_TAG" ; then
    mkdir -p $DOCKERFILE_DIR
    cp $BASE_DIR/generation/Dockerfile $DOCKERFILE_DIR
    echo -e "\tbuild_docker_image: Running docker build with Dockerfile located in $DOCKERFILE_DIR..."
    echo -e "\tbuild_docker_image: Tagging image with ${TAG_NAME}:${HASH_GEN_TAG}"
    docker build -t "${TAG_NAME}:${HASH_GEN_TAG}" -f $DOCKERFILE_DIR/Dockerfile .
else
    echo -e "\tbuild_docker_image: Used cached image tagged with ${TAG_NAME}:${HASH_GEN_TAG}"
fi
DOCKER_ID=$(docker images | grep "$HASH_GEN_TAG" | awk '{print $3}')
echo -e "\tDocker build finished and found DOCKER_ID=${DOCKER_ID}"

# 
#    Copyright (C) 2018 Modelon AB
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the Common Public License as published by
#    IBM, version 1.0 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY. See the Common Public License for more details.
#
#    You should have received a copy of the Common Public License
#    along with this program.  If not, see
#     <http://www.ibm.com/developerworks/library/os-cpl.html/>.
