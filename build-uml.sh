#!/usr/bin/env bash

#
# To build the UML files.
#
export PLANT_UML_JAR_FILE="./bin/plantuml/plantuml.jar"

#
# To check that it is the MIT licence version being used.
#
# java -jar ${PLANT_UML_JAR_FILE} -license

java -jar ${PLANT_UML_JAR_FILE} docs/images/*.plantuml