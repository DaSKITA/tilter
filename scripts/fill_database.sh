#!/usr/bin/env bash

SCRIPT_DIR=$(cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )
BASEDIR=$(dirname "$SCRIPT_DIR")

if [ -d "$BASEDIR/.venv" ]; then
    source $BASEDIR/.venv/bin/activate
else
    echo "No Python Environment found. Actiavte your python environment!"
    exit
fi

pip install tqdm==4.59.0 click==7.1.2 requests==2.25.1
python $SCRIPT_DIR/feeder.py jsonify-policies -d $BASEDIR/data -l "de"
python $SCRIPT_DIR/feeder.py post-tasks -d $BASEDIR/data/json_policies
deactivate
