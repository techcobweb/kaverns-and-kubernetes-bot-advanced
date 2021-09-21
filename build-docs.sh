#!/usr/bin/env bash

#
# Builds html docs locally
#
pushd docs
make clean gen html
popd

open ./docs/_build/html/index.html
