#!/usr/bin/env bash

# A script which builds a docker container, and installs everything we need to test our code in.
# It really checks that nothing has been left out of the setup.sh or requirements from pip.
# A full unit-testing environment is created, so it can then executed inside the docker container.
# See the test-in-docker.sh script for more info.

 

# Build the docker image of the test environment.
docker build \
--build-arg USER_ID=$(id -u) \
--build-arg GROUP_ID=$(id -g) \
--file build/testing.Dockerfile \
--tag roguebot-test-env .

