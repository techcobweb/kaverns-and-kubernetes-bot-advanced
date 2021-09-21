#!/usr/bin/env bash

# A script which runs the tests on your current code, using a docker test environment.
# This can be used if you can't run the scripts locally for some reason, like python pre-reqs not installing
# correctly.

# Build the docker image
./build-test-env.sh

# Lets check that the test env works
docker run --rm roguebot-test-env bash ./test.sh 



