#!/usr/bin/env bash

#
# Tests the bot code in every way we currently can...
#


# Lint the source code to conform to pep8 standards
# ... But that generates too many trivial messages.
# So we can supress messages using the --disable option.
#   R0913: Too many arguments for a method.
#   C0116: Method missing docstring.
#   C0301: Line too long
#   C0303: Trailing whitespace
#   R0902: Too many instance attributes
#   C0114: Missing module docstring
#   R0903: Too few public methods
#   C0305: Trailing newlines
#   W0611: Unused import
#   W0613: Unused argument
#   R0201: Method could be a function (no-self-use)
#
# --const-rgx=... allow single-letter parameter variable names like x,y,z.
# --argument-rgx... allow single-letter variable argument names like x,y,z.
#
lint_output_file="./lint-output.txt"
pylint --fail-under 7.0 \
--disable=R0913,C0116,C0301,C0303,R0902,C0114,R0903,C0305,W0611,W0613,R0201 \
--variable-rgx='[a-z_][a-z0-9_]{0,30}$' \
--argument-rgx='[a-z_][a-z0-9_]{0,30}$' \
roguebot/* > ${lint_output_file}

echo "-------------------------pylint-------------------------"

# Show warnings and errors...
cat lint-output.txt | grep ": W"
cat lint-output.txt | grep ": E"

# Show overall code score...
cat lint-output.txt | grep "Your code has been rated"
echo "More detailed lint output is available here: ${lint_output_file}"

# Run the unit tests gathering data into .coverage, as dictated by setup.cfg
# --full-trace means "if you kill it with Ctrl-C signal, show a full stack trace"
# This is really helpful if your logic loops and seems to hang. You can find out
# at least one point where the loop is.
# For more detail, add --full-trace
coverage run -m pytest 

# Format and display a textual report.
coverage report 

# Convert it to cov.xml so that VSCode plugin can display red/green 
# coverage with Shift-Cmd-7 toggle.
coverage xml
