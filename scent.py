from sniffer.api import *  # import the really small API
import os
import termstyle

from pylint import lint
from subprocess import call
import nose

# you can customize the pass/fail colors like this
pass_fg_color = termstyle.green
pass_bg_color = termstyle.bg_default
fail_fg_color = termstyle.red
fail_bg_color = termstyle.bg_default

# All lists in this variable will be under surveillance for changes.
watch_paths = ['.', 'tests/']

# this gets invoked on every file that gets changed in the directory. Return
# True to invoke any runnable functions, False otherwise.
#
# This fires runnables only if files ending with .py extension and not prefixed
# with a period.


@file_validator
def py_files(filename):
    is_py_file = False
    if filename.endswith('.py') or filename.endswith('.feature'):
        if not os.path.basename(filename).startswith('.'):
            is_py_file = True
    return is_py_file


@runnable
def coverage(*args):
    is_ok = True

    # Run unit tests with coverage. Using setup.cfg settings.
    if is_ok:
        command_coverage = "coverage run -m pytest"
        is_ok = (call(command_coverage, shell=True) == 0)

    # Pep8 linting:
    # if is_ok:
    #     command_lint = "pylint roguebot"
    #     is_ok = (call(command_lint, shell=True)==0)

    # Report on previously gathered code coverage. Using setup.cfg settings.
    if is_ok:
        command_report_coverage = "coverage report"
        is_ok = (call(command_report_coverage, shell=True) == 0)

    # Convert the data to an XML format that the VSCode Coverage Gutter plugin can understand.
    # Note: Enabling this can cause locking/contention issues on a coverage file.
    if is_ok:
        command_coverage_to_xml = "coverage xml"
        is_ok = (call(command_coverage_to_xml, shell=True) == 0)

    return is_ok
