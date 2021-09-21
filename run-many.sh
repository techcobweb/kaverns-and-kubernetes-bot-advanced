#!/usr/bin/env bash

export ROGUELIKE_SERVER_URL="http://localhost:3000"
#export ROGUELIKE_SERVER_URL="http://cave1-roguelike.apps.kaverns.cp.fyre.ibm.com/"

# Pick up some environment settings which are shared with other ways of running the bot.
. ./runtime-env-settings.sh

# Invoke the roguebot python package. In effect, this calls the `__main__.py` module in the `roguebot` package.
export players=2
export ROGUELIKE_DEBUG="False"

for ((i=0; i<$players; i++)) 
do 
    echo "ROGUELIKE_BOT_HTTP_SERVER_PORT : ${ROGUELIKE_BOT_HTTP_SERVER_PORT}"
    python -m roguebot 2>&1 & 
    export ROGUELIKE_BOT_HTTP_SERVER_PORT=$((${ROGUELIKE_BOT_HTTP_SERVER_PORT}+1))
done

echo "Hit enter to stop things"
read var1

for ((i = 0; i < $players; i++)) 
do 
    kill $i ; 
done
