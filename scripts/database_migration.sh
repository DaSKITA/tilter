#!/usr/bin/env bash

SCRIPT_DIR=$(cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )
BASEDIR=$(dirname "$SCRIPT_DIR")

python $SCRIPT_DIR/database_migration/database_migration.py -t delete_unbound_obj
python $SCRIPT_DIR/database_migration/database_migration.py -t task_html_entry
python $SCRIPT_DIR/database_migration/database_migration.py -t subtask_annotation
