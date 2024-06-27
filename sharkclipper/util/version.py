import argparse
import logging
import os
import re
import sys

import sharkclipper.util.file
import sharkclipper.util.log

PACKAGE_CONFIG_PATH = os.path.join(sharkclipper.util.file.ROOT_DIR, 'pyproject.toml')
OVERRIDE_VERSION_PATH = os.path.join(sharkclipper.util.file.ROOT_DIR, 'VERSION.txt')
UNKNOWN_VERSION = '?.?.?'
VERSION_REGEX = r'^version\s*=\s*["\'](\d+\.\d+\.\d+)["\']$'

def get_version():
    # First, check for the version override file.
    if (os.path.isfile(OVERRIDE_VERSION_PATH)):
        with open(OVERRIDE_VERSION_PATH, 'r') as file:
            return file.read().strip()

    # Next, check for the base version in the project config.
    if (not os.path.isfile(PACKAGE_CONFIG_PATH)):
        logging.error("Could not find version file: '%s'." % (PACKAGE_CONFIG_PATH))
        return UNKNOWN_VERSION

    with open(PACKAGE_CONFIG_PATH, 'r') as file:
        for line in file:
            line = line.strip()
            if (line == ''):
                continue

            match = re.search(VERSION_REGEX, line)
            if (match is not None):
                return match.group(1)

    return UNKNOWN_VERSION

def main():
    args = _get_parser().parse_args()
    sharkclipper.util.log.init_from_args(args)

    print(get_version())

    return 0

def _get_parser():
    parser = argparse.ArgumentParser(description = "Get the server's version.")
    sharkclipper.util.log.set_cli_args(parser)
    return parser

if __name__ == '__main__':
    sys.exit(main())
