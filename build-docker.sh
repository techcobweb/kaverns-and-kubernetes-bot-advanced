#!/usr/bin/env bash

#
# Builds a docker image with the bot inside.
#
docker build --file build/production.Dockerfile --tag roguebot .