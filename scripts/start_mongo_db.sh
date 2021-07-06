#!/usr/bin/env bash

SCRIPT_DIR=$(cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )
BASEDIR=$(dirname "$SCRIPT_DIR")
ENV_FILE_DIR="${BASEDIR}/app/secrets/local/mongodb-local.env"

docker run -p 27017:27017 -v $BASEDIR/volumes:/data/db \
    -e MONGO_INITDB_ROOT_USERNAME=$MONGODB_USERNAME \
    -e MONGO_INITDB_ROOT_PASSWORD=$MONGODB_PASSWORD \
    -e MONGO_INITDB_DATABASE=$MONGODB_INITDB_DATABASE \
    -e MONGODB_DATA_DIR=/data/db \
    -e MONDODB_LOG_DIR=/dev/null \
    mongo:4.4.4
