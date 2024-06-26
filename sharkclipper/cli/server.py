#!/usr/bin/env python3

import argparse
import sys

import sharkclipper.api.server
import sharkclipper.util.log
import sharkclipper.util.ffmpeg

def check_requirements():
    result = True

    if (not sharkclipper.util.ffmpeg.is_available()):
        result = False

    return result

def main():
    args = _get_parser().parse_args()
    sharkclipper.util.log.init_from_args(args)

    if (not check_requirements()):
        print("Not all requirements to run tool are met.")
        return 1

    sharkclipper.api.server.run(**(vars(args)))

    return 0

def _get_parser():
    parser = argparse.ArgumentParser(description = 'Run a web GUI for clipping fin images from shark videos.')

    parser.add_argument('--port', dest = 'port',
        action = 'store', type = int, default = sharkclipper.api.server.DEFAULT_PORT,
        help = 'Port to launch the web GUI on (default: %(default)s).')

    parser.add_argument('--out', dest = 'out_dir',
        action = 'store', type = str, default = sharkclipper.api.server.DEFAULT_OUT_DIRNAME,
        help = 'Where to store output files (default: %(default)s).')

    parser.add_argument('--no-cleanup', dest = 'cleanup_temp',
        action = 'store_false', default = True,
        help = 'Do not cleanup any intermitent results (good for debugging) (default: %(default)s).')

    sharkclipper.util.log.set_cli_args(parser)

    return parser

if __name__ == '__main__':
    sys.exit(main())
