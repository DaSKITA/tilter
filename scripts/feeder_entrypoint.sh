#!/bin/bash

SCRIPT_DIR=$(cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )
BASEDIR=$(dirname "$SCRIPT_DIR")

RESPONSE=$(curl -G --write-out '%{http_code}' --silent --output /dev/null http://localhost:5000/)
until [ ${RESPONSE} == 200 ]; do
    >&2 echo "Service not up yet, sleeping..."
    sleep 1
    RESPONSE=$(curl -G --write-out '%{http_code}' --silent --output /dev/null http://localhost:5000/)
    echo "HTTP-Error Code:"
    echo $RESPONSE
done

>&2 echo "Service is up, feeding data..."
python $SCRIPT_DIR/feeder.py jsonify-policies -d $BASEDIR/data/official_policies -o $BASEDIR/data/json_policies -u $BASEDIR/data/official_policies/url-mappings.json
python $SCRIPT_DIR/feeder.py post-tasks -d $BASEDIR/data/json_policies -u "http://localhost:5000/"
