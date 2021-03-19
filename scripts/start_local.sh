#!/usr/bin/env bash

SCRIPT_DIR=$(cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )
BASEDIR=$(dirname "$SCRIPT_DIR")
echo $SCRIPT_DIR
export FLASK_ENV="development"
export FLASK_DEBUG=true
export FLASK_APP=main.py
export $(grep -v '^#' $BASEDIR/app/secrets/local/flask-local.env | xargs -0)

gnome-terminal -- bash -c "sh ${SCRIPT_DIR}/start_mongo_db.sh"

(cd "${BASEDIR}/app" && flask run )
