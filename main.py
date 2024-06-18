#!/usr/bin/env python3

import argparse
import sys

import log
import ffmpeg
import server

def check_requirements():
    result = True

    if (not ffmpeg.is_available()):
        result = False

    return result

def main():
    args = _get_parser().parse_args()
    log.init_from_args(args)

    if (not check_requirements()):
        print("Not all requirements to run tool are met.")
        return 1

    server.run(**(vars(args)))

    return 0

def _get_parser():
    parser = argparse.ArgumentParser(description = 'Run a web GUI for clipping fin images from shark videos.')

    parser.add_argument('--port', dest = 'port',
        action = 'store', type = int, default = server.DEFAULT_PORT,
        help = 'Port to launch the web GUI on (default: %(default)s).')

    parser.add_argument('--out', dest = 'out_dir',
        action = 'store', type = str, default = server.DEFAULT_OUT_DIRNAME,
        help = 'Where to store output files (default: %(default)s).')

    parser.add_argument('--no-cleanup', dest = 'cleanup_temp',
        action = 'store_false', default = True,
        help = 'Do not cleanup any intermitent results (good for debugging) (default: %(default)s).')

    log.set_cli_args(parser)

    return parser

if __name__ == '__main__':
    sys.exit(main())
