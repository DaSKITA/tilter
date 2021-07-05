#!/usr/bin/env bash

SCRIPT_DIR=$(cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )
BASEDIR=$(dirname "$SCRIPT_DIR")
ENV_FILE_DIR="${BASEDIR}/app/secrets/local/mongodb-local.env"

docker run -p 27017:27017 --env-file=$ENV_FILE_DIR -v $BASEDIR/volumes:/data/db mongo:4.4.4
