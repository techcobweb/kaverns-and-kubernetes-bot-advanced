#!/usr/bin/env bash

#
# Fred the warrior will use the `RandomExplorerBrain`
#

export K_AND_K_BOT_NAME="assassin-bot"
export K_AND_K_BOT_ROLE="warrior"


# Comment this out if you don't want debug output.
export K_AND_K_BOT_DEBUG="True"


# Speed of the bot. How many ticks does it ignore 
# before thinking of a move to make.
# 1-10. 10 is the fastest. 1 the slowest. 
# Optional. Defaults to 5.
# Useful if you want to follow the bot to see what it does,
# or slow it down.
export K_AND_K_BOT_SPEED="10"

# Each turn the bot can move along a path, how many move
# commands should it send the server at once ?
# This gives the bot warp-speed, but network vaguaries may
# cause the bot to hit walls and go in unexpected places.
# Optional. Defaults to 1
export K_AND_K_BOT_ACTIONS_PER_TURN="5"



# Which port should the bot bind its' own small HTTP server up to ?
# ie: The address and port that the bots' HTTP server listens to for 
# in-coming requests.
# Kubbernetes we can inquire about the bots' health.
export K_AND_K_BOT_HTTP_SERVER_PORT=4001
export K_AND_K_BOT_HTTP_SERVER_ADDRESS=127.0.0.1

# The number of seconds the bot waits between starting up it's own 
# http server, and when it starts playing.
# This allows kubernetes to see an 'ALIVE' state for this amount of 
# time before the bot goes 'READY'
# Defaults to 0 seconds.
export K_AND_K_BOT_STARTUP_DELAY_SECONDS=1
