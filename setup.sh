#!/usr/bin/env bash

#
# Make sure python3 is available. 
# We need python to be working at 3.8.0 or above.
#

pip install --upgrade -r build/requirements.txt
pip install --upgrade -r build/requirements-dev.txt
pip install --upgrade -r build/requirements-test.txt


python3 ./setup.py develop




