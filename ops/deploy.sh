SCRIPT_DIR=$(cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )
BASEDIR=$(dirname "$SCRIPT_DIR")


# generate docker secrets
echo "SuperUser" | docker secret create mongo_password -
docker secret create mongo_user "root"

# start application
(cd $BASEDIR | exit
docker-compose up --build
)
