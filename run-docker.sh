#!/usr/bin/env bash

# host.docker.internal allows the container-resident program to connect to the localhost of the machine it is running on
# only works for docker desktop environment. Not in production on kube.
export ROGUELIKE_SERVER_URL="http://host.docker.internal:3000"

# Pick up some environment settings which are shared with other ways of running the bot.
. ./runtime-env-settings.sh

# Use -d to run it in disconnected mode
# --rm discards any state which accumulattes in the docker image as it runs.
# -e defines an environment variabble.
# roguebot is the image name. A 'latest' tag is used if not specified.
# eg: roguebot:latest 
docker run --rm \
  -it \
  -e ROGUELIKE_SERVER_HOST="$ROGUELIKE_SERVER_HOST" \
  -e ROGUELIKE_SERVER_PORT="$ROGUELIKE_SERVER_PORT" \
  -e ROGUELIKE_NAME="$ROGUELIKE_NAME" \
  -e ROGUELIKE_ROLE="$ROGUELIKE_ROLE" \
 roguebot python3 -m roguebot