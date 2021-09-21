#!/usr/bin/env bash

#
# Make sure python3 is available. 
# We need python to be working at 3.8.0 or above.
#

# The roguelike server is where ?
export K_AND_K_SERVER_URL="http://localhost:3000"
#export K_AND_K_SERVER_URL="http://frontend-kandk.apps.jordan-test.cp.fyre.ibm.com/cave/0"

# To connect to someone else's server... eg:
#export K_AND_K_SERVER_URL="http://9.145.175.200:3000"

# If connecting to someone else's server, find their external internet address
# using the last line when you run the `ifconfig` command
# or use:
# ifconfig | tail -1 | cut -f2 -d' '

# Pick up some environment settings which are shared with other ways of running the bot.
. ./runtime-env-settings.sh

# Invoke the roguebot python package. In effect, this calls the `__main__.py` module in the `roguebot` package.
python3 -m roguebot 2>&1 | tee out.txt


